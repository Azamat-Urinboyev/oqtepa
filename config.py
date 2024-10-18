import functions as func
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN")
ADMINS = func.get_admins()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
