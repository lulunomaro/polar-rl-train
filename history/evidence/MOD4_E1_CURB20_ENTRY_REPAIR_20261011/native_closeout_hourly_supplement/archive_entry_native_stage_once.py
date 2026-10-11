from repair_io import *
import subprocess
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name
ID='curb20-entry-reset-native-repair-started-and-hourly-monitor-approved'
def g(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def refs():
 tags={line.split('|')[0]:(line.split('|')[1],line.split('|')[2] or line.split('|')[1]) for line in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==g('rev-parse','HEAD')
 for n,(o,c) in tags.items():assert remote[n]==o and remote.get(n+'^{}',c)==c
 return tags
def capture(dest):
 assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 files=[];entries=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=H(raw))
  if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip') or len(raw)>50_000_000:row.update(capture='large_actual_original_SHA_index_only',original_retained=True)
  else:
   try:t=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:t=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,n=redact(t);data=clean.encode('utf8' if n else 'latin1' if encoding=='latin1_byte_preserving' else 'utf8')
   out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',encoding=encoding,redactions=n,Git_path=name,archived_sha256=H(data))
  entries.append(row)
 index=dest/'REPORT_CAPTURE_INDEX.json';index.write_bytes(json.dumps(dict(epoch=time.time(),entries=entries,all_saved_current_stage_reports_sources_errors_hourly_monitors_captured=True,credentials_excluded=True,large_originals_retained=True,later_native_final_fullstate_and_Git_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(index.relative_to(REPO).as_posix());return entries,files
def main():
 assert not g('status','--porcelain') and not (R/'STAGE_GIT_RECORDED.json').exists()
 assert json.loads((R/'ENTRY_NATIVE_HOURLY_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 assert json.loads((R/'HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['rrule']=='FREQ=HOURLY;INTERVAL=1'
 old=refs();assert not g('tag','--list','*'+ID)
 save('ENTRY_ARCHIVE_STARTED.json',dict(epoch=time.time(),unique_trial_id=ID,prior_main=g('rev-parse','HEAD'),old_tag_count=len(old),original_objects_preserved=True))
 note=R/'STAGE_REPORT.md';assert not note.exists();note.write_text('''# 独立CURB20入口修复实际启动与每小时驻守

人类询问何时开始修复，随后明确驻守改为一小时一次。实际核验005总授权1188000秒/七扩展、own404完整保存PASSED与原唯一段、父guardian孩子实际退出、两OS锁free/active-Sactive空后部署全新source398隔离root。完整129 source3643c97暖启动，旧389全部389源码SHA保持；E0/Wave/SLOPE权重与optimizer保持。新reset单轴将实际CURB起点放在两侧0.8/1.65米独立入口，Y按原完整bank碰撞extent移入格边，原heading/关节/commands/20mm竖直150mm条带/plane30+20/20/15/15/DR/reward/LR/hardware/clock不变。没有因果改善或毕业声明。

V1 CPU完整footprint cell containment在GPU前拒绝，原code/error/false保留；V2包含Y安全边界后原20k映射2820CURB/其它17180不变，完整前支撑>=.442米、全碰撞sample bbox合法不重叠、重复XY严格拒绝通过。CPU不冒SDK接触/全路线。新的SDK10x300control/1200callback已自己的PASSED，20k24warm+120timed native实际运行/pending或自己的后续PASSED以actual为准。新controller只SDK-native，无PPO/optimizer/canonical写；state/CUDA/fullsave/fullresume/PPO/formal待下一真正新准入，不能把native叫训练毕业。已有全部clock/DR/geometry证据复用，无旧once/GPU回放。

新budget guard在新sourcefreeze明确注册sum+base10h=1188000并保留老硬编码828000源码，不热改/复活旧入口，不再次加100小时。中央current新增入口scope与下一fullstate有界复训工作单，主master/PLAN_APPROVAL/tracks/RM/canonical bytes保持。mod4-10同一heartbeat已由native automation_update改为ACTIVE每1h，同target/原healthy pending DONT_NOTIFY，不加5min任务。原两小时提示历史保留。local wrong-cwd/path/missing CODEX_HOME observer错误保留，不当物理错误。

所有保存源码、CPU拒绝、准入/dispatch/native当前快照、metadata同步、hourly回执与工作单全部捕获。权重/碰撞bank/rawNPZ只真实path-size-SHA索引，原件保持。之后native final、trace合同、fullstate/PPO/final/monitor/Git回执追加普通supplement；不为归档重跑旧record/tag，push失败续原objects。
''',encoding='utf8')
 entries,files=capture(DEST)
 p=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Start isolated CURB20 reset entry repair SDK native scope and apply hourly heartbeat','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual priorownsave/exits/2OSlocks/idlecanonical1188000 verified; source398 preserves389 SHA. CPUv1 rejected beforeGPU retained; v2 fullfootprint/2820 map/nonoverlap proof. SDK10 PASSED; native20k newscope actual pending. NoPPO/budgettransaction, fullstate formal pending. Current metadata synced protected masterapprovaltracksRMbudget exact. Existing heartbeat ACTIVE1h actual TOML checked. Allsaved reports/source/errors/hourly receipts captured, large originals SHA index.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if p.returncode:save('ENTRY_STAGE_RECORD_ERROR.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,no_repeat_record_tag_or_commit=True));raise RuntimeError('Inspect original record objects before continuing')
 tag,head=p.stdout.strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for n,(o,c) in old.items():assert remote[n]==o and remote.get(n+'^{}',c)==c
 save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(old),captured_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,captured_files=len(files))))
if __name__=='__main__':main()
