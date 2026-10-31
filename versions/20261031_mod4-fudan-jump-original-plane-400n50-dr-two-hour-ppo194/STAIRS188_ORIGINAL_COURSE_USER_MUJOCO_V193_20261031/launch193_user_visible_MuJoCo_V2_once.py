"""Open exactly this newly requested view, preserve all existing user windows."""
from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent;R=B/'reports';D=B/'VISIBLE_MUJOCO193_ACTUAL_V2'
assert not D.exists()
receipt=json.loads((R/'ROOT193_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())
assert receipt['passed'] and receipt['two_host_SHA_equal']
with (R/'DISPLAY193_V2_USER_REQUESTED_LOCAL_VISUAL_READ_PURPOSE.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),human_requested_visible_window=True,
        one_new193_pose_artifact=receipt,visual_byte_opens=1,visual_integrity_passes=1,npz_member_reads_each=1,
        old_model_raw_or_reference_reads=0,neural_inference=0,physics_steps=0,
        original277_meshes_for_this_new_display=True,maximum_window_seconds=7200,
        no_old_window_restart_or_close=True),f,indent=2)
python=Path('C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe')
script=B/'view193_latest188_original_Fudan_true_MOD4_V2.py';assert python.is_file()
args=[str(python),'-B','-X','utf8',str(script),'--base',str(B),'--out',str(D)]
with (R/'DISPLAY193_V2_LOCAL_ORIGINAL_CONSOLE.log').open('xb') as log:
    child=subprocess.Popen(args,cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with (R/'DISPLAY193_V2_ORIGINAL_LOCAL_LAUNCH_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),pid=child.pid,exe=str(python),argv=args,cwd=str(B),
                   user_requested_GUI=True,new_source_SHA=hashlib.sha256(script.read_bytes()).hexdigest(),
                   window_creation_not_yet_claimed=True),f,indent=2)
deadline=time.monotonic()+30
while time.monotonic()<deadline:
    start=D/'DISPLAY193_WINDOW_STARTED_ACTUAL.json';shot=D/'MUJOCO193_LATEST188_ORIGINAL_FUDAN_INITIAL_FRAME.png'
    if start.exists() and shot.exists():
        value=json.loads(start.read_bytes());assert value['pid']==child.pid and value['visible']
        print(json.dumps(dict(window_started=True,pid=child.pid,source_iteration=5065,frame=str(shot),
                              original_course=True,new_recorded_case=True)))
        break
    if child.poll() is not None:
        print(json.dumps(dict(window_started=False,returncode=child.returncode,
                              original_console=str(R/'DISPLAY193_V2_LOCAL_ORIGINAL_CONSOLE.log'))))
        raise SystemExit(1)
    time.sleep(.5)
else:
    print(json.dumps(dict(window_start_pending=True,pid=child.pid,only_same_known_handle=True)))
