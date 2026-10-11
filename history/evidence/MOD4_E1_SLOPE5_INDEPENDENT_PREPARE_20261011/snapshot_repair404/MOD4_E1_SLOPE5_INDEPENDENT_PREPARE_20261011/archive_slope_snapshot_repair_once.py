from archive_slope_scope_stage_once import *
import io,contextlib,importlib.util,os,tomllib
ID='e1-slope5-prelearn-snapshot-rejection-preserved-and-isolated-list-repaired'
def main():
 assert not g('status','--porcelain')
 before=g('rev-parse','HEAD');assert before=='5952168c2a196e19daa15d86e9b039b78b7503e8'
 tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 app=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml';v=tomllib.loads(app.read_text(encoding='utf8'));prompt=(D/'MONITOR_CURRENT_SNAPSHOT_REVIEWED_PROMPT.md').read_text(encoding='utf8').strip();assert v['prompt'].strip()==prompt and v['status']=='ACTIVE' and v['rrule']=='FREQ=HOURLY;INTERVAL=2'
 save('SNAPSHOT_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),app_prompt_exact=True,status=v['status'],rrule=v['rrule'],bytes=len(v['prompt'].encode()),sha256=H(v['prompt'].encode()),no_new_automation_or_budget=True))
 save('SNAPSHOT_REPAIR_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_or_tag_replay=True))
 note=R/'SNAPSHOT_REPAIR_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# SLOPE5学习前快照列表拒绝与独立修复

source402的SDK10/native20k/128x2完整PPO已actualPASSED。big20kx4在bounded_learn前复制不存在的slope5_command_migration_environment_view.py被拒绝，没有PPO/控制步。完整八份实际CUDA来源恢复回执已写入；旧source402、原日志/部分快照/回执/false/cost保留，原父guardian孩子自然退出，两OS锁free/noactive与small及failedbig唯一结清核验。

source404新root逐字保留402全部402文件，增加独立worker与唯一wrapper。worker只把快照清单缺失文件名改为真实slope5_command_migration.py，其余源码与旧workerexact；CPU启动前逐项检查必需快照文件存在、原完整source3643c97 CPU102及全部sourceSHA。原SDK/native/small PASSED按实际原件SHA复用，不重复这些GPU合同。仅修复后big20kx4、freshsameSLOPE20k零control零PPO完整恢复通过后才300s formal；正式源仍完整129的3c97，所有discard权重弃用。futureformal/135结果未生成是pending，不声称已通过。

新阶段CPU/readers有三项独立拒绝：误将rawnative当PASSED导致KeyError、boundedreader省略大sensor而误断八份回执为七、wrapper source属性应从prior显式取值导致AttributeError。另一次本地PowerShell引号解析在任何Python/远端前拒绝。原source/error均保存，独立仅补尚未执行readerCPU准入，旧remote/source与false不改，不当物理或训练故障。

source404 unique main/import/Popen argv核验并已dispatch，local15s guardian原账本扣load-learn-save-exit，无扩展/重复结账。中央metadata CAS只更新scope.root及原错误/实际CPU/dispatch/current引用，历史master/approval/tracks/RM保持；自动化仍ACTIVE每2h。新fullformal保存及135完整坡面/flat/spin/world实际配对后才判断下一轴。E0/Wave/CURB不更新，gate未训/硬件未标定/S8后续具体批准，本地WASD播放器不干预。

全部已保存的前595阶段后native/small/实际巡检/同步/monitor/Git回执、此次big失败/原成本与新404源码/CPU/dispatch/读者错误/工作单完整索引入Git；大型weights/raw/NPZ/USD/ZIP只actualpath-size-SHA。后续actualbig/fresh/formal/135/同步仍补充提交，旧标签保持，push失败仅续原objects。
''',encoding='utf8')
 dest=DEST/'snapshot_repair404';entries,files=capture(dest)
 # record_experiment's own validators/commit/tag remain unchanged; avoid Windows argument limits for git add.
 spec=importlib.util.spec_from_file_location('slope_snapshot_record_experiment',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 validation='Source402 big refused before PPO for missing snapshot literal; eight actual CUDA startup receipts and original unique settled cost retained. SDK/native/small exact SHA reused. Source404 preserves402 plus2 files; worker only snapshot literal changed, all mandatory snapshot members and CPU102 fullsource checked, unique wrapper dispatched. No hotpatch, oldonce replay, budget extension or premature formal/135 pass. Central scope CAS masterapprovaltracksRM preserved; ACTIVE2h monitor exact. All saved post595 reports/errors indexed; large originals actual path-size-SHA only.'
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Preserve slope5 prelearn snapshot failure and deploy isolated source-list repair','--kind','repair','--note-file',str(note),'--files',*files,'--validation',validation,'--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('SNAPSHOT_REPAIR_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_do_not_repeat_record=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('SNAPSHOT_REPAIR_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_REPAIR_ARCHIVE_ERROR.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
