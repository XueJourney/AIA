def join_lines_with_newline(text: str) -> str:
    # 去掉开头和结尾的空行，并按行分割
    lines = text.strip().splitlines()
    
    # 用 \n 拼接每一行，并加上双引号转义
    joined = "\\n".join(line.strip() for line in lines)
    
    return joined

# 示例输入
multi_line_text = """
"""

# 调用函数
result = join_lines_with_newline(multi_line_text)

# 打印结果
print(result)
