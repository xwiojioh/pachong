import copy
import re
from urllib.parse import urlparse


def _pair_list_to_dict(pairs):
    if isinstance(pairs, dict):
        return {str(key): value for key, value in pairs.items() if value not in (None, '')}
    result = {}
    for item in pairs or []:
        key = (item.get('key') or '').strip()
        value = item.get('value')
        if key and value not in (None, ''):
            result[key] = value
    return result


def _dict_to_pair_list(data):
    if not data:
        return []
    return [{'key': key, 'value': value} for key, value in data.items()]


PRESET_DEFINITIONS = [
    {
        'key': 'news_cn_world_index',
        'name': '新华网国际频道',
        'pattern': re.compile(r'^https?://www\.news\.cn/world/index\.html(?:[?#].*)?$', re.IGNORECASE),
        'supported': True,
        'description': '将先抓取国际频道列表中的新闻链接，再自动进入详情页抓取标题、正文、来源和发布时间。',
        'preview_fields': ['文章标题', '正文', '来源', '发布时间', '详情链接'],
        'selector_config': {
            'list_selector': '#recommendDepth .column-center-item .tit a[href*="/c.html"]',
            'list_selector_type': 'css',
            'fields': [
                {
                    'name': 'title',
                    'selector': '&',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'url',
                    'selector': '&',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'href',
                },
            ],
            'detail_page': {
                'enabled': True,
                'link_field': 'url',
                'max_items': 20,
                'selector_config': {
                    'list_selector': '',
                    'list_selector_type': 'css',
                    'fields': [
                        {
                            'name': 'title',
                            'selector': 'h1 .title, .mheader .title',
                            'selector_type': 'css',
                            'extract_type': 'text',
                        },
                        {
                            'name': 'content',
                            'selector': '#detailContent',
                            'selector_type': 'css',
                            'extract_type': 'text',
                        },
                        {
                            'name': 'source',
                            'selector': '.source, .mheader .info span',
                            'selector_type': 'css',
                            'extract_type': 'text',
                        },
                        {
                            'name': 'publish_time',
                            'selector': '.mheader .info, .header-time',
                            'selector_type': 'css',
                            'extract_type': 'text',
                        },
                    ],
                },
                'request_config': {
                    'method': 'GET',
                    'headers': {},
                    'cookies': {},
                    'body_type': 'json',
                    'body': None,
                    'render_mode': 'request',
                    'wait_until': 'domcontentloaded',
                    'wait_for_selector': '',
                    'wait_for_timeout_ms': 0,
                    'emulate_mobile': False,
                    'device_name': '',
                    'timeout': 30,
                },
            },
        },
        'request_config': {
            'method': 'GET',
            'headers': {},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'request',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': '',
            'wait_for_timeout_ms': 0,
            'emulate_mobile': False,
            'device_name': '',
            'timeout': 30,
        },
    },
    {
        'key': 'douban_movie_chart',
        'name': '豆瓣电影排行榜',
        'pattern': re.compile(r'^https?://movie\.douban\.com/chart(?:[/?#].*)?$', re.IGNORECASE),
        'supported': True,
        'description': '将通过浏览器渲染抓取豆瓣电影排行榜中的电影标题、简介、评分、详情链接和海报。',
        'preview_fields': ['电影标题', '简介', '评分', '详情链接', '海报'],
        'selector_config': {
            'list_selector': 'tr.item',
            'list_selector_type': 'css',
            'fields': [
                {
                    'name': 'title',
                    'selector': '.pl2 > a',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'url',
                    'selector': '.pl2 > a',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'href',
                },
                {
                    'name': 'content',
                    'selector': '.pl2 > p',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'rating',
                    'selector': '.rating_nums, .pl',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'poster',
                    'selector': 'img',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'src',
                },
            ],
        },
        'request_config': {
            'method': 'GET',
            'headers': {'Referer': 'https://movie.douban.com/'},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'playwright',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': 'tr.item',
            'wait_for_timeout_ms': 3000,
            'emulate_mobile': False,
            'device_name': '',
            'timeout': 60,
        },
    },
    {
        'key': 'douban_movie_top250',
        'name': '豆瓣电影 Top250',
        'pattern': re.compile(r'^https?://movie\.douban\.com/top250(?:[/?#].*)?$', re.IGNORECASE),
        'supported': True,
        'description': '将自动抓取电影标题、评分、简介、详情链接、海报和一句话短评。',
        'preview_fields': ['电影标题', '评分', '简介', '详情链接', '海报', '一句话短评'],
        'selector_config': {
            'list_selector': '.grid_view > li',
            'list_selector_type': 'css',
            'fields': [
                {
                    'name': 'title',
                    'selector': '.hd .title',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'url',
                    'selector': '.hd a',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'href',
                },
                {
                    'name': 'content',
                    'selector': '.bd p',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'rating',
                    'selector': '.rating_num',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'quote',
                    'selector': '.quote span',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'poster',
                    'selector': '.pic img',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'src',
                },
            ],
        },
        'request_config': {
            'method': 'GET',
            'headers': {'Referer': 'https://movie.douban.com/'},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'request',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': '',
            'wait_for_timeout_ms': 0,
            'emulate_mobile': False,
            'device_name': '',
            'timeout': 30,
        },
    },
    {
        'key': 'douban_mobile_movie_home',
        'name': '豆瓣电影移动首页',
        'pattern': re.compile(r'^https?://m\.douban\.com/movie/?(?:[?#].*)?$', re.IGNORECASE),
        'supported': True,
        'description': '将通过浏览器动态渲染抓取“影院热映”区域的电影标题、评分、详情链接和海报。',
        'preview_fields': ['电影标题', '评分', '详情链接', '海报'],
        'selector_config': {
            'list_selector': 'a.onjTL.pAB_V',
            'list_selector_type': 'css',
            'fields': [
                {
                    'name': 'title',
                    'selector': '.W7erk',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'content',
                    'selector': '.frc-rating-num',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'url',
                    'selector': '&',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'href',
                },
                {
                    'name': 'poster',
                    'selector': 'img.frc-size-cover-background',
                    'selector_type': 'css',
                    'extract_type': 'attr',
                    'attr': 'src',
                },
            ],
        },
        'request_config': {
            'method': 'GET',
            'headers': {'Referer': 'https://m.douban.com/movie/'},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'playwright',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': 'a.onjTL.pAB_V',
            'wait_for_timeout_ms': 8000,
            'emulate_mobile': True,
            'device_name': 'iPhone 13',
            'timeout': 60,
        },
        'warning': '',
        'recommended_url': '',
    },
    {
        'key': 'news_cn_article',
        'name': '新华网文章详情页',
        'pattern': re.compile(r'^https?://www\.news\.cn/.+/c\.html(?:[?#].*)?$', re.IGNORECASE),
        'supported': True,
        'description': '将直接抓取这篇新华网文章的标题、正文、来源和发布时间。',
        'preview_fields': ['文章标题', '正文', '来源', '发布时间'],
        'selector_config': {
            'list_selector': '',
            'list_selector_type': 'css',
            'fields': [
                {
                    'name': 'title',
                    'selector': 'h1 .title, .mheader .title',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'content',
                    'selector': '#detailContent',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'source',
                    'selector': '.source, .mheader .info span',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
                {
                    'name': 'publish_time',
                    'selector': '.mheader .info, .header-time',
                    'selector_type': 'css',
                    'extract_type': 'text',
                },
            ],
        },
        'request_config': {
            'method': 'GET',
            'headers': {},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'request',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': '',
            'wait_for_timeout_ms': 0,
            'emulate_mobile': False,
            'device_name': '',
            'timeout': 30,
        },
    },
]


def build_generic_preset(url):
    parsed = urlparse(url)
    host = parsed.netloc or '网页'
    return {
        'key': 'generic_smart_page',
        'name': f'{host}智能抓取',
        'supported': True,
        'description': '系统会自动判断这是列表页还是详情页。详情页直接抓正文；列表页会尝试进入里面的文章链接继续抓取具体内容。',
        'preview_fields': ['文章标题', '正文', '来源', '发布时间', '详情链接'],
        'selector_config': {
            'smart_mode': True,
            'smart_max_items': 20,
            'list_selector': '',
            'list_selector_type': 'css',
            'fields': [],
        },
        'request_config': {
            'method': 'GET',
            'headers': {},
            'cookies': {},
            'body_type': 'json',
            'body': None,
            'render_mode': 'auto',
            'wait_until': 'domcontentloaded',
            'wait_for_selector': '',
            'wait_for_timeout_ms': 0,
            'emulate_mobile': False,
            'device_name': '',
            'timeout': 30,
        },
        'recommended_url': '',
        'warning': '',
    }


def detect_task_preset(url):
    normalized_url = (url or '').strip()
    if not normalized_url:
        return {
            'key': '',
            'name': '等待识别',
            'supported': True,
            'matched': False,
            'description': '输入网址后，系统会自动告诉你将抓取什么内容。',
            'preview_fields': [],
            'selector_config': {},
            'request_config': {},
            'recommended_url': '',
            'warning': '',
        }

    for preset in PRESET_DEFINITIONS:
        if preset['pattern'].match(normalized_url):
            result = copy.deepcopy(preset)
            result['matched'] = True
            return result

    result = build_generic_preset(normalized_url)
    result['matched'] = False
    return result


def apply_max_items_to_selector_config(selector_config, max_items, override_detail_max=False):
    config = copy.deepcopy(selector_config or {})
    if max_items in (None, ''):
        return config

    try:
        normalized_max_items = max(1, int(max_items))
    except (TypeError, ValueError):
        return config

    config['result_limit'] = normalized_max_items

    if config.get('smart_mode'):
        config['smart_max_items'] = normalized_max_items

    detail_page = config.get('detail_page') or {}
    if detail_page.get('enabled') and (override_detail_max or not detail_page.get('max_items')):
        detail_page['max_items'] = normalized_max_items
        config['detail_page'] = detail_page

    return config


def merge_request_config(base_config, override_config):
    base = copy.deepcopy(base_config or {})
    override = copy.deepcopy(override_config or {})

    merged = {
        'method': override.get('method') or base.get('method') or 'GET',
        'body_type': override.get('body_type') or base.get('body_type') or 'json',
        'body': override.get('body') if override.get('body') not in (None, '') else base.get('body'),
        'render_mode': override.get('render_mode') or base.get('render_mode') or 'request',
        'wait_until': override.get('wait_until') or base.get('wait_until') or 'domcontentloaded',
        'wait_for_selector': override.get('wait_for_selector') or base.get('wait_for_selector') or '',
        'wait_for_timeout_ms': (
            override.get('wait_for_timeout_ms')
            if override.get('wait_for_timeout_ms') not in (None, '')
            else base.get('wait_for_timeout_ms', 0)
        ),
        'emulate_mobile': (
            override.get('emulate_mobile')
            if override.get('emulate_mobile') is not None
            else base.get('emulate_mobile', False)
        ),
        'device_name': override.get('device_name') or base.get('device_name') or '',
        'timeout': (
            override.get('timeout')
            if override.get('timeout') not in (None, '')
            else base.get('timeout', 30)
        ),
        'headers': {},
        'cookies': {},
    }
    merged['headers'].update(base.get('headers') or {})
    merged['headers'].update(override.get('headers') or {})
    merged['cookies'].update(base.get('cookies') or {})
    merged['cookies'].update(override.get('cookies') or {})
    return merged


def normalize_request_config_for_form(request_config):
    config = copy.deepcopy(request_config or {})
    return {
        'method': config.get('method') or 'GET',
        'body_type': config.get('body_type') or 'json',
        'body': config.get('body'),
        'render_mode': config.get('render_mode') or 'request',
        'wait_until': config.get('wait_until') or 'domcontentloaded',
        'wait_for_selector': config.get('wait_for_selector') or '',
        'wait_for_timeout_ms': config.get('wait_for_timeout_ms') or 0,
        'emulate_mobile': bool(config.get('emulate_mobile')),
        'device_name': config.get('device_name') or '',
        'timeout': config.get('timeout') or 30,
        'headers': _dict_to_pair_list(config.get('headers')),
        'cookies': _dict_to_pair_list(config.get('cookies')),
    }


def normalize_request_config_from_form(request_config):
    config = copy.deepcopy(request_config or {})
    return {
        'method': config.get('method') or 'GET',
        'body_type': config.get('body_type') or 'json',
        'body': config.get('body'),
        'render_mode': config.get('render_mode') or 'request',
        'wait_until': config.get('wait_until') or 'domcontentloaded',
        'wait_for_selector': config.get('wait_for_selector') or '',
        'wait_for_timeout_ms': int(config.get('wait_for_timeout_ms') or 0),
        'emulate_mobile': bool(config.get('emulate_mobile')),
        'device_name': config.get('device_name') or '',
        'timeout': int(config.get('timeout') or 30),
        'headers': _pair_list_to_dict(config.get('headers')),
        'cookies': _pair_list_to_dict(config.get('cookies')),
    }
