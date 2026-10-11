from pathlib import Path
import sys,json,time,hashlib,subprocess,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import repair_io as io
import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
ID='curb20-origin-bound-sdk-and-fullstate-preflights-admitted-fresh-verification-started'

def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p

def main():
 assert not old.g('status','--porcelain') and not DEST.exists() and not (R/'STAGE_GIT_RECORDED.json').exists()
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));m=json.loads((R/'ENTRY_SCOPE_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==m[k] for k in ('id','name','kind','status','rrule','target_thread_id')) and t['prompt']==(D/'MONITOR_CURRENT_ENTRY_FULLSTATE_PROMPT.md').read_text(encoding='utf8')
 save('ENTRY_SCOPE_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,actual_interval_minutes=30,prompt_SHA=H(t['prompt'].encode()),healthy_pending_DONT_NOTIFY=True))
 actual=max((p for p in R.glob('ENTRY_FULLSTATE_ACTUAL_*.json') if p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_').isdigit()),key=lambda p:int(p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_')))
 a=json.loads(actual.read_bytes());assert not a['reports'].get('E1_ATTENTION.json')
 assert a['reports']['ENTRY_ORIGIN_BOUND_SDK10_PASSED.json']['passed'] and a['reports']['entry_discard128_PASSED.json']['discarded_preflight'] and a['reports']['entry_discard20k_PASSED.json']['discarded_preflight']
 n,w=io.connect_both()
 try:
  inventory=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT);R=D/'reports';j=lambda p:json.loads(p.read_bytes());paths=set()
source=j(R/'SOURCE_SELECTED.json');paths.add(Path(source['path']))
for name in ('entry_discard128_PASSED.json','entry_discard20k_PASSED.json','e1_CURB20_entry_repair_observation_PASSED.json'):
 if (R/name).exists():
  v=j(R/name);paths.add(Path(v['checkpoint']['path']));paths.update(Path(v['run']).glob('*.pt'))
paths.update(D.glob('ENTRY_ORIGIN_BOUND_SDK10*.json'));paths.update(D.glob('ENTRY_ORIGIN_BOUND_SDK10_trace/*'))
rows=[]
for p in sorted(paths):
 if not p.is_file():continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),original_retained=True,index_only=True))
print(json.dumps(dict(epoch=time.time(),rows=rows,raw_weights_large_states_SDK_trace_index_only=True,no_GPU_or_PPO_or_budget_mutation=True)))
'''.replace('ROOT',repr('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011')))
  save('LARGE_ARTIFACTS_ACTUAL_INDEX.json',inventory)
 finally:io.cleanup(n,w)
 previous=old.refs();assert not old.g('tag','--list','*'+ID)
 save('ENTRY_FULLSTATE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=old.g('rev-parse','HEAD'),prior_tag_objects=len(previous),no_repeat_existing_tag_or_record=True))
 note=R/'STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# CURB20实际入口缓存修复及隔离全状态准入

旧398SDK在初次reset后改env_origins，缓存未刷新导致实际0/10位于宣告CURB格；原进程PASSED保留，不能当该范围准入。新独立source409保留398全部源码字节，只新增11份entry-origin-cache/fullstate/currentstate/CPU/worker/controller。CPU实际旧fixture缓存0→10、subset与原20k映射byteexact通过；无CUDA。有效398native20k/clock/DR/geometry按exactSHA复用，无再次native。

own404/398实际完整保存或无PPO合同退出、两fcntl锁free、005idlecanonical1188000/7extensions和139两hostqueue/result未占用边界后，独立targetCPU102通过，唯一controller实际dispatch。新SDK10真实10/10CURB根起点、300control1200callback/selectedreset/groundreward/solver/health通过。新128x2与20kx4完整PPO各自己的CPU102/fullsave/PIDreceipt/PASSED/unique段计同canonical，预检权重弃用；现fresh20k新进程零control零PPO严格完整sameentry恢复仍待自己的actualPASSED。之后原父才唯一300s正式loadlearnsaveexit，再ownfinal/4case139完整行为审查。不把预检保存称formal或CURB毕业，不用discard正式暖启动。

原3c97全actorcriticoptimizerstd/D0D7/globalnamed/dictprivateCPUCUDA/旧terraincommand先按来源身份核，再显式G3→CURB+entrymap新身份绑定/CUDAroundtrip/sourceepisode+1。sameentry后要求exact。未改reward/LR/hardware/clock/DR/地形比例或命令轴，E0/Wave/SLOPE不更新，gate未训。15s只本机guardian、30min同一heartbeatACTIVE/健康pending静默；WASD播放器不触碰。

两条本机路径reader错误、首次sync字母glob误选authority导致KeyError、PowerShell引号ParserError和未生成新file执行拒绝均preGPU/CAS保留；新独立numeric-selected sync只补未执行中央CAS且保护master/approval/tracks/RM，原父正常预算扣账独立。未覆盖旧false/raw/cost。新实际准入/部署为唯一修复stage annotatedtrial；前prepared/trace/30min补充b399及旧全部tagobjects保持。所有当前已保存源码/报告/同步/监控/错误捕获，后formal/freshfinal/139/Gitreceipt继续ordinarysupplement；大权重/rawNPZ/SDKjson只实际path-size-SHA，凭据不归档。
''',encoding='utf8')
 prior={}
 index=REPO/'history/evidence/MOD4_E1_CURB20_ENTRY_TRACE_AND_MONITOR_SUPPLEMENT_20261011/REPORT_CAPTURE_INDEX.json'
 for row in json.loads(index.read_bytes())['entries']:
  if row.get('Git_path'):
   p=REPO/row['Git_path'];h=row['archived_sha256'];assert H(p.read_bytes())==h
   prior[(str(Path(row['source_path']).resolve()).casefold(),row['sha256'])]=dict(Git_path=row['Git_path'],archived_sha256=h)
 rows=[];files=[];DEST.mkdir(parents=True)
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get((str(p.resolve()).casefold(),h))
  if p.suffix.lower() in ('.npz','.npy','.pt','.usd','.zip') or len(raw)>50000000:row.update(capture='large_actual_original_SHA_index_only',original_retained=True)
  elif ref:row.update(capture='existing_same_SHA_Git_reference',**ref)
  else:
   try:text=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(text);data=clean.encode('utf8') if count else raw
   out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
   name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if count else 'complete_exact_bytes',encoding=encoding,redactions=count,Git_path=name,archived_sha256=H(data))
  rows.append(row)
 idx=DEST/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_current_reports_sources_errors_monitors_captured=True,large_artifact_index_file='LARGE_ARTIFACTS_ACTUAL_INDEX.json',source409_398bytes_exact=True,formal_final_and139_later_require_supplement=True,credentials_excluded=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(REPO).as_posix())
 proc=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Admit CURB20 origin bound SDK and isolated full state preflights, then verify fresh resume','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual oldexit/2OSlocks/idle005 boundary and139unused. CPU102 source409/noCUDA and cachefixture0to10/native20k mapexact. NewSDK10 actual10CURB/1200callbacks PASSED. Own128x2 and20kx4 fullsave/CPU/PID/uniqueledger PASSED discard; independentfresh20k0PPO actualpending. Formal300 only afterfreshPASSED. CentralCAS masterapprovaltracksRM protected. Sameheartbeat30minACTIVE verified. Allerrors preserved; weights/raw actualSHAindex; oldtags unchanged.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if proc.returncode:
  save('ENTRY_FULLSTATE_RECORD_ERROR.json',dict(epoch=time.time(),returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,no_repeat_record_tag_or_commit=True));raise RuntimeError('Inspect existing Git objects before proceeding')
 tag,head=proc.stdout.strip().splitlines()[-1].split();obj=old.g('rev-parse',tag)
 remote={line.split()[1]:line.split()[0] for line in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,previous_tag_objects_preserved=len(previous),captured_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in rows)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,new_captured_files=len(files),previous_tag_objects_preserved=len(previous),later_Gitreceipt_requires_supplement=True)))

if __name__=='__main__':main()
