"""CPU-only direction/contact review of the already completed matched132/139 raw."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011'))
from diagnose_curb133_prefix_actual import inspect
H=lambda b:hashlib.sha256(b).hexdigest()

def main():
 collection=sorted(R.glob('CURB139_COLLECTED_[0-9]*.json'))[-1];c=json.loads(collection.read_bytes());assert not c['pending'] and len(c['cases'])==4
 jid=next(k for k,x in c['cases'].items() if 'full_route_raw' in x['probe'])
 candidate=inspect(R/'cases'/jid,c['cases'][jid]['probe'])
 base=W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/cases/clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat'
 source=inspect(base,json.loads((base/'probe.json').read_bytes()))
 prior=json.loads((W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json').read_bytes())['candidate']
 assert sum(x['complete'] for x in source['rows'])==26 and sum(x['complete'] for x in candidate['rows'])==23 and sum(x['complete'] for x in prior['rows'])==22
 failed=[x for x in candidate['rows'] if not x['complete']]
 pairs={str(x['env']):dict(source132=next(y for y in source['rows'] if y['env']==x['env']),prior133=next(y for y in prior['rows'] if y['env']==x['env']),candidate139=x) for x in failed}
 result=dict(epoch=time.time(),trial_id='CURB139-COMPLETE-MATCHED-PREFIX-DIAGNOSIS-01',collection=str(collection),collection_SHA=H(collection.read_bytes()),source132=source,prior133_raw_index=dict(path=prior['raw_path'],bytes=prior['bytes'],sha256=prior['sha256']),candidate139=candidate,incomplete_pairs=pairs,
  source132_ascending_complete=26,prior133_ascending_complete=22,candidate139_ascending_complete=23,ascending_count=27,
  incomplete_envs=[x['env'] for x in failed],all_incomplete_original_orientation=all(x['orientation']==1 for x in failed),
  no_shorter_approach_or_longer_window_or_reset_teleport_credit=True,no_original_result_or_false_or_cost_relabel=True,
  interpretation='Entry-reset short training still does not meet complete upward curb passage. The matched frozen test is one environment better than prior133 but remains three below source132. This is not a causal entry-reset ablation; command/reset coverage or optimization causes require a separate diagnosis.',
  no_GPU_PPO_queue_or_budget_write=True)
 p=save('ENTRY139_COMPLETE_PREFIX_ACTUAL_DIAGNOSIS.json',result)
 print(json.dumps(dict(report=str(p),source132=26,prior133=22,candidate139=23,incomplete_envs=result['incomplete_envs'],all_incomplete_original_orientation=result['all_incomplete_original_orientation'],pairs=pairs),ensure_ascii=True))

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY139_COMPLETE_PREFIX_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True,no_GPU_replay=True));raise
