"""Append actual stage receipt and current hourly handoff; no new trial or runtime."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,tomllib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
BASE='caec1ea59ca1c8995d71b127ebd03049a2535dc2'
s=importlib.util.spec_from_file_location('curb35_ordinary_pure_helpers',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain')
 prompt=D/'MONITOR_CURB35_FIRST_REAL_PRODUCTION_STAGE_REMOTE_VERIFIED_ACTUAL_V3_20261016.txt'
 cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert cfg['id']=='mod4-10' and cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 assert cfg['prompt'].encode('utf8')==prompt.read_bytes()
 receipt=R/'CURB35_ACTUAL_STAGE_REMOTE_AND_CURRENT_MONITOR_VERIFIED.json'
 with receipt.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),stage_commit=BASE,tag='trial-20261016-e1-curb35-qualified878-height-native-first-training',object='a300e7abf4a51056f0e59a83122160ef125b1ab7',actual_remote_main_tag_peeled_all1352oldtags_tracked1545sources_verified=True,actual_verification='Prior archive V2 successful tool output, not inferred from a local tag',same_hourly_active_target_exact_prompt=True,prompt_SHA=H(prompt),no_second_monitor_or_runtime_mutation=True),f,indent=2)
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1353
 dest=REPO/'history/evidence'/D.name/'ordinary_first_production_stage_remote_receipt_hourly_handoff_v2';assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 rows=[];files=[]
 for p in (Path(__file__).resolve(),receipt,prompt):
  raw=p.read_bytes();clean,count=redact(raw.decode('utf8'));data=clean.encode('utf8') if count else raw;out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);rows.append(dict(source_path=str(p),bytes=len(raw),sha256=H(p),capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_post_stage_saved_reports_included=True,no_new_trial_tag=True,later_actual_training_FINAL_and_evaluation_require_ordinary_supplements=True),indent=2),encoding='utf8');files.append(idx.relative_to(REPO).as_posix())
 git('add',*files);git('commit','-m','Append CURB35 actual first-production stage receipt and current hourly handoff');head=git('rev-parse','HEAD');git('push','origin','HEAD');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(ordinary_commit=head,actual_remote_main_all1353oldtags_original_objects_peels_and_trackedSHA_verified=True,new_sources=len(rows),no_new_trial_tag=True,final_verification_as_tool_output=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CURB35_FIRST_PRODUCTION_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_objects_not_record_tag_commit_replay=True),f,indent=2)
  raise
