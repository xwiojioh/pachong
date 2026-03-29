import requests
from bs4 import BeautifulSoup

url = 'https://book.douban.com/chart'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f'状态码: {response.status_code}')
    print(f'内容长度: {len(response.text)}')
    
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    print('\n=== 页面标题 ===')
    print(soup.title.string if soup.title else '无标题')
    
    print('\n=== 查找 .item 元素 ===')
    items = soup.select('.item')
    print(f'找到 {len(items)} 个 .item 元素')
    
    if items:
        print('\n前3个:')
        for i, item in enumerate(items[:3]):
            print(f'\n{i+1}. {item.get_text(strip=True)[:100]}')
    
    print('\n=== 查找 li 元素 ===')
    lis = soup.find_all('li')
    print(f'找到 {len(lis)} 个 li 元素')
    
    if lis:
        print('\n前5个:')
        for i, li in enumerate(lis[:5]):
            text = li.get_text(strip=True)[:80]
            print(f'{i+1}. {text}')
    
    print('\n=== 保存HTML到文件 ===')
    with open('douban.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print('已保存到 douban.html')
    
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()