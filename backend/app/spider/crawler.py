
import requests
from bs4 import BeautifulSoup
import time
import json
from app.models.task import Task, CrawledData


class SimpleCrawler:
    def __init__(self, task_id):
        self.task_id = task_id
        self.task = Task.get_by_id(task_id)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def parse(self, html, config):
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        results = []
        
        list_selector = config.get('list_selector', '')
        if list_selector:
            items = soup.select(list_selector)
        else:
            items = [soup]
        
        field_selectors = config.get('fields', {})
        
        for item in items:
            data = {}
            for field_name, selector in field_selectors.items():
                if selector.get('type') == 'text':
                    elem = item.select_one(selector.get('selector', ''))
                    data[field_name] = elem.get_text(strip=True) if elem else ''
                elif selector.get('type') == 'attr':
                    elem = item.select_one(selector.get('selector', ''))
                    attr = selector.get('attr', 'href')
                    data[field_name] = elem.get(attr, '') if elem else ''
            
            if data:
                results.append(data)
        
        return results
    
    def run(self):
        if not self.task:
            return
        
        Task.update_status(self.task_id, 'running')
        
        try:
            html = self.fetch(self.task['url'])
            if not html:
                Task.update_status(self.task_id, 'failed')
                return
            
            config = self.task.get('selector_config', {})
            parsed_data = self.parse(html, config)
            
            for item in parsed_data:
                CrawledData.create(
                    task_id=self.task_id,
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    url=item.get('url', self.task['url']),
                    extra={k: v for k, v in item.items() if k not in ['title', 'content', 'url']}
                )
            
            Task.update_status(self.task_id, 'completed')
        except Exception as e:
            print(f"爬虫执行失败: {e}")
            Task.update_status(self.task_id, 'failed')
