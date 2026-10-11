"""Ordinary completion evidence supplement to the original source410 physical trial."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest();DEST=REPO/'history/evidence'/D.name;EXTRA=DEST/'entry139_complete_direction_review_supplement'

def main():
 assert old.g('rev-parse','HEAD')=='d76748acaaeb916bc0cd36213152ccaf07084d3f' and not old.g('status','--porcelain') and not old.g('diff','--cached','--name-only') and not EXTRA.exists()
 previous=old.refs();assert len(previous)==1289
 receipt=json.loads((R/'ENTRY139_COMPLETE_METADATA_SYNCED.json').read_bytes());assert receipt['metadata_synced'] and receipt['actual139_review_complete'] and receipt['actual_monitor_minutes']==60
 note=R/'ENTRY139_COMPLETE_GIT_SUPPLEMENT.md';assert not note.exists()
 note.write_bytes('''# source410正式短窗139完整验收补充

本补充归档既有source410实际训练阶段的后来139全结果、完整独立审查、读者原错误和独立修正、配对有效失败前缀、保存的真实训练命令暴露、scope决定/下一独立命令轴CPU工作单以及中央/每小时驻守设置和核验回执。没有新增物理/PPO实验、重发评测、重复record/tag、预算事务或WASD动作。此前唯一annotatedtrial f54c1909/tagbf258和全部旧tag/peeled保持。

139四case actualcomplete/errorfree、两主机8份JSON byteSHA和完整180943239bytes NPZ SHA d4c9b622b6c37fa2ca750a9e0f86c830eae1570433266e63f435ff20b40e4cc7与原ground/contact积分COMlinkhardware、完整root30q/参数recipesassignment/6000callbacks、signedcircle已独立核验。上行source13226/27、old13322/27、新13923/27，下行27/27，ordinary0/closure.652400020mm；未完整env6/12/15/18都原向正BODYvx+.3/yaw0，一轮未越坎后转向侧走至声明路线截断。三来源完整退化、一个来源也未完整；旧133的3/9改善而12新增失败，不用净增1掩盖退化。own4102fe只冻结审查证据，未qualifiedCURB、不作下一默认暖启动/同entry900s盲训/升高度，不称永久抗遗忘/整RM/gate毕业。

旧技能作为诊断：负4pi7/8→5/8、正8/8，world仍63/64/maxcross.050733746，±1.5误差.020799875/.046490490；originalstrictfalse/raw/cost全部保留。原reader要求所有最终sensor暖态导致正常finalenv69 route reset拒绝；独立newreader绑定完整raw最终truncated行/实际sample1500 age0及旧reset/apply源SHA，未reset行严格年龄/暖态，原ground/contact/COMlink/hardware/health容差和production源均未改。

own410保存完整168controls的实际command trace CPU审查证明2820CURB/步、473760样本，两侧正负gentle及standing均有；不能说正向未覆盖。towardcenter189577、away184623、stand99560是暴露事实，不是通行/接触/原因的因果消融。下一已授权单轴工作单仅episode-bound实际CURB入口方向与signedgentle命令匹配，先CPU组件/真实assignment/footprint/reset/streams/fullstate和必要新scope物理准入，再首300s有界复训与四case完整验收。当前没有新的learningexecutor或GPU/PPO部署，不缩接近/延窗口、不改reward/LR/DR/geometry/配额、不喂真值或teacher。

原生app每小时sameheartbeat/target/ACTIVE和quiethealthy/pending保持，仅更新实际complete事实。首prompt核验在任何中央写前拒绝；实际native app只去掉结尾一个LF，独立exact-one-LF reader续尚未执行CAS，原source/error保留，没有重更新automation。新的完整中央报告/reference/handoff已同步，master/approval/tracks/RM/canonical字节保持，005七扩展/330h没有重扩展/clear/recharge。

所有当前保存的source/reports/原错误/locator/schema拒绝/实际完整结果/nextworkorder/monitor prompt历史/工具回执/同步证明都按完整索引归档。已归档同SHA原Git路径复用，大weights/rawNPZ/USD/ZIP只实际path-size-SHA，原件保留、credentials不入Git。未来任何新保存报告仍需追加，最终Git远端核验只作工具输出避免无限回执循环。
'''.encode('utf8'))
 prior={}
 for index in (DEST/'REPORT_CAPTURE_INDEX.json',DEST/'seed_reviewed_late_capture/REPORT_CAPTURE_INDEX.json',DEST/'own_final139_partial_supplement/REPORT_CAPTURE_INDEX.json',DEST/'hourly_reaffirmed139_three_skills_supplement/REPORT_CAPTURE_INDEX.json'):
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
 idx=EXTRA/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_complete139_errors_monitor_and_sync_receipts_captured=True,ordinary_supplement_same_existing_stage=True,large_artifacts_SHA_path_size_only=True,credentials_excluded=True,later_saved_reports_require_supplement=True),ensure_ascii=False,indent=2).encode('utf8'))
 files=[p.relative_to(REPO).as_posix() for p in sorted(EXTRA.rglob('*')) if p.is_file()];old.g('add','--',*files);old.g('commit','-m','Record complete CURB139 direction regression and strict reset reader review');head=old.g('rev-parse','HEAD')
 try:old.g('push','origin','HEAD:main')
 except BaseException as ex:
  p=R/'ENTRY139_COMPLETE_SUPPLEMENT_PUSH_PENDING.json';assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),existing_commit=head,error=str(ex),continue_existing_objects_only=True),indent=2).encode());raise
 assert old.refs()==previous and not old.g('status','--porcelain')
 tracked=old.g('ls-files','--',str(EXTRA.relative_to(REPO)).replace('\\','/')).splitlines();assert set(tracked)==set(files)
 print(json.dumps(dict(commit=head,remote_main_verified=True,old_tags_and_peeled_preserved=len(previous),new_tracked_files=len(files),indexed_sources=len(rows),large_indices=sum(x['capture']=='large_actual_SHA_index_only' for x in rows),same_SHA_old_Git_references=sum(x['capture']=='same_SHA_existing_Git_reference' for x in rows),working_tree_clean=True,all_current_saved_reports_and_receipts_recorded=True,actual_monitor_minutes=60,no_new_trial_tag=True,new_training_deployed=False,final_verification_is_tool_output=True)))

if __name__=='__main__':main()
