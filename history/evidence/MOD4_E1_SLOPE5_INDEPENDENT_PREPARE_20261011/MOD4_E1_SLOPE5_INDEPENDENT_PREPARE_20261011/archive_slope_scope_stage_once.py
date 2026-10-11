from slope_io import *
import subprocess,traceback
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name
ID='e1-slope5-complete-mirrored-route-reviewed-and-independent-fullscope-started'
sys.path.insert(0,str(PRE));from archive_complete133_slope134_stage_once import known_refs
def g(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def capture(dest):
 assert not dest.exists();dest.mkdir(parents=True);known=known_refs();entries=[];files=[]
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 for scope in (PRE,D):
  for p in sorted(scope.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h)
   if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip','.partial') or len(raw)>50_000_000:
    row.update(capture='actual_large_original_index_only',original_retained=True);entries.append(row);continue
   assert p.suffix.lower() in ('.py','.md','.json','.txt','.log','.toml'),p
   if h in known:
    ref=known[h];row.update(capture='existing_same_SHA_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256']);entries.append(row);continue
   clean,n=redact(raw.decode('utf8'));out=dest/scope.name/p.relative_to(scope);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(clean.encode());gp=out.relative_to(REPO).as_posix();files.append(gp)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',redactions=n,Git_path=gp,archived_bytes=out.stat().st_size,archived_sha256=H(out.read_bytes()));entries.append(row);known[h]=row
 for p in R.glob('SLOPE_ACTUAL_[0-9]*.json'):
  v=json.loads(p.read_bytes())
  for r in v['report_indices']+[x for run in v['runs'] for x in run['indices']]:
   if r['bytes']>=1800000:entries.append(dict(source_path=r['path'],bytes=r['bytes'],sha256=r['sha256'],capture='actual_large_remote_original_index_only',original_retained=True))
 ip=dest/'REPORT_CAPTURE_INDEX.json';ip.write_bytes(json.dumps(dict(epoch=time.time(),entries=entries,all_current_saved_reports_source_reader_rejections_workorders_captured=True,all_old_false_raw_cost_retained=True,credentials_excluded=True,large_originals_indices_only=True,later_formal_native_PPO_135_and_sync_receipts_need_supplement=True),ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(REPO).as_posix())
 return entries,files
def main():
 assert not g('status','--porcelain') and json.loads((R/'SCOPE_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:dict(object=x.split('|')[1],peeled=x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 for t,v in tags.items():assert remote[t]==v['object'] and remote.get(t+'^{}',v['peeled'])==v['peeled']
 save('STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tags=tags,no_record_replay_if_objects_created=True))
 actual=json.loads(sorted(R.glob('SLOPE_ACTUAL_[0-9]*.json'))[-1].read_bytes());note=R/'STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# 完整坡面基线与独立SLOPE新范围

已独立审查134真实完整5°/2m镜像坡面，80env/15s，完整两轮上下坡与200mm后支撑各27/27，原1N接触证据吻合；完整两主机JSON字节SHA/大rawNPZ/初末root30q/参数recipesassignments/6000callback/groundcontactintegralCOMlinkhardware原容差保持。不是实际RM全坡面或新学习专家毕业。

新隔离source402保留旧389全部字节，只新增13文件；source3643c97完整129已审来源，独立actorcriticoptimizer存储/旧严格command身份再显式assignment绑定targetCPU通过。旧389own保存/PASSED/唯一330.259s/实际三进程退出/两fcntl锁free/noactive边界实核后才部署。新SDK/native/small128x2/big20kx4/fresh20k同scope完整状态恢复/首次300s由唯一新controller按实际PASSED顺序执行；所有discard权重不用作formal源，旧clock/DR证据精确复用，不重复旧scope。未完成项目仍pending，不能借CPU/活动进程称formal已通过。

133方向退化与所有旧false/raw/cost有效prefix保持，独立专家不会覆盖E0/Wave/CURB。未完成135完整候选四case之前不更多PPO/升坡度；gate未训/硬件未标定/S8后续具体批准。人类WASD播放器不干预。新135reader-builder首次anchor字面量检查在任何review/GPU之前拒绝，源码和错误保存；独立只完成尚未写入的新reviewer，完整原合同不放松。

canonical828000s/六扩展各一次/新增0；无PPO的CPU/SDK/native/restore-only不扣，PPOload/learn/save/exit原parent唯一扣；不复制/clear/重tail/kill/hotpatch/双20k。134complete和新scope中央CAS已同步并保持master/approval/tracks/RM/canonical字节。所有已保存新报告、来源/reader/错误/工作单/同步回执入Git，大weights/rawNPZ/USD/ZIP只真实path-size-SHA；后续native/PPO/formal/135/monitor/Git回执追加supplement。
'''+ '\n实际归档快照phase: '+actual['phase']+'\n',encoding='utf8')
 entries,files=capture(DEST)
 run=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete mirrored slope5 route and start isolated full-state scope','--kind','training','--note-file',str(note),'--files',*files,'--validation','Complete134 byteexact twohost JSON fullraw and original tolerances; ascending27/27 descending27/27 actual contact confirmed. Source3643c97 CPU102 independent storage strict command state view and explicitnewassignment validated. Original389 fullsaved actual exits twoOSlocksfree canonicalidle sourcefreeze389 preserved; new402 isolated scope dispatched. SDK/native/PPO/formal actual stage gates, pending future results not claimed. First readerbuilder pre-review anchor literal rejected and repaired independently; noevalreplay. Complete134/newscope centralCAS synced masterapprovaltracksRMcanonical unchanged. Allsaved reports source errors indexed; large originals actualpathsizeSHA only; no newbudget or oldonce replay.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:save('STAGE_RECORD_ERROR.json',dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,may_have_committed_do_not_repeat_record=True));raise RuntimeError('Continue original Git objects after inspection')
 tag,commit=run.stdout.strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,v in tags.items():assert remote[t]==v['object'] and remote.get(t+'^{}',v['peeled'])==v['peeled']
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked and not g('status','--porcelain')
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 result=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('STAGE_GIT_RECORDED.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ARCHIVE_ERROR.json',dict(error=traceback.format_exc(),do_not_replay_record_or_tag=True));raise
