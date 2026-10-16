"""Pure CPU accounting/ready rejection tests, and complete source freeze."""
from pathlib import Path
import ast,hashlib,json,time,shutil
D=Path(__file__).resolve().parent;Q=D/'training_payload';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not (R/'COMPLETE_TWO_CONTINUATION_ACCOUNTING_GRANT_NEGATIVES_CPU_ACTUAL.json').exists();script=D/'two_continuation_cohort_finite_owner_node_v1.py';tree=ast.parse(script.read_text('utf8'));ns=dict(hashlib=hashlib,json=json);exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('valid_ready','terminal','charge_values')],type_ignores=[]),'actual_pure_cohort_functions','exec'),ns);cfg=dict(source_SHA='a'*64,manifest_SHA='b'*64);v=dict(passed=True,source_SHA=cfg['source_SHA'],controls=144,callbacks=576);row=dict(phase='ready',native_GPU_waited_EXIT0=True,native_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True),manifest_SHA=cfg['manifest_SHA']);assert ns['valid_ready'](row,cfg);rejected=0
 for key,bad in [('phase','production'),('native_GPU_waited_EXIT0',False),('manifest_SHA','c'*64),('original_error',True)]:
  x=dict(row);x[key]=bad;assert not ns['valid_ready'](x,cfg);rejected+=1
 for key,bad in [('passed',False),('source_SHA','c'*64),('controls',143),('callbacks',575)]:
  badv=dict(v);badv[key]=bad;x=dict(row,native_CPU=dict(value=badv,SHA=hashlib.sha256(json.dumps(badv,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True));assert not ns['valid_ready'](x,cfg);rejected+=1
 x=dict(row,native_CPU=dict(row['native_CPU'],SHA='c'*64));assert not ns['valid_ready'](x,cfg);rejected+=1
 c=dict(charged_training_seconds=1000.,remaining_training_seconds=1187000.);active=dict(experts={},charged_expert_seconds=0.);go=dict(curb=dict(learning_started_epoch=10.),e2=dict(learning_started_epoch=20.));rows=dict(curb=dict(returncode=None),e2=dict(returncode=None));c,active=ns['charge_values'](c,active,go,rows,30.);assert active['charged_expert_seconds']==30.;rows['curb']=dict(returncode=0,actual_exit=dict(epoch=35.));c,active=ns['charge_values'](c,active,go,rows,40.);assert active['charged_expert_seconds']==45.;rows['e2']=dict(returncode=0,actual_exit=dict(epoch=44.),owner_received_terminal_epoch=45.);c,active=ns['charge_values'](c,active,go,rows,50.);assert active['charged_expert_seconds']==50.;c,active=ns['charge_values'](c,active,go,rows,100.);assert active['charged_expert_seconds']==50. and c['charged_training_seconds']==1050.;assert not ns['terminal'](dict(returncode=0)) and ns['terminal'](dict(returncode=1,terminal_all_own_children_waited=True));frozen=[]
 for key in ('curb','e2'):
  b=Q/key;shutil.copy2(script,b/'cohort_finite.py');p=b/'production_worker.py';original=p.read_text('utf8');(b/'production_worker_PRE_GRANT_GUARD_ORIGINAL.py.txt').write_text(original,encoding='utf8');needle="go=json.loads((B/'GO_PRODUCTION_ACTUAL.json').read_bytes());deadline=go['save_deadline']" if key=='curb' else "go=json.loads((j/('GO_'+phase.upper()+'.json')).read_bytes());deadline=go['save_deadline']";assert needle in original;variable='task';changed=original.replace(needle,needle+";assert go['source_SHA']==task['source_SHA'] and go['max_parent_seconds']==2700 and go['exit_headroom_seconds']==300");ast.parse(changed);p.write_text(changed,encoding='utf8');m=json.loads((b/'CONTINUATION_MANIFEST.json').read_bytes());m['files']=[]
  for p in sorted(b.rglob('*')):
   if p.is_file() and p.name not in ('CONTINUATION_MANIFEST.json','CONTINUATION_COMPLETE_MANIFEST_V2.json'):
    if p.suffix=='.py':ast.parse(p.read_text('utf8'))
    m['files'].append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  out=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';out.write_text(json.dumps(m,indent=2),encoding='utf8');frozen.append(dict(key=key,source_SHA=m['source_SHA'],source_Adamstep=m['source_Adamstep'],GPU_UUID=m['GPU_UUID'],manifest_SHA=H(out),files=len(m['files'])))
 report=dict(epoch=time.time(),passed_CPU_only=True,ready_rejected_negative_cases=rejected,actual_own_children_terminal_required=True,distinct_interval_sum_and_no_repeated_completed_charge_passed=True,remote_interval_includes_original_owner_received_actual_child_terminal_handoff_not_guessed_GPU_exit=True,original_canonical_not_read_or_written_in_fixture=True,no_CUDA_no_optimizer_no_target_deploy=True,frozen=frozen);(R/'COMPLETE_TWO_CONTINUATION_ACCOUNTING_GRANT_NEGATIVES_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback
  (R/('COHORT_ACCOUNTING_GRANT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True),indent=2),encoding='utf8');raise
