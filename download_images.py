#!/usr/bin/env python3
"""
Скрипт для скачивания ВСЕХ изображений с сайта metriks96.ru в максимальном качестве
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import time
from pathlib import Path
import re
import json

class AdvancedImageDownloader:
    def __init__(self, base_url="https://metriks96.ru"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.downloaded_images = set()
        self.image_folder = Path("downloaded_images")
        self.image_folder.mkdir(exist_ok=True)
        self.visited_urls = set()
        self.all_found_urls = set()
        
    def get_page_content(self, url):
        """Получить содержимое страницы"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return None
    
    def get_high_quality_url(self, image_url):
        """Попытаться получить URL изображения в максимальном качестве"""
        # Для Tilda (на котором построен сайт) часто есть параметры качества
        parsed = urlparse(image_url)
        
        # Убираем параметры сжатия и ресайза
        high_quality_variants = [
            image_url,  # оригинальный URL
            re.sub(r'resize=\d+x\d+', '', image_url),  # убираем resize
            re.sub(r'quality=\d+', 'quality=100', image_url),  # максимальное качество
            re.sub(r'format=webp', 'format=jpg', image_url),  # JPG вместо WebP
            re.sub(r'_\d+x\d+\.', '.', image_url),  # убираем размеры из имени файла
            re.sub(r'thumb_', '', image_url),  # убираем префикс thumb
            re.sub(r'small_', '', image_url),  # убираем префикс small
            re.sub(r'medium_', '', image_url),  # убираем префикс medium
        ]
        
        # Добавляем варианты без параметров
        if '?' in image_url:
            base_url = image_url.split('?')[0]
            high_quality_variants.append(base_url)
        
        return high_quality_variants

    def extract_images_from_html(self, html_content, base_url):
        """Извлечь ВСЕ URL изображений из HTML с максимальным качеством"""
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = set()
        
        # 1. Найти все теги img с различными атрибутами
        for img in soup.find_all('img'):
            # Стандартные атрибуты
            for attr in ['src', 'data-src', 'data-original', 'data-lazy', 'data-srcset', 'srcset']:
                value = img.get(attr)
                if value:
                    # Обработка srcset (может содержать несколько URL)
                    if 'srcset' in attr:
                        urls = re.findall(r'(https?://[^\s,]+)', value)
                        for url in urls:
                            image_urls.update(self.get_high_quality_url(url))
                    else:
                        full_url = urljoin(base_url, value)
                        image_urls.update(self.get_high_quality_url(full_url))
        
        # 2. Найти CSS background-image во всех элементах
        for element in soup.find_all():
            style = element.get('style', '')
            if 'background' in style:
                urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                for url in urls:
                    full_url = urljoin(base_url, url)
                    if self.is_image_url(full_url):
                        image_urls.update(self.get_high_quality_url(full_url))
        
        # 3. Найти изображения в JavaScript коде
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Поиск URL изображений в JS
                js_urls = re.findall(r'["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg|bmp|ico)[^"\']*)["\']', script.string, re.IGNORECASE)
                for url in js_urls:
                    full_url = urljoin(base_url, url)
                    image_urls.update(self.get_high_quality_url(full_url))
        
        # 4. Найти изображения в data-атрибутах
        for element in soup.find_all():
            for attr_name, attr_value in element.attrs.items():
                if 'data-' in attr_name and isinstance(attr_value, str):
                    if self.is_image_url(attr_value):
                        full_url = urljoin(base_url, attr_value)
                        image_urls.update(self.get_high_quality_url(full_url))
        
        # 5. Поиск в тексте страницы (иногда URL встречаются в тексте)
        text_urls = re.findall(r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp|svg|bmp|ico)[^\s<>"]*', html_content, re.IGNORECASE)
        for url in text_urls:
            image_urls.update(self.get_high_quality_url(url))
        
        return image_urls
    
    def is_image_url(self, url):
        """Проверить, является ли URL изображением"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return any(path.endswith(ext) for ext in image_extensions)
    
    def try_download_best_quality(self, image_urls):
        """Попытаться скачать изображение в лучшем качестве из списка вариантов"""
        for image_url in image_urls:
            if image_url in self.downloaded_images:
                continue
                
            try:
                # Проверяем доступность URL
                head_response = self.session.head(image_url, timeout=5)
                if head_response.status_code == 200:
                    # Скачиваем изображение
                    response = self.session.get(image_url, timeout=15)
                    response.raise_for_status()
                    
                    # Проверяем, что это действительно изображение
                    content_type = response.headers.get('content-type', '').lower()
                    if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                        continue
                    
                    # Определить имя файла
                    parsed_url = urlparse(image_url)
                    filename = os.path.basename(parsed_url.path)
                    if not filename or '.' not in filename:
                        # Определяем расширение по content-type
                        ext = '.jpg'
                        if 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        filename = f"image_{abs(hash(image_url)) % 100000}{ext}"
                    
                    # Убедиться, что имя файла уникально
                    counter = 1
                    original_filename = filename
                    while (self.image_folder / filename).exists():
                        name, ext = os.path.splitext(original_filename)
                        filename = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Сохранить файл
                    file_path = self.image_folder / filename
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Отметить все варианты как скачанные
                    for url in image_urls:
                        self.downloaded_images.add(url)
                    
                    size_mb = len(response.content) / (1024 * 1024)
                    print(f"✓ Скачано: {filename} ({size_mb:.2f} MB)")
                    return True
                    
            except requests.RequestException:
                continue
        
        print(f"✗ Не удалось скачать ни один вариант из {len(image_urls)} URL")
        return False
    
    def discover_all_pages(self):
        """Автоматически найти все страницы сайта"""
        discovered_pages = set()
        pages_to_check = [self.base_url]
        
        while pages_to_check:
            current_url = pages_to_check.pop(0)
            if current_url in self.visited_urls:
                continue
                
            print(f"🔍 Исследуем: {current_url}")
            self.visited_urls.add(current_url)
            
            html_content = self.get_page_content(current_url)
            if not html_content:
                continue
                
            discovered_pages.add(current_url)
            
            # Найти все ссылки на этой странице
            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                
                # Проверить, что ссылка ведет на тот же домен
                if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                    if full_url not in self.visited_urls and full_url not in pages_to_check:
                        pages_to_check.append(full_url)
            
            time.sleep(0.5)  # Пауза между запросами
        
        return list(discovered_pages)

    def get_all_pages(self):
        """Получить список всех страниц для парсинга"""
        # Основные страницы
        pages = [
            self.base_url,
            f"{self.base_url}/catalog",
            f"{self.base_url}/payment", 
            f"{self.base_url}/contacts",
            f"{self.base_url}/politics",
        ]
        
        # Добавить страницы категорий товаров
        categories = [
            "Саморезы", "Винты", "Заклепки", "Болты", 
            "Гайки", "Шайбы", "Шпильки", "Кронштейны", "Нагель"
        ]
        
        for category in categories:
            catalog_url = f"{self.base_url}/catalog?tfc_storepartuid[606177230]={category}&tfc_div=:::"
            pages.append(catalog_url)
        
        # Автоматически найти дополнительные страницы
        print("🔍 Автоматический поиск всех страниц сайта...")
        discovered_pages = self.discover_all_pages()
        pages.extend(discovered_pages)
        
        # Убрать дубликаты
        return list(set(pages))
    
    def download_all_images(self):
        """Основная функция для скачивания ВСЕХ изображений в максимальном качестве"""
        print(f"🚀 Начинаем агрессивное скачивание ВСЕХ изображений с {self.base_url}")
        print(f"📁 Папка для сохранения: {self.image_folder.absolute()}")
        
        pages = self.get_all_pages()
        print(f"📄 Найдено страниц для парсинга: {len(pages)}")
        
        # Группируем изображения по вариантам качества
        image_groups = {}
        
        # Собрать все URL изображений со всех страниц
        for i, page_url in enumerate(pages, 1):
            print(f"\n🔍 [{i}/{len(pages)}] Парсинг: {page_url}")
            html_content = self.get_page_content(page_url)
            
            if html_content:
                image_urls = self.extract_images_from_html(html_content, page_url)
                print(f"   Найдено вариантов изображений: {len(image_urls)}")
                
                # Группируем похожие изображения
                for url in image_urls:
                    # Создаем ключ группы на основе базового имени файла
                    base_name = re.sub(r'[?&].*', '', url)  # убираем параметры
                    base_name = re.sub(r'_\d+x\d+', '', base_name)  # убираем размеры
                    base_name = re.sub(r'(thumb_|small_|medium_)', '', base_name)  # убираем префиксы
                    
                    if base_name not in image_groups:
                        image_groups[base_name] = []
                    image_groups[base_name].append(url)
                
                time.sleep(0.8)  # Пауза между запросами
        
        print(f"\n📊 Найдено групп изображений: {len(image_groups)}")
        total_variants = sum(len(variants) for variants in image_groups.values())
        print(f"📊 Всего вариантов изображений: {total_variants}")
        
        # Скачать лучший вариант из каждой группы
        print(f"\n⬇️  Начинаем скачивание в максимальном качестве...")
        downloaded_count = 0
        
        for i, (base_name, variants) in enumerate(image_groups.items(), 1):
            print(f"\n[{i}/{len(image_groups)}] Группа: {os.path.basename(base_name)}")
            print(f"   Вариантов: {len(variants)}")
            
            # Сортируем варианты по приоритету качества
            sorted_variants = self.sort_by_quality_priority(variants)
            
            if self.try_download_best_quality(sorted_variants):
                downloaded_count += 1
            
            time.sleep(0.3)  # Пауза между скачиваниями
        
        print(f"\n✅ ЗАВЕРШЕНО! Скачано {downloaded_count} изображений в максимальном качестве")
        print(f"📁 Все файлы сохранены в: {self.image_folder.absolute()}")
        return downloaded_count
    
    def sort_by_quality_priority(self, variants):
        """Сортировать варианты изображений по приоритету качества"""
        def quality_score(url):
            score = 0
            url_lower = url.lower()
            
            # Приоритет оригинальным изображениям
            if 'original' in url_lower or 'full' in url_lower:
                score += 1000
            
            # Штраф за сжатые версии
            if 'thumb' in url_lower:
                score -= 500
            if 'small' in url_lower:
                score -= 400
            if 'medium' in url_lower:
                score -= 200
            
            # Приоритет по размеру в URL
            size_matches = re.findall(r'(\d+)x(\d+)', url)
            if size_matches:
                width, height = map(int, size_matches[-1])
                score += width * height / 1000  # больше размер = больше приоритет
            
            # Приоритет форматам без потерь
            if url_lower.endswith('.png'):
                score += 50
            elif url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
                score += 30
            elif url_lower.endswith('.webp'):
                score += 20
            
            # Штраф за параметры сжатия
            if 'quality=' in url and 'quality=100' not in url:
                score -= 100
            if 'compress' in url_lower:
                score -= 150
            
            return score
        
        return sorted(variants, key=quality_score, reverse=True)

def main():
    downloader = AdvancedImageDownloader()
    downloader.download_all_images()

if __name__ == "__main__":
    main()
