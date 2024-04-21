# 使用 Python 官方基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 检查语法错误
RUN python -m py_compile bot.py

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt 

# 运行机器人
CMD ["python", "bot.py"]