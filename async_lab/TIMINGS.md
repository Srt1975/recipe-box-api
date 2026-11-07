Synchronous baseline (httpx, one-by-one)

1 ingredient (eggs):   ~1.0456 s
3 ingredients:         ~3.0580 s
5 ingredients:         ~5.1055 s

Observation: total time grows roughly with the number of sequential calls.

Threaded calls 

synchronous 3× HTTP calls:      1.0493 
threaded 3× HTTP calls:         0.037944958
async concurrent 3× HTTP calls: 0.004551333000000005

We set a 1.0s per‑call timeout so the script stays responsive, trading away any slow responses that would have arrived after 1s.


with slow service-0.01s user 0.01s system 1% cpu 1.058 total
without slow service-0.01s user 0.01s system 37% cpu 0.037 total

async shows almost 5x faster than threads

{"statuses":[200,200,200]}
curl -i http://127.0.0.1:5001/recipes/slow-test  0.01s user 0.01s system 1% cpu 1.058 total

(venv) steven@Stevens-MacBook-Air slow-service % time curl -i http://127.0.0.1:5001/recipes/slow-test
HTTP/1.1 500 INTERNAL SERVER ERROR
Server: Werkzeug/3.1.8 Python/3.9.6
Date: Sat, 07 Nov 2026 01:25:45 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 265
Connection: close

<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>
curl -i http://127.0.0.1:5001/recipes/slow-test  0.01s user 0.01s system 37% cpu 0.037 total

with slow service-0.01s user 0.01s system 1% cpu 1.058 total
without slow service-0.01s user 0.01s system 37% cpu 0.037 total

async shows almost 5x faster than threads

## /recipes/slow-test

This endpoint calls the slow nutrition service for three ingredients:
- `GET /nutrition/eggs`
- `GET /nutrition/tomatoes`
- `GET /nutrition/onion`

All three calls are made concurrently using `httpx.AsyncClient` and `asyncio.gather`.

### Timings (measured on my machine)

- Nutrition service RUNNING:
  - Command: `time curl -s -o /dev/null http://127.0.0.1:5001/recipes/slow-test`
  - Result: ~1.06s total

- Nutrition service STOPPED:
  - Command: `time curl -i http://127.0.0.1:5001/recipes/slow-test`
  - Result: ~0.04s total (fails fast with JSON error)

### Execution model decision

I implemented `/recipes/slow-test` as an **async** endpoint using `asyncio.gather` because it makes three independent, I/O‑bound HTTP requests that mostly wait on network. Async lets these requests overlap, so the total latency is close to the slowest call instead of the sum of all three, which a synchronous version would incur. Threads could also overlap these calls, but for this I/O‑heavy workload async avoids extra thread overhead and integrates cleanly with `httpx.AsyncClient`, while giving me precise control over timeouts and fallback behavior.