from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import csv
import os
import json
import secrets
from datetime import datetime
import hashlib
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Добавляем фильтр для JSON
def from_json(value):
    """Фильтр для парсинга JSON строки"""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            return []
    return value

templates.env.filters["from_json"] = from_json

# Админские учетные данные (в продакшене лучше использовать переменные окружения)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "metriks2024"

# Простое хранение сессий (в продакшене лучше использовать Redis или базу данных)
admin_sessions = {}

def create_session_token(username: str) -> str:
    """Создание токена сессии"""
    token = secrets.token_urlsafe(32)
    admin_sessions[token] = {
        "username": username,
        "created_at": datetime.now().isoformat()
    }
    return token

def verify_session_token(token: str) -> str:
    """Проверка токена сессии"""
    if token in admin_sessions:
        return admin_sessions[token]["username"]
    return None

def get_current_admin(request: Request):
    """Проверка аутентификации админа через сессию"""
    # Проверяем токен в cookies
    session_token = request.cookies.get("admin_session")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/admin/login"}
        )
    
    username = verify_session_token(session_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Invalid session",
            headers={"Location": "/admin/login"}
        )
    
    return username

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Страница входа в админ панель"""
    return templates.TemplateResponse("admin/login.html", {
        "request": request
    })

@router.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Обработка входа в админ панель"""
    # Проверяем учетные данные
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Создаем сессию
        session_token = create_session_token(username)
        
        # Создаем ответ с перенаправлением
        response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        
        # Устанавливаем cookie с токеном сессии
        response.set_cookie(
            key="admin_session",
            value=session_token,
            httponly=True,
            secure=False,  # В продакшене должно быть True для HTTPS
            samesite="lax",
            max_age=86400  # 24 часа
        )
        
        return response
    else:
        # Неверные учетные данные
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

@router.get("/admin/logout")
async def admin_logout():
    """Выход из админ панели"""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="admin_session")
    return response

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: str = Depends(get_current_admin)):
    """Главная страница админ панели"""
    # Загружаем статистику
    stats = get_admin_stats()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": admin,
        "stats": stats
    })

@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request, admin: str = Depends(get_current_admin)):
    """Управление товарами"""
    products = load_all_products()
    
    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "admin": admin,
        "products": products
    })

@router.get("/admin/products/hidden", response_class=HTMLResponse)
async def admin_hidden_products(request: Request, admin: str = Depends(get_current_admin)):
    """Управление скрытыми товарами"""
    from app.main import get_hidden_products
    hidden_products = get_hidden_products()
    
    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "admin": admin,
        "products": hidden_products,
        "is_hidden_page": True
    })

@router.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, admin: str = Depends(get_current_admin)):
    """Просмотр заявок"""
    orders = load_orders()
    
    return templates.TemplateResponse("admin/orders.html", {
        "request": request,
        "admin": admin,
        "orders": orders
    })

@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, admin: str = Depends(get_current_admin)):
    """Настройки системы"""
    settings = load_settings()
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "admin": admin,
        "settings": settings
    })

@router.post("/admin/test-telegram")
async def admin_test_telegram(request: Request, admin: str = Depends(get_current_admin)):
    """Тест отправки в Telegram"""
    from app.telegram_service import TELEGRAM_SERVICE
    
    success = await TELEGRAM_SERVICE.send_test_message()
    
    if success:
        return {"success": True, "message": "Тестовое сообщение отправлено в Telegram!"}
    else:
        return {"success": False, "message": "Ошибка при отправке тестового сообщения"}

@router.post("/admin/refresh-products")
async def refresh_products_cache(request: Request, admin: str = Depends(get_current_admin)):
    """Принудительное обновление кэша товаров"""
    try:
        from app.main import force_refresh_products_cache
        products = force_refresh_products_cache()
        return JSONResponse(
            status_code=200,
            content={
                "success": True, 
                "message": f"Кэш товаров обновлен. Загружено {len(products)} товаров",
                "products_count": len(products)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при обновлении кэша: {str(e)}"}
        )

@router.post("/admin/products/hide")
async def hide_product(request: Request, admin: str = Depends(get_current_admin), product_id: str = Form(...)):
    """Скрыть товар с сайта"""
    try:
        from app.main import hide_product, load_hidden_products
        
        # Проверяем, что товар существует
        from app.main import PRODUCTS
        product_exists = any(p['id'] == product_id for p in PRODUCTS)
        if not product_exists:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Товар не найден"}
            )
        
        # Проверяем, не скрыт ли уже товар
        hidden_products = load_hidden_products()
        if product_id in hidden_products:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Товар уже скрыт"}
            )
        
        # Скрываем товар
        success = hide_product(product_id)
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True, 
                    "message": "Товар успешно скрыт с сайта"
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Ошибка при скрытии товара. Проверьте права доступа к файлу hidden_products.json"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при скрытии товара: {str(e)}"}
        )

@router.post("/admin/products/show")
async def show_product(request: Request, admin: str = Depends(get_current_admin), product_id: str = Form(...)):
    """Показать скрытый товар"""
    try:
        from app.main import show_product, load_hidden_products
        
        # Проверяем, что товар существует
        from app.main import PRODUCTS
        product_exists = any(p['id'] == product_id for p in PRODUCTS)
        if not product_exists:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Товар не найден"}
            )
        
        # Проверяем, скрыт ли товар
        hidden_products = load_hidden_products()
        if product_id not in hidden_products:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Товар не скрыт"}
            )
        
        # Показываем товар
        success = show_product(product_id)
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True, 
                    "message": "Товар успешно показан на сайте"
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Ошибка при показе товара. Проверьте права доступа к файлу hidden_products.json"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при показе товара: {str(e)}"}
        )

@router.get("/admin/products/edit/{product_id}", response_class=HTMLResponse)
async def edit_product_page(request: Request, product_id: str, admin: str = Depends(get_current_admin)):
    """Страница редактирования товара"""
    try:
        from app.main import get_product_by_id, CATEGORIES
        
        product = get_product_by_id(product_id)
        if not product:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Товар не найден"}
            )
        
        return templates.TemplateResponse("admin/edit_product.html", {
            "request": request,
            "product": product,
            "categories": CATEGORIES
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при загрузке страницы редактирования: {str(e)}"}
        )

@router.post("/admin/products/update/{product_id}")
async def update_product(
    request: Request,
    product_id: str,
    admin: str = Depends(get_current_admin),
    name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(""),
    sku: str = Form(""),
    description: str = Form(""),
    image: str = Form(""),
    material: str = Form(""),
    application: str = Form(""),
    standard: str = Form(""),
    analogs: str = Form(""),
    weight: str = Form(""),
    length: str = Form(""),
    width: str = Form(""),
    height: str = Form(""),
    diameter_length: str = Form(""),
    drive: str = Form("")
):
    """Обновление товара в CSV файле"""
    try:
        from app.main import get_product_by_id, update_product_in_csv
        
        # Проверяем, что товар существует
        product = get_product_by_id(product_id)
        if not product:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Товар не найден"}
            )
        
        # Валидация обязательных полей
        if not name.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Название товара обязательно"}
            )
        
        if not category.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Категория товара обязательна"}
            )
        
        # Подготавливаем данные для обновления
        updated_data = {
            "Brand": brand.strip(),
            "SKU": sku.strip(),
            "Mark": standard.strip(),
            "Category": category.strip(),
            "Title": name.strip(),
            "Description": description.strip(),
            "Text": description.strip(),
            "Photo": image.strip(),
            "Characteristics:Применение": application.strip(),
            "Characteristics:Аналоги": analogs.strip(),
            "Characteristics:Материал": material.strip(),
            "Characteristics:d / l": diameter_length.strip(),
            "Characteristics:Привод": drive.strip(),
            "Weight": weight.strip(),
            "Length": length.strip(),
            "Width": width.strip(),
            "Height": height.strip()
        }
        
        # Обновляем товар в CSV
        success = update_product_in_csv(product_id, updated_data)
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True, 
                    "message": "Товар успешно обновлен"
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Ошибка при обновлении товара"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при обновлении товара: {str(e)}"}
        )

@router.post("/admin/products/add")
async def add_product(
    request: Request,
    admin: str = Depends(get_current_admin),
    name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(""),
    sku: str = Form(""),
    description: str = Form(""),
    image: str = Form(""),
    material: str = Form(""),
    application: str = Form(""),
    standard: str = Form(""),
    analogs: str = Form(""),
    weight: str = Form(""),
    length: str = Form(""),
    width: str = Form(""),
    height: str = Form(""),
    diameter_length: str = Form(""),
    drive: str = Form("")
):
    """Добавление нового товара в CSV файл"""
    try:
        # Валидация обязательных полей
        if not name.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Название товара обязательно"}
            )
        
        if not category.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Категория товара обязательна"}
            )
        
        # Генерируем уникальный ID для товара
        product_id = str(uuid.uuid4().int)[:12]  # 12-значный числовой ID
        
        # Подготавливаем данные для CSV
        csv_data = {
            "Tilda UID": product_id,
            "Brand": brand.strip(),
            "SKU": sku.strip(),
            "Mark": standard.strip(),
            "Category": category.strip(),
            "Title": name.strip(),
            "Description": description.strip(),
            "Text": description.strip(),
            "Photo": image.strip(),
            "Price": "0",
            "Quantity": "",
            "Price Old": "",
            "Editions": "",
            "Modifications": "",
            "External ID": "",
            "Parent UID": "",
            "Characteristics:Применение": application.strip(),
            "Characteristics:Аналоги": analogs.strip(),
            "Characteristics:Материал": material.strip(),
            "Characteristics:d / l": diameter_length.strip(),
            "Characteristics:lt": "",
            "Characteristics:s": "",
            "Characteristics:k": "",
            "Characteristics:Привод": drive.strip(),
            "Characteristics:dk": "",
            "Characteristics:lb": "",
            "Characteristics:XX": "",
            "Characteristics:1": "",
            "Characteristics:Диаметр резьбы": "",
            "Characteristics:L1 (длина кронштейна)": "",
            "Weight": weight.strip(),
            "Length": length.strip(),
            "Width": width.strip(),
            "Height": height.strip(),
            "SEO title": "",
            "SEO descr": "",
            "SEO keywords": "",
            "FB title": "",
            "FB descr": ""
        }
        
        # Добавляем товар в CSV файл
        import os
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_file = os.path.join(BASE_DIR, "store-7407308-202509021623.csv")
        
        # Проверяем, существует ли файл
        file_exists = os.path.exists(csv_file)
        
        # Определяем режим открытия файла
        mode = 'a' if file_exists else 'w'
        
        with open(csv_file, mode, newline='', encoding='utf-8') as file:
            # Получаем заголовки из существующего файла или используем стандартные
            if file_exists:
                # Читаем заголовки из существующего файла
                with open(csv_file, 'r', encoding='utf-8') as read_file:
                    reader = csv.reader(read_file, delimiter=';')
                    headers = next(reader)
            else:
                # Используем стандартные заголовки
                headers = list(csv_data.keys())
            
            writer = csv.DictWriter(file, fieldnames=headers, delimiter=';', quoting=csv.QUOTE_ALL)
            
            # Записываем заголовки только если файл новый
            if not file_exists:
                writer.writeheader()
            
            # Записываем данные товара
            writer.writerow(csv_data)
        
        # Обновляем кэш товаров в main.py
        try:
            from app.main import force_refresh_products_cache
            force_refresh_products_cache()
        except Exception as e:
            print(f"Warning: Could not reload products cache: {e}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True, 
                "message": f"Товар '{name}' успешно добавлен с ID: {product_id}",
                "product_id": product_id
            }
        )
        
    except Exception as e:
        print(f"Error adding product: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Ошибка при добавлении товара: {str(e)}"}
        )


def get_admin_stats():
    """Получение статистики для админ панели (оптимизированная версия)"""
    stats = {
        "total_products": 0,
        "visible_products": 0,
        "hidden_products": 0,
        "total_orders": 0,
        "total_quantity": 0,
        "last_order": None
    }
    
    try:
        # Используем кэшированные товары
        from app.main import PRODUCTS, get_visible_products, get_hidden_products
        stats["total_products"] = len(PRODUCTS)
        stats["visible_products"] = len(get_visible_products())
        stats["hidden_products"] = len(get_hidden_products())
        
        # Подсчет заявок (только последние 50)
        orders = load_orders()
        stats["total_orders"] = len(orders)
        stats["total_quantity"] = sum(order.get('total_quantity', 0) for order in orders)
        
        if orders:
            stats["last_order"] = max(orders, key=lambda x: x.get('timestamp', ''))
            
    except Exception:
        # В продакшене не выводим детальные ошибки
        pass
    
    return stats

def load_all_products():
    """Загрузка всех товаров (оптимизированная версия)"""
    # Используем глобальные товары из main.py для экономии памяти
    from app.main import PRODUCTS
    return PRODUCTS

def load_orders():
    """Загрузка заявок (оптимизированная версия для продакшена)"""
    orders = []
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    orders_file = os.path.join(BASE_DIR, "orders.json")
    
    if os.path.exists(orders_file):
        try:
            with open(orders_file, 'r', encoding='utf-8') as file:
                orders = json.load(file)
                # Обрабатываем items для каждой заявки
                for order in orders:
                    if 'items' in order:
                        if isinstance(order['items'], str):
                            try:
                                order['items'] = json.loads(order['items'])
                            except:
                                order['items'] = []
                        elif not isinstance(order['items'], list):
                            order['items'] = []
                    else:
                        order['items'] = []
                
                # Ограничиваем количество заявок для отображения (последние 50)
                orders = orders[-50:] if len(orders) > 50 else orders
                
        except Exception as e:
            # В продакшене не выводим детальные ошибки
            pass
    
    return orders


def load_settings():
    """Загрузка настроек (оптимизированная версия)"""
    # Кэшируем настройки для экономии ресурсов
    settings = {
        "min_order_quantity": 100,
        "telegram_enabled": True,
        "email_enabled": True,
        "site_title": "МЕТРИКС",
        "contact_phone": "+7 (900) 199-39-69",
        "contact_email": "metriks66@bk.ru"
    }
    
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings_file = os.path.join(BASE_DIR, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as file:
                saved_settings = json.load(file)
                settings.update(saved_settings)
        except Exception:
            # В продакшене не выводим детальные ошибки
            pass
    
    return settings

