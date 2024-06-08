Objective:
The Image Server project aims to develop an image server capable of scraping menu images from various restaurants in Mumbai, extracting items and prices using Optical Character Recognition (OCR), and storing this information in a database.

Functionality:
Scraping Menu Images:

The server is designed to crawl through specified restaurant websites to locate and download menu images.

The scraping process identifies menu images from HTML content, ensuring compatibility across different website structures.
OCR Processing:

After downloading menu images, the server utilizes Optical Character Recognition (OCR) technology to extract text data. I have use tesseract for this.
This process involves converting the images into machine-readable text, enabling the identification of menu items and their corresponding prices.
Assumptions are made regarding the clarity and format of menu images to optimize OCR accuracy.
Storage in Database:

Extracted menu items and prices are stored in a database for future retrieval and analysis.
The server utilizes a MySQL database to store structured data, facilitating easy querying and manipulation.
Each menu item is associated with its respective price and restaurant source, allowing for efficient organization and management of data.
Usage:
Setup:

Ensure all necessary dependencies, including Scrapy, pytesseract, and MySQL Connector, are installed.
Configure the MySQL database connection parameters in the code to match your environment.
Execution:

Run the MenuSpider class to initiate the scraping process.
The spider will visit the specified restaurant URLs, download menu images, perform OCR, and store the extracted data in the database.
Assumptions:
The menu images on the specified websites predominantly contain clear and OCR-readable text.
Prices are consistently formatted and identifiable within the menu images.
Menu items and prices are typically located in close proximity within the images for accurate extraction.
Stable internet connectivity is available throughout the scraping process.
The MySQL database is properly configured and accessible for data storage.
