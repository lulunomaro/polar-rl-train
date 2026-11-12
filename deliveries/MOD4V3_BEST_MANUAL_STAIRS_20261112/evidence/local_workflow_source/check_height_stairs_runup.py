from pathlib import Path
import sys,json
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from showcase import Replay,EXPECTED
rows=[]
for height in [.365,.4]:
 s=Replay();s.args.vx=2.2;trajectory=[];success=False
 for k in range(1000):
  s.set_height(.28+(height-.28)*min(k/100,1.))
  s.step({'w'} if k>=150 else set());x=float(s.env.d.qpos[0]);ground=s.ground(x,float(s.env.d.qpos[1]));trajectory.append(dict(t=k*.02,x=x,y=float(s.env.d.qpos[1]),ground=ground,z=float(s.z),vx=float(s.env.vx),height=s.height,closure=s.closure,resets=s.reset_count-1,reason=s.reason))
  if x>-.9 and ground>.30 and s.z>.18 and s.cos_tilt>.766 and s.reset_count==1:success=True;break
  if s.reset_count>1:break
 rows.append(dict(height=height,height_ramp_seconds=2.,command_vx=2.2,runup_start_seconds=3.,tile='r00_c00',single_step_height=.165,platform_height=.33,success=success,trajectory=trajectory));s.close();print('RUNUP_RESULT',height,success,trajectory[-1]['x'],trajectory[-1]['ground'],flush=True)
(B/'HEIGHT_STAIRS_RUNUP_CHECK.json').write_text(json.dumps(dict(scope='One short run-up condition per height on same actor and exact playback physics; no training',checkpoint_sha256=EXPECTED,cases=rows),indent=2),encoding='utf8')
