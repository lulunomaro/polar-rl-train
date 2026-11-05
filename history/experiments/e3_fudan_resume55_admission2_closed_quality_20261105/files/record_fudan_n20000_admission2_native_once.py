"""One meaningful actual N20000 native stage archive; never replay after record/push."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_n20000_admission2_native_20261104');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70' and not G('status','--porcelain') and not dest.exists()
G('merge-base','--is-ancestor','ebf1ecf8370e7ce2541b9b2747a6fb5f07af32f1','HEAD')
release=json.loads((D/'FDN_AFTER_N20000_W4_ORIGINAL_AUTHORITY_WATCH_RESULT.json').read_bytes());assert release['returncode']==0;released=release['events'][-1];assert released['event']=='FINAL' and released['status']=='ORIGINAL_CANONICAL_OWNER_NONE_OBSERVED' and released['owner']is None and released['read_only']is True
ad=json.loads(Path(json.loads((D/'FDN_N20000_W5_FIRST_ADMISSION_PATH.json').read_bytes())['path']).read_bytes());assert ad['actual_root_admission']['actual_original_authority_EX_private_GPU_EX_finite_SH'] is True and ad['owner_current']['training_num_envs']==20000
out=Path(json.loads((D/'FDN_N20000_W5_COLLECTOR_ONCE.json').read_bytes())['output']);snap=json.loads((out/'LATEST_METADATA_SNAPSHOT.json').read_bytes());assert snap['root']==ad['root']
up=snap.get('native_update') or {};w=up.get('window_counters') or {};u=w.get('updates',0)
positive=type(u)is int and u>0 and up.get('rollout_N')==20000 and w.get('policy_optimizer_steps')==20*u and w.get('encoder_optimizer_steps')==20*u and w.get('transitions_seen')==960000*u
actual_closed_failure=False
if (out/'CLOSED_RESULT.json').exists():
 c=json.loads((out/'CLOSED_RESULT.json').read_bytes());m=c['metadata'];ex=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert c['closed'] and outer['original_owner_reaped'] and all(ex[k]for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
 actual_closed_failure=bool(ex.get('errors') or m.get('FDN_NATIVE_ERROR.json') or m.get('FDN_SAVE_ERROR.json') or m.get('FDN_FINAL_METADATA_ERROR.json'))
assert positive or actual_closed_failure,'Archive after genuine positive N20000 optimizer evidence or actual closed failure, not a healthy status-only trial'
# The parent runs this only after the one delegated source file has been delivered.
assert(D/'stage_fudan_n20000_frozen_original_once.py').is_file()
note=(D/'CURRENT_PROGRESS_V10_N20000_NATIVE_WINDOW_TRUTH.md').read_text(encoding='utf8');dest.mkdir(parents=True);files=[];rows=[]
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png','.jpg','.jpeg','.webp','.usd','.usda','.usdc','.zip','.mp4','.xml','.stl','.obj','.ply','.dae','.mesh','.pyc','.pyo','.tmp'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO or p.name=='RESULT.json':row['status']='weight_geometry_image_video_raw_or_transient_reference_only_skipped_before_stat_read_hash';rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();target=dest/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rp=target.relative_to(repo).as_posix();files.append(rp);row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=rp);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_current_text_reports_snapshot=True,dynamic_metadata_only_point_in_time=True,models_raw_images_video_geometry_not_opened_for_Git=True,physical_or_once_replay_for_Git=False,main_push_or_reset=False),indent=2),encoding='utf8')
(dest/'.gitattributes').write_text('* -text\n',encoding='utf8')
(dest/'NOTE.md').write_text(note+'\n\n## Archive scope\nActual N20000 Admission2 after W4 zero-GO timeout and original canonical owner release. Original resource gates, authority/private/finite locks, canonical accounting and finite lifecycle remain unchanged. The 4096 source has 64 optimized updates and 38 unoptimized pending controls; new N20000 transitions are computed from the positive current window only. This captures all new sources, static errors, failures and point-in-time own metadata. H1, Registryv12 and frozen mothers are unchanged. Counts, admission, initialization and CPU/static checks are not independent skill success. Models, media and raw binaries are skipped before stat/read/hash. Already-archived earlier demo artifacts remain in the earlier trial rather than being physically reopened. Later real closure/quality reports require a later meaningful stage, never replay of this script.\n',encoding='utf8')
files.extend((rel/n).as_posix()for n in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
trial_id='e3-fudan-n20000-admission2-native';sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 Fudan actual N20000 learner-continuation window with original lifecycle and quality boundaries','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','E3-only;user-N20000-T48;actual-original-GO-not-queued-only;4k64-base-separate-positive-20k-window;bothAdam-and-transition-arithmetic;fresh-DR-history-stream-cut;whole-CPU-source-cache-once;original-resource-locks-canonical-charge-close-inner-outer-wait;original-74-scope-no-benchmark-weakening;all-static-and-native-errors-preserved;H1-mothers-frozen;no-model-raw-stat-read-hash-forGit;feature-only-main-read-only','--files',*files];record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag' and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(x.split()for x in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,main_push_or_reset=False,physical_or_once_replay_for_Git=False,source_entries=len(rows)),indent=2))
