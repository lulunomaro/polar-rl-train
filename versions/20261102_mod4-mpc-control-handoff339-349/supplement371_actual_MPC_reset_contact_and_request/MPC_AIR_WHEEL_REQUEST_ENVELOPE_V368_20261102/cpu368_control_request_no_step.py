from pathlib import Path
import copy,json,sys,numpy as np
D=Path(sys.argv[1]);sys.path.insert(0,str(D/'source'))
from source_event_mpc353 import SourceEventMPC353
b=json.loads((D/'source353_gains.json').read_bytes());base=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02));changed=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02,bound_air_wheel_request=True))
x=np.r_[base.g['q'],np.zeros(7)];x[0]=-.8;q=np.array([x[3],x[3]+x[4],0,x[5],x[5]+x[6],0]);v=np.zeros(6)
a=base.command(0.,x,q,v);r=changed.command(0.,x,q,v);assert np.array_equal(a['tau'],r['tau'])and np.array_equal(a['processed_target'],r['processed_target'])
fixtures=[]
for t in(.02,.2,.6):
 aa=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02));bb=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02,bound_air_wheel_request=True))
 for controller in(aa,bb):controller.launch_time=0.;controller.launch_pose=np.array([x[3],x[4],x[5],x[6]]);controller.launch_velocity=np.zeros(4)
 state=x.copy();state[2]=-.7;state[9]=-5.
 old=aa.command(t,state,q,v);new=bb.command(t,state,q,v)
 assert np.array_equal(new['tau_source_requested'],old['tau'])
 assert np.array_equal(new['tau'][[0,1,3,4]],old['tau'][[0,1,3,4]])
 assert np.max(np.abs(new['tau'][[2,5]]))<=5.775909774436091
 assert np.isfinite(new['processed_target']).all()
 fixtures.append(dict(phase=new['phase'],source_wheel=old['tau'][[2,5]].tolist(),bounded_wheel=new['tau'][[2,5]].tolist()))
print(json.dumps(dict(passed=True,approach_identical=True,leg_requests_identical=True,fixtures=fixtures,NN=0,SDK=0,physics=0)))
