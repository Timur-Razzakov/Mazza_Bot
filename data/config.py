import os

from decouple import config, Csv

BOT_TOKEN = config('BOT_TOKEN')
# id admin
ADMIN_ID = config("ADMINS_ID", cast=Csv(int))
IP = config("IP_ADDRESS")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_NAME = config("DB_NAME")
DB_HOST = config("DB_HOST")
DB_PORT = config("PORT")

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Image_PATH = os.path.join(BASE_DIR, 'media', 'images', 'image_malika.png')
