import os
import html

# 要修复的文件列表
files_to_fix = [
    r'd:\爬虫开发\frontend\src\views\Login.vue',
    r'd:\爬虫开发\frontend\src\views\Layout.vue',
    r'd:\爬虫开发\frontend\src\views\Tasks.vue',
    r'd:\爬虫开发\frontend\src\views\TaskDetail.vue',
    r'd:\爬虫开发\frontend\src\views\Visualization.vue',
]

for file_path in files_to_fix:
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

print('\n所有文件修复完成！')