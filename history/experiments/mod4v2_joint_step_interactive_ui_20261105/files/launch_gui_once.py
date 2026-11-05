"""Start exactly one owned interactive GUI process, with retained logs and no hidden training."""
from pathlib import Path
import subprocess,json,time,hashlib
D=Path(__file__).resolve().parent;marker=D/'GUI_LAUNCH.json';assert not marker.exists()
py=Path(r'C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/pythonw.exe');script=D/'joint_step_viewer.py';scene=D/'interactive_scene.xml';ik=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/kinematics_v2.py'
assert all(p.is_file()for p in(py,script,scene,ik))
args=[str(py),'-B',str(script),'--scene',str(scene),'--ik',str(ik),'--render-width','1000','--render-height','760','--fps','15','--lookup-points','256']
with(D/'GUI_STDOUT.log').open('xb')as out,(D/'GUI_STDERR.log').open('xb')as err:
 p=subprocess.Popen(args,cwd=str(D),stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS)
 r=dict(epoch=time.time(),pid=p.pid,argv=args,worker_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),source_model_modified=False,GUI_requested_not_yet_verified=True,training_started=False,native_PhysX_started=False)
 marker.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
