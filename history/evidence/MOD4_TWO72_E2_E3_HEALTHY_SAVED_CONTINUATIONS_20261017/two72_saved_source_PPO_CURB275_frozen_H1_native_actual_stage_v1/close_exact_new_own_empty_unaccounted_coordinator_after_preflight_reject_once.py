from pathlib import Path
import sys,json,time,os,traceback
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N));import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 prior=json.loads((R/'REJECTED_DEPLOY_ACTUAL_EMPTY_OWNER_AND_TARGET_SELF_ARG_MATCH_READONLY.json').read_bytes());id=prior['source']['actual_process'];assert id['pid']==593869 and id['creation']==1792169649.03 and not id['children'];c=None
 try:
  c=a.t.connect();v=a.code(c,a.t.PY,"from pathlib import Path;import sys,json,time,psutil,signal;B=Path(sys.argv[1]);expected=json.loads(sys.argv[2]);p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'] and p.cmdline()==expected['argv'] and not p.children(recursive=True);current=json.loads((B/'OWNER_CURRENT.json').read_bytes());assert current['rows']=={'e2':{},'recovery':{}} and current['go']=={} and current['stop'] and not current['original_canonical_active'] and not current['original_two_fcntl_held'];C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=C.read_bytes();cv=json.loads(before);assert (cv['active_segment'] or {}).get('owner_parent_pid')!=p.pid;old=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),children=[]);p.send_signal(signal.SIGTERM)\ntry:p.wait(timeout=20)\nexcept psutil.TimeoutExpired:raise RuntimeError('Exact own empty coordinator did not exit; no further signal or retry')\nassert not psutil.pid_exists(old['pid']) or psutil.Process(old['pid']).status()==psutil.STATUS_ZOMBIE;after=json.loads(C.read_bytes());assert (after['active_segment'] or {}).get('owner_parent_pid')!=old['pid'];print(json.dumps(dict(epoch=time.time(),exact_own_new_empty_identity=old,actual_signal='SIGTERM',no_GPU_children_no_grant_no_original_locks_no_canonical_write=True,no_reuse_of_old172447_permission_or_other_job_signal=True,old_v1_failure_retained_not_natural_EXIT0=True,actual_process_out_or_reaped_zombie=True,current_original_account_owner=(after['active_segment'] or {}).get('owner_parent_pid'))))",a.SOURCE,json.dumps(id));put('EXACT_NEW_EMPTY_COORDINATOR593869_ACTUAL_TERMINATED_NO_TRAINING_BUDGET_MUTATION.json',v);print(json.dumps(v),flush=True)
 finally:a.t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('EXACT_EMPTY_COORDINATOR_CLOSE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_further_signal_or_retry=True));raise
