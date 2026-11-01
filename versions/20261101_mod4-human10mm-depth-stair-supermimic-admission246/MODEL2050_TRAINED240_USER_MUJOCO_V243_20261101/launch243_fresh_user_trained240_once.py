from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent;R=B/'reports';O=B/'VISIBLE_MUJOCO243_ACTUAL';assert not O.exists()
receipt=json.loads((R/'ROOT243_SELECTED242_POSE_TRANSFERS_ACTUAL.json').read_bytes());assert receipt['passed']
script=B/'view243_trained240_actual242_true_MOD4.py'
with(R/'ROOT243_LOCAL_VISUAL_READ_ONCE_BEFORE_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),user_requested_visible=True,selected_pose_receipts=receipt,local_pose_byte_opens_each=1,selected5_npz_members_each_read_once=True,local_model_NN_SDK_physics_calls=0,window_seconds_max=7200,viewer_source_SHA=hashlib.sha256(script.read_bytes()).hexdigest(),display_scope='trained240 iteration2135 actual242 fourcases / RECORDED NOT LIVE / original closure resets'),f,indent=2)
python=Path('C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe');args=[str(python),'-B','-X','utf8',str(script),'--base',str(B),'--out',str(O)]
with(R/'ROOT243_VIEWER_ORIGINAL_CONSOLE.log').open('xb')as log:child=subprocess.Popen(args,cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with(R/'ROOT243_LOCAL_LAUNCH_ACTUAL.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=child.pid,exe=str(python),argv=args,cwd=str(B),user_requested_GUI=True,creation_not_yet_verified=True),f,indent=2)
deadline=time.monotonic()+35
while time.monotonic()<deadline:
 p=O/'DISPLAY243_WINDOW_STARTED_ACTUAL.json';shot=O/'MUJOCO243_TRAINED240_INITIAL_FRAME.png'
 if p.exists()and shot.exists():
  q=json.loads(p.read_bytes());assert q['pid']==child.pid and q['visible']and q['model_iteration']==2135;print(json.dumps(dict(started=True,pid=child.pid,creation=q['creation'],model_iteration=2135,frame=str(shot))));break
 if child.poll()is not None:print(json.dumps(dict(started=False,returncode=child.returncode,console=str(R/'ROOT243_VIEWER_ORIGINAL_CONSOLE.log'))));raise SystemExit(1)
 time.sleep(.5)
else:print(json.dumps(dict(start_pending=True,pid=child.pid,only_original_handle=True)))
