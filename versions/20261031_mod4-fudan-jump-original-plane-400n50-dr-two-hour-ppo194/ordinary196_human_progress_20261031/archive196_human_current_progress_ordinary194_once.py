"""Append one expressly requested saved-progress status, no extra model or GPU access."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess,sys,time
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
D=G/'versions/20261031_mod4-fudan-jump-original-plane-400n50-dr-two-hour-ppo194/ordinary196_human_progress_20261031'
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return dict(line.split()[::-1] for line in s.splitlines() if line.strip())
assert not git('status','--porcelain') and not D.exists()
v=json.loads((R/'ROOT196_194_ONE_CURRENT_SAVED_PROGRESS_RETURNED_ACTUAL.json').read_bytes())
assert v['authority']['passed'] and v['authority']['active194_at_this_read']
closed=json.loads((R/'ROOT196_STATUS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json').read_bytes());assert closed['global_serial_lease']=='FREE'
row=next(x for x in v['source210']['files'] if x['path'].endswith('LATEST_PROGRESS.json'));p=row['value'];d=p['original_jump_diagnostic']
summary=dict(epoch=time.time(),source_epoch=p['epoch'],source_BJT=datetime.fromtimestamp(p['epoch'],timezone(timedelta(hours=8))).isoformat(),
 actual_source_model_generation='194 learning window; current saved progress, no checkpoint read',
 actual_new_PPO_updates=p['new_PPO_updates'],own_environment_control_transitions=p['new_environment_transitions'],
 completed_controls=d['completed_controls'],Fudan_contact_flight_environment_controls=d['flight_environment_controls'],
 maximum_root_world_height_m=d['maximum_root_height_m'],terminations_cumulative=d['terminations'],
 successful_jump_and_stable_landing='NOT_MEASURED by this progress producer',
 flight_count_is_not_unique_env_episode_or_success_count=True,root_height_is_not_jump_height_or_wheel_clearance=True,
 source64_or_first_snapshot_not_replayed=True,one_new_progress_small_JSON_read=True,model_raw_NPZ_SDK_GPU_reads=0,
 existing194_training_and195_pending_source_unchanged=True,normal_time_unchanged='20:41 earliest /20:51 save /20:56 nominal exit')
with (R/'CURRENT194_ONE_HUMAN196_PROGRESS_SNAPSHOT_NO_SKILL_CLAIM.json').open('x',encoding='utf8') as f:json.dump(summary,f,indent=2)
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1500 and all(remote.get(k)==x for k,x in old.items())
with (R/'ARCHIVE196_ORDINARY194_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),ordinary_append=True,old1500_tags_protected=True,no_new_tag_or_experiment_record=True),f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
D.mkdir();files=[N/'human196_194_one_saved_progress_status_once.py',Path(__file__).resolve()]
files+=sorted(p for p in R.glob('*196*') if p.is_file())
rows=[];selected=[]
for source in files:
 raw=source.read_bytes();text=raw.decode('utf8');assert redact(text)[0]==text,str(source)
 rel=source.relative_to(N);dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 rows.append(dict(path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'));selected.append(dest.relative_to(G).as_posix())
index=D/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase='ordinary194-human-current-progress196',files=rows,
 human_request='现在有成功跳跃的迹象吗',unmodified_training=True,one_remote_saved_progress_read=True,source72_small_JSON_reads=3,source210_small_JSON_reads=v['source210']['small_JSON_reads'],
 model_raw_NPZ_SDK_GPU_calls=0,success_claim=False,no_second_watcher_or_early_normal=True),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
git('add','--',*selected);git('commit','-m','Append human-requested current JUMP194 saved progress196 without a skill claim');git('push','origin','HEAD')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==x and remote.get(k)==x for k,x in old.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,ordinary_append=True,protected1500_tags_objects_peels=True,source_BJT=summary['source_BJT'],actual_new_updates=p['new_PPO_updates'],new_skill_claim=False,clean=True)))
