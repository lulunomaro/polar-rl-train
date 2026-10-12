from pathlib import Path
import sys,json,time,hashlib,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012'));import wave_direction_io as transport
H=lambda raw:hashlib.sha256(raw).hexdigest()
REMOTE='D:/MOD4_async_eval/scut_wave50_gate_compare_20261012'
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'

def save(name,v):
    p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p

def connect():
    n,w=transport.io.connect_both();n.close();return w

def execute(w,code,timeout=60):
    enc=base64.b64encode(code.encode()).decode()
    cmd='"'+PY+'" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
    _,o,e=w.exec_command(cmd,timeout=timeout);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
    if rc:
        save('REMOTE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_GPU_or_4090_write=True));raise RuntimeError('Reference CPU command failed; original error retained.')
    return json.loads(raw)
