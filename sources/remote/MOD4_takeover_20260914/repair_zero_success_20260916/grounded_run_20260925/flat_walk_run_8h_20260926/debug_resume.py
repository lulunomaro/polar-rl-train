from pathlib import Path
import json,os,subprocess
stage=Path(__file__).resolve().parent
ck=sorted((stage.parent/'fudan_plane_v7/run').glob('logs/*/model_*.pt'))[-1]
src=json.loads((ck.parent/'run_manifest.json').read_text())['env']
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
env.update({k:str(v) for k,v in src.items() if k.startswith('RM_') and v is not None})
env.update(RM_MOD4_MAP='fudan_plane',RM_MOD4_TERRAIN='flat',
 RM_MOD4_USD=str(stage/'asset/robot_wheel_convex24.usd'),
 RM_DR_OFF='1',RM_GAS_FORCE_DR='1',RM_GAS_FORCE_FRAME='full_stroke',
 RM_GAS_FORCE_NOMINAL_N='500',RM_GAS_FORCE_MIN_N='500',
 RM_GAS_FORCE_MAX_N='500',RM_CMD_VX_MIN='0.05',RM_CMD_VX_MAX='0.55',
 RM_CMD_WZ_MIN='0',RM_CMD_WZ_MAX='0',RM_HEIGHT_MIN='0.30',
 RM_HEIGHT_MAX='0.30',RM_LEG_ACTION_SCALE='0.5',
 RM_CRANK_ACTION_SCALE='0.75',RM_W_RUN_POSE='0',
 RM_W_FLAT_ORIENT='-80',RM_W_RUN_HEIGHT_DEFICIT='-30',
 RM_W_STAND_QUIET='8',RM_W_STAND_MOTION='-2',
 RM_WORKSPACE_ROOT='/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source',
 RM_SOLVER_POS='16',RM_SOLVER_VEL='4',OMNI_KIT_ACCEPT_EULA='YES',
 PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0')
cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
 str(stage/'source/mod4/train_mod4_ppo.py'),
 '--headless','--num_envs','64','--steps_per_env','48',
 '--additional_iterations','1','--save_interval','1',
 '--init_checkpoint',str(ck),'--log_root',str(stage/'debug_logs')]
print('launch',cmd,flush=True)
p=subprocess.run(cmd,env=env)
print('returncode',p.returncode,flush=True)
