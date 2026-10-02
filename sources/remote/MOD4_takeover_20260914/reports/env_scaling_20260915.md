# MOD4 environment scaling benchmark

- Recommended tested envs: **1536**
- Maximum stable tested envs: **1536**
- 2048 env: **FAIL — PhysX 64K material limit**

| envs | status | steady steps/s | iter s | GPU % | VRAM MiB | power W | closure m | mimic rad |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1536 | PASS | 3262 | 11.31 | 77.9 | 4911 | 133.9 | 0.000300 | 0.001600 |
| 1792 | FAIL | 4624 | 9.41 | 70.9 | 5103 | 133.7 | 0.000500 | 0.001500 |
| 2048 | FAIL |  |  |  |  |  |  |  |
