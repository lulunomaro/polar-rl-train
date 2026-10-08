"""Bounded Windows sharing-conflict retries for evaluator JSON receipts only."""
from pathlib import Path
import json,os,time,uuid

def atomic(path,value,*,replace=None,sleep=None,attempts=20):
    replace=replace or os.replace;sleep=sleep or time.sleep
    assert attempts>=1
    path=Path(path)
    temporary=path.with_name(path.name+'.'+str(os.getpid())+'.'+uuid.uuid4().hex+'.partial')
    temporary.write_text(json.dumps(value,indent=2),encoding='utf8')
    for attempt in range(attempts):
        try:
            replace(temporary,path)
            return
        except OSError as error:
            if getattr(error,'winerror',None) not in (5,32,33) or attempt+1==attempts:
                # Preserve the exact proposed JSON for a persistent real failure.
                raise
            sleep(min(.025*2**attempt,.5))

