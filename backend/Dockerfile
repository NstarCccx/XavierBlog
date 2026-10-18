# FastAPI 后端镜像：配置全部通过环境变量注入（DB_HOST/DB_PASSWORD/SECRET_KEY...），
# .env 不打进镜像。上传目录 /app/uploads 与日志 /app/logs 由 compose 挂卷持久化。
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
