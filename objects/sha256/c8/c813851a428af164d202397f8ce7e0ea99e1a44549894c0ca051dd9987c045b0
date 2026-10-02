from pathlib import Path
import json,os,subprocess
st=Path(__file__).resolve().parent
ck=sorted((st.parent/'fudan_plane_v7/run').glob('logs/*/model_*.pt'))[-1]
src=json.loads((ck.parent/'run_manifest.json').read_text())['env']
base={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
base.update({k:str(v) for k,v in src.items() if k.startswith('RM_') and v is not None})
base.update(RM_MOD4_USD=str(st/'asset/robot_wheel_convex24.usd'),
 OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
variants=[
 ('base',{}),
 ('gas500',{'RM_GAS_FORCE_FRAME':'reference','RM_GAS_FORCE_MIN_N':'500','RM_GAS_FORCE_MAX_N':'500'}),
 ('vx',{'RM_CMD_VX_MIN':'0.05','RM_CMD_VX_MAX':'0.55'}),
 ('leg',{'RM_LEG_ACTION_SCALE':'0.5','RM_CRANK_ACTION_SCALE':'0.75'}),
 ('all',{'RM_GAS_FORCE_FRAME':'reference','RM_GAS_FORCE_MIN_N':'500','RM_GAS_FORCE_MAX_N':'500',
         'RM_CMD_VX_MIN':'0.05','RM_CMD_VX_MAX':'0.55',
         'RM_LEG_ACTION_SCALE':'0.5','RM_CRANK_ACTION_SCALE':'0.75'})]
for name,delta in variants:
 env=base.copy();env.update(delta)
 log=st/f'debug_ab_{name}.log'
 cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
      str(st/'source/mod4/train_mod4_ppo.py'),'--headless',
      '--num_envs','64','--dry_run','1']
 print('START',name,flush=True)
 with log.open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 s=log.read_text(errors='replace')
 print('DONE',name,p.returncode,'dry_run',('[mod4-isaac] dry run:' in s),
       'last',s[-200:],flush=True)
