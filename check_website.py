import requests
from bs4 import BeautifulSoup

url = 'http://www.zgjx.cn/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    print(f'状态码: {response.status_code}')
    print(f'内容长度: {len(response.text)}')
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    print('\n=== 页面标题 ===')
    print(soup.title.string if soup.title else '无标题')
    
    print('\n=== 所有链接 ===')
    links = soup.find_all('a', href=True)
    for i, link in enumerate(links[:20]):
        print(f'{i+1}. {link.get_text(strip=True)[:30]} -> {link["href"]}')
    
    print('\n=== 所有列表项 ===')
    for tag in ['li', 'div', 'article', 'section']:
        items = soup.find_all(tag)
        if items:
            print(f'\n找到 {len(items)} 个 <{tag}> 标签')
            for i, item in enumerate(items[:5]):
                text = item.get_text(strip=True)[:50]
                print(f'  {i+1}. {text}')
    
except Exception as e:
    print(f'错误: {e}')