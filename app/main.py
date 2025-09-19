import csv
import os
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from dotenv import load_dotenv
from app.telegram_service import TELEGRAM_SERVICE
from app.routers import admin

# Загружаем переменные окружения
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(admin.router)

# Templates
templates = Jinja2Templates(directory="templates")

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.bk.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "metriks66@bk.ru")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "metriks66@bk.ru")

# Minimum order quantity
MIN_ORDER_QUANTITY = int(os.getenv("MIN_ORDER_QUANTITY", "100"))

def load_products_from_csv():
    """Load products from CSV file (оптимизированная версия для слабых серверов)"""
    products = []
    csv_file = os.path.join(BASE_DIR, "store-7407308-202509021623.csv")
    
    if not os.path.exists(csv_file):
        return []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Skip empty rows
                if not row.get('Title') or row.get('Title').strip() == '':
                    continue
                
                # Extract category from Category field
                category = row.get('Category', '').strip()
                if ';' in category:
                    category = category.split(';')[0].strip()
                
                # Create product object (оптимизированный для слабых серверов)
                product = {
                    'id': row.get('Tilda UID', ''),
                    'name': row.get('Title', '').strip(),
                    'description': row.get('Description', '').strip() or row.get('Text', '').strip(),
                    'category': category,
                    'image': row.get('Photo', ''),
                    'brand': row.get('Brand', '').strip(),
                    'sku': row.get('SKU', '').strip(),
                    # Только самые важные характеристики
                    'material': row.get('Characteristics:Материал', '').strip(),
                    'application': row.get('Characteristics:Применение', '').strip(),
                    'standard': row.get('Mark', '').strip()
                }
                
                # Only add products with valid names
                if product['name']:
                    products.append(product)
                    
    except Exception as e:
        # В продакшене не выводим детальные ошибки
        pass
    
    return products

# Load products from CSV (кэшируем для экономии ресурсов)
PRODUCTS = load_products_from_csv()
PRODUCTS_LOAD_TIME = datetime.now()

def reload_products_if_needed():
    """Перезагружает товары если прошло больше 1 часа"""
    global PRODUCTS, PRODUCTS_LOAD_TIME
    if (datetime.now() - PRODUCTS_LOAD_TIME).seconds > 3600:  # 1 час
        PRODUCTS = load_products_from_csv()
        PRODUCTS_LOAD_TIME = datetime.now()

def force_refresh_products_cache():
    """Принудительное обновление кэша товаров"""
    global PRODUCTS, PRODUCTS_LOAD_TIME
    PRODUCTS = load_products_from_csv()
    PRODUCTS_LOAD_TIME = datetime.now()
    return PRODUCTS

# Система скрытых товаров
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIDDEN_PRODUCTS_FILE = os.path.join(BASE_DIR, "hidden_products.json")

def load_hidden_products():
    """Загрузка списка скрытых товаров"""
    hidden_products = set()
    if os.path.exists(HIDDEN_PRODUCTS_FILE):
        try:
            with open(HIDDEN_PRODUCTS_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                hidden_products = set(data.get('hidden_products', []))
        except Exception as e:
            print(f"Ошибка при загрузке скрытых товаров: {str(e)}")
    else:
        print(f"Файл {HIDDEN_PRODUCTS_FILE} не найден, создаем пустой список")
    return hidden_products

def save_hidden_products(hidden_products):
    """Сохранение списка скрытых товаров"""
    try:
        with open(HIDDEN_PRODUCTS_FILE, 'w', encoding='utf-8') as file:
            json.dump({'hidden_products': list(hidden_products)}, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении скрытых товаров: {str(e)}")
        return False

def hide_product(product_id):
    """Скрыть товар"""
    hidden_products = load_hidden_products()
    hidden_products.add(product_id)
    return save_hidden_products(hidden_products)

def show_product(product_id):
    """Показать товар"""
    hidden_products = load_hidden_products()
    hidden_products.discard(product_id)
    return save_hidden_products(hidden_products)

def get_visible_products():
    """Получить только видимые товары"""
    hidden_products = load_hidden_products()
    return [product for product in PRODUCTS if product['id'] not in hidden_products]

def get_hidden_products():
    """Получить только скрытые товары"""
    hidden_products = load_hidden_products()
    return [product for product in PRODUCTS if product['id'] in hidden_products]

def get_product_by_id(product_id):
    """Получить товар по ID"""
    for product in PRODUCTS:
        if product['id'] == product_id:
            return product
    return None

def update_product_in_csv(product_id, updated_data):
    """Обновить товар в CSV файле"""
    csv_file = os.path.join(BASE_DIR, "store-7407308-202509021623.csv")
    
    if not os.path.exists(csv_file):
        return False
    
    try:
        # Читаем все данные из CSV
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            rows = list(reader)
        
        # Находим и обновляем нужную строку
        updated = False
        for row in rows:
            if row.get('Tilda UID', '').strip() == product_id:
                # Обновляем поля
                for key, value in updated_data.items():
                    if key in row:
                        row[key] = value
                updated = True
                break
        
        if not updated:
            return False
        
        # Записываем обновленные данные обратно в CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as file:
            if rows:
                writer = csv.DictWriter(file, fieldnames=rows[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(rows)
        
        # Обновляем кэш товаров
        global PRODUCTS, PRODUCTS_LOAD_TIME
        PRODUCTS = load_products_from_csv()
        PRODUCTS_LOAD_TIME = datetime.now()
        
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении товара в CSV: {str(e)}")
        return False

# Categories for filtering (соответствуют категориям в CSV)
CATEGORIES = [
    {"id": "Саморезы", "name": "Саморезы"},
    {"id": "Болты", "name": "Болты"},
    {"id": "Винты", "name": "Винты"},
    {"id": "Гайки", "name": "Гайки"},
    {"id": "Шайбы", "name": "Шайбы"},
    {"id": "Шпильки", "name": "Шпильки"},
    {"id": "Штифты", "name": "Штифты"},
    {"id": "Заклепки", "name": "Заклепки"},
    {"id": "Кронштейны", "name": "Кронштейны"},
    {"id": "Винты установочные", "name": "Винты установочные"},
    {"id": "Нагель", "name": "Нагель"}
]

def send_email(name: str, email: str, phone: str, items: str, total_quantity: int):
    """Send email with order request (оптимизированная версия)"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Новая заявка - {total_quantity} шт."
        
        # Упрощенное тело письма для экономии ресурсов
        body = f"""Новая заявка:
Имя: {name}
Email: {email}
Телефон: {phone}
Количество: {total_quantity} шт.

Товары: {items[:500]}..."""  # Ограничиваем длину
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Быстрое подключение с таймаутом
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        return True
    except Exception:
        # В продакшене не выводим детальные ошибки
        return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/catalog", response_class=HTMLResponse)
async def catalog(request: Request, page: int = 1, limit: int = 20):
    """Каталог товаров с пагинацией для оптимизации"""
    # Получаем только видимые товары
    visible_products = get_visible_products()
    # Для JavaScript передаем все видимые товары, пагинация будет на клиенте
    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "products": visible_products,  # Передаем только видимые товары
        "categories": CATEGORIES,
        "current_page": page,
        "total_pages": (len(visible_products) + limit - 1) // limit,
        "total_products": len(visible_products)
    })

@app.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "min_order_quantity": MIN_ORDER_QUANTITY
    })

@app.get("/payment", response_class=HTMLResponse)
async def payment(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: str):
    """Product detail page"""
    # Проверяем, не скрыт ли товар
    hidden_products = load_hidden_products()
    if product_id in hidden_products:
        return templates.TemplateResponse("404.html", {"request": request})
    
    # Find product by ID
    product = None
    for p in PRODUCTS:
        if p['id'] == product_id:
            product = p
            break
    
    if not product:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product
    })

@app.post("/api/submit-request")
async def submit_request(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    items: str = Form(...),
    total_quantity: int = Form(...),
    comment: str = Form("")
):
    if total_quantity < MIN_ORDER_QUANTITY:
        return {"success": False, "message": f"Минимальный заказ {MIN_ORDER_QUANTITY} шт."}
    
    # Сохраняем заявку в файл для админ панели
    from datetime import datetime
    order_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "items": items,
        "total_quantity": total_quantity,
        "comment": comment,
        "timestamp": datetime.now().isoformat()
    }
    
    # Загружаем существующие заявки
    orders_file = os.path.join(BASE_DIR, "orders.json")
    orders = []
    if os.path.exists(orders_file):
        try:
            with open(orders_file, 'r', encoding='utf-8') as file:
                orders = json.load(file)
        except:
            orders = []
    
    # Добавляем новую заявку
    order_data['id'] = len(orders) + 1
    orders.append(order_data)
    
    # Ограничиваем количество заявок до 100 последних (для экономии памяти)
    if len(orders) > 100:
        orders = orders[-100:]
    
    # Сохраняем заявки
    try:
        with open(orders_file, 'w', encoding='utf-8') as file:
            json.dump(orders, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения заявки: {e}")
    
    # Отправляем email
    email_success = send_email(name, email, phone, items, total_quantity)
    
    # Отправляем уведомление в Telegram
    telegram_success = False
    if TELEGRAM_SERVICE:
        telegram_success = await TELEGRAM_SERVICE.send_order_notification(
            name=name,
            email=email,
            phone=phone,
            items=items,
            total_quantity=total_quantity,
            comment=comment
        )
    
    if email_success and telegram_success:
        return {"success": True, "message": "Заявка отправлена успешно! Вы получите уведомление в Telegram."}
    elif email_success:
        return {"success": True, "message": "Заявка отправлена успешно! (Email отправлен, Telegram недоступен)"}
    elif telegram_success:
        return {"success": True, "message": "Заявка отправлена успешно! (Telegram уведомление отправлено, Email недоступен)"}
    else:
        return {"success": False, "message": "Ошибка при отправке заявки"}

@app.get("/api/test-telegram")
async def test_telegram():
    """Тестовый эндпоинт для проверки работы Telegram бота"""
    if not TELEGRAM_SERVICE:
        return {"success": False, "message": "Telegram сервис не настроен. Проверьте переменные окружения."}
    
    success = await TELEGRAM_SERVICE.send_test_message()
    
    if success:
        return {"success": True, "message": "Тестовое сообщение отправлено в Telegram!"}
    else:
        return {"success": False, "message": "Ошибка при отправке тестового сообщения"}

@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "telegram": TELEGRAM_SERVICE is not None,
            "email": bool(SMTP_PASSWORD),
            "products_loaded": len(PRODUCTS) > 0
        }
    }


# Обработчики ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Обработчик 404 ошибки"""
    return templates.TemplateResponse("errors/404.html", {
        "request": request,
        "error_code": 404,
        "error_title": "Страница не найдена",
        "error_message": "К сожалению, запрашиваемая страница не существует или была удалена.",
        "error_description": "Возможно, вы перешли по неверной ссылке или страница была перемещена."
    }, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Обработчик 500 ошибки"""
    return templates.TemplateResponse("errors/500.html", {
        "request": request,
        "error_code": 500,
        "error_title": "Внутренняя ошибка сервера",
        "error_message": "Произошла внутренняя ошибка сервера. Мы уже работаем над её устранением.",
        "error_description": "Попробуйте обновить страницу через несколько минут или обратитесь к администратору."
    }, status_code=500)

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """Обработчик 403 ошибки"""
    return templates.TemplateResponse("errors/403.html", {
        "request": request,
        "error_code": 403,
        "error_title": "Доступ запрещен",
        "error_message": "У вас нет прав для доступа к этой странице.",
        "error_description": "Обратитесь к администратору для получения необходимых прав доступа."
    }, status_code=403)

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    """Обработчик 400 ошибки"""
    return templates.TemplateResponse("errors/400.html", {
        "request": request,
        "error_code": 400,
        "error_title": "Неверный запрос",
        "error_message": "Сервер не может обработать ваш запрос из-за неверного синтаксиса.",
        "error_description": "Проверьте правильность введенных данных и попробуйте снова."
    }, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
