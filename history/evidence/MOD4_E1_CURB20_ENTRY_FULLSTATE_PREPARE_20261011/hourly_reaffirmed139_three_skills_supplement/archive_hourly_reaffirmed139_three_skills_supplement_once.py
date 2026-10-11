"""Ordinary evidence supplement for the existing stage and latest cadence instruction."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest();DEST=REPO/'history/evidence'/D.name;EXTRA=DEST/'hourly_reaffirmed139_three_skills_supplement'
def main():
 assert old.g('rev-parse','HEAD')=='b8497f5c501b2f440067f8b54ccf99a45ac508b8' and not old.g('status','--porcelain') and not old.g('diff','--cached','--name-only') and not EXTRA.exists()
 previous=old.refs();assert len(previous)==1289
 receipt=json.loads((R/'MOD4_HOURLY_REAFFIRMED_AND139_THREE_SKILL_METADATA_SYNCED.json').read_bytes());assert receipt['actual_interval_minutes']==60 and receipt['metadata_synced']
 note=R/'HOURLY_REAFFIRMED_AND139_THREE_SKILLS_SUPPLEMENT.md';assert not note.exists()
 note.write_text('''# 同一驻守改回每小时及139三技能部分审查补充

人类最新直接要求“监守调成一小时一次吧”，已通过原生automation_update将同一mod4-10 heartbeat、同一target改为ACTIVE每1小时一次，实际TOML/提示/字段核验通过；旧30分钟与2小时只作历史。保持健康或pending静默，仅有实质阶段/真实修复/重大退化/完成/需人类动作时通知。没有新增驻守、SSH/ping/Rich周期、预算或物理训练操作，没有触碰本地WASD播放器。

本次先前heartbeat已只读收集139-flat/spin/world三case complete/errorfree并独立核验两hostprobe/result字节SHA与完整115/129初始root30q/参数/recipe/assignment/6000callback、signedcircle沿横向去漂移和原容差。候选own410负4pi5/8、来源3647/8，正8/8；world仍63/64、maxcross.050733746m/s；直线±1.5误差.020799875/.046490490m/s。原strictfalse/残差均保留，旧完整结果未重发。跨坎terrain最后一case仍由原健康worker自然运行/attentionnull，review_complete=false，不称CURB毕业或永久抗遗忘，不追加PPO或提高几何；后来的实际完整结果优先。

只向中央新增设置请求/实际核验、三技能collection/review与同步回执，annotation/latest handoff记最新1小时要求；master/approval/tracks/RM/canonical字节严格保持。源码、保存报告、prompt历史、原生工具回执和同步证据按原阶段普通supplement提交。原stage唯一annotatedtrial及1289tag对象/peeled保持，不新增record/tag、预算事务或GPU回放。大权重/NPZ/raw仅实际path-size-SHA，所有未来139完整或新保存报告继续Git补交。
''',encoding='utf8')
 prior={}
 for index in (DEST/'REPORT_CAPTURE_INDEX.json',DEST/'seed_reviewed_late_capture/REPORT_CAPTURE_INDEX.json',DEST/'own_final139_partial_supplement/REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(index.read_bytes())['entries']:
   if row.get('Git_path'):prior[(str(Path(row['source_path']).resolve()).casefold(),row['sha256'])]=row
 EXTRA.mkdir();rows=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get((str(p.resolve()).casefold(),h))
  if ref:
   assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(text);data=clean.encode('utf8') if count else raw;out=EXTRA/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=out.relative_to(REPO).as_posix(),archived_sha256=H(data),redactions=count,encoding=encoding)
  rows.append(row)
 idx=EXTRA/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_monitor_and_sync_receipts_captured=True,ordinary_supplement_same_existing_stage=True,large_artifacts_SHA_path_size_only=True,credentials_excluded=True,later139_complete_requires_supplement=True),ensure_ascii=False,indent=2),encoding='utf8')
 files=[p.relative_to(REPO).as_posix() for p in sorted(EXTRA.rglob('*')) if p.is_file()];old.g('add','--',*files);old.g('commit','-m','Record hourly monitor request and CURB139 three-skill review');head=old.g('rev-parse','HEAD')
 try:old.g('push','origin','HEAD:main')
 except BaseException as ex:
  p=R/'HOURLY_REAFFIRMED_SUPPLEMENT_PUSH_PENDING.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),existing_commit=head,error=str(ex),continue_existing_objects_only=True),indent=2),encoding='utf8');raise
 assert old.refs()==previous and not old.g('status','--porcelain')
 tracked=old.g('ls-files','--',str(EXTRA.relative_to(REPO)).replace('\\','/')).splitlines();assert set(tracked)==set(files)
 print(json.dumps(dict(commit=head,remote_main_verified=True,old_tags_and_peeled_preserved=len(previous),new_tracked_files=len(files),indexed_sources=len(rows),working_tree_clean=True,all_current_saved_reports_and_cadence_receipts_recorded=True,actual_monitor_minutes=60,no_new_trial_tag=True,final_verification_is_tool_output=True)))
if __name__=='__main__':main()
