# CSH-07 review round 1

Candidate: 9e77e721b13a1e11785937a6097c3c89c211beb9
Reviewer: gpt-6.1-sol (medium)
Verdict: REJECTED
Boundary: ok

High: parsing continues after the -- separator. For `ask ui -- --server.address=127.0.0.1`, the wrapper suppresses its default but Streamlit treats that token as an app argument, allowing ambient non-loopback binding. Stop parsing server options at --; preserve app arguments and insert default before separator. Add argv and real listener regression coverage.
