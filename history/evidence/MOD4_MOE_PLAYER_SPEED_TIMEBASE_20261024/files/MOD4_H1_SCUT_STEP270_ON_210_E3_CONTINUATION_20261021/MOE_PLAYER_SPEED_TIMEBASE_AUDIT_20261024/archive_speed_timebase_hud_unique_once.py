from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
S=Path(__file__).resolve().parent;R=S/'reports';T=S.parent;W=T.parent;P=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023';D=P/'player';G=W/'polar-rl-train';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';DEST=G/'history/evidence/MOD4_MOE_PLAYER_SPEED_TIMEBASE_20261024';ID='moe-player-wallclock-speed-hud';TAG='trial-20261024-'+ID;BASE='b4f48ead23ecbf764589d21c2c7ad25b0938b07a'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 proof=json.loads((R/'SPEED_TIMEBASE_SOURCE_AND_PURE_CPU_ACTUAL.json').read_bytes());assert proof['passed_source_AST_and_pure_clock_CPU'] and proof['no_local_policy_physics_rollout_or_launch']
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1431
 put(R/'UNIQUE_RECORD_STARTED_ACTUAL.json',dict(epoch=time.time(),base_HEAD=BASE,tag=TAG,no_training_host_query_or_budget_write=True))
 note='Human reports both target slider and actual HUD show1.5m/s while visual travel feels slow. Existing actual_vx is MuJoCo body-forward metres per simulation second; outer loop advances one100Hz control tick and only sleeps remaining real-time budget, with no catch-up when compute/render costs exceed10ms. Old snapshots include initial pause/reset and no active-wall telemetry, so they do not establish actual historical slowdown factor or profile physics versus inference. Latest retained coarse human packet is command0.744/actual-0.222 at sim9.74; it is not the reported earlier1.5 interval and is not an exact human replay. Added independent versioned speed-clock player entry retaining the collision candidate, original controls/physics block and10ms schedule. Top label identifies target command, lower HUD separates simulation-second actual velocity, rolling active wall/simulation ratio, horizontal path metres per active wall second, combined policy/control/physics time and viewer sync time. Pause/fault waiting clears clock baseline; reset clears window; bounded1Hz1200-packet timing log supports future human testing without policy/action/physics changes. Five pure CPU sequences verify real-time1.5, quarter-rate0.375 wall speed, pause exclusion, reset/teleport rebase and stationary motion. No local agent inference, physics rollout, native GUI launch, model export, remote test or training signal. Initial builder generated an extra closing parenthesis and failed AST before driver/entry creation; original source/error and V2 first-success correction preserved. Source formatting scope and last-packet limitations retained. Original player/collision entry, model/gate, XML/mesh, gains, timestep,100/50Hz and skill buttons unchanged. This is diagnostic instrumentation, not proof of local compute bottleneck, performance optimization or skill qualification.'
 for name in ('STAGE_NOTE.md','TAG_NOTE.txt'):(S/name).write_text(note+'\n','utf8')
 template=C/'append_current_clearance_v4_closed63_pair64_ordinary_once.py';old=template.read_text('utf8');assert 'len(tags.splitlines())==1431' in old;(R/'UNUSED_ORDINARY_TEMPLATE_BEFORE_SPEED_TAG_1432_BINDING.py').write_text(old,'utf8');new=old.replace('len(tags.splitlines())==1431','len(tags.splitlines())==1432');template.write_text(new,'utf8')
 put(R/'FUTURE_ORDINARY_1432_TAG_BINDING_ACTUAL.json',dict(epoch=time.time(),only_unused_ordinary_tag_count_changed=True,original_source_retained=True,template=str(template),old_SHA=H(old.encode()),new_SHA=H(new.encode()),not_executed=True))
 sys.path.insert(0,str(T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'));from capture_index_ordered_parts_v1 import read_capture_index
 prior=read_capture_index(G/'versions/20261020_two_linux_policy50_series/ninth_budget200h_closed63_pair64V2_20261024/COMPLETE_FILE_CAPTURE_INDEX.json',G);bySHA={x['SHA']:x for x in prior['entries'] if x.get('SHA') and x.get('archive')}
 sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 extras=[D/'player_wallclock_speed_v1.py',D/'drive_rm7v7_contact_speed_timebase_v2.py',P/'试玩速度计时诊断版.bat',P/'速度计时诊断版说明.md',D/'drive_rm7v7_contact_stable_candidate_v1.py',D/'rm7v7_contact_stable_candidate_v1.py',D/'sim_runtime.py',D/'rm7v7_moe_sim.py',D/'current_moe_sim.py',D/'runtime_config.json',D/'player_camera.py',P/'policy/manifest.json',template]
 selected=sorted({p for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts}|set(extras));DEST.mkdir(parents=True);entries=[];files=[];newfiles={}
 def add(p,raw):
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);rel=p.relative_to(G).as_posix();files.append(rel);newfiles[rel]=H(raw)
 for p in selected:
  raw=p.read_bytes();sha=H(raw);saved=bySHA.get(sha)
  if saved:entries.append(dict(path=str(p),bytes=len(raw),SHA=sha,archive=saved['archive'],archive_SHA=saved.get('archive_SHA',sha),mode=saved.get('mode','full'),capture='existing_complete_Git_SHA_reference'));continue
  clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8');assert len(data)<49_000_000;q=DEST/'files'/p.relative_to(W);add(q,data);row=dict(path=str(p),bytes=len(raw),SHA=sha,archive=q.relative_to(G).as_posix(),archive_SHA=H(data),mode='redacted' if n else 'full',redactions=n,original_retained=True);entries.append(row);bySHA[sha]=row
 manifest=json.loads((P/'policy/manifest.json').read_bytes());model=P/'policy/hybrid_moe.onnx';index=dict(epoch=time.time(),kind='passive_speed_timebase_HUD_no_rollout',entries=entries,artifacts=[dict(path=str(model),bytes=model.stat().st_size,SHA=manifest['onnx_SHA'],SHA_kind='existing producer manifest; not rehashed',original_retained=True)],prior_complete_index=prior['kind'],human_exact_1p5_interval_not_recorded=True,old_log_cannot_establish_active_realtime_factor=True,no_inference_physics_launch_remote_query_training_or_budget_change=True,original_errors_and_false_preserved=True)
 q=DEST/'REPORT_CAPTURE_INDEX.json';add(q,json.dumps(index,ensure_ascii=False,indent=2).encode())
 rec=importlib.import_module('record_experiment')
 def record_git(*args):
  if args[:2]==('add','--'):return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in args[2:])+b'\0')
  if args[:2]==('tag','-a'):assert args[2]==TAG;return git('tag','-a',TAG,'-F',str(S/'TAG_NOTE.txt'))
  if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*args)
 rec.git=record_git;sys.argv=['record_experiment.py','--id',ID,'--title','Separate simulation speed from wall-clock playback in versioned MoE HUD','--kind','repair','--note-file',str(S/'STAGE_NOTE.md'),'--files',*files,'--validation','Five pure clock CPU cases and source AST/critical block equality; no local policy/physics rollout or GUI launch.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for line in tags.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 for rel,sha in newfiles.items():assert H(subprocess.run(['git','-C',str(G),'show',head+':'+rel],capture_output=True,check=True).stdout)==sha
 assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1432
 print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=obj,peeled=head,total_tags=1432,all1431_old_objects_peels_unchanged=True,fulltext_references=len(entries),new_Git_files=len(files),all_new_blobs_verified=True,no_policy_physics_or_GUI_launch=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('UNIQUE_RECORD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
