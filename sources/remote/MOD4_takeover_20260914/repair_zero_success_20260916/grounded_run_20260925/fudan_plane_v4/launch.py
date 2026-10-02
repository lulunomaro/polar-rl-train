from pathlib import Path
import hashlib, json, os, re, subprocess, sys, time
stage=Path(__file__).resolve().parent
isaac_python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
parent=stage.parent
code=stage/'source'/'mod4'
prior=next((parent/'train_gas500_mild_v1'/'logs').glob('*/model_10.pt'))
source=json.loads((prior.parent/'run_manifest.json').read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in source.items() if k.startswith('RM_') and v is not None})
changes={
 'RM_MOD4_MAP':'fudan_plane','RM_MOD4_TERRAIN':'flat',
 'RM_MOD4_USD':str(stage/'asset'/'robot_wheel_convex24.usd'),
 'RM_DR_OFF':'1','RM_GAS_FORCE_DR':'1','RM_GAS_FORCE_FRAME':'full_stroke',
 'RM_GAS_FORCE_MIN_N':'300','RM_GAS_FORCE_MAX_N':'700','RM_GAS_FORCE_NOMINAL_N':'500',
 'RM_HEIGHT_MIN':'0.30','RM_HEIGHT_MAX':'0.30',
 'RM_CMD_VX_MIN':'0.0','RM_CMD_VX_MAX':'0.0','RM_CMD_WZ_MIN':'0.0','RM_CMD_WZ_MAX':'0.0',
 'RM_W_RUN_POSE':'0','RM_LEG_ACTION_SCALE':'0','RM_CRANK_ACTION_SCALE':'0',
 'RM_W_STAND_QUIET':'6','RM_W_STAND_MOTION':'-1','RM_RUN_REF_HIP_RAD':'0.45','RM_RUN_REF_CRANK_RAD':'-0.10',
 'RM_W_RUN_HEIGHT_DEFICIT':'-8','RM_INIT_STD':'0.05',
 'RM_WORKSPACE_ROOT':'/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source'
}
env.update(changes)
env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
sys.path.insert(0,str(code))
from repair_contracts import require_explicit_training_env
require_explicit_training_env(env)
out=stage/'run'
out.mkdir(exist_ok=True)
status=out/'status.json'
record={
 'status':'SMOKE','source_checkpoint':None,'baseline_env_manifest':str(prior.parent/'run_manifest.json'),
 'checkpoint_sha256':None,
 'terrain_source':'Fudan plane default, yly-true/fudan_rl_wheel_leg@8204e853',
 'terrain_geometry':'static plane; MOD4 contact material retained',
 'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [code/'mod4_task.py',code/'skills_isaac.py',code/'repair_contracts.py']},
 'changes':{k:{'old':source.get(k),'new':v} for k,v in changes.items()},
 'num_envs':12000,'steps_per_env':48,'iterations':20,'seed':202609257
}
def save():
 status.write_text(json.dumps(record,indent=2)+'\n')
save()
smoke=[isaac_python,str(code/'train_mod4_ppo.py'),'--headless','--num_envs','64','--dry_run','50','--seed','202609257','--report',str(out/'smoke_report.json')]
with (out/'smoke.log').open('w') as f:
 result=subprocess.run(smoke,env=env,stdout=f,stderr=subprocess.STDOUT)
record['smoke_returncode']=result.returncode
if result.returncode or not (out/'smoke_report.json').exists():
 record['status']='SMOKE_FAILED';save();raise SystemExit(2)
record['status']='TRAINING';save()
cmd=[isaac_python,str(code/'train_mod4_ppo.py'),'--headless','--num_envs','12000',
 '--additional_iterations','20','--save_interval','5','--steps_per_env','48',
 '--learning_rate','0.00004','--run_name','fudan_plane_stand_wheels_only_v4',
 '--seed','202609257','--log_root',str(out/'logs'),
 '--report',str(out/'train_report.json')]
with (out/'train.log').open('x') as f:
 result=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
record['train_returncode']=result.returncode
text=(out/'train.log').read_text(errors='replace')
matches=re.findall(r'Learning iteration\s+(\d+)/(\d+)',text)
record['last_logged_iteration']=int(matches[-1][0]) if matches else None
models=list((out/'logs').glob('*/model_*.pt'))
if models:
 latest=max(models,key=lambda p:p.stat().st_mtime_ns)
 record['latest_checkpoint']=str(latest)
 record['latest_sha256']=hashlib.sha256(latest.read_bytes()).hexdigest()
record['status']='FINISHED_UNEVALUATED' if result.returncode==0 and (out/'train_report.json').exists() else 'STOPPED_OR_FAILED'
save()
raise SystemExit(0 if record['status']=='FINISHED_UNEVALUATED' else 3)
