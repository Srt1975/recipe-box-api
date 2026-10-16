from app import create_app

dev_app = create_app("development")
prod_app = create_app("production")

print("Dev:", dev_app.config["DEBUG"], dev_app.config["DATABASE"])
print("Prod:", prod_app.config["DEBUG"], prod_app.config["DATABASE"])