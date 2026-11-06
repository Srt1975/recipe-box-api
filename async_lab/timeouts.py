
import httpx
import asyncio
import time
SLOW_SERVICE_URL = "http://127.0.0.1:5001/one"  # Default URL for the slow service
SLOW_SERVICE_URLS = [
    "http://127.0.0.1:5001/one",
    "http://127.0.0.1:5001/two",
    "http://127.0.0.1:5001/three",
]

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_with_timeout(client, url, f"call-{i}")
            for i, url in enumerate(SLOW_SERVICE_URLS, start=1)
        ]
        results = await asyncio.gather(*tasks)
        print(results)

async def fetch_with_timeout(client, url: str, name: str):
    try:
        resp = await asyncio.wait_for(
            client.get(url),
            timeout=1.0,
        )
        return {"name": name, "status": "ok", "code": resp.status_code}
    except asyncio.TimeoutError:
        return {"name": name, "status": "timeout"}
    except httpx.RequestError:
        return {"name": name, "status": "unreachable"}

if __name__ == "__main__":
    asyncio.run(main())