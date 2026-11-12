from pathlib import Path
import sys,time,subprocess,json
T=Path(__file__).resolve().parent;E=T/'evidence'
while not (E/'MONITOR_COMPLETE.json').exists():time.sleep(3)
r=subprocess.run([sys.executable,'-X','utf8',str(T/'finalize_superseded.py')],cwd=T.parents[2])
(E/'SUPERSEDED_ARCHIVE_PROCESS_DONE.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=r.returncode))+'\n',encoding='utf8')
raise SystemExit(r.returncode)
