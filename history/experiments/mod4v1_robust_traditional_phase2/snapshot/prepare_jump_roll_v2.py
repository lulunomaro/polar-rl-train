"""NewjumpTRAINcounterfactual: reservelegtorqueheadroom+AHRSrollvirtualwork.
OldR13/R14source unchanged. Physicalmotor/DC/geometrylimitsnotwidened.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;src=(R/'run_jump270_timed_v1.py').read_text(encoding='utf-8');src=src.replace("dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5)","dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,roll_kp=float(c.get('ground_roll_kp',20.)),roll_kd=2.)")
needle="tau[[2,5]]=wheel\n   elif t-launch-push<recover_at:";assert needle in src
replacement="""tau[[2,5]]=wheel
    # Contact-phasehypothesis only: rootrollmoment allocatedvia measuredq footJ.
    reserve=float(c.get('push_reserve_Nm',8.));tau[leg]=np.clip(tau[leg],-40.+reserve,40.-reserve);rollmoment=float(np.clip(-float(c.get('push_roll_kp',40.))*e.roll-float(c.get('push_roll_kd',5.))*e.omega_body[0],-8.,8.));Rbody=rotation(quat_step(est.q,e.omega_body,e.sensor_age_s))
    for side,inds,qq in(('left',[0,1],actualq[:2]),('right',[3,4],actualq[2:])):
     J=est.geom.jacobian(float(qq[0]),float(qq[1]),side)[:3,:];fz=rollmoment/.4376*(1 if side=='left'else -1);tau[inds]-=J.T@(Rbody.T@np.array([0.,0.,fz]))
    yd=float(np.clip(-1.2*x[8]-.4*x[1],-.5,.5));tau[2]-=yd;tau[5]+=yd
   elif t-launch-push<recover_at:"""
src=src.replace(needle,replacement).replace("ref['push_pitch_d']*x[9]","float(c.get('push_pitch_d',ref['push_pitch_d']))*x[9]");src=src.replace("ROOT/'sensor_core_jump_v1.py',","ROOT/'sensor_core_jump_v1.py',ROOT/'prepare_jump_roll_v2.py',");src=src.replace('SENSORONLY_TIMED_JUMP270_PROTOTYPE_NOT_CONTACTFSM_RELEASE','SENSORONLY_TIMED_JUMP270_ROLLVMC_V2_NOT_CONTACTFSM_RELEASE');ast.parse(src);p=R/'run_jump270_roll_v2.py';assert not p.exists();p.write_text(src,encoding='utf-8',newline='\n');print(p)
