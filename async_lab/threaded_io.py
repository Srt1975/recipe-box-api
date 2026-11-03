import httpx
import time
import threading

# ingredients = ["eggs", "milk", "bread", "cheese", "flour"]
ingredients = ["eggs", "milk", "bread"]

def fetch_nutrition(ingredient):
    response = httpx.get(f"http://127.0.0.1:5001/nutrition/{ingredient}")
    print(f"Status Code: {response.status_code} for {ingredient}")

start = time.perf_counter()

threads = []
for ingredient in ingredients:
    thread = threading.Thread(target=fetch_nutrition, args=(ingredient,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end = time.perf_counter()
print(f"Time taken: {end - start:.4f} seconds for ({len(ingredients)} ingredients)")