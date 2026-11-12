from pathlib import Path
import sys,json,time
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from showcase import Replay,FAMILIES,EXPECTED
rows=[]
for height in [.365,.40]:
 s=Replay();s.set_height(height);s.args.vx=1.;trajectory=[];success=False
 for k in range(900):
  s.step({'w'} if k>=100 else set());x=float(s.env.d.qpos[0]);ground=s.ground(x,float(s.env.d.qpos[1]));trajectory.append(dict(t=k*.02,x=x,y=float(s.env.d.qpos[1]),ground=ground,z=float(s.z),vx=float(s.env.vx),closure=s.closure,resets=s.reset_count-1,reason=s.reason))
  if x>-.9 and ground>.30 and s.z>.18 and s.cos_tilt>.766 and s.reset_count==1:success=True;break
  if s.reset_count>1:break
 rows.append(dict(height=height,command_vx=1.,tile='r00_c00',single_step_height=.165,platform_height=.33,success=success,trajectory=trajectory));s.close();print('HEIGHT_RESULT',height,success,trajectory[-1]['x'],trajectory[-1]['ground'],flush=True)
result=dict(scope='Short nominal local replay, same actor/plant/collision as the currently playing manual viewer; height commands set explicitly, no PPO',checkpoint_sha256=EXPECTED,cases=rows)
(B/'HEIGHT_STAIRS_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf8')
