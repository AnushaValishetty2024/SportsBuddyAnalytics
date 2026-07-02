import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sports-buddy-secret-key-change-in-production')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'sports_buddy')
    MYSQL_CURSORCLASS = 'DictCursor'

    # OpenAI API Configuration
    # IMPORTANT: Set OPENAI_API_KEY environment variable in production.
    # Never hardcode the API key. Store it only on the backend.
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
