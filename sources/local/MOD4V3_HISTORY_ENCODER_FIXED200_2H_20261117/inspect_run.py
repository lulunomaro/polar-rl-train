"""Read-only status, including training speed stages saved in full checkpoints."""
from pathlib import Path
import json,datetime,torch
T=Path(__file__).resolve().parent;E=T/'evidence';W=T/'weights'
def read(f):return json.loads(f.read_text())if f.exists()else{}
def snapshot(f):
 d=torch.load(f,map_location='cpu',weights_only=False);s=d.get('terrain_curriculum_state',{}).get('training_speed_state',{});out=dict(checkpoint=str(f),iteration=d.get('iter'),PPO_updates=d.get('PPO_updates_in_experiment'),optimizer_minibatches=d.get('history_auxiliary',{}).get('actual_optimizer_minibatches'))
 if s:
  population=torch.bincount(s['speed_stage'].long(),minlength=4).tolist();population[0]-=1229
  out['training_speed_course']=dict(limits_m_s=[1.3,1.,.8,.6],stair_population=population,completions_by_stage=s['speed_completed'].tolist(),strict0p6_completions=int(s['strict_success_count']),speed_penalty_sum=float(s['speed_penalty_sum']),source='actual checkpoint counters, not frozen independent score')
 return out
if __name__=='__main__':
 p=read(E/'training/LATEST_PROGRESS.json');r=dict(now=datetime.datetime.now().astimezone().isoformat(),iteration=p.get('iteration'),training_seconds=p.get('training_elapsed_seconds'),losses=p.get('losses'),closed=bool(read(E/'training/SAFE_CLOSED.json')),training_error=read(E/'training/ERROR.json'),midrun_evaluations={f.parent.name:read(f)for f in(E/'checkpoint_evals').glob('*/EVALUATION.json')})
 files=[f for f in W.glob('model_*.pt')if f.name!='model_step000.pt']
 if files:r['latest_full_checkpoint']=snapshot(max(files,key=lambda f:f.stat().st_mtime))
 print(json.dumps(r,ensure_ascii=False,indent=2))
