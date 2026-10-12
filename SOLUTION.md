## Results
All values are milliseconds per operation (PING is the average round-trip time).

| Method          | Local | Same-Zone | Different Region |
|-----------------|------:|----------:|-----------------:|
| REST add        |  2.91 |      3.57 |           352.70 |
| gRPC add        |  0.72 |      1.18 |           185.02 |
| REST rawimg     |  5.57 |      7.50 |          1575.31 |
| gRPC rawimg     | 11.07 |     13.33 |           367.79 |
| REST dotproduct |  3.36 |      4.28 |           446.63 |
| gRPC dotproduct |  0.81 |      1.39 |           296.02 |
| REST jsonimg    | 25.30 |     31.11 |          1832.74 |
| gRPC jsonimg    | 22.21 |     26.53 |           222.51 |
| PING            | 0.053 |     0.443 |           177.82 |

## Observations
On the local and same-zone setups, the network contributed almost nothing (ping was 0.05 ms and 0.44 ms), so the timings mostly reflect software overhead. gRPC was about 3–4× faster than REST for small calls like `add` and `dotproduct`, because it sends a compact binary message over an HTTP/2 connection that is already open. REST opens a new TCP connection, sends HTTP headers and JSON, and goes through Flask on every request. Cross-region, network latency became the dominant cost. With a 178 ms ping, REST `add` took 353 ms, about two round trips (one for the TCP handshake, one for the request). gRPC `add` took 185 ms, about one round trip, because it reuses a single TCP connection for all queries. The difference was largest for the images. REST needed roughly 9–10 round trips per image, because every new connection has to go through TCP slow start, while gRPC's already-warm connection needed only 1–2. That made gRPC 4.3× faster for raw images and 8.2× faster for JSON images.

### Additional points:
- Connection reuse matters more than the data format: gRPC's main advantage across regions comes from keeping one connection open, not from its binary encoding.
- gRPC was slower for raw images on low-latency links: about 2× locally and 1.7× within the zone. I re-ran these tests twice and got the same result. The same code ran faster with gRPC on a laptop, so this appears to be the cost of gRPC moving a 1.6 MB message on a small 2-vCPU VM.
- Base64 encoding is expensive: `jsonimg` was the slowest operation locally for both protocols, and needed about one more round trip than `rawimg` cross-region because of the 33% larger payload.