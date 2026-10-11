"""Ordinary supplement for all saved late evidence; preserve the one stage trial."""
from pathlib import Path
import sys,json,time,hashlib,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
DEST=REPO/'history/evidence'/D.name;EXTRA=DEST/'own_final139_partial_supplement'
def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p
def main():
 assert old.g('rev-parse','HEAD')=='f54c19095a2618c4c88b6a427485dd1975a9abab' and not old.g('status','--porcelain') and not old.g('diff','--cached','--name-only') and not EXTRA.exists()
 previous=old.refs();assert len(previous)==1289
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'ENTRY_FINAL_MONITOR_BYTE_IDENTITY_CORRECTION.json').read_bytes());prompt=(D/'MONITOR_CURRENT_410_FINAL_BYTE_VERIFIED_PROMPT.md').read_text(encoding='utf8')
 assert all(t[k]==req[k] for k in ('id','name','kind','status','rrule','target_thread_id')) and t['prompt'].replace('\r\n','\n')==prompt
 assert t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
 save('ENTRY_FINAL_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,actual_interval_minutes=30,actual_prompt_raw_string_SHA=H(t['prompt'].encode()),normalized_prompt_SHA=H(prompt.encode()),normalized_prompt_matches_requested=True,actual_own_checkpoint_bytes=17616498,own_final_and139_partial_current=True,all_saved_reader_and_monitor_schema_errors_retained=True))
 note=R/'OWN_FINAL_AND139_PARTIAL_SUPPLEMENT_REPORT.md';assert not note.exists()
 note.write_text('''# CURB20入口正式复训完整保存和139实际部分审查

source410在新fresh同CURB/entry严格完整恢复实际通过后，从完整129来源3c97执行首300秒正式复训，实际330.20350074768066秒含加载学习保存退出已原父唯一结清。自己的model32069 SHA2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04，17,616,498字节，CPU102、source410、87实际snapshot、ownPID2748108及PASSED/唯一账段完整核验。7updates、168control、3.36Menvsteps、672callbacks exact；ordinary/integrity/unknown0、nonfinitefalse、STOPnone，closure.947713444mm。声明截断unique1977，timeout1693/route285有1重叠，两coverageexact，原计数不相加当unique。

父2746349、guardian2746422、孩子2748108实际自然退出，两实际fcntl锁free、active-Sactive空，是合法单课审查边界。完整actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA来源身份、显式G3→CURB+newentry迁移/CUDA磁盘roundtrip/savedsourceepisode+1与八startup receipts已核；新geometry/entry exactfalse是披露，不是PhysXexactresume或漏恢复。SDK/小大PPO/native原有效scope精确SHA复用，没有重跑任何物理/预检/clock/预算事务。

139四case已原父自然保存后实际自动发布。首只读收集仅retention-flat complete/errorfree、两hostprobe/result字节SHAexact，115/129完整初始化30q/参数/recipe/assignment/6000callback与原schema严格配对通过，±1.5直线误差.020799875/.046490490m/s；originalstrictfalse保留。terrain/spin/world尚待实际结果，review_complete=false，不能称CURB毕业、永久抗遗忘或MoE已部署，不追加PPO/提高几何。新collector/reviewer已按当前namespace准备并部分实际验证，132/115/129 validcomplete不重发。

所有late错误保留：monitor数字snapshot glob匹配BOUNDARY的ValueError发生在request/update前；final只读者误用stdlib环境importTorch被拒绝，独立admittedCPU环境仅读完成相同immutable证据；monitor曾误填旧weight大小17,615,794，actual文件17,616,498更正并保留原提示；Windows TOML escaped CRLF与Python read_text LF比较拒绝、缺request的PowerShell非终止错误/JSON.parse拒绝都在自动化update前保留，仅续未执行请求，没有GPU/CAS/预算回放。

新final/139partial/reader来源错误/中央只annotation同步/同30分钟ACTIVE驻守回执/阶段Gitreceipt与全部后来保存源码报告按普通supplement入Git，旧stagef54c1909唯一annotatedtrial及所有1289旧tag对象不变。权重/大型NPZ/raw等仅实际path-size-SHA索引，原件保留，凭据不入Git。Git最终核验使用工具输出，避免无限新回执。未来139完整结果/新保存报告仍须后续Git补交；本supplement不追加budget或训练授权、不触碰WASD播放器/其他专家。
''',encoding='utf8')
 prior={}
 for index in (DEST/'REPORT_CAPTURE_INDEX.json',DEST/'seed_reviewed_late_capture/REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(index.read_bytes())['entries']:
   if row.get('Git_path'):prior[(str(Path(row['source_path']).resolve()).casefold(),row['sha256'])]=row
 EXTRA.mkdir();rows=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get((str(p.resolve()).casefold(),h))
  if ref:
   assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.npz','.npy','.usd','.zip') or len(raw)>8000000:
   row.update(capture='large_actual_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(text);data=clean.encode('utf8') if count else raw
   out=EXTRA/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=out.relative_to(REPO).as_posix(),archived_sha256=H(data),redactions=count,encoding=encoding)
  rows.append(row)
 idx=EXTRA/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_errors_sync_monitors_and_stage_Git_receipt_captured=True,ordinary_supplement_same_stage=True,large_weights_raw_SHA_path_size_only=True,credentials_excluded=True,no_old_trial_or_tag_recreated=True,later139_complete_requires_new_supplement=True),ensure_ascii=False,indent=2),encoding='utf8')
 files=[p.relative_to(REPO).as_posix() for p in sorted(EXTRA.rglob('*')) if p.is_file()];old.g('add','--',*files);old.g('commit','-m','Archive CURB20 entry own final and 139 partial review evidence');head=old.g('rev-parse','HEAD')
 try:old.g('push','origin','HEAD:main')
 except BaseException as ex:
  save('ENTRY_FINAL_SUPPLEMENT_PUSH_PENDING_ERROR.json',dict(epoch=time.time(),existing_commit=head,error=str(ex),retry_existing_objects_only=True,no_recommit_record_or_tag=True));raise
 verified=old.refs();assert verified==previous and not old.g('status','--porcelain')
 tracked=old.g('ls-files','--',str(EXTRA.relative_to(REPO)).replace('\\','/')).splitlines();assert set(tracked)==set(files)
 print(json.dumps(dict(commit=head,remote_main_verified=True,all_old_tag_objects_and_peeled_preserved=len(previous),new_tracked_files=len(files),indexed_sources=len(rows),working_tree_clean=True,all_current_saved_reports_and_stage_Git_receipt_recorded=True,no_new_trial_tag=True,final_verification_is_tool_output_no_extra_saved_report=True)))
if __name__=='__main__':main()
