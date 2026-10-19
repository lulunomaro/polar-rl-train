"""Small player wiring smoke check; not a jump or recovery qualification."""
from pathlib import Path
import hashlib,json,sys,time,traceback
import numpy as np
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=B/'reports/FULLMAP_LATEST_BUNDLE_RUNTIME_CPU_ACTUAL.json';assert not out.exists()
    sys.path.insert(0,str(D))
    from rm7v7_moe_sim import RM7V7MoESim
    sim=RM7V7MoESim();params=sim.parameter_readback()
    assert sim.policy.path.name=='latest_moe_scut_fudan_hour7_20261019.onnx'
    assert sim.cfg.leg_kp==60 and sim.cfg.leg_kd==2 and sim.cfg.crank_scale==.5 and sim.cfg.yaw_assist_gain==0
    assert sim.command.height==.25 and not sim.command.auto_mode
    results=[]
    for mode in (0,4,3,6):
        sim.reset_route('flat_run');sim.select_skill(mode)
        for _ in range(5):
            action=sim.step_control();assert action.shape==(6,) and np.isfinite(action).all()
        h=sim.health();assert h['finite']
        results.append(dict(mode=mode,controls=5,health=h,actual_action=action.tolist()))
    unchanged={n:H(D/n)==H(B/'prechange'/n) for n in ('runtime_config.json','START_WASD.bat','START_RM7V7_MOE.bat','current_moe_sim.py')}
    assert all(unchanged.values())
    result=dict(epoch=time.time(),status='PASS',scope='Existing full RM7v7 map, original robot and controls; five-step mode wiring smoke only',
        checkpoint=str(sim.policy.path),onnx_SHA=H(sim.policy.path),parameter_readback=params,
        original_files_unchanged=unchanged,player_model_path=str(D/'rm7v7_latest_moe.xml'),
        scenarios=results,skill_qualification=False,remote_transport=False,training_or_accounting_changed=False)
    with out.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(status='PASS',checkpoint=str(sim.policy.path),parameter_readback=params)))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (B/'reports'/('FULLMAP_SMOKE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc()),f,indent=2)
        raise
