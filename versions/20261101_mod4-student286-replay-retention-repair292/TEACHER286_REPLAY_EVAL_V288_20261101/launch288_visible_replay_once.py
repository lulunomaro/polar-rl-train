from pathlib import Path
import json,subprocess,time
N=Path(__file__).resolve().parent;R=N/'reports';assert not(N/'VISIBLE_REPLAY288').exists()
exe='C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe'
args=[exe,'-B','-X','utf8',str(N/'view288_actual_final286_replay.py')]
with(R/'VIEW288_ORIGINAL_CONSOLE.log').open('xb')as f:p=subprocess.Popen(args,cwd=N,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with(R/'VIEW288_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=p.pid,args=args,user_requested_visible=True),f,indent=2)
end=time.time()+35
while time.time()<end:
    result=N/'VISIBLE_REPLAY288/VIEW288_STARTED.json'
    if result.exists():print(result.read_text('utf8'));break
    if p.poll()is not None:raise RuntimeError((R/'VIEW288_ORIGINAL_CONSOLE.log').read_text('utf8'))
    time.sleep(.5)
