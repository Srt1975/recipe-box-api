import os
from dotenv import load_dotenv


load_dotenv()

class Config:
   DEBUG = False
   PORT = 5001
   JWT_SECRET = os.getenv("JWT_SECRET")
   DATABASE = os.getenv("DATABASE")
   JWT_ALGORITHM = "HS256"

   if not JWT_SECRET:
       raise ValueError("JWT_SECRET environment variable is not set.")

   if not DATABASE:
       raise ValueError("DATABASE environment variable is not set.")

class DevelopmentConfig(Config):
   DEBUG = True
   PORT = 5001
   DATABASE = "recipes_dev.db"

class ProductionConfig(Config):
   DEBUG = False
   PORT = 5001
   DATABASE = "recipes_prod.db"

class TestingConfig(Config):
   DEBUG = True
   PORT = 5001
   DATABASE = "recipes_test.db"
   