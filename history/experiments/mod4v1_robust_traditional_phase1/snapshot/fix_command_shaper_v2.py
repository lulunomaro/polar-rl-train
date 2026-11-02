"""PreserveV1numericalfailure; replace endpoint accelerationreset byboundedjerkfilter."""
from pathlib import Path
import hashlib,json,ast
R=Path(__file__).resolve().parent;out=R/'snapshots/sensor_core_v1_jerk_failure';assert not out.exists();out.mkdir(parents=True)
for n in('sensor_core.py','test_sensor_core.py'):
 raw=(R/n).read_bytes();(out/n).write_bytes(raw)
(out/'ERROR.json').write_text(json.dumps({'kind':'PURE_NUMERICAL_UNIT_FAILURE_NOT_PHYSICS','job':'pwsh-4b56676e58d343f0','tests':10,'passed':9,'failed':'test_cmd_shaper_rates','actual_error':'Endpoint set a=0 from a=2 inone.01supdate violatesJ10 bound .1','physics_steps':0,'original_source_SHA':hashlib.sha256((out/'sensor_core.py').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
p=R/'sensor_core.py';s=p.read_text(encoding='utf-8');a=s.index('  wanted=float(np.clip((v-self.v)/dt');b=s.index('  self.w+=',a);s=s[:a]+"  if not math.isfinite(dt)or dt<=0:raise ValueError('Positive finite controlperiod required')\n  olda=self.a;j=float(np.clip(16.*(v-self.v)-8.*self.a,-self.jerk,self.jerk));self.a=float(np.clip(self.a+j*dt,-self.accel,self.accel));self.v+=.5*(olda+self.a)*dt\n  if abs(v-self.v)<1e-5 and abs(self.a)<self.jerk*dt:self.v=float(v);self.a=0.\n"+s[b:];ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
p=R/'test_sensor_core.py';s=p.read_text(encoding='utf-8').replace('self.assertAlmostEqual(v,2.);self.assertAlmostEqual(w,4*math.pi)','self.assertAlmostEqual(v,2.,places=3);self.assertAlmostEqual(w,4*math.pi)');p.write_text(s,encoding='utf-8',newline='\n');print('V1failurepreserved; V2boundedjerkcriticalfilterwith1e-3settleassert(noinstantendpointsnap)')
