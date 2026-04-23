
import requests
from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

from lxml import etree, html as lxml_html

from app.models.task import CrawledData, Task, TaskLog
from app.spider.browser_renderer import BrowserRenderer
from app.utils.task_presets import merge_request_config


class SimpleCrawler:
    BAD_TITLE_VALUES = {
        '全部导航',
        '导航',
        '首页',
        '正文',
        '内容',
    }

    COMMON_DETAIL_TITLE_SELECTORS = [
        'h1 .title',
        'h1.title',
        'h1',
        '.head-line .title',
        '.mheader .title',
        '.article-title',
        '.content-title',
        '.news_title',
        '.articleTitle',
        '.ArticleTitle',
        '.detail-title',
    ]

    COMMON_DETAIL_CONTENT_SELECTORS = [
        '#detailContent',
        '.rm_txt_con',
        'article',
        '.article',
        '.article-content',
        '.articleContent',
        '.ArticleContent',
        '.content',
        '.content-main',
        '.news_content',
        '.newsContent',
        '.detail-content',
        '.main-content',
        '.entry-content',
        '.TRS_Editor',
        '#zoom',
        '.pages_content',
        '.article_txt',
    ]

    COMMON_DETAIL_SOURCE_SELECTORS = [
        '.source',
        '.origin',
        '.comefrom',
        '.news-source',
        '.ly',
        '.info span',
    ]

    COMMON_DETAIL_TIME_SELECTORS = [
        'time',
        '.time',
        '.date',
        '.pubtime',
        '.publish-time',
        '.header-time',
        '.info',
    ]

    EXCLUDED_LINK_TEXT = (
        '更多',
        '登录',
        '注册',
        '打开app',
        '打开App',
        '首页',
        '下一页',
        '上一页',
        '关于',
        '联系我们',
        '客户端下载',
        '专题',
        '视频',
        '图片',
        '邮箱',
    )

    EXCLUDED_LINK_SCHEMES = ('javascript:', 'mailto:', 'tel:', '#')
    EXCLUDED_LINK_SUFFIXES = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.pdf', '.zip', '.mp4', '.mp3')

    def __init__(self, task_id, stop_event=None):
        self.task_id = task_id
        self.task = None
        self.stop_event = stop_event
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.browser_renderer = BrowserRenderer(logger=self.log)

    def refresh_task(self):
        self.task = Task.get_by_id(self.task_id)
        return self.task

    def log(self, message, level='info'):
        TaskLog.create(self.task_id, message, level)
        print(f"[Task {self.task_id}] {message}")

    def should_stop(self):
        if self.stop_event and self.stop_event.is_set():
            return True
        task = Task.get_by_id(self.task_id)
        return bool(task and task.get('stop_requested'))

    def mark_stopped(self, progress):
        self.log('任务已停止', 'warning')
        Task.update_runtime(
            self.task_id,
            status='stopped',
            progress=progress,
            stop_requested=False,
            finished_at=datetime.now(),
        )

    def fetch_with_request(self, url, request_config):
        try:
            method = (request_config.get('method') or 'GET').upper()
            headers = request_config.get('headers') or {}
            cookies = request_config.get('cookies') or {}
            body = request_config.get('body')
            body_type = (request_config.get('body_type') or 'json').lower()
            timeout = int(request_config.get('timeout') or 10)

            request_kwargs = {
                'headers': headers or None,
                'cookies': cookies or None,
                'timeout': timeout,
            }
            if method == 'POST':
                if body_type == 'json' and isinstance(body, (dict, list)):
                    request_kwargs['json'] = body
                elif body_type == 'form' and isinstance(body, dict):
                    request_kwargs['data'] = body
                elif body not in (None, ''):
                    request_kwargs['data'] = body

            response = self.session.request(method, url, **request_kwargs)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return {
                'html': response.text,
                'title': '',
                'final_url': response.url,
            }
        except Exception as e:
            self.log(f"请求失败: {e}", 'error')
            return None

    def fetch_with_browser(self, url, request_config):
        try:
            return self.browser_renderer.render(url, request_config)
        except Exception as error:
            self.log(f"动态渲染失败: {error}", 'error')
            return None

    def fetch(self, url, request_config):
        render_mode = (request_config.get('render_mode') or 'request').lower()
        if render_mode == 'playwright':
            self.log('使用浏览器渲染抓取页面')
            return self.fetch_with_browser(url, request_config)

        return self.fetch_with_request(url, request_config)

    def _normalize_selector_config(self, config):
        normalized = config or {}
        fields = normalized.get('fields') or []

        if isinstance(fields, dict):
            converted = []
            for name, selector in fields.items():
                converted.append(
                    {
                        'name': name,
                        'selector': selector.get('selector', ''),
                        'selector_type': selector.get('selector_type', 'css'),
                        'extract_type': selector.get('type', 'text'),
                        'attr': selector.get('attr', 'href'),
                    }
                )
            normalized['fields'] = converted

        normalized.setdefault('list_selector', '')
        normalized.setdefault('list_selector_type', 'css')
        normalized.setdefault('fields', [])
        return normalized

    def _build_context(self, fragment_html):
        fragment_html = fragment_html or ''
        return {
            'html': fragment_html,
            'soup': BeautifulSoup(fragment_html, 'lxml'),
            'tree': lxml_html.fromstring(fragment_html) if fragment_html.strip() else None,
        }

    def _first_non_empty_text(self, soup, selectors):
        for selector in selectors:
            try:
                node = soup.select_one(selector)
            except Exception:
                node = None
            if node:
                text = node.get_text(' ', strip=True)
                if text and not self.is_bad_title(text):
                    return text
        return ''

    def _first_non_empty_meta(self, soup, meta_names):
        for meta_name in meta_names:
            node = soup.find('meta', attrs={'name': meta_name})
            if node:
                content = (node.get('content') or '').strip()
                if content and not self.is_bad_title(content):
                    return content
        return ''

    def clean_title(self, title):
        text = (title or '').strip()
        if not text:
            return ''

        separators = ['--', '_', '丨', '|']
        for separator in separators:
            if separator in text:
                parts = [part.strip() for part in text.split(separator) if part.strip()]
                if parts:
                    text = max(parts, key=len)
                    break

        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_bad_title(self, title):
        text = self.clean_title(title)
        if not text:
            return True
        if text in self.BAD_TITLE_VALUES:
            return True
        if '导航' in text and len(text) <= 8:
            return True
        return False

    def choose_best_title(self, soup):
        candidates = []

        for selector in self.COMMON_DETAIL_TITLE_SELECTORS:
            try:
                node = soup.select_one(selector)
            except Exception:
                node = None
            if not node:
                continue
            text = self.clean_title(node.get_text(' ', strip=True))
            if self.is_bad_title(text):
                continue
            score = len(text)
            if node.name == 'h1':
                score += 50
            if 'title' in ' '.join(node.get('class', [])).lower():
                score += 20
            candidates.append((score, text))

        meta_title = self.clean_title(self._first_non_empty_meta(soup, ['og:title', 'twitter:title', 'title']))
        if meta_title and not self.is_bad_title(meta_title):
            candidates.append((len(meta_title) + 30, meta_title))

        if soup.title:
            page_title = self.clean_title(soup.title.get_text(' ', strip=True))
            if page_title and not self.is_bad_title(page_title):
                candidates.append((len(page_title) + 10, page_title))

        if not candidates:
            return ''

        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def detail_item_has_meaningful_content(self, item):
        if not item:
            return False
        title = (item.get('title') or '').strip()
        content = (item.get('content') or '').strip()
        return bool(title) and len(content) >= 40

    def _best_content_text(self, soup):
        best_text = ''

        for selector in self.COMMON_DETAIL_CONTENT_SELECTORS:
            try:
                node = soup.select_one(selector)
            except Exception:
                node = None
            if node:
                text = node.get_text(' ', strip=True)
                if len(text) > len(best_text):
                    best_text = text

        if len(best_text) >= 80:
            return best_text

        candidates = []
        for node in soup.find_all(['article', 'div', 'section', 'main']):
            text = node.get_text(' ', strip=True)
            if len(text) < 80:
                continue
            paragraph_count = len(node.find_all('p'))
            link_text_length = sum(len(link.get_text(' ', strip=True)) for link in node.find_all('a'))
            link_density = link_text_length / max(len(text), 1)
            score = len(text) + paragraph_count * 200 - int(link_density * 2000)
            candidates.append((score, text))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            return candidates[0][1]

        body = soup.body.get_text(' ', strip=True) if soup.body else ''
        return body

    def extract_article_from_html(self, html, page_url):
        soup = BeautifulSoup(html or '', 'lxml')
        if not soup:
            return None

        title = self.choose_best_title(soup)

        content = self._best_content_text(soup)
        if len(content.strip()) < 40:
            content = self._first_non_empty_meta(soup, ['description', 'og:description']) or content
        source = self._first_non_empty_text(soup, self.COMMON_DETAIL_SOURCE_SELECTORS)
        if not source:
            source = self._first_non_empty_meta(soup, ['source'])
        publish_time = self._first_non_empty_text(soup, self.COMMON_DETAIL_TIME_SELECTORS)
        if not publish_time:
            publish_time = self._first_non_empty_meta(soup, ['publishdate', 'pubdate'])

        if not title and not content:
            return None

        if len(content.strip()) < 40 and not title:
            return None

        return {
            'title': title.strip(),
            'content': content.strip(),
            'url': page_url,
            'extra': {
                'source': source.strip(),
                'publish_time': publish_time.strip(),
            },
        }

    def _domain_candidates(self, url):
        host = urlparse(url).netloc.lower()
        if not host:
            return set()
        parts = host.split('.')
        domains = {host}
        if len(parts) >= 2:
            domains.add('.'.join(parts[-2:]))
        return domains

    def is_candidate_link(self, base_url, href, text):
        href = (href or '').strip()
        text = (text or '').strip()
        if not href or not text:
            return False
        if any(href.lower().startswith(prefix) for prefix in self.EXCLUDED_LINK_SCHEMES):
            return False
        if any(href.lower().endswith(suffix) for suffix in self.EXCLUDED_LINK_SUFFIXES):
            return False
        if len(text) < 6:
            return False
        if any(keyword in text for keyword in self.EXCLUDED_LINK_TEXT):
            return False

        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        if parsed.scheme not in {'http', 'https'}:
            return False

        base_domains = self._domain_candidates(base_url)
        candidate_domains = self._domain_candidates(absolute_url)
        if base_domains and candidate_domains and not (base_domains & candidate_domains):
            allowed_news_combo = {'zgjx.cn', 'news.cn'}
            if not (base_domains & allowed_news_combo and candidate_domains & allowed_news_combo):
                return False

        return True

    def discover_candidate_links(self, html, base_url, limit=30):
        soup = BeautifulSoup(html or '', 'lxml')
        candidates = []
        visited = set()

        for anchor in soup.find_all('a', href=True):
            href = anchor.get('href', '')
            text = anchor.get_text(' ', strip=True)
            if not self.is_candidate_link(base_url, href, text):
                continue

            absolute_url = urljoin(base_url, href)
            if absolute_url in visited:
                continue

            score = len(text)
            lower_href = absolute_url.lower()
            if re.search(r'/\d{6,}.*?/c\.html', lower_href) or lower_href.endswith('.html') or lower_href.endswith('.htm'):
                score += 50

            parent_classes = ' '.join(anchor.parent.get('class', [])) if anchor.parent else ''
            parent_tag = anchor.parent.name if anchor.parent else ''
            if any(keyword in parent_classes.lower() for keyword in ['title', 'tit', 'news', 'article', 'list', 'item']):
                score += 30
            if parent_tag in {'h1', 'h2', 'h3', 'h4', 'li'}:
                score += 20

            if any(keyword in absolute_url for keyword in ['/news/', '/world/', '/politics/', '/story/', '/article/', '/content/']):
                score += 20

            candidates.append({'title': text, 'url': absolute_url, 'score': score})
            visited.add(absolute_url)

        candidates.sort(key=lambda item: item['score'], reverse=True)
        return candidates[:limit]

    def smart_crawl(self, html, base_url, request_config, selector_config):
        smart_mode = selector_config.get('smart_mode') or not (selector_config.get('fields') or [])
        if not smart_mode:
            return []

        article = self.extract_article_from_html(html, base_url)
        candidate_links = self.discover_candidate_links(html, base_url, limit=int(selector_config.get('smart_max_items') or 30))

        if len(candidate_links) >= 3:
            self.log(f'智能识别为列表页，发现 {len(candidate_links)} 个候选详情链接')
            detail_selector_config = {
                'detail_page': {
                    'enabled': True,
                    'link_field': 'url',
                    'max_items': int(selector_config.get('smart_max_items') or 20),
                    'selector_config': {
                        'list_selector': '',
                        'list_selector_type': 'css',
                        'fields': [
                            {'name': 'title', 'selector': 'h1 .title', 'selector_type': 'css', 'extract_type': 'text'},
                            {'name': 'content', 'selector': '#detailContent', 'selector_type': 'css', 'extract_type': 'text'},
                        ],
                    },
                    'request_config': {
                        'method': 'GET',
                        'headers': {},
                        'cookies': {},
                        'body_type': 'json',
                        'body': None,
                        'render_mode': request_config.get('render_mode') or 'auto',
                        'wait_until': request_config.get('wait_until') or 'domcontentloaded',
                        'wait_for_selector': request_config.get('wait_for_selector') or '',
                        'wait_for_timeout_ms': request_config.get('wait_for_timeout_ms') or 0,
                        'emulate_mobile': bool(request_config.get('emulate_mobile')),
                        'device_name': request_config.get('device_name') or '',
                        'timeout': int(request_config.get('timeout') or 30),
                    },
                }
            }
            items = [{'title': item['title'], 'url': item['url']} for item in candidate_links]
            return self.crawl_detail_pages(base_url, request_config, items, detail_selector_config)

        if article and len(article.get('content', '')) >= 80:
            self.log('智能识别为详情页，直接抓取当前页面正文')
            result = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'url': article.get('url', base_url),
            }
            result.update(article.get('extra', {}))
            return [result]

        return []

    def apply_result_limit(self, parsed_data, selector_config):
        if not parsed_data:
            return parsed_data

        limit = selector_config.get('result_limit')
        if limit in (None, '', 0):
            return parsed_data

        try:
            normalized_limit = max(1, int(limit))
        except (TypeError, ValueError):
            return parsed_data

        return parsed_data[:normalized_limit]

    def _select_items(self, full_html, config):
        list_selector = (config.get('list_selector') or '').strip()
        list_selector_type = (config.get('list_selector_type') or 'css').lower()

        if not list_selector:
            return [self._build_context(full_html)]

        if list_selector_type == 'xpath':
            tree = lxml_html.fromstring(full_html)
            items = tree.xpath(list_selector)
            contexts = []
            for item in items:
                if isinstance(item, etree._Element):
                    contexts.append(self._build_context(etree.tostring(item, encoding='unicode')))
                else:
                    contexts.append(self._build_context(str(item)))
            return contexts

        soup = BeautifulSoup(full_html, 'lxml')
        items = soup.select(list_selector)
        return [self._build_context(str(item)) for item in items]

    def _extract_field(self, item_context, field):
        selector = (field.get('selector') or '').strip()
        if not selector:
            return ''

        selector_type = (field.get('selector_type') or 'css').lower()
        extract_type = (field.get('extract_type') or field.get('type') or 'text').lower()
        attr = field.get('attr', 'href')

        if selector in {'&', ':self', '__self__'}:
            if selector_type == 'xpath':
                tree = item_context['tree']
                if tree is None:
                    return ''
                if extract_type == 'attr':
                    return tree.get(attr, '')
                if extract_type == 'html':
                    return etree.tostring(tree, encoding='unicode')
                text_list = [text.strip() for text in tree.itertext() if text and text.strip()]
                return ' '.join(text_list).strip()

            soup = item_context['soup']
            root = soup.body.find() if soup.body else soup.find()
            if root is None:
                return ''
            if extract_type == 'attr':
                return root.get(attr, '')
            if extract_type == 'html':
                return str(root)
            return root.get_text(' ', strip=True)

        if selector_type == 'xpath':
            tree = item_context['tree']
            if tree is None:
                return ''
            matches = tree.xpath(selector)
            if not matches:
                return ''
            first_match = matches[0]
            if isinstance(first_match, etree._Element):
                if extract_type == 'attr':
                    return first_match.get(attr, '')
                if extract_type == 'html':
                    return etree.tostring(first_match, encoding='unicode')
                text_list = [text.strip() for text in first_match.itertext() if text and text.strip()]
                return ' '.join(text_list).strip()
            return str(first_match).strip()

        soup = item_context['soup']
        element = soup.select_one(selector)
        if not element:
            return ''
        if extract_type == 'attr':
            return element.get(attr, '')
        if extract_type == 'html':
            return str(element)
        return element.get_text(' ', strip=True)

    def parse(self, html, config):
        if not html:
            return []

        config = self._normalize_selector_config(config)
        results = []

        items = self._select_items(html, config)
        field_selectors = config.get('fields', [])

        for item in items:
            data = {}
            for selector in field_selectors:
                field_name = (selector.get('name') or '').strip()
                if not field_name:
                    continue
                data[field_name] = self._extract_field(item, selector)

            if data:
                results.append(data)

        return results

    def resolve_item_url(self, base_url, candidate_url):
        if not candidate_url:
            return ''
        return urljoin(base_url, candidate_url)

    def crawl_detail_pages(self, base_url, request_config, parsed_data, selector_config):
        detail_config = selector_config.get('detail_page') or {}
        if not detail_config.get('enabled'):
            return parsed_data

        detail_selector_config = detail_config.get('selector_config') or {}
        detail_request_config = merge_request_config(
            request_config,
            detail_config.get('request_config') or {},
        )
        link_field = detail_config.get('link_field') or 'url'
        max_items = int(detail_config.get('max_items') or len(parsed_data) or 0)
        if max_items <= 0:
            return parsed_data

        merged_items = []
        visited_urls = set()
        total_items = min(len(parsed_data), max_items)

        for index, item in enumerate(parsed_data[:max_items], start=1):
            detail_url = self.resolve_item_url(base_url, item.get(link_field))
            if not detail_url:
                self.log(f'第 {index} 条数据缺少详情页链接，已跳过', 'warning')
                continue
            if detail_url in visited_urls:
                continue

            visited_urls.add(detail_url)
            detail_payload = self.fetch(detail_url, detail_request_config)
            if not detail_payload:
                self.log(f'详情页抓取失败: {detail_url}', 'warning')
                continue

            detail_items = self.parse(detail_payload['html'], detail_selector_config)
            if not detail_items or not self.detail_item_has_meaningful_content(detail_items[0]):
                smart_detail = self.extract_article_from_html(detail_payload['html'], detail_url)
                if smart_detail:
                    detail_items = [
                        {
                            'title': smart_detail.get('title', ''),
                            'content': smart_detail.get('content', ''),
                            'url': smart_detail.get('url', detail_url),
                            'source': smart_detail.get('extra', {}).get('source', ''),
                            'publish_time': smart_detail.get('extra', {}).get('publish_time', ''),
                        }
                    ]
            if detail_items:
                detail_data = detail_items[0]
                merged = {**item, **detail_data}
            else:
                merged = {**item}

            merged['url'] = merged.get('url') or detail_url
            merged_items.append(merged)
            self.log(f'详情页抓取成功 {index}/{total_items}: {detail_url}')
            progress = min(95, 30 + int(index / total_items * 50))
            Task.update_runtime(self.task_id, progress=progress)

            if self.should_stop():
                break

        return merged_items or parsed_data

    def maybe_render_dynamic(self, url, request_config, parsed_data):
        render_mode = (request_config.get('render_mode') or 'request').lower()
        if render_mode != 'auto' or parsed_data:
            return None

        dynamic_config = deepcopy(request_config)
        dynamic_config['render_mode'] = 'playwright'
        dynamic_config.setdefault('wait_for_timeout_ms', 3000)
        self.log('静态抓取没有匹配到数据，尝试动态渲染兜底')
        return self.fetch_with_browser(url, dynamic_config)

    def run(self):
        task = self.refresh_task()
        if not task:
            return

        self.log('任务开始执行')
        Task.update_runtime(
            self.task_id,
            status='running',
            progress=0,
            stop_requested=False,
            last_error='',
            last_run_at=datetime.now(),
            finished_at=None,
        )

        try:
            if self.should_stop():
                self.mark_stopped(0)
                return

            Task.update_runtime(self.task_id, progress=10)
            request_config = task.get('request_config', {}) or {}
            page_payload = self.fetch(task['url'], request_config)
            if not page_payload:
                Task.update_runtime(
                    self.task_id,
                    status='failed',
                    progress=10,
                    last_error='页面请求失败',
                    finished_at=datetime.now(),
                    stop_requested=False,
                )
                return
            html = page_payload['html']

            if self.should_stop():
                self.mark_stopped(15)
                return

            Task.update_runtime(self.task_id, progress=30)
            config = task.get('selector_config', {})
            parsed_data = self.parse(html, config)

            if not parsed_data:
                parsed_data = self.smart_crawl(
                    html,
                    page_payload.get('final_url') or task['url'],
                    request_config,
                    config,
                )

            fallback_payload = self.maybe_render_dynamic(task['url'], request_config, parsed_data)
            if fallback_payload:
                html = fallback_payload['html']
                parsed_data = self.parse(html, config)
                if not parsed_data:
                    parsed_data = self.smart_crawl(
                        html,
                        fallback_payload.get('final_url') or task['url'],
                        request_config,
                        config,
                    )

            parsed_data = self.crawl_detail_pages(
                page_payload.get('final_url') or task['url'],
                request_config,
                parsed_data,
                config,
            )

            parsed_data = self.apply_result_limit(parsed_data, config)

            self.log(f'解析完成，共提取到 {len(parsed_data)} 条数据')
            if not parsed_data:
                Task.update_runtime(
                    self.task_id,
                    status='completed',
                    progress=100,
                    stop_requested=False,
                    finished_at=datetime.now(),
                    last_error='',
                )
                self.log('任务执行完成，但未匹配到数据', 'warning')
                return

            for index, item in enumerate(parsed_data, start=1):
                if self.should_stop():
                    progress = min(95, 30 + int(index / max(len(parsed_data), 1) * 60))
                    self.mark_stopped(progress)
                    return

                CrawledData.create(
                    task_id=self.task_id,
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    url=item.get('url', task['url']),
                    extra={k: v for k, v in item.items() if k not in ['title', 'content', 'url']}
                )

                progress = min(95, 30 + int(index / len(parsed_data) * 60))
                Task.update_runtime(self.task_id, progress=progress)

            Task.update_runtime(
                self.task_id,
                status='completed',
                progress=100,
                stop_requested=False,
                finished_at=datetime.now(),
                last_error='',
            )
            self.log(f'任务执行完成，成功保存 {len(parsed_data)} 条数据')
        except Exception as e:
            self.log(f"爬虫执行失败: {e}", 'error')
            Task.update_runtime(
                self.task_id,
                status='failed',
                last_error=str(e),
                finished_at=datetime.now(),
                stop_requested=False,
            )
