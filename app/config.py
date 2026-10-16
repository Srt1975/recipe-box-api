class Config:
   DEBUG = False
   PORT = 5001

class DevelopmentConfig(Config):
   DEBUG = True
   PORT = 5001
   DATABASE = "recipes_dev.db"

class ProductionConfig(Config):
   DEBUG = False
   PORT = 5001
   DATABASE = "recipes_prod.db"