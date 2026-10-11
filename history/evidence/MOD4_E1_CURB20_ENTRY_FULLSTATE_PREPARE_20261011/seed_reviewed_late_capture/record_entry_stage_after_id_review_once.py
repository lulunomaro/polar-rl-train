from pathlib import Path
import sys,json,time,re,hashlib,subprocess,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
ID='curb20-entry-origin-sdk-and-seed-reviewed-fullstate'

def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p

def main():
 assert re.fullmatch('[a-z0-9][a-z0-9-]{2,80}',ID)
 assert old.g('rev-parse','HEAD')=='b3990e45a621e207e1f872467604b40c8ee65ce0' and not old.g('diff','--cached','--name-only')
 assert not old.g('tag','--list','*curb20-origin-bound*') and not old.g('tag','--list','*'+ID) and not (R/'STAGE_GIT_RECORDED.json').exists()
 previous=old.refs();assert len(previous)==1288
 original=json.loads((R/'ENTRY_FULLSTATE_RECORD_ERROR.json').read_bytes());assert 'Invalid experiment id' in original['stderr']
 save('ENTRY_RECORD_ID_LENGTH_PRECOMMIT_REVIEW.json',dict(epoch=time.time(),original_requested_id='curb20-origin-bound-sdk-and-fullstate-preflights-admitted-fresh-verification-started',original_record_error=str(R/'ENTRY_FULLSTATE_RECORD_ERROR.json'),actual_record_guard='[a-z0-9][a-z0-9-]{2,80}',no_original_commit_tag_experiment_objects_created=True,original_captured_directory_retained=True,actual_HEAD=old.g('rev-parse','HEAD'),shorter_unique_id=ID,only_unexecuted_record_continued=True))
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'ENTRY_SEED_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==req[k] for k in ('id','name','kind','status','rrule','target_thread_id')) and t['prompt']==(D/'MONITOR_CURRENT_SEED_REVIEWED_PROMPT.md').read_text(encoding='utf8')
 save('ENTRY_SEED_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],status=t['status'],rrule=t['rrule'],same_existing_heartbeat=True,actual_interval_minutes=30,target_thread_id=t['target_thread_id'],prompt_SHA=H(t['prompt'].encode()),source410_actual_dispatch_and409_failed_fresh_disclosed=True))
 note=R/'STAGE_SEED_REVIEWED_REPORT.md';assert not note.exists()
 note.write_text('''# CURB20入口原点范围补证与严格seed恢复准入修复

新的source409保留398全部源码并新增11份独立来源/entry/fullstate接口。CPU实际旧SDK原点更改缓存0→10、subset和原20kmap byteexact通过。真正新SDK10实际10/10CURB起点、300control1200callbacks/selectedreset/原groundrewardsolverhealth通过；旧398SDK一般PASSED与实际0/10覆盖缺口并列保留。398有效native20k精确SHA复用，没有重native/clock/DR。source409小128x2和big20kx4完整PPO自己的CPU102/fullsave/PIDreceipt/PASSED/唯一同canonical结清，权重弃用。

source409独立fresh20k零control零PPO因argv缺seed20260928、默认42触发旧严格terrain seedguard，在完整恢复与任何控制/PPO之前失败。全部原source/error/false/raw/成本保持，没有formal或139发布。父guardian孩子actual自然退出/两OS锁free/active-Sactive空后，source410保留409所有源码字节，只新增一个唯一wrapper，明确fresh --seed20260928。新CPU102/正确import-main-Popenargv/sourcefreeze准入及dispatch真实完成；只补失败的fresh范围，所有有效SDK/small/big/native原PASSED精确复用，无重新PPO预检。独立fresh实际PASSED之后才首300s正式从3c97加载、自己的完整保存和139四case行为审查，不用discard源/不称已正式毕业。

本次初始归档ID超过record工具81字符正则上限，在commit/tag/experiment对象之前拒绝；实际HEAD及原1288tags unchanged，原untracked捕获目录和错误保留，较短uniqueID仅续尚未执行record。两reader路径错误、metadata字母glob误选authority KeyError、PowerShell inline ParserError及缺新file尝试全部保存preGPU/CAS，不重写旧失败。source409/410新scope中央只增annotation，历史master/approval/tracks/RM字节保护；canonical0051188000/7extensions原parent唯一正常扣，fresh零PPO不计，无加时或清账。

30min同一heartbeatACTIVE真实核验/健康pending静默。E0/Wave/SLOPE权重不更新，gate未训/硬件未标定/S8未新增批准，本地WASD播放器未触碰；reward/LR/hardware/clock/DR/地形比例与命令轴不改。所有当前源码/成功失败/错误/同步/监控/工作单/Git拒绝报告补档，原大raw/权重仅真实path-size-SHA，凭据不入Git。后来fresh/formal/139/ownCPU/新同步/Git回执追加普通supplement。
''',encoding='utf8')
 index=DEST/'REPORT_CAPTURE_INDEX.json';initial=json.loads(index.read_bytes());prior={}
 for row in initial['entries']:
  if row.get('Git_path'):prior[(str(Path(row['source_path']).resolve()).casefold(),row['sha256'])]=row
 extra=DEST/'seed_reviewed_late_capture';assert not extra.exists();extra.mkdir()
 rows=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get((str(p.resolve()).casefold(),h))
  if ref:
   assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_initial_capture_or_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.npz','.npy','.pt','.usd','.zip') or len(raw)>50000000:row.update(capture='large_actual_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(text);data=clean.encode('utf8') if count else raw
   out=extra/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=out.relative_to(REPO).as_posix(),archived_sha256=H(data),redactions=count,encoding=encoding)
  rows.append(row)
 idx=extra/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_and_errors_captured=True,original_prerecord_capture_preserved=True,old409_failed_fresh_preserved_source410_only_new_seed_wrapper=True,large_artifact_index=str((R/'LARGE_ARTIFACTS_ACTUAL_INDEX.json').resolve()),later_actual_final_and139_Git_receipts_require_supplement=True,credentials_excluded=True),ensure_ascii=False,indent=2),encoding='utf8')
 files=[p.relative_to(REPO).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file()]
 proc=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Repair CURB20 origin bound SDK and seed matched full state admission','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Source409 actualnewSDK10/1200callbacks and128x2/20kx4 fullsave CPU102 ownPID uniqueledger passed. Old398 native20k reused. Fresh4090PPO rejected defaultseed42 beforecontrols retained, alloldexits/locks/idle boundary then source410 onlyexplicitseed wrapper CPU/dispatch. Fresh410/formal/139 actualpending. Original ID rejected beforecommit/tag; only missingrecord continued. CentralprotectedmasterapprovaltracksRM, 30minACTIVE, allsaved errors captured, raw actualSHAindex, 1288oldtags preserved.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if proc.returncode:
  save('ENTRY_SEED_RECORD_PENDING_ERROR.json',dict(epoch=time.time(),returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,no_repeat_record_tag_or_commit=True));raise RuntimeError('Inspect existing objects; do not rerun record')
 tag,head=proc.stdout.strip().splitlines()[-1].split();obj=old.g('rev-parse',tag);remote={line.split()[1]:line.split()[0] for line in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tag_objects_preserved=len(previous),captured_files=len(files),original_invalid_ID_did_not_create_objects=True))
 assert not old.g('status','--porcelain')
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,old_tags_preserved=len(previous),captured_files=len(files),working_tree_clean=True)))

if __name__=='__main__':main()
