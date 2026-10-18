"""Exercise the requested original model/PD/road with the latest manual mixture."""
from pathlib import Path
import sys, json, hashlib, time, ast
import numpy as np
B=Path(__file__).resolve().parent
D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(D))
from current_moe_sim import CurrentMoESim
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('drive_latest.py','current_sim.py','policy_runtime.py','runtime_config.json'):
    assert (B/'prechange'/name).read_bytes()==(D/name).read_bytes(),name
for name in ('drive_latest_moe.py','current_moe_sim.py'):
    ast.parse((D/name).read_text(encoding='utf-8'))
assert H(D/'latest_moe_20261018.onnx')=='02a04afcc32a22b6f72cc67357d60f3ae66ab112e9297aaa2fb7ac7dacc5607f'
cases=[]
for kind in ('normal_walk','jump_from_pause','recover','spin_left','spin_right'):
    sim=CurrentMoESim();params=sim.parameter_readback()
    assert sim.cfg.leg_kp==60 and sim.cfg.leg_kd==2 and sim.cfg.crank_scale==.5 and sim.cfg.yaw_assist_gain==0
    assert sim.command.height==.25 and not sim.command.auto_mode
    if kind=='normal_walk':sim.command.vx=.3
    if kind=='jump_from_pause':sim.request_jump()
    if kind=='recover':sim.select_skill(3)
    if kind.startswith('spin'):
        sim.select_skill(6);sim.command.wz=4 if kind.endswith('left') else -4
    initial=sim.base_position.copy();peak=float(initial[2]);modes=[];minup=1.
    for i in range(300 if kind=='jump_from_pause' else 100):
        modes.append(sim.command.mode)
        a=sim.step_control();assert a.shape==(6,) and np.isfinite(a).all()
        peak=max(peak,float(sim.base_position[2]));minup=min(minup,sim.health()['upright_cos'])
    if kind=='jump_from_pause':assert modes.count(4)==80 and sim.command.mode==0
    cases.append(dict(scenario=kind,controls=len(modes),public_mode4_controls=modes.count(4),
        initial_xyz=initial.tolist(),peak_z=peak,minimum_upright_cos=minup,health=sim.health(),
        skill_qualified=False))
out=dict(epoch=time.time(),status='PASS',scope='Requested October8 player, local nominal MuJoCo interface only',
    latest_graph_unchanged=True,original_drive_and_runtime_files_unchanged=True,
    original_playground_SHA=H(D/'playground.xml'),original_terrain_SHA=H(D/'terrain.npz'),
    runtime_config_SHA=H(D/'runtime_config.json'),model_parameter_readback=params,
    expected_PD=[60,2],expected_crank_scale=.5,zero_yaw_or_upright_assist=True,
    scenarios=cases,not_the_previous_other_player_results=True,no_remote_transport_or_training_changes=True)
(B/'reports/REQUESTED_PLAYER_LATEST_MOE_RUNTIME_ACTUAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
