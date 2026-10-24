from pathlib import Path
import hashlib,json,re,time,traceback,statistics
M=Path(__file__).resolve().parent;R=M/'reports';R.mkdir(exist_ok=True);T=M.parent;N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 proof=json.loads((N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 put('HUMAN_POST67_MIXED_PRECISION_STEP_BENCHMARK_AUTH_ACTUAL.json',dict(epoch=time.time(),human_request='这一轮做完看一下提升有多大吧，step速度能提多少',scope='After actual67 complete save/CPU/original cost/allout, isolated bounded FP32/BF16/FP16 precision performance comparison. Measure collection env-step/s, PPO update time and end-to-end env-step/s; compare finite outputs/gradients/KL without changing current production, physics/commands/goals or using benchmark copies as qualified training source.',previous_replay_repair_request_still_active=True,no_local_agent_inference_or_physics_rollout=True,no_extra_budget_extension_or_reserve_change=True))
 result={}
 for key,rel in [('h1','h1/job0/production_WORKER.log'),('recovery','recovery/job0/production_WORKER.log')]:
  path=N/'current_pair_closed_text'/rel;raw=path.read_bytes();text=raw.decode('utf8',errors='replace');collection=[float(x) for x in re.findall(r'Collection time:\s*([0-9.]+)s',text)];learning=[float(x) for x in re.findall(r'Learning time:\s*([0-9.]+)s',text)]
  assert len(collection)==len(learning)==proof['models'][key]['updates']
  rows=[dict(update=i+1,collection_s=c,learning_s=l,collection_env_steps_s=480000/c,end_to_end_env_steps_s=480000/(c+l),learning_fraction=l/(c+l),upper_bound_gain_if_update_free=(c+l)/c-1,gain_if_update_2x=(c+l)/(c+l/2)-1) for i,(c,l) in enumerate(zip(collection,learning))]
  steady=rows[2:];result[key]=dict(log=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),updates=len(rows),excluded_first_updates=2,units='environment transitions per wall second; 20k envs x24 decisions/update, not per-env policy Hz or physics callbacks',medians={k:statistics.median(r[k] for r in steady) for k in ('collection_s','learning_s','collection_env_steps_s','end_to_end_env_steps_s','learning_fraction','upper_bound_gain_if_update_free','gain_if_update_2x')},rows=rows,rounded_log_times_not_CUDA_profiler=True)
 put('ACTUAL67_FP32_LOG_TIMING_BASELINE_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,source=proof['models'],slots=result,no_precision_benchmark_ran_yet=True,no_new_PT_raw_GPU_or_hostquery=True,no_claim_collection_actor_fraction_measured=True))
 print(json.dumps({k:v['medians'] for k,v in result.items()}))
except BaseException:
 put('FP32_TIMING_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

