import httpx
import time


# ingredients = ["eggs", "milk", "bread", "cheese", "flour"]
ingredients = ["eggs", "milk", "bread"]
start = time.perf_counter()
for ingredient in ingredients:
    response = httpx.get(f"http://127.0.0.1:5001/nutrition/{ingredient}")
    print(f"Status Code: {response.status_code} for {ingredient}")
end = time.perf_counter()
print(f"Time taken: {end - start:.4f} seconds for ({len(ingredients)} ingredients)")