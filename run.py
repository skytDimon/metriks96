#!/usr/bin/env python3
"""
Простой скрипт для запуска приложения МЕТРИКС
"""

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск приложения МЕТРИКС...")
    print("📱 Откройте браузер и перейдите по адресу: http://localhost:8000")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Отключаем reload для экономии ресурсов
        log_level="warning",  # Меньше логов = меньше I/O
        workers=1,  # Один worker для экономии памяти
        access_log=False  # Отключаем access логи
    )
