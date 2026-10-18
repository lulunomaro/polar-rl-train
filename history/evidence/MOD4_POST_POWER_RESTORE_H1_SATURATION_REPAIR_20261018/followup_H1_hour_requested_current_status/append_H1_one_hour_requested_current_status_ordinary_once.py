"""Ordinary saved-status evidence supplement; no new trial tag or runtime action."""
from pathlib import Path
import json,time,tomllib,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='b6e86c0f0f487f584c262279a168424fd44e2dde';DEST=REPO/'history/evidence'/B.name/'followup_H1_hour_requested_current_status';NOTE=B/'H1_HOUR_REQUESTED_CURRENT_STATUS_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('previous_stage_pure_functions_only',B/'archive_ce3_original_fp32_native_reuse_training_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 a=json.loads((B/'AUTOMATION_H1_ONE_HOUR_ACTUAL_PRODUCTION_HOURLY_ARGS_V13.json').read_bytes());actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert a['prompt'].rstrip('\r\n')==actual['prompt'].rstrip('\r\n') and actual['status']=='ACTIVE' and actual['rrule']==a['rrule']=='FREQ=HOURLY;INTERVAL=1' and actual['target_thread_id']==a['targetThreadId']=='01a07a2d-9036-7531-a012-692df9f56353'
 with (R/'H1_ONE_HOUR_ACTUAL_PRODUCTION_MONITOR_APP_RECEIPT_V13_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_automation_tool_receipt=dict(automationId='mod4-10',mode='update',status='ACTIVE'),normalized_prompt_exact=True,submitted_SHA=hashlib.sha256(a['prompt'].encode()).hexdigest(),actual_SHA=hashlib.sha256(actual['prompt'].encode()).hexdigest(),original_target_hourly_no_second_monitor=True,no_training_or_budget_mutation=True),f,indent=2)
 old=json.loads((REPO/'history/evidence'/B.name/'actual_H1_8a7c_review_one_hour_continuation/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')};known={str(Path(r['source_path']).resolve()):r for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT};tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1377
 with NOTE.open('x',encoding='utf8') as f:f.write('Ordinary supplement of already recorded H1 onehour stageb6e86c0f/tagobjectcd220ac5/all1376oldtags/tracked verified. Human asked whether training now. FreshlocalCIMknownfinite0 then a single readonly72+210metadata connection returned actualproductionworker22790/create1792312703.97/node22089/owner110623,GO1792312701.371657=Beijing16:38:21.371657,saveGO+3600=17:38:21.371657,lifecyclecap3900=17:43:21.371657. Capture1792313200.758282 reports2completedupdates/960000envsteps and no target/owner errors. Native original independentCPU passed before actualGO. This is metadata evidence of actuallearning,not wholemodelCPU qualification,public4auxeffect,futureFINAL or permanentPIDalive. Noheavyfirst/PTaudit/frozencheck midhour,model/rawhash,task/native/fullreplay,GPUsignal/livepatch or accountmutation. Collectorreturned and freshCIMhandbackknownfinite0. Existinghourlymonitor sameoriginaltarget updatedV13 andactualappreadback exact; no newmonitor/window/budget,old24cutoff removed and originalsafetyguards unchanged. Agenttechnicalplan responsibility/no repeated approvalframing remains. All newstatussource/report/workorder/appreceipt captured with priorcompleteSHAreferences; large originals indexedonly, no newlarge. No newrecord/tag or repeatedoldhelper; finalremoteverification is toolreceipt,not endlessformalHEADwriteback.')
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];deferred=[];captured=0
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No previous complete producer hash; no archive rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['sha256'],capture='actual_large_index_only',index_provenance='prior complete stage index',original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture-only credential redaction; original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,ordinary_only_no_new_tag=True),indent=2),encoding='utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1377
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1377_tags_objects_peels_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_HOUR_CURRENT_ORDINARY_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_push_existing_objects_only_no_repeat_record_tag=True),f,indent=2)
  raise
