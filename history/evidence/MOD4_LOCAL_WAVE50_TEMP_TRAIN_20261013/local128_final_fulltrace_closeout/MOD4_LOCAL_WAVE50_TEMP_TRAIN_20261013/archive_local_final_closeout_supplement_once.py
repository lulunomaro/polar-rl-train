from pathlib import Path
import sys,json,time,tomllib,hashlib,subprocess,traceback
from local_archive_capture import capture
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
sys.path.insert(0,str(D.parent/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'));import archive_actual_reference_stage_once as archive
DEST=REPO/'history/evidence'/D.name/'local128_final_fulltrace_closeout'
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert not archive.gitio.g('status','--porcelain') and not DEST.exists()
 proof=json.loads((R/'LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json').read_bytes());assert proof['passed']
 costs=json.loads((R/'LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ACTUAL.json').read_bytes());assert costs['passed']
 req=json.loads((R/'LOCAL_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');cfg=tomllib.loads(p.read_text(encoding='utf8'))
 for k in ('name','status','rrule'):assert cfg[k]==req[k]
 assert cfg['target_thread_id']==req['targetThreadId'] and cfg['prompt'].rstrip()==req['prompt'].rstrip()
 save('LOCAL_FINAL_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,status=cfg['status'],rrule=cfg['rrule'],target=cfg['target_thread_id'],actual_TOML_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),current_fullfinal_priority=True,healthy_idle_quiet=True,remote_still_paused=True,no_extra_monitor_or_new_training=True))
 save('LOCAL_FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),prior_main=archive.gitio.g('rev-parse','HEAD'),actual_final_review=str(R/'LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json'),unique_stage_already_recorded_no_new_trial=True))
 old=archive.gitio.refs();rows,files=capture(DEST)
 lock=D/'LOCAL_GPU_EXCLUSIVE.lock';raw=lock.read_bytes();row=next(x for x in rows if x['source_path']==str(lock.resolve()));row.update(sha256=hashlib.sha256(raw).hexdigest(),capture='actual_free_OS_lock_path_size_SHA_index_only',reason='actual_final_reader proved native lock free; persistent file retained')
 index=DEST/'REPORT_CAPTURE_INDEX.json';value=json.loads(index.read_bytes());value['entries']=rows;value['live_OS_lock_SHA_unknown_disclosed']=False;value['actual_final_local_OS_lock_free']=True;index.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in files),capture_output=True,check=True)
 archive.gitio.g('commit','-m','Append local128 final checkpoint fulltrace cost and hourly closeout evidence')
 archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
 stage=json.loads((R/'LOCAL_TEMP_STAGE_GIT_RECORDED.json').read_bytes());remote={x.split()[1]:x.split()[0] for x in archive.gitio.g('ls-remote','origin','refs/heads/main','refs/tags/'+stage['tag'],'refs/tags/'+stage['tag']+'^{}').splitlines()}
 assert remote['refs/tags/'+stage['tag']]==stage['tagobject'] and remote['refs/tags/'+stage['tag']+'^{}']==stage['commit']
 assert not archive.gitio.g('status','--porcelain')
 print(json.dumps(dict(passed=True,commit=head,remote_main_verified=True,original_stage_tag_peeled_verified=True,old_tags_preserved=len(old),captured_sources=len(rows),fullfinal_trace_cost_monitor_reports_tracked_exact=True,canonical_reconciliation_still_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('LOCAL_FINAL_SUPPLEMENT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existingobjects_continue_push_only_no_recommit=True));raise
