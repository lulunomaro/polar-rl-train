"""One ordinary supplement of stage tool receipt and app newline-normalization readback."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;REPO=B.parent/'polar-rl-train';R=B/'reports';BASE='691e2ab3a1dc4a91c73d9d6bbb2e07511695694a';DEST=REPO/'history/evidence'/B.name/'followup_ce3_fp32_stage_receipt_app_readback';NOTE=B/'CE3_FP32_RECEIPT_APP_READBACK_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('recorded_fp32_stage_functions_only',B/'archive_ce3_original_fp32_native_reuse_training_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 old=json.loads((REPO/'history/evidence'/B.name/'actual_ce3_original_fp32_native_reuse_training/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')};known={str(Path(r['source_path']).resolve()):r for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1376
 with NOTE.open('x',encoding='utf8') as f:f.write('Ordinary supplement of already recorded ce3 original-FP32 native-reuse training stage691e2ab3,tagobject622769eb/all1375oldtags verified. Capture exact unique-stage remote toolreceipt and normalized automation app readback. Initial inline strict prompt equality failed because app removed exactly one trailing newline; original AssertionError/reason retained and V2 confirms all content plus ACTIVEhourly/originaltarget exact after normalization. No GPU fault, changed training parameter, newmonitor, newGO, budget operation, oldnative/raw/PT replay, record/tag or repeatedoldhelper. Existing new immutablefirst whole199tensor105float/sourcecore/17Adam646100to646120/actor9critic8 changes remain true; first is not FINAL or jump skill. Technical choice owned by agent and no repeated approval framing. Large artifacts retain existing complete producer indices only. Final toolverification is receipt; do not manufacture more commits merely to write final HEAD back.')
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];deferred=[];captured=0
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing producer hash; no archive rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['sha256'],capture='actual_large_index_only',index_provenance='recorded stage complete index',original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture-only credential redaction; original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,ordinary_only_no_new_tag=True),indent=2),encoding='utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1376
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1376_tag_objects_peels_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred,no_new_tag_or_repeat_stage=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_FP32_RECEIPT_ORDINARY_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),push_existingobjects_if_committed_no_repeat_record_or_GPU=True),f,indent=2)
  raise
