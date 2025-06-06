import re
import os
from pathlib import Path

def parse_ass_file(ass_path):
    """
    解析ASS字幕文件，提取中英文字幕对话
    返回包含(英文, 中文)的列表
    """
    dialogues = []
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')  # 中文字符正则
    
    # 尝试不同的编码方式读取文件
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'utf-16']
    lines = None
    
    for encoding in encodings:
        try:
            with open(ass_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                print(f"成功使用 {encoding} 编码读取文件")
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return dialogues
    
    if lines is None:
        print(f"错误：无法使用任何支持的编码读取文件 {ass_path}")
        return dialogues
    
    # 找到事件部分开始的位置
    events_start = False
    for line in lines:
        line = line.strip()
        if line.startswith('[Events]'):
            events_start = True
            continue
        if not events_start:
            continue
        
        # 解析对话行
        if line.startswith('Dialogue:'):
            parts = line.split(',', 9)
            if len(parts) < 10:
                continue
            
            text = parts[9].strip()
            # 移除特效标签
            text = re.sub(r'\{.*?\}', '', text)
            # 分割中英文 (假设中英文用\\N或\n分隔)
            if '\\N' in text:
                en, zh = text.split('\\N', 1)
            elif '\n' in text:
                en, zh = text.split('\n', 1)
            else:
                # 如果没有明确分隔符，尝试自动判断
                zh_chars = chinese_pattern.findall(text)
                if zh_chars:
                    # 简单假设中文在英文之后
                    en = re.sub(r'[\u4e00-\u9fff]', '', text).strip()
                    zh = ''.join(zh_chars)
                else:
                    en = text.strip()
                    zh = ''
            
            en = en.strip()
            zh = zh.strip()
            
            if en or zh:  # 忽略空行
                dialogues.append((en, zh))
    
    return dialogues

def save_to_txt(dialogues, output_path):
    """将提取的对话保存到文本文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, (en, zh) in enumerate(dialogues, start=1):
            f.write(f"{i}. {en} - {zh}\n")
    print(f"已保存: {output_path}")

def process_directory(directory='.'):
    """处理目录中的所有ASS文件"""
    ass_files = list(Path(directory).glob('*.ass'))
    
    if not ass_files:
        print("当前目录下未找到.ass文件!")
        return
    
    print(f"找到 {len(ass_files)} 个.ass文件:")
    for file in ass_files:
        print(f" - {file.name}")
    
    for ass_file in ass_files:
        print(f"\n正在处理: {ass_file.name}")
        dialogues = parse_ass_file(ass_file)
        
        if not dialogues:
            print(f"警告: {ass_file.name} 中未提取到任何对话!")
            continue
        
        # 设置输出路径
        output_path = ass_file.with_suffix('.txt')
        
        # 保存结果
        save_to_txt(dialogues, output_path)

def get_input_path():
    """获取用户输入的路径"""
    while True:
        path = input("请输入ASS文件所在目录的绝对路径（直接回车使用当前目录）: ").strip()
        if not path:  # 如果用户直接回车
            return '.'
        
        # 处理路径中的转义字符
        path = path.replace('\\', '')
        
        # 检查路径是否存在
        if not os.path.exists(path):
            print(f"错误：输入的路径不存在: {path}")
            continue
        
        # 检查是否是目录
        if not os.path.isdir(path):
            print(f"错误：输入的路径不是目录: {path}")
            continue
        
        return path

if __name__ == '__main__':
    print("=== ASS字幕提取工具 ===")
    print("将处理指定目录下所有.ass文件")
    
    # 获取用户输入的路径
    directory = get_input_path()
    
    # 处理文件
    process_directory(directory)
    
    print("\n处理完成!")
    input("按Enter键退出...")