"""Record this one requested startup test. Never open weights or trajectories for Git."""
from pathlib import Path
import sys,json,time,hashlib,subprocess,ctypes
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v1_e3_rear_stowed_startup_20261104');dest=repo/rel
G=lambda *a:subprocess.run(['git','-C',str(repo),*a],check=True,capture_output=True,text=True,encoding='utf8').stdout.strip()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='cb5fddee0f1445c96c9c0bbe162de2b64b5651a6'and not G('status','--porcelain')and not dest.exists()
summary=json.loads((D/'SUMMARY.json').read_bytes());assert summary['model_SHA']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'and summary['cases']==2
snapshot=dict(epoch=time.time(),visible_at_sample=bool(ctypes.windll.user32.IsWindowVisible(8795156)),current_replay=json.loads((D/'CURRENT_REPLAY.json').read_bytes()),no_future_continuous_alive_claim=True);(D/'DISPLAY_VERIFIED_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2),encoding='utf8')
dest.mkdir(parents=True);rows=[];files=[]
for p in sorted(D.iterdir()):
 row={'source_path':str(p)}
 # RESULT contains per-control trajectories, so skip it before stat/read too.
 if p.name=='RESULT.json'or p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png'):
  row['status']='model_or_raw_binary_or_trajectory_reference_only_no_stat_read_hash_for_Git';rows.append(row);continue
 if not p.is_file():continue
 if p.name=='CURRENT_REPLAY.json':row['status']='live_status_reference_only_point_in_time_snapshot_archived';rows.append(row);continue
 raw=p.read_bytes();out=dest/'files'/p.name;out.parent.mkdir(exist_ok=True);out.write_bytes(raw);files.append(out.relative_to(repo).as_posix());row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=out.relative_to(repo).as_posix());rows.append(row)
old=D.parent/'mod4v1_e3_mujoco_view_20261104'/'CLOSED_V2.json'
if old.exists():
 raw=old.read_bytes();out=dest/'files'/'PREVIOUS_OWNED_VIEWER_CLOSED_V2.json';out.write_bytes(raw);files.append(out.relative_to(repo).as_posix());rows.append(dict(source_path=str(old),status='previous_owned_viewer_normal_context_close',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()))
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,weights_not_opened_for_Git=True,actual_trajectory_not_reopened_for_Git=True,main_push_or_reset=False),indent=2),encoding='utf8');(dest/'.gitattributes').write_text('* -text\n',encoding='utf8');note=(D/'STARTUP_TEST_RESULTS.md').read_text(encoding='utf8');(dest/'NOTE.md').write_text(note+'\nOne actual zero-torque control and one E3 physics rollout; current viewer replays the actual recorded test and opens no weights. Old side-fall viewer was identity-checked and closed via its WM_CLOSE after startup viewer was verified. No foreign process signals, training, native SDK, ledger or registry changes. Future live replay closure/log changes are pending ordinary follow-up, not grounds for another test.\n',encoding='utf8');files +=[(rel/x).as_posix()for x in('INDEX.json','.gitattributes','NOTE.md')]
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
sys.argv=['record_experiment.py','--id','mod4v1-e3-rear-stowed-startup-test','--title','Test current E3 rear-folded power-on standing and movement','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','same1cd43090-E3;two13s-local-MuJoCo-rollouts;rear-stowed-flat-closed-linkage-zero-velocity;rise-and-drive-observed;rollback0.8565m-explicit;zero-torque-control-tips36.9deg;actual-replay-not-live-policy;no-weights-or-trajectories-read-forGit;not-native-fullDR-or-hardware-graduation','--files',*files];record_experiment.main();head=G('rev-parse','HEAD');tag='trial-20261104-mod4v1-e3-rear-stowed-startup-test';obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag);remote={ref:sha for sha,ref in(x.split()for x in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain');print(json.dumps(dict(commit=head,tag=tag,remote=remote,main_push_or_reset=False,no_test_replayed_for_Git=True,visible_at_sample=snapshot['visible_at_sample']),indent=2))
