from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 n,w=io.connect_both()
 try:
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT);R=D/'reports';B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());reports={};indices=[]
for p in sorted(R.glob('*.json')):
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 if p.name not in ('SOURCE_FREEZE.json','SOURCE_SELECTED.json','ENTRY_NATIVE_ACTUAL_REVIEW.json','CURB_FOUR_CASE_TEMPLATES.json') and p.stat().st_size<3000000:reports[p.name]=j(p)
state=reports.get('E1_STATE.json');locs=[]
if state:
 locs.append(state['owner'])
 if state.get('child'):locs.append(state['child'])
if reports.get('E1_GUARDIAN_STARTED.json'):locs.append(reports['E1_GUARDIAN_STARTED.json'])
actual=[]
for loc in locs:
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  f=(p/'stat').read_text().split(') ',1)[1].split();a=dict(pid=loc['pid'],state=f[0],start_ticks=int(f[19]),argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\0') if x],cwd=str((p/'cwd').resolve()))
 actual.append(dict(locator=loc,actual=a))
b=j(B);run_reports=[]
for p in D.glob('*_logs/*/latest_complete.json'):
 row=j(p);run=p.parent;manifest=j(run/'run_manifest.json');snap=run/'src_snapshot'
 run_reports.append(dict(run=str(run),own_latest_complete=row,manifest_pid=manifest.get('pid'),init_checkpoint_sha256=manifest['init_checkpoint_sha256'],actual_src_snapshot_file_count=sum(q.is_file() for q in snap.rglob('*')),actual_source_freeze_count=len(manifest['source_map']),health=j(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None,startup_files=[q.name for q in run.glob('*STARTUP_VERIFIED.json')]))
output={}
for p in D.glob('ENTRY_ORIGIN_BOUND_SDK10*.json'):output[p.name]=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
print(json.dumps(dict(epoch=time.time(),reports=reports,report_indices=indices,actual_processes=actual,own_runs=run_reports,SDK_output_indices=output,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=b['authorized_training_seconds'],remaining_seconds=b['remaining_training_seconds'],active_segment=b['active_segment'],controller_log_tail=(D/'controller.log').read_text(errors='replace')[-5000:],formal_final_pending='e1_CURB20_entry_repair_observation_PASSED.json' not in reports,no_mutation=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(io.B)))
  p=save('ENTRY_SEED_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),phase=v['reports'].get('E1_STATE.json'),attention=v['reports'].get('E1_ATTENTION.json'),SDK_passed='ENTRY_ORIGIN_BOUND_SDK10_PASSED.json' in v['reports'],small_passed='entry_discard128_PASSED.json' in v['reports'],big_passed='entry_discard20k_PASSED.json' in v['reports'],fresh_passed='ENTRY_FRESH_SAME_SCOPE_PASSED.json' in v['reports'],formal_final_pending=v['formal_final_pending'],actual_processes=v['actual_processes'],active_segment=v['active_segment'])))
 finally:io.cleanup(n,w)

if __name__=='__main__':main()
