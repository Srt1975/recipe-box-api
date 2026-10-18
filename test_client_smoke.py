from app import create_app

def main():
    app = create_app("testing")


    client = app.test_client()

    # 1) register
    response = client.post(
    "/register",
    json={
        "username": "testuser_t1",
        "email": "testuser_t1@example.com",
        "password": "testpassword",
    },
    )
    print("register status:", response.status_code)
    print("register body:", response.get_json())
    # 2) login
    login_resp = client.post(
    "/login",
    json={
        "username": "testuser_t1",
        "password": "testpassword",
    },
)
    print("login status:", login_resp.status_code)
    print("login body:", login_resp.get_json())
    # 3) list recipes
    recipes_resp = client.get("/recipes")
    print("recipes status:", recipes_resp.status_code)
    print("recipes body:", recipes_resp.get_json())

if __name__ == "__main__":
    main()