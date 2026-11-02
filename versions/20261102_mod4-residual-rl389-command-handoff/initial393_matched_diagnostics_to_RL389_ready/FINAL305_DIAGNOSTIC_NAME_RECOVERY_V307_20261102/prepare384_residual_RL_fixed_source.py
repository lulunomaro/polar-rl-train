"""Independent384 fixes383 local missing joint catalog; no old once replay."""
from pathlib import Path
import hashlib,json,time
P=Path(__file__).resolve().parent;source=P/'prepare383_residual_RL_production.py'
with(P/'reports/LOCAL383_FEEDFORWARD_PREPARER_ORIGINAL_FAILURE.json').open('x',encoding='utf8')as f:
 json.dump(dict(epoch=time.time(),passed=False,source=str(source),SHA=hashlib.sha256(source.read_bytes()).hexdigest(),error="KeyError: joint_names in SOURCE347 export; joint catalog exists in alreadyqualified planned377 control package",exitcode=1,network=0,SDK=0,model_reads=0,GO=False,partial383preserved=True),f,indent=2)
s=source.read_text('utf8').replace('383','384')
s=s.replace("trace=T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102/reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json'","trace=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102/planned_mpc_motor377.json'")
s=s.replace("forward(self.residual_origin_actor,x).detach()","forward(self.residual_origin_actor,x)")
exec(compile(s,str(P/'prepare384_residual_generated.py'),'exec'),dict(__name__='__main__',__file__=str(P/'prepare384_residual_generated.py')))
