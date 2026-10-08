"""Read the installed Articulation/implicit-drive APIs without starting Isaac."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
root='D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab'
names=['assets/articulation/articulation.py','assets/articulation/articulation_data.py','actuators/actuator_pd.py']
physx='D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab_physx/isaaclab_physx'
c=connect_eval()
try:
    src=D/'installed_sdk_sources';src.mkdir(exist_ok=True);rows=[]
    with c.open_sftp() as f:
        for name in names:
            raw=f.open(root+'/'+name).read();p=src/Path(name).name;p.write_bytes(raw)
            rows.append(dict(path=root+'/'+name,sha256=hashlib.sha256(raw).hexdigest(),local=str(p)))
        for name in ('assets/articulation/articulation.py','assets/articulation/articulation_data.py'):
            raw=f.open(physx+'/'+name).read();p=src/('physx_'+Path(name).name);p.write_bytes(raw)
            rows.append(dict(path=physx+'/'+name,sha256=hashlib.sha256(raw).hexdigest(),local=str(p)))
    report=dict(epoch=time.time(),files=rows,read_only=True,no_Isaac_GPU_training_launch=True)
    (R/'INSTALLED_SPRING_SDK_SOURCE.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report))
finally:c.close()
