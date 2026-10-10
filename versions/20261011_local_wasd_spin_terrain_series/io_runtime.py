"""Bounded atomic telemetry; a locked telemetry file must not kill playback."""
from pathlib import Path
import json,os,time,uuid

def write_json(path,value,required=False):
    path=Path(path);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
        for attempt in range(3):
            try:os.replace(temp,path);return None
            except PermissionError:
                if attempt==2:raise
                time.sleep(.01)
    except OSError as exc:
        if required:raise
        return dict(type=type(exc).__name__,message=str(exc),path=str(path),attempts=3)
    finally:
        try:temp.unlink(missing_ok=True)
        except OSError:pass
