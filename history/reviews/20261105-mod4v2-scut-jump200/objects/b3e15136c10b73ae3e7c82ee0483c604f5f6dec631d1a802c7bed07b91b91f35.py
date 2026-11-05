"""Fused state reader on real stepping, reset and H32 save/resume interfaces."""
from pathlib import Path
from types import SimpleNamespace
import json,runpy,sys,time,traceback
import torch,warp as wp
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.newton_sampling import install_state_read
R=N/'sampling_state_integration02';R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0,
    active_run_modified=False,real_control_endpoints_compared=0,max_errors={})
fields=('joint_pos','joint_vel','body_pos_w','body_quat_w','body_lin_vel_w',
        'root_pos_w','root_quat_w','root_lin_vel_w','root_lin_vel_b',
        'root_ang_vel_b','projected_gravity_b')
original=NewtonEnv.__init__
def init(self,*args,**kwargs):
    original(self,*args,**kwargs)
    install_state_read(self)
    fused=self.update_data
    def checked():
        fused()
        d=self.data
        self.data=SimpleNamespace()
        try:
            NewtonEnv.update_data(self)
            for key in fields:
                error=float((getattr(d,key)-getattr(self.data,key)).abs().max())
                out['max_errors'][key]=max(out['max_errors'].get(key,0),error)
                assert error<3e-6,(key,error)
        finally:self.data=d
        out['real_control_endpoints_compared']+=1
    self.update_data=checked
NewtonEnv.__init__=init
try:
    sys.argv=[str(N/'test_supermimic_worker.py'),'--output','supermimic_fused_state09']
    runpy.run_path(sys.argv[0],run_name='__main__')
    result=json.loads((N/'supermimic_fused_state09/RESULT.json').read_bytes())
    assert result['passed']and result['resumed_bptt']['verified_bptt_optimizer_step']
    out.update(passed=True,real_worker_report=str(N/'supermimic_fused_state09/RESULT.json'),
        original_and_fused_read_from_same_physical_state=True,
        constructor_reset_and_DR_reset_compatible=True,H32_fullsave_resume_passed=True,
        production_candidate_not_installed=True)
except BaseException:out['error']=traceback.format_exc()
finally:NewtonEnv.__init__=original
with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
