# Конфигурация Gunicorn для продакшна

import os
import multiprocessing

# Количество worker процессов
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Тип worker'а (uvicorn для FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"

# Количество потоков на worker
threads = int(os.getenv("THREADS", "2"))

# Максимальное количество запросов на worker перед перезапуском
max_requests = int(os.getenv("MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "100"))

# Таймауты
timeout = int(os.getenv("TIMEOUT", "30"))
keepalive = int(os.getenv("KEEPALIVE", "2"))

# Привязка
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"

# Логирование
accesslog = os.getenv("ACCESS_LOG", "-")
errorlog = os.getenv("ERROR_LOG", "-")
loglevel = os.getenv("LOG_LEVEL", "info")

# Предзагрузка приложения для экономии памяти
preload_app = True

# Переменные окружения
raw_env = [
    f"PYTHONPATH={os.getcwd()}",
]

# Ограничения памяти
worker_tmp_dir = "/tmp"

# Безопасность
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Graceful shutdown
graceful_timeout = 30
