"""Record the requested physical GPU snapshot without changing any runtime."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;REPO=B.parent/'polar-rl-train';R=B/'reports';BASE='8ff01e533dadcf88cacf0a58d6ce4bab7dd710a5';DEST=REPO/'history/evidence'/B.name/'followup_three_4090_requested_status';NOTE=B/'THREE_4090_REQUESTED_STATUS_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_stage_pure_git_functions_only',B/'archive_ce3_original_fp32_native_reuse_training_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 H=B/'hour1_h1_8a7c_v1';status=json.loads((H/'reports/THREE_4090_HUMAN_STATUS_1652_READONLY_ACTUAL.json').read_bytes());assert status['actual_transport_returned'] and not status['host210']['compute'] and status['host72']['rows']['job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json']['completed']==10
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1377
 with NOTE.open('x',encoding='utf8') as f:f.write('Ordinary saved status requested by human asking whether all three GPUs are working. Fresh localCIMknownfinite0 then exactly one bounded readonly72 and210 connection, actualreturned and freshCIMhandbackknownfinite0. Snapshot1792313588:72GPU0 UUID16828f91 has actualH1 productionworker22790,about14.5GiBMiB allocation and logged10completedupdates/4.8Menvsteps;72GPU1 UUIDc27eecbd has13MiBbaseline and no compute process, priorfrozencase completed,currentlyidle;210GPU UUID937bdb0b has225MiBbaseline and no compute process,currentlyidle,actualmountedDfree21626654720bytes about20.14GiB beloworiginal25GiBstartguard. InstantGPUutilization0percent is retained as instantaneoussample,notfabricated100percent or evidence of all GPUs training. Onlyoneofthree activeforourscope. E2E3paidholdsremain, no inventednewworker/evaluation or loweringresourceguards. Original hourblocksave17:38Beijing continues, no midhourmodel/behavioraudit or training interruption. No launch/stop/modelrawhash/runtimechange/budgetmutation, no newmonitor/polling. Capture newscript/started+fullsnapshotreports/thissource/note exact or credential-redacted, originalpreserved. No newlargeartifact or trialtag; original1377tagobjects/peels unchanged. Final remoteverification tooloutput is receipt, no endlessHEADwriteback.')
 paths=[H/'check_three_4090_requested_status_1652_readonly_once.py',H/'reports/THREE_4090_HUMAN_STATUS_1652_COLLECTOR_STARTED_ACTUAL.json',H/'reports/THREE_4090_HUMAN_STATUS_1652_READONLY_ACTUAL.json',Path(__file__).resolve(),NOTE]
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[]
 for p in paths:
  raw=p.read_bytes();text=raw.decode('utf8');safe,n=redact(text);data=safe.encode('utf8') if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);rows.append(dict(source_path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=hashlib.sha256(data).hexdigest(),redaction_count=n,redaction_reason='Capture-only credential redaction; original retained' if n else None,original_retained=True))
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=[],prior_complete_capture_index='history/evidence/'+B.name+'/followup_H1_hour_requested_current_status/REPORT_CAPTURE_INDEX.json',ordinary_only_no_new_tag=True,no_new_large_artifacts=True),indent=2),encoding='utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1377
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1377_tag_objects_peels_and_saved_evidence_SHA_verified=True,new_texts=len(rows),deferred=[],no_runtime_or_budget_mutation=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_4090_STATUS_ORDINARY_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_only_push_existing_objects_no_repeat_record_tag=True),f,indent=2)
  raise
