'''Read the current native reward factory without starting Isaac/PPO.'''
from pathlib import Path
import sys,json,shlex,textwrap
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import P,connect,execute
code='import os,sys;os.environ["MOD4_SCUT_SOURCE_PATHS"]='+repr(P['source_paths'])+';sys.path[:0]='+repr([P['shared_package'],P['support']])+'\n'+textwrap.dedent('''
import ast,json,importlib.util,math
from pathlib import Path
from copy import deepcopy
root=Path(SUPPORT)/'mod4v3_ppo_v1'
spec=importlib.util.spec_from_file_location('inventory_reward_cfg',root/'scut_flat_rewards.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ns=dict(vars(m));ns.update(Path=Path,json=json,deepcopy=deepcopy,__file__=str(root/'scut_rough_scut_v1_env.py'))
for fn,name in [('scut_flat_forward_square_env.py','configuration_forward_square'),('scut_rough_r2_env.py','configuration_r2'),('scut_rough_scut_v1_env.py','configuration_scut_v1')]:
 tree=ast.parse((root/fn).read_text(encoding='utf-8-sig'));unit=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name],type_ignores=[]);ast.fix_missing_locations(unit);exec(compile(unit,str(root/fn),'exec'),ns)
cfg=ns['configuration_scut_v1']()
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [clean(v) for v in x]
 if isinstance(x,float) and not math.isfinite(x):return str(x)
 if x is None or isinstance(x,(str,bool,int,float)):return x
 return str(x)
print(json.dumps(clean(vars(cfg)),ensure_ascii=False))
''').replace('Path(SUPPORT)','Path('+repr(P['support'])+')')
c=connect()
try:cfg=json.loads(execute(c,shlex.quote(P['python'])+' -B -c '+shlex.quote(code)))
finally:c.close()
startup=json.loads((T/'evidence/training/STARTUP.json').read_text(encoding='utf8'));assert cfg['rewards']==startup['reward_weights']
(T/'evidence/reward_inventory/CONFIG_READBACK.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
keys=['lin_vel_xy_sigma','lin_vel_xy_square_sigma','lin_vel_err_constraint','ang_vel_z_sigma','ang_vel_z_square_sigma','ang_vel_err_constraint','height_tight_sigma','height_square_sigma','height_err_constraint','orientation_y_A','orientation_y_sigma','orientation_y_bias','orientation_y_exp_sigma','orientation_x_A','orientation_x_sigma','orientation_x_bias','orientation_x_exp_sigma','no_fork_distance','no_fork_square_sigma','undesired_contact_force_threshold','stand_still_lin_vel_threshold','stand_still_yaw_rate_threshold','vel_upright_gate_enabled','vel_height_gate_enabled','vel_orientation_x_gate_enabled','vel_orientation_y_gate_enabled']
print(json.dumps({k:cfg.get(k) for k in keys},ensure_ascii=False))
print('AIRBORNE_CFG',json.dumps(cfg['airborne_state_machine_cfg'],ensure_ascii=False))
