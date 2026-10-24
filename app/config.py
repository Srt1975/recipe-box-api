import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 👈 add this near the top


load_dotenv()

class Config:
   DEBUG = False
   PORT = 5001
   JWT_SECRET = os.getenv("JWT_SECRET")
   DATABASE = os.getenv("DATABASE")
   JWT_ALGORITHM = "HS256"
   SQLALCHEMY_TRACK_MODIFICATIONS = False  # 👈 new

   if not JWT_SECRET:
       raise ValueError("JWT_SECRET environment variable is not set.")

   if not DATABASE:
       raise ValueError("DATABASE environment variable is not set.")


   
class DevelopmentConfig(Config):
   DEBUG = True
   PORT = 5001
   DATABASE = "recipes_dev.db"
   SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "..", "recipes_dev.db"
   )

class ProductionConfig(Config):
   DEBUG = False
   PORT = 5001
   DATABASE = "recipes_prod.db"
   SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "..", "recipes_prod.db"
   )

class TestingConfig(Config):
   DEBUG = True
   PORT = 5001
   DATABASE = "recipes_test.db"
   SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "..", "recipes_test.db"
   )

   