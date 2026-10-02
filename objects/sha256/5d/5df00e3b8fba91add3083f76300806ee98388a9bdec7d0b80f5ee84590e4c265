from pathlib import Path
import json,os,subprocess
stage=Path(__file__).parent
prior=next((stage.parent/'train_gas500_mild_v1'/'logs').glob('*/run_manifest.json'))
src=json.loads(prior.read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in src.items() if k.startswith('RM_') and v is not None})
env.update({k:v['new'] for k,v in json.loads((stage/'run'/'status.json').read_text())['changes'].items()})
env['RM_MOD4_USD']=str(stage/'asset'/'robot_wheel_convex24.usd')
env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
with (stage/'run'/'probe.log').open('w') as f:
 raise SystemExit(subprocess.run(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(stage/'probe_plane.py'),'--headless'],env=env,stdout=f,stderr=subprocess.STDOUT).returncode)
