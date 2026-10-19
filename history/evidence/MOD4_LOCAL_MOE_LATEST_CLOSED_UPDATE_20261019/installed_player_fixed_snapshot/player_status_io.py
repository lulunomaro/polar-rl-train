"""Best-effort atomic UI status snapshots under Windows sharing contention.

Only transient access/sharing errors are suppressed. A failed replacement keeps
the last complete JSON, logs the original error, and lets the next snapshot try
again. This module does not affect physics or policy exceptions.
"""
import json
import os
from pathlib import Path
import time


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    data = json.dumps(value, ensure_ascii=False, indent=2).encode('utf8')
    delays = (0.002, 0.004, 0.008)
    for attempt in range(len(delays) + 1):
        try:
            temp.write_bytes(data)
            temp.replace(path)
            return True
        except OSError as exc:
            if getattr(exc, 'winerror', None) not in (5, 32, 33):
                raise
            if attempt < len(delays):
                time.sleep(delays[attempt])
                continue
            warning = dict(epoch=time.time(), path=str(path), temp=str(temp),
                attempts=attempt + 1, winerror=exc.winerror, original_error=str(exc),
                previous_complete_json_retained=True, next_snapshot_will_retry=True)
            try:
                with (path.parent / 'STATUS_WRITE_WARNINGS.jsonl').open('a', encoding='utf8') as stream:
                    stream.write(json.dumps(warning, ensure_ascii=False) + '\n')
            except OSError:
                # A UI status warning must not terminate the simulation either.
                pass
            return False
