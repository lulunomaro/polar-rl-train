"""Ordinary evidence-only supplement; no new trial, transport, GPU or budget action."""
from pathlib import Path
import importlib.util,json,time,hashlib,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train'
BASE='fdd9f06640abea00b03020d0bbb75db6c3e9736d'
DEST=REPO/'history/evidence'/B.name/'followup_original_human_training_config_history'
NOTE=B/'ORIGINAL_HUMAN_TRAINING_CONFIG_HISTORY_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('old_consumed_ordinary_functions_only',B/'append_approved_ce3_native_first_actual_ordinary_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
git=m.git;H=m.H;TEXT=m.TEXT
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 evidence=json.loads((R/'HUMAN_ORIGINAL_TRAINING_PARAMETERS_AND_FP32_FP64_PROVENANCE_RECONCILED_CPU_ACTUAL.json').read_bytes());assert evidence['CPU_RNG_unchanged'] and evidence['CUDA0_optimizer0']
 assert evidence['reference_provenance']['reply_is_history_lookup_instruction_not_explicit_protocol_selection']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1375
 old=json.loads((REPO/'history/evidence'/B.name/'followup_approved_ce3_native_first_actual/REPORT_CAPTURE_INDEX.json').read_bytes())
 prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')}
 known={str(Path(r['source_path']).resolve()):r for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 note='Ordinary original-chat history/config reconciliation of the already recorded ce3 approved native stage. Actual human requested original training parameters after audit-reference question; this is not fabricated FP32 consent or a second training grant. Read current chat two original rollouts; exclude synthetic heartbeat and agent question text from human instructions.773 unique human inputs/181 training-related turns; no human precision-switch request found in that limited evidence. Original human20k, later explicit2.5ms request and32/4 continuation supersede older2ms16/4 baseline. Actual selected current H1 configuration20kx24,2.5msx4,TGS32/4,100Hz,5msbin3,actor35critic38action6,25612864ELU,LRconfig1e-4adaptive/5epochs4batches/clip.2/entropy.005/value2/gamma.99/lam.95/KL.01/grad1,seedCLI20260928 distinct from full restored RNG state. Read existing complete ce3 source metadata without PT rehash: actual actor/criticF32, owned24/17Adam646100, saved optimizerLR1e-5 and six learned STD retained; defaultINITSTD.3 is not a reset authorization. FP64 was a later AI CPU audit reference, not a human request for double-precision training. Preserve original FP32 audit pass and dualFP64false separately; no model/GPU/threshold change or unique floating-cause claim. Own context attribution mistake explicit. Human latest reply received/history lookup complete, not unanswered but not explicit protocol choice. Existing single1800/300/max24 original-budget approval remains; no newGO/deployer/namespace/SSH/GPU/charge, no duplicate question, no removal of V9 actual handoff and protocol-choice boundary. Preserve source lookup/schema failures,V1zero event schema,V3zero channel schema,correctV2/V4 actual captures. Same hourly monitor V10 exact app readback, no new monitor/budget. All new reports/scripts/workingplan/appreceipt/history evidence complete exact or capture-only credential-redacted text; raw chats not copied, only source path-line-textSHA excerpts. Large originals existing actual indices, no archival PT/raw rehash. Old tags/once/trials preserved; ordinary supplement only, no new record/tag. Tool remote verification is final receipt.'
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];deferred=[];captured=0
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No previous producer index; do not rehash for Git'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['sha256'],capture='actual_large_index_only',index_provenance='prior complete followup index',original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture-only credential redaction; original unchanged' if n else None,original_retained=True);rows.append(r);prior[sha]=r;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,ordinary_only_no_new_tag=True,no_archival_GPU_or_account_change=True),indent=2),encoding='utf8')
 git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main')
 v=m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1375
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1375_old_tag_objects_peels_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred,no_new_record_tag_or_repeat_old_helper=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORIGINAL_TRAINING_CONFIG_HISTORY_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_push_existing_objects_only=True,no_repeat_old_record_or_GPU=True),f,indent=2)
  raise
