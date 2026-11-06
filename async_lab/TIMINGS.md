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
