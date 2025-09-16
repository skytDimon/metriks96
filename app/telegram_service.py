import asyncio
import logging
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, bot_token: str, chat_ids: list):
        self.bot_token = bot_token
        self.chat_ids = chat_ids if isinstance(chat_ids, list) else [chat_ids]
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_order_notification(self, name: str, email: str, phone: str, items: str, total_quantity: int, comment: str = ""):
        """Отправляет уведомление о новой заявке в Telegram"""
        try:
            # Парсим товары из JSON
            import json
            try:
                cart_items = json.loads(items)
                items_text = ""
                total_price = 0
                
                for item in cart_items:
                    item_name = item.get('name', 'Неизвестный товар')
                    item_quantity = item.get('quantity', 0)
                    item_price = item.get('price', 0)
                    item_total = item_quantity * item_price
                    total_price += item_total
                    
                    items_text += f"• {item_name}\n"
                    items_text += f"  Количество: {item_quantity} шт.\n"
                    if item_price > 0:
                        items_text += f"  Цена: {item_price} руб./шт.\n"
                        items_text += f"  Сумма: {item_total} руб.\n"
                    items_text += "\n"
                
                if total_price > 0:
                    items_text += f"💰 <b>Общая сумма: {total_price} руб.</b>\n\n"
                    
            except (json.JSONDecodeError, TypeError):
                # Если не удалось распарсить JSON, показываем как есть
                items_text = items
            
            message = f"""🛒 <b>Новая заявка с сайта МЕТРИКС</b>

👤 <b>Клиент:</b> {name}
📧 <b>Email:</b> {email}
📞 <b>Телефон:</b> {phone}
📦 <b>Общее количество:</b> {total_quantity} шт.

📋 <b>Товары:</b>
{items_text}"""

            # Добавляем комментарий, если он есть
            if comment and comment.strip():
                message += f"💬 <b>Комментарий:</b>\n{comment.strip()}\n\n"
            
            message += f"⏰ <b>Время заявки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            
            # Отправляем сообщение всем получателям
            success_count = 0
            async with httpx.AsyncClient() as client:
                for chat_id in self.chat_ids:
                    try:
                        response = await client.post(
                            f"{self.api_url}/sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": message,
                                "parse_mode": "HTML"
                            }
                        )
                        
                        if response.status_code == 200:
                            success_count += 1
                            logger.info(f"Заявка от {name} успешно отправлена в Telegram (chat_id: {chat_id})")
                        else:
                            logger.error(f"Ошибка отправки в Telegram (chat_id: {chat_id}): {response.status_code} - {response.text}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке в chat_id {chat_id}: {e}")
            
            # Возвращаем True если хотя бы одно сообщение отправлено успешно
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return False
    
    async def send_test_message(self):
        """Отправляет тестовое сообщение для проверки работы бота"""
        try:
            message = "🤖 <b>Тест подключения</b>\n\nБот успешно подключен к сайту МЕТРИКС!"
            
            # Отправляем тестовое сообщение всем получателям
            success_count = 0
            async with httpx.AsyncClient() as client:
                for chat_id in self.chat_ids:
                    try:
                        response = await client.post(
                            f"{self.api_url}/sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": message,
                                "parse_mode": "HTML"
                            }
                        )
                        
                        if response.status_code == 200:
                            success_count += 1
                            logger.info(f"Тестовое сообщение успешно отправлено (chat_id: {chat_id})")
                        else:
                            logger.error(f"Ошибка отправки тестового сообщения (chat_id: {chat_id}): {response.status_code} - {response.text}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке тестового сообщения в chat_id {chat_id}: {e}")
            
            # Возвращаем True если хотя бы одно сообщение отправлено успешно
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке тестового сообщения: {e}")
            return False

# Создаем экземпляр сервиса
def get_telegram_service():
    """Создает экземпляр TelegramService с настройками из переменных окружения"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_ids_str = os.getenv("TELEGRAM_CHAT_IDS", "")
    
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
        return None
    
    if not chat_ids_str:
        logger.warning("TELEGRAM_CHAT_IDS не установлены в переменных окружения")
        return None
    
    # Парсим chat_ids из строки
    chat_ids = [chat_id.strip() for chat_id in chat_ids_str.split(",") if chat_id.strip()]
    
    if not chat_ids:
        logger.warning("Не удалось распарсить TELEGRAM_CHAT_IDS")
        return None
    
    return TelegramService(bot_token=bot_token, chat_ids=chat_ids)

# Создаем экземпляр сервиса
TELEGRAM_SERVICE = get_telegram_service()
