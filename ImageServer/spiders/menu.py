
import scrapy
import mysql.connector
import os
import pytesseract
from PIL import Image

class MenuSpider(scrapy.Spider):
    name = "menu"
    allowed_domains = [
        "sequelmumbai.in",
        "restaurant-guru.in",
        "magicpin.in",
        "mumbai77.com",
        "lapanthera.in",
        "eazydiner.com",
    ]
    start_urls = [
        "https://sequelmumbai.in/dine-in-menu",
        "https://restaurant-guru.in/Manna-Restaurant-Mumbai/menu",
        "https://magicpin.in/Mumbai/Mumbai-Cst-Area/Restaurant/Ustaadi/store/a8a03/menu",
        "https://www.mumbai77.com/city/1483/food-cuisine/menu/",
        "https://lapanthera.in/food-menu/",
        'https://www.eazydiner.com/mumbai/fusion-ville-marol-central-mumbai-685317/menu',
    ]

    def __init__(self, *args, **kwargs):
        super(MenuSpider, self).__init__(*args, **kwargs)

        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin@1234",
            database="imageserver"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS menu_items(
                               id INT AUTO_INCREMENT PRIMARY KEY,
                               item_name TEXT,
                               price FLOAT
                            )''')

        self.image_dir = 'downloaded_images'
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        self.menu_data = {}

    def parse(self, response):
        menu_image_selectors = []

  

        if "restaurant-guru.in" in response.url:
            all_image_urls = response.css('img::attr(src)').getall()
            menu_image_selectors = [url for url in all_image_urls if 'menu' in os.path.basename(url).lower()]

     
        elif "mumbai77.com" in response.url:
            all_image_urls = response.css('img::attr(src)').getall()
            menu_image_selectors = [url for url in all_image_urls if 'Typical-Cafe-Food-Menu' in os.path.basename(url)]
            
        elif "eazydiner.com" in response.url:
            menu_image_selectors = response.css(".restaurantDetails_three_col_menu__vsRWX img::attr(src)").getall()
            
        else:
            menu_image_selectors = response.css('img::attr(src)').getall()

        for image_url in menu_image_selectors:
            full_url = response.urljoin(image_url)
            yield scrapy.Request(full_url, callback=self.download_image_and_process, meta={'page_url': response.url})

    def download_image_and_process(self, response):
        image_url = response.url
        page_url = response.meta['page_url']
        image_name = image_url.split("/")[-1].lower()
        image_path = os.path.join(self.image_dir, image_name)

        allowed_extensions = ['.jpg', '.jpeg', '.png']
        if any(image_name.endswith(ext) for ext in allowed_extensions):
            with open(image_path, 'wb') as f:
                f.write(response.body)
            
            ocr_text = self.perform_ocr(image_path)
            if ocr_text:
                items_prices = self.extract_items_prices(ocr_text)
                if items_prices:
                    if page_url not in self.menu_data:
                        self.menu_data[page_url] = {}
                    for item, price in items_prices:
                        self.menu_data[page_url][item] = price
                        self.store_item_and_price(item, price)
        else:
            self.logger.info(f"Skipped non-image file: {image_url}")

    def perform_ocr(self, image_path):
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            ocr_text = pytesseract.image_to_string(Image.open(image_path), config='--psm 1')
            return ocr_text
        except Exception as e:
            self.logger.error(f"Error performing OCR for image {image_path}: {e}")
            return None

    def extract_items_prices(self, ocr_text):
        items_prices = []
        lines = ocr_text.split('\n')
        for line in lines:
            parts = line.rsplit(' ', 1)
            if len(parts) == 2:
                item = parts[0].strip()
                price = parts[1].strip()
                try:
                    price = float(price.replace(',', '').replace('₹', '').replace('$', ''))
                    items_prices.append((item, price))
                except ValueError:
                    self.logger.info(f"Skipping line due to price parsing issue: {line}")
        return items_prices

    def store_item_and_price(self, item, price):
        try:
            self.logger.info(f"Inserting item: {item}, price: {price}")
            self.cursor.execute('INSERT INTO menu_items (item_name, price) VALUES (%s, %s)', (item, price))
            self.conn.commit()
        except mysql.connector.Error as err:
            self.logger.error(f"Error inserting into database: {err}")

    def close(self, reason):
        self.conn.close()
        self.logger.info(f"Menu data: {self.menu_data}")
