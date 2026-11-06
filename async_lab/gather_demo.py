import asyncio
import time

async def one():
    await asyncio.sleep(3)
    return "one"

async def two():
    await asyncio.sleep(1)
    return "two"

async def three():
    await asyncio.sleep(2)
    return "three"

async def main():
    start = time.perf_counter()
    print("main: start")
    results = await asyncio.gather(one(), two(), three())
    print("main: end")
    print("total:", time.perf_counter() - start, "seconds")
    print("results:", results)

async def main():
    start = time.perf_counter()
    results = await asyncio.gather(one(), two(), three())
    total_time = time.perf_counter() - start
    print(total_time, results)


asyncio.run(main())