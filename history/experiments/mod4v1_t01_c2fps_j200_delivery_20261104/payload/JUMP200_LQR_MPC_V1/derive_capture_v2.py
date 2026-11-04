"""One existing-mechanism adaptation: MiniHop early capture/quarantine/smooth reference. No gain grid."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
s=(D/'run_case.py').read_text(encoding='utf-8')
a='t=float(p.d.time);packet=p.sensor_packet();e=est.update(packet);'
b="t=float(p.d.time);isolated=launch is not None and t<launch+push+float(c['observer_quarantine_after_push_s'])\n   est.wheel_measurement_enabled=not isolated;est.ground_kinematic_constraint_enabled=not isolated;est.accel_correction=0. if isolated else 1.5\n   packet=p.sensor_packet();e=est.update(packet);"
assert s.count(a)==1;s=s.replace(a,b)
a='if land_start is None:land_start=t;land.ref[0]=x[0]+.15*x[7];est.vb[0]=x[7];est.distance=x[0]'
b=a+';landing_q0=np.asarray(actualq,float).copy()'
assert s.count(a)==1;s=s.replace(a,b)
a="est.wheel_measurement_enabled=True;est.ground_kinematic_constraint_enabled=True;est.accel_correction=1.5;vx=1.2 if t-land_start<.4 else 0.;tau=land.command(e,vx,0.)"
b="u=float(np.clip((t-land_start)/float(c['landing_ref_blend_s']),0.,1.));blend=u*u*(3.-2.*u);landing_q1=np.array([gl['q'][3],gl['q'][3]+gl['q'][4],gl['q'][5],gl['q'][5]+gl['q'][6]]);desired=(1.-blend)*landing_q0+blend*landing_q1;land.ref[3:7]=[desired[0],desired[1]-desired[0],desired[2],desired[3]-desired[2]];vx=1.2 if t-land_start<.4 else 0.;tau=land.command(e,vx,0.)"
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("('approach','landing','recovery')","('approach','landing','recovery','timed_landing_recovery')")
s=s.replace("'producer_streamed':True","'producer_streamed':False")
s=s.replace("producer_streamed=True","producer_streamed=False")
s=s.replace('JUMP200_LOCAL_MOD4_LQR_PHASES_AND_GROUND_ONLY_SCALAR_MPC_NOT_AERIAL_MPC','JUMP200_CAPTURE_V2_EXISTING_MINIHOP_SCHEDULE_GROUND_ONLY_MPC_NOT_AERIAL_MPC')
s=s.replace('WheelKFoffduringpredictedflight; inertialvelocitypushintegration; assumptionsnotvalidatedforarbitrarycontactfailure','ExistingMiniHop capture.35/observerQuarantine.50/referenceBlend.20; no contact truth in phase; inertialhandoff assumptions unqualified')
with(D/'run_capture_v2.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
c=json.loads((D/'baseline001.json').read_bytes());c.update(kind='J200_CAPTURE_V2_ONE_EXISTING_MECHANISM_NOT_GAIN_FIT',seed=200002,recover_after_push_s=.35,observer_quarantine_after_push_s=.50,landing_ref_blend_s=.20,mechanism_source='MINIHOP_LANDING_V3+MINIHOP_OBSERVER_V2 existing .35/.50/.20 schedule; measured q reference starts continuous; all K/push/motor/score unchanged')
with(D/'capture_v2_001.json').open('x',encoding='utf-8')as f:json.dump(c,f,indent=2)
print('new existing capture mechanism source ready; no physics in adaptation')
