import os
import html

# 要修复的 JS 文件列表
js_files_to_fix = [
    r'd:\爬虫开发\frontend\src\main.js',
    r'd:\爬虫开发\frontend\src\router\index.js',
    r'd:\爬虫开发\frontend\src\stores\user.js',
    r'd:\爬虫开发\frontend\src\api\index.js',
    r'd:\爬虫开发\frontend\src\utils\request.js',
]

for file_path in js_files_to_fix:
    if os.path.exists(file_path):
        print(f'修复文件: {file_path}')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解码 HTML 实体
        decoded_content = html.unescape(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded_content)
        
        print('  ✓ 修复完成')
    else:
        print(f'文件不存在: {file_path}')

print('\n所有 JS 文件修复完成！')