"""Preserve failed admissions and dispatch a new, separately versioned probe."""
from pathlib import Path
import json,ast,runpy,sys
R=Path(__file__).resolve().parent
e=R/'reports/NATIVE_DEPLOY_001_ERROR.json'
assert not e.exists()
e.write_text(json.dumps({'attempt':'native_pair_deploy_v1','status':'failed_before_sdk_or_parent_dispatch','error':'Paramiko SFTP mode x does not imply write; new staged file must use wx','native_calls':0,'source_model_opens':0,'old_scripts_preserved':True,'additional_local_attempt':'PowerShell inline v2 builder had a quoting ParserError and executed no Python','SDK_source_fact':'Current SimulationCfg uses physics=PhysxCfg, not physx=PhysxCfg','old_candidate_mock_companion_scope':'Packaged runtime_adapter v1 used cfg.sim.physx in its mock; new task must use actual cfg.sim.physics or original task __post_init__'},indent=2),encoding='utf-8')
p=R/'native_mod4v1_probe_v2.py';assert not p.exists()
src=(R/'native_mod4v1_probe.py').read_text(encoding='utf-8').replace('physx=PhysxCfg(solver_type=1)','physics=PhysxCfg(solver_type=1)').replace('av.get_link_velocities()','av.get_dof_velocities()')
ast.parse(src);p.write_text(src,encoding='utf-8')
p=R/'deploy_native_pair_v2_once.py';assert not p.exists()
src=(R/'deploy_native_pair_once.py').read_text(encoding='utf-8').replace("R/'native_mod4v1_probe.py'","R/'native_mod4v1_probe_v2.py'").replace("s.open(job+'/PLAN.json','x')","s.open(job+'/PLAN.json','wx')").replace('MOD4V1_NATIVE0PT_PAIR_','MOD4V1_NATIVE0PT_PAIR_V2_')
ast.parse(src);p.write_text(src,encoding='utf-8');sys.path.insert(0,str(R));runpy.run_path(str(p),run_name='__main__')
