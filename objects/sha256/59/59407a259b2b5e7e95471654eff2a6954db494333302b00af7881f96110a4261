from pathlib import Path
import hashlib, json, os, subprocess, sys, re
root=Path('/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/grounded_run_20260925')
code=root/'source/mod4'
prior=next((root/'train_d08/logs').glob('*/model_10.pt'))
manifest=prior.parent/'run_manifest.json'
out=root/'train_pose_mid_v1'
out.mkdir(exist_ok=True)
source=json.loads(manifest.read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in source.items() if k.startswith('RM_') and v is not None})
changes={'RM_W_RUN_POSE':'-20','RM_RUN_REF_HIP_RAD':'0.45','RM_RUN_REF_CRANK_RAD':'-0.10','RM_W_RUN_TILT':'0','RM_W_RUN_HEIGHT_DEFICIT':'0','RM_DR_OFF':'1','RM_INIT_STD':'0.05','RM_WORKSPACE_ROOT':'/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source'}
env.update(changes)
env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
record={'status':'STARTING','source_checkpoint':str(prior),'source_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'source_task_sha256':hashlib.sha256((code/'mod4_task.py').read_bytes()).hexdigest(),'changes':{k:{'old':source.get(k),'new':v} for k,v in changes.items()},'num_envs':12000,'steps_per_env':48,'iterations':20,'seed':202609253}
status=out/'stage_status.json'
if status.exists(): raise FileExistsError(status)
status.write_text(json.dumps(record,indent=2)+'\n')
cmd=[sys.executable,str(code/'train_mod4_ppo.py'),'--headless','--num_envs','12000','--additional_iterations','20','--save_interval','5','--steps_per_env','48','--learning_rate','0.00003','--run_name','flat_run_pose_mid_v1','--seed','202609253','--log_root',str(out/'logs'),'--init_checkpoint',str(prior),'--report',str(out/'train_report.json')]
with (out/'train.log').open('x') as log: result=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
record['returncode']=result.returncode
matches=re.findall(r'Learning iteration\s+(\d+)/(\d+)',(out/'train.log').read_text(errors='replace'))
record['last_logged_iteration']=int(matches[-1][0]) if matches else None
models=list((out/'logs').glob('*/model_*.pt'))
if models:
 latest=max(models,key=lambda p:p.stat().st_mtime_ns)
 record['latest_checkpoint']=str(latest)
 record['latest_sha256']=hashlib.sha256(latest.read_bytes()).hexdigest()
record['status']='FINISHED_UNEVALUATED' if result.returncode==0 and (out/'train_report.json').exists() and record['last_logged_iteration']==19 else 'STOPPED_OR_FAILED'
status.write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(0 if record['status']=='FINISHED_UNEVALUATED' else 3)
