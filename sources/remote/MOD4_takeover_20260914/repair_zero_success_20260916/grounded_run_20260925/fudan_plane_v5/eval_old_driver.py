import json,os,subprocess
from pathlib import Path
stage=Path(__file__).resolve().parent
manifest=next((stage/'run'/'logs').glob('*/run_manifest.json'))
e=json.loads(manifest.read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in e.items() if k.startswith('RM_') and v is not None})
env.update(RM_MOD4_USD=str(stage/'asset'/'robot_wheel_convex24.usd'),RM_LEG_ACTION_SCALE='0.5',RM_CRANK_ACTION_SCALE='0.75',RM_CMD_VX_MIN='0',RM_CMD_VX_MAX='0',RM_CMD_WZ_MIN='0',RM_CMD_WZ_MAX='0',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
ck='/home/egde/rl_candidates/MOD4_takeover_20260914/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/model_2775.pt'
cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(stage/'source'/'mod4'/'play_mod4.py'),'--headless','--checkpoint',ck,'--num_envs','64','--steps','300']
with (stage/'run'/'eval_old.log').open('w') as f:raise SystemExit(subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT).returncode)
