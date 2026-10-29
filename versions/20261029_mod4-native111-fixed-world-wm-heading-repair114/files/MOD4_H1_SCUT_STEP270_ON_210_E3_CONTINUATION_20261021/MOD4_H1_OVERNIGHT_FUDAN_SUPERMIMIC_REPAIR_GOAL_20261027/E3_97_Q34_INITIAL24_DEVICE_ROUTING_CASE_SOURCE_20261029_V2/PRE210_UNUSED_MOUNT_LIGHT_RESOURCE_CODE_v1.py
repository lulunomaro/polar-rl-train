
from pathlib import Path
import json,subprocess,shutil,psutil,time
J=Path(v['job']);mount=Path('/mnt/mod4_linux_durable_20261013');assert mount.is_mount() and not J.parent.exists() and J.resolve().is_relative_to(mount.resolve())
m=json.loads(subprocess.check_output(['findmnt','--json','--target',str(mount),'-o','UUID,OPTIONS'],text=True))['filesystems'][0];assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
line=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(mount).free>25*1024**3
J.mkdir(parents=True,mode=0o700);print(json.dumps(dict(passed=True,epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=apps.splitlines(),user_light_util_le30=True,no_unknown_PID_or_argv_read=True,mount=m,job=str(J))))
