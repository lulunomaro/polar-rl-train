"""Same local nominal stair replay for parent and every timed saved actor. No updates."""
from pathlib import Path
import sys,json,time,hashlib,traceback
import torch
torch.set_num_threads(1)
T=Path(__file__).resolve().parent;R=T.parents[2];O=T/'evidence/local_stair_replay';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'tmp/rough_v1_local_showcase_20261112'))
import showcase as show
parent=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt'
all_rows=[]
for label,p in [('parent',parent)]+[(f'{m:03d}m',T/f'weights/model_{m:03d}m.pt') for m in (5,10,15,20)]:
 while not p.exists():
  if (T/'evidence/training_round/ERROR.json').exists():raise RuntimeError('training error; missing checkpoint '+str(p))
  time.sleep(15)
 show.CKPT=p;show.EXPECTED=hashlib.sha256(p.read_bytes()).hexdigest()
 for direction,height,speed in [('up',.365,2.2),('up',.4,2.2),('up',.28,1.),('down',.28,1.)]:
  s=show.Replay(direction=direction);s.args.vx=speed;trajectory=[];success=False;peak_x=-100.;peak_ground=0.
  try:
   for k in range(1000):
    s.set_height(.28+(height-.28)*min(k/100.,1.))
    s.step({'w'} if k>=150 else set())
    x,y=map(float,s.env.d.qpos[:2]);ground=s.ground(x,y);peak_x=max(x,peak_x);peak_ground=max(ground,peak_ground)
    trajectory.append(dict(t=k*.02,x=x,y=y,ground=ground,relative_height=float(s.z),vx=float(s.env.vx),command_height=s.height,closure=s.closure,resets=s.reset_count-1,reason=s.reason))
    success=bool(s.reset_count==1 and s.cos_tilt>.766 and s.z>.18 and ((direction=='up' and x>-.9 and ground>.30) or (direction=='down' and x>3.8 and ground<.02)))
    if success or s.reset_count>1:break
   row=dict(model=label,checkpoint_sha256=show.EXPECTED,direction=direction,height=height,speed=speed,height_ramp_seconds=2.,forward_start_seconds=3.,success=success,peak_x=peak_x,peak_ground=peak_ground,resets=s.reset_count-1,reason=s.reason,trajectory=trajectory)
   all_rows.append(row)
   (O/f'{label}_{direction}_h{height}.json').write_text(json.dumps(row,indent=2),encoding='utf8')
   print(json.dumps({k:v for k,v in row.items() if k!='trajectory'}),flush=True)
  finally:s.close()
 (O/'RESULT.json').write_text(json.dumps(dict(protocol='One deterministic nominal MuJoCo replay per case/model; exact previous tile r00_c00, two16.5cm steps,0.33m platform;2.5ms physics; native local2mm guard; same standing pose; not fullDR or success-rate estimate',cases=all_rows),indent=2),encoding='utf8')
(O/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(all_rows))),encoding='utf8')

