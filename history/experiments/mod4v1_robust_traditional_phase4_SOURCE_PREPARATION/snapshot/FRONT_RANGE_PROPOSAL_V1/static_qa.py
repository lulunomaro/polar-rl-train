"""Static0Stepgeometry/guardchecks only. Syntheticmount/supportnotrealBSP."""
from pathlib import Path
import sys,json,math,dataclasses,ast,traceback
import numpy as np,mujoco
HERE=Path(__file__).resolve().parent;R=HERE.parent;sys.path.insert(0,str(R))
from rm_grid_terrain_v1 import configure
from physics_bridge_rm_grade_v1 import BufferedImuPlant
from physics_bridge import FullDR,load_gain,geometry
from range_sensor_sim import ProposedToF,RangePacket
from front_geometry import SupportView,infer_front
D=HERE/'attempts/001';D.mkdir(parents=True,exist_ok=False);checks=0

def check(value,message):
 global checks
 checks+=1
 if not value:raise AssertionError(message)

def run():
 gain=load_gain(R/'nominal_gain_v1.json');q=gain['q'];q4=(q[3],q[3]+q[4],q[5],q[5]+q[6]);chart=geometry();reports=[];stepcalls=0
 original=mujoco.mj_step
 def forbid(*a,**kw):raise AssertionError('physicssteppingforbiddeninstaticQA')
 mujoco.mj_step=forbid
 try:
  for difficulty in(.0,.5,1.):
   configure(9001,difficulty);plant=BufferedImuPlant(False);plant.attach_dr(FullDR(0,nominal=True));plant.reset(gain['symmetric'],.8);sensor=ProposedToF(plant.m,noise_half_m=0.,delay_samples=0);rows=[]
   for index,x in enumerate(np.linspace(.7,1.8,45)):
    plant.d.qpos[0]=x;mujoco.mj_forward(plant.m,plant.d);now=index*.01;packet=sensor.sample(plant.d,now);support=SupportView(now,np.eye(3),q4,True,.010,.005);result=infer_front(packet,support,chart,now);check(packet is not None and packet.valid,'validfloorrange');check(not result['qualified_for_actuation'],'neverqualifyactuation');rows.append(dict(x_m=float(x),range_m=packet.range_m,result=result))
   expected=.02+.04*difficulty;largest=max(r['result'].get('height_est_m',-99)for r in rows);check(abs(largest-expected)<.006,'topheightexactgeometry');check(abs(rows[0]['result']['height_est_m'])<.006,'initialfloorbaseline');reports.append(dict(difficulty=difficulty,expected_height=expected,max_inferred_height=largest,candidates=sum(r['result']['kind']=='ELEVATED_SURFACE_CANDIDATE'for r in rows),rows=rows));check(plant.d.time==0,'modeltimezero')
  base_packet=RangePacket(1.,1.,1,.5,True,(.15,0.,.05),(math.cos(math.radians(40)),0.,-math.sin(math.radians(40))),.005)
  good_support=SupportView(1.,np.eye(3),q4,True,.01,.005)
  bad=[(None,good_support,1.01),(dataclasses.replace(base_packet,valid=False),good_support,1.01),(dataclasses.replace(base_packet,range_m=float('nan')),good_support,1.01),(base_packet,dataclasses.replace(good_support,assumed_flat_supported_approach=False),1.01),(base_packet,dataclasses.replace(good_support,root_height_error_bound_m=None),1.01),(base_packet,dataclasses.replace(good_support,sampled_s=.8),1.01),(base_packet,good_support,1.1),(base_packet,dataclasses.replace(good_support,attitude_error_bound_rad=-1.),1.01),(dataclasses.replace(base_packet,direction_B=(0.,0.,0.)),good_support,1.01)]
  for packet,support,now in bad:check(infer_front(packet,support,chart,now)['kind']=='UNKNOWN','badinputunknown')
  delayed=ProposedToF(plant.m,noise_half_m=.005,delay_samples=1);check(delayed.sample(plant.d,0.)is None,'delaywarmupunknown');late=delayed.sample(plant.d,.01);check(late.sampled_s==0. and late.arrival_s==.01,'delaytimestampnotfaked');check(len(delayed.history)==2,'boundedhistory')
 finally:mujoco.mj_step=original
 imports=[n.module for n in ast.walk(ast.parse((HERE/'front_geometry.py').read_text()))if isinstance(n,ast.ImportFrom)];check(all('mujoco'not in str(x)for x in imports),'detectorSDKfree')
 out=dict(kind='PROPOSED_TOF_STATIC_GEOMETRY_ONLY_NOT_HARDWARE',checks=checks,failures=0,physics_steps=0,pose_forward_calls=135,hardware_binding=False,qualified_for_actuation=False,reports=reports);(D/'RESULT.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(dict(checks=checks,failures=0,physics_steps=0,heights=[dict(height=r['expected_height'],estimated=r['max_inferred_height'],candidates=r['candidates'])for r in reports]),indent=2))

if __name__=='__main__':
 try:run()
 except BaseException:
  (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
