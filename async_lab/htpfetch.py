import asyncio
import time, httpx

async def fetch_one(client):
    start = time.perf_counter()
    response = await client.get("http://127.0.0.1:5001/health")
    return response.status_code, time.perf_counter() - start

async def run_sequential():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        one = await fetch_one(client)
        two = await fetch_one(client)
        three = await fetch_one(client)
    print("sequential results:", time.perf_counter() - start, one, two, three)

async def run_concurrent():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_one(client),
            fetch_one(client),
            fetch_one(client),
        )
    print("concurrent results:", time.perf_counter() - start, results)

if __name__ == "__main__":
    asyncio.run(run_sequential())
    asyncio.run(run_concurrent())