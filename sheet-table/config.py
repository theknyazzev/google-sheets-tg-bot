import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Google Sheets settings
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Sheet1')
    
    # Access control
    ALLOWED_USER_IDS = [
        int(user_id.strip()) 
        for user_id in os.getenv('ALLOWED_USER_IDS', '').split(',') 
        if user_id.strip().isdigit()
    ]
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Google Credentials
    CREDENTIALS_FILE = 'credentials.json'
