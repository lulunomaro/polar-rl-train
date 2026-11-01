"""Fresh user-requested E0 copy225 view. No old-window actions or inference."""
from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent;R=B/'reports';D=B/'VISIBLE_MUJOCO237_ACTUAL'
assert not D.exists()
receipt=json.loads((R/'ROOT237_ONE_SELECTED230_POSE_TRANSFER_INTEGRITY_ACTUAL.json').read_bytes());assert receipt['passed']
script=B/'view237_E0_copy225_actual230_true_MOD4.py'
with (R/'ROOT237_LOCAL_VISUAL_READ_ONCE_BEFORE_LAUNCH.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),human_requested_visible_E0_branch=True,selected_pose=receipt,
   local_pose_byte_opens=1,integrity_passes=1,selected_npz_members_each=1,model_NN_SDK_physics_calls=0,
   maximum_window_seconds=7200,viewer_source_SHA=hashlib.sha256(script.read_bytes()).hexdigest(),
   display_scope='recorded230 / independent225 repaircopy from trained32341 /not live,not original frozenE0'),f,indent=2)
python=Path('C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe')
args=[str(python),'-B','-X','utf8',str(script),'--base',str(B),'--out',str(D)]
with (R/'ROOT237_LOCAL_VIEWER_ORIGINAL_CONSOLE.log').open('xb') as log:
 child=subprocess.Popen(args,cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with (R/'ROOT237_ORIGINAL_LOCAL_LAUNCH_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),pid=child.pid,exe=str(python),argv=args,cwd=str(B),user_requested_GUI=True,creation_not_yet_verified=True),f,indent=2)
deadline=time.monotonic()+35
while time.monotonic()<deadline:
 start=D/'DISPLAY237_WINDOW_STARTED_ACTUAL.json';shot=D/'MUJOCO237_E0_COPY225_INITIAL_FRAME.png'
 if start.exists() and shot.exists():
  v=json.loads(start.read_bytes());assert v['pid']==child.pid and v['visible'] and v['independent_repair_copy225']
  print(json.dumps(dict(started=True,pid=child.pid,creation=v['creation'],model_iteration=32341,repair_copy225=True,frame=str(shot))));break
 if child.poll() is not None:
  print(json.dumps(dict(started=False,returncode=child.returncode,console=str(R/'ROOT237_LOCAL_VIEWER_ORIGINAL_CONSOLE.log'))));raise SystemExit(1)
 time.sleep(.5)
else:print(json.dumps(dict(start_pending=True,pid=child.pid,only_original_handle=True)))
