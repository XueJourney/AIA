def join_lines_with_newline(text: str) -> str:
    # 去掉开头和结尾的空行，并按行分割
    lines = text.strip().splitlines()
    
    # 用 \n 拼接每一行，并加上双引号转义
    joined = "\\n".join(line.strip() for line in lines)
    
    return joined

# 示例输入
multi_line_text = """我叫薛中泽，在较为正式的聊天中你可以叫我薛先生，闲聊中你可以叫我薛哥或薛总
我目前住在中国广东省深圳市，也出生在这里
我是一名初三的学生，爱好广泛，比较喜欢编程
闲聊时我们可以谈论民生、政治等新闻内容，或者对某件事情的看法
"""

# 调用函数
result = join_lines_with_newline(multi_line_text)

# 打印结果
print(result)
