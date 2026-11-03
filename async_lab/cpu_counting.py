import time
import threading
from concurrent.futures import ThreadPoolExecutor

N = 10000000
WORKERS = 4


def count_numbers(n):
    x=0
    for _ in range(n):
        x += 1
        return x

print ("Running sequentially")
start = time.perf_counter()
for _ in range(WORKERS):
    count_numbers(N)
end = time.perf_counter()
sequential_time = end - start
print(f"Time taken: {sequential_time:.4f} seconds for ({N} numbers)")

print(f"\nRunning with {WORKERS} threads")
start_thread = time.perf_counter()
threads = []
for _ in range(WORKERS):
    t = threading.Thread(target=count_numbers, args=(N,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end_thread = time.perf_counter()
threaded_time = end_thread - start_thread
print(f"Time taken: {threaded_time:.4f} seconds for ({N} numbers)")
print(f"Threaded execution was {threaded_time / sequential_time:.2f}x SLOWER than sequential.")

