import os 
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_LOCATIONS_URL = os.getenv("API_LOCATIONS_URL")
API_TRIPS_URL = os.getenv("API_TRIPS_URL")
CHECK_RESERVED_SEATS_URL = os.getenv("CHECK_RESERVED_SEATS_URL")