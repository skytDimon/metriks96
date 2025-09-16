from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import csv
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def load_product_by_id(product_id: str):
    """Load specific product from CSV file by ID"""
    csv_file = "store-7407308-202509021623.csv"
    
    if not os.path.exists(csv_file):
        return None
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                if row.get('Tilda UID', '').strip() == product_id:
                    # Extract category from Category field
                    category = row.get('Category', '').strip()
                    if ';' in category:
                        category = category.split(';')[0].strip()
                    
                    # Create detailed product object
                    product = {
                        'id': row.get('Tilda UID', ''),
                        'name': row.get('Title', '').strip(),
                        'description': row.get('Description', '').strip() or row.get('Text', '').strip(),
                        'category': category,
                        'image': row.get('Photo', ''),
                        'brand': row.get('Brand', '').strip(),
                        'sku': row.get('SKU', '').strip(),
                        'material': row.get('Characteristics:Материал', '').strip(),
                        'application': row.get('Characteristics:Применение', '').strip(),
                        'analogs': row.get('Characteristics:Аналоги', '').strip(),
                        'standard': row.get('Mark', '').strip(),
                        'weight': row.get('Weight', ''),
                        'length': row.get('Length', ''),
                        'width': row.get('Width', ''),
                        'height': row.get('Height', ''),
                        # Размеры и характеристики
                        'diameter_length': row.get('Characteristics:d / l', '').strip(),
                        'lt': row.get('Characteristics:lt', '').strip(),
                        's': row.get('Characteristics:s', '').strip(),
                        'k': row.get('Characteristics:k', '').strip(),
                        'drive': row.get('Characteristics:Привод', '').strip(),
                        'dk': row.get('Characteristics:dk', '').strip(),
                        'lb': row.get('Characteristics:lb', '').strip(),
                        'thread_diameter': row.get('Characteristics:Диаметр резьбы', '').strip(),
                        'bracket_length': row.get('Characteristics:L1 (длина кронштейна)', '').strip(),
                        'editions': row.get('Editions', '').strip(),
                        'modifications': row.get('Modifications', '').strip()
                    }
                    return product
    except Exception as e:
        print(f"Error loading product: {e}")
        return None
    
    return None

@router.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: str):
    """Product detail page"""
    product = load_product_by_id(product_id)
    
    if not product:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product
    })
