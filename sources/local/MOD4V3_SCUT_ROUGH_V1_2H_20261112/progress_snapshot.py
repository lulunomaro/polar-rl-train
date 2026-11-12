from pathlib import Path
import argparse,json,time
p=argparse.ArgumentParser();p.add_argument('--wait',type=float,default=0);p.add_argument('--full',action='store_true');a=p.parse_args()
T=Path(__file__).resolve().parent;E=T/'evidence';M=E/'training_round'
limit=time.monotonic()+min(a.wait,55.)
baseline=len(list(M.glob('model_*m_CHECK.json')))
while time.monotonic()<limit:
 if len(list(M.glob('model_*m_CHECK.json')))>baseline or (M/'MONITOR_COMPLETE.json').exists() or (M/'ERROR.json').exists():break
 time.sleep(min(1.,max(0.,limit-time.monotonic())))
def read(path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except (FileNotFoundError,json.JSONDecodeError):return None
progress=read(E/'LATEST_PROGRESS.json') or {}
pt=sorted(M.glob('model_*m_FULL_PT.json'))
evals=sorted(M.glob('model_*m_EVAL_SUMMARY.json'))
result=dict(elapsed_s=progress.get('training_elapsed_seconds'),iteration=progress.get('iteration'),mean_reward=progress.get('mean_reward'),done_totals=progress.get('done_totals'),latest_checkpoint=read(pt[-1]) if pt else None,checkpoint_count=len(pt),cpu_replays_finished=len(evals),latest_cpu_replay=read(evals[-1]) if evals else None,final=read(M/'FINAL.json'),closed=read(M/'SAFE_CLOSED.json'),complete=(M/'MONITOR_COMPLETE.json').exists(),training_error=read(M/'ERROR.json'))
if not a.full:
 if result['latest_checkpoint']:
  value=result['latest_checkpoint'];result['latest_checkpoint']={k:value.get(k) for k in ('iteration','sha256','full_ppo_rng_present','all_policy_critic_optimizer_tensors_finite')}
 if result['latest_cpu_replay']:
  value=result['latest_cpu_replay'];result['latest_cpu_replay']=dict(checkpoint=value['checkpoint'],physics=value['physics'],six_task_passed=sum(x['passed'] for x in value['rows'] if x['passed'] is not None),resets=sum(x['resets'] for x in value['rows']),rows=[dict(command=x['command'],vx=round(x['vx_mean'],4),wz=round(x['wz_mean'],4),height=round(x['height_mean'],4),passed=x['passed']) for x in value['rows']])
print(json.dumps(result,ensure_ascii=False))
