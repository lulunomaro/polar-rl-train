"""Keep periodic evaluations and final evidence collection attached to this run."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--access-dir',required=True);a=parser.parse_args()
observe=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'observe72.py'),'--access-dir',a.access_dir],cwd=T)
if observe.returncode:
    (T/'evidence/PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),observer_exit=observe.returncode),indent=2)+'\n',encoding='utf8')
    raise SystemExit(observe.returncode)
subprocess.run([sys.executable,'-X','utf8','-B',str(T/'finish_results.py')],cwd=T,check=True)
archive=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_results.py'),'--phase','final'],cwd=T,
                       capture_output=True,text=True,encoding='utf8')
if archive.returncode:
    print(archive.stdout+archive.stderr,flush=True)
    raise SystemExit(archive.returncode)
