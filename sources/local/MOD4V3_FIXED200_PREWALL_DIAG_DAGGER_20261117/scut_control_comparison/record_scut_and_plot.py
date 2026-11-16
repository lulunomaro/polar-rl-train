"""Read frozen SCUT model/config, record primary sources, plot actual mode trials."""
from pathlib import Path
import sys,json,hashlib,yaml,torch,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;X=T.parent;R=X.parents[2];W=R.parent;REF=W/'refs/wheeled-legged_RL-main';B=REF/'pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21'
sys.path.insert(0,str(X));from common import guard,put,sha

def val(n):
 if isinstance(n,yaml.ScalarNode):return n.value
 if isinstance(n,yaml.SequenceNode):return [val(x)for x in n.value]
 return {val(k):val(v)for k,v in n.value}
def main():
 guard();env=val(yaml.compose((B/'params/env.yaml').read_text(encoding='utf-8')));agent=yaml.safe_load((B/'params/agent.yaml').read_text(encoding='utf-8'));ck=torch.load(B/'model_1000.pt',map_location='cpu',weights_only=False);sd=ck['model_state_dict'];shape={k:list(v.shape)for k,v in sd.items()if 'actor'in k}
 src=T/'scut_frozen_parameters';src.mkdir(exist_ok=False)
 for name in ['env.yaml','agent.yaml']:shutil.copy2(B/'params'/name,src/name)
 paths=[B/'model_1000.pt',B/'params/env.yaml',B/'params/agent.yaml',REF/'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py']
 d=dict(checkpoint=str(B/'model_1000.pt'),checkpoint_sha256=sha(B/'model_1000.pt'),actor_weight_shapes=shape,agent=agent,saved_env_selected=dict(observation_space=env['observation_space'],scene_num_envs=env['scene']['num_envs'],stand_still_deadzone_enabled=env['stand_still_deadzone_enabled'],stand_still_deadzone_threshold=env['stand_still_deadzone_threshold'],command_resampling=env['commands']['resampling_time_range'],standing_fraction=env['commands']['rel_standing_envs'],airborne_enabled=env['airborne_state_machine_cfg']['enabled'],jump_enabled=env['jump_takeoff_state_machine_cfg']['enabled'],stair_enabled=env['stair_state_machine_cfg']['enabled'],mode_layout=env['jump_takeoff_extra_obs_layout'],obs_history_len=env['obs_history_len']),primary_sources=[dict(path=str(p),sha256=sha(p))for p in paths],official_sources=['https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/main/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/agent.yaml','https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/main/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/env.yaml','https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/main/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py'],interpretation_limits='Saved-run parameters/checkpoint primary; latest public env code is separately identified, not silently relabelled as exact frozen training source. No SCUT same-plant low200mm graduation claimed.',PPO_updates=0,optimizer_updates=0)
 put(T/'SCUT_FROZEN_MODEL_AUDIT.json',d)
 fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True)
 for j,tag in enumerate(['original010m','repair10m']):
  for mode,color in [('normal','#248269'),('stair','#b64248')]:
   a=np.load(T/f'mode_contrast/{tag}/{mode}/start_+000mm/rollout.npz');tr=a['trace'];axs[j,0].plot(tr[:,0],tr[:,1],color=color,label=mode);axs[j,1].plot(tr[:,0],tr[:,3],color=color,label=mode)
  axs[j,0].set_title(tag+' - base x');axs[j,1].set_title(tag+' - base height');axs[j,0].set_ylabel('Base x (m)');axs[j,1].set_ylabel('Base origin z (m)')
  axs[j,1].axhline(.4091,color='#777',ls=':',lw=1)
  for ax in axs[j]:ax.axvline(1.,color='#777',ls='--',lw=1);ax.grid(alpha=.25);ax.legend();ax.set_xlim(0,3);ax.set_xlabel('Simulation time (s)')
 fig.suptitle('Paired mode input intervention: same weights, pose, commands and physics; 0 updates');fig.tight_layout(rect=(0,0,1,.95));fig.savefig(T/'MODE_CONTRAST.png',dpi=150);plt.close(fig)
 print('SCUT_ACTOR',shape,'saved stairFSM',d['saved_env_selected']['stair_enabled'],'PPO_updates0');guard()
if __name__=='__main__':main()
