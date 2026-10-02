import json,os,subprocess
from pathlib import Path
stage=Path(__file__).resolve().parent
manifest=next((stage/'run'/'logs').glob('*/run_manifest.json'))
e=json.loads(manifest.read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in e.items() if k.startswith('RM_') and v is not None})
env.update(RM_MOD4_USD=str(stage/'asset'/'robot_wheel_convex24.usd'),RM_DR_OFF='1',RM_CMD_VX_MIN='0',RM_CMD_VX_MAX='0',RM_CMD_WZ_MIN='0',RM_CMD_WZ_MAX='0',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
with (stage/'run'/'balance_sweep.log').open('w') as f:raise SystemExit(subprocess.run(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(stage/'balance_sweep.py'),'--headless'],env=env,stdout=f,stderr=subprocess.STDOUT).returncode)
