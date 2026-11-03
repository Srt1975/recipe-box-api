# Execution Model Decision Rule (DRAFT)

## 1. When to use simple synchronous I/O

- When each step logically depends on the previous result.
- When there are only a few calls and latency is acceptable.
- When I want the simplest code and don’t need overlap.


## 2. When to use threaded I/O

- When calls are I/O-bound and independent (they don’t depend on each other).
- When I want to overlap network waiting time to cut total latency.
- When I’m okay with extra complexity (threads) to speed up I/O.


## 3. When to consider async (conceptual, not measured yet)

- When there are *many* concurrent I/O operations (more than is comfortable with threads).
- When I need high scalability and tighter control over concurrency.
- When I’m willing to trade simplicity for performance and scalability.

## 4. When to use processes for CPU-bound work (concept only)

- When the workload is CPU-bound and I need to use multiple cores.
- When threads don’t speed things up because of the GIL.
- When the overhead of extra processes is worth the CPU parallelism.