"""Future text-only aggregation; never chooses cases or opens a model."""
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from native87R5_frozen_acceptance_contract_v1 import SEEDS,require,validate_eval_binding
def read(path):return json.loads(Path(path).read_bytes())
def summarize(q,cases,guard_exit=None):
 validate_eval_binding(q);require(set(cases)==set(SEEDS),'all three fixed attempts required; missing/errors cannot be hidden')
 rows=[];canonicals=set()
 for seed in SEEDS:
  c=cases[seed];status=c['status'];authority=c['authority']
  require(c['function_return']['passed'] is True and not c['close_or_original_errors'],'actual case/error/close incomplete')
  require(status['seed']==seed and status['source_identity']['model']['SHA']==q['source_model']['SHA'],'seed or shared selected source differs')
  require(status['policy_parameters_and_saved_normalizers_literal_unchanged'] is True,'frozen Pi/norm changed')
  require(status['termination'] in ('actual_original_done','fixed5s_cap_censored_if_original_done_absent'),'original case error/incomplete')
  require(0<status['controls']<=500 and status['physics_callbacks']==4*status['controls']<=2000,'original finite complete callbacks')
  require(authority['passed'] is True and authority['no_account_write'] and authority['no_canonical_copy'],'readonly authority exit missing')
  require(authority['canonical_unchanged'] is (q['execution_backend']=='target72'),'authority backend differs')
  canonicals.add(authority['canonical_SHA']);last=status['last_original_state']
  rows.append(dict(seed=seed,controls=status['controls'],physics_callbacks=status['physics_callbacks'],termination=status['termination'],
   original_goal_success=bool(last['success']),original_takeoff_count=last['takeoff_count'],original_landing_count=last['landing_count'],original_recovery_count=last['recovery_count'],
   original_stable_callback_ticks=last['stable_callback_ticks'],exact_original_success_caches=last['actual_original_success_caches'],termination_terms=status['last_termination_terms']))
 require(len(canonicals)==1,'canonical changed between fixed fresh cases')
 if q['execution_backend']=='source210':
  require(guard_exit is not None and guard_exit['passed'] is True and guard_exit['canonical_bytes_unchanged'] is True and guard_exit['root_waited_release_received'] is True and guard_exit['no_account_write_or_copy'] is True,'source210 requires actual parent-waited72 guard EXIT, not its ready template')
  require(guard_exit['canonical_SHA'] in canonicals,'source210 guard entry/exit source differs')
 return dict(passed=True,scope='fixed_three_fresh_N1_native87R5_frozen_mean_attempts',source=q['source_model'],selected_key=q['selected_key'],selection_scope=q['selection_scope'],
  seeds=list(SEEDS),cases=rows,original_goal_success_count=sum(r['original_goal_success'] for r in rows),case_count=3,
  no_seed_retry_or_best_case_selection=True,no_learning=True,not_exact_training_trajectory_replay=True,not_automatic_skill_graduation_or_paper_speed_reproduction=True,canonical_bytes_unchanged_across_cases=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--binding',required=True);p.add_argument('--guard-exit');p.add_argument('--guard-exit-SHA');args=p.parse_args();q=read(args.binding);root=Path(q['eval_root']);cases={}
 for seed in SEEDS:
  folder=root/('seed_'+str(seed));errors=[str(p) for p in folder.rglob('*.json') if 'ERROR' in p.name]
  cases[seed]=dict(status=read(folder/'episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json'),authority=read(folder/'READONLY_AUTHORITY_CASE_EXIT.json'),function_return=read(folder/'FROZEN_SINGLE_CASE_FUNCTION_RETURNED_ACTUAL.json'),close_or_original_errors=errors)
 guard=None
 if q['execution_backend']=='source210':
  require(args.guard_exit and args.guard_exit_SHA,'actual72 guard exit immutable SHA required')
  raw=Path(args.guard_exit).read_bytes();require(hashlib.sha256(raw).hexdigest()==args.guard_exit_SHA,'actual72 guard exit SHA differs');guard=json.loads(raw)
 result=summarize(q,cases,guard)
 with (root/'FROZEN_FIXED_THREE_SEED_ORIGINAL_GOAL_RESULTS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,original_goal_success_count=result['original_goal_success_count'],all_three_cases_recorded=True)))
if __name__=='__main__':main()
