import asyncio
import time

async def one():
    print("one: start")
    await asyncio.sleep(1)
    print("one: end")

async def two():
    print("two: start")
    await asyncio.sleep(1)
    print("two: end")

async def main():
    start = time.perf_counter()
    print("main: start")
    t1 = asyncio.create_task(one())
    t2 = asyncio.create_task(two())
    await t1
    await t2
    print("main: end")
    print("total:", time.perf_counter() - start, "seconds")

asyncio.run(main())