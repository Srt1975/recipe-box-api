from app import create_app
from app.init_db import init_db

def main():
    # Create the Flask app with the testing configuration
    app = create_app("testing")

    # Initialize the database
    init_db(app)

if __name__ == "__main__":
    main()