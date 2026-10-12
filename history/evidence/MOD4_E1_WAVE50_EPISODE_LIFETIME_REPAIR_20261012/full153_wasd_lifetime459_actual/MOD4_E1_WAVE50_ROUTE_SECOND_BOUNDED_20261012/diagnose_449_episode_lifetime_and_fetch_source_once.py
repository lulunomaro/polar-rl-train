from pathlib import Path
import sys,os,json,time,hashlib,shlex,traceback
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_LOCAL_WASD_WAVE50_70_20261012'))
from build_linux_only_continuation_once import connect_linux_only
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(name,v):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
CODE=r'''
from pathlib import Path
import json,hashlib,numpy as np,torch,shutil,time,os
torch.set_num_threads(1)
D=Path(ROOT_TOKEN);v=json.loads(OWN_TOKEN);p=Path(v['own_checkpoint']['path']);run=p.parent
assert hashlib.sha256(p.read_bytes()).hexdigest()==v['own_checkpoint']['sha256'];ck=torch.load(p,map_location='cpu',weights_only=False)
recipe=json.loads((run/'RETENTION_COMMAND_ACTUAL.json').read_bytes());m=json.loads((run/'run_manifest.json').read_bytes())
total=0;ends=[];ids=None;spawn=None;steps=None;integral=None;net=None;stand=None;episode_index=None;fully_seen=None
for name in recipe['trace_files']:
 with np.load(run/name) as z:
  x=z['rows'];assert np.isfinite(x).all() and x.shape[1:]==(20000,16)
  if ids is None:
   ids=np.flatnonzero(x[0,:,10]==4);assert len(ids)==2820
   spawn=x[0,ids,:2].astype('float64');steps=np.zeros(len(ids),np.int64);integral=np.zeros(len(ids));net=np.zeros(len(ids));stand=np.zeros(len(ids),np.int64);episode_index=np.zeros(len(ids),np.int64);fully_seen=np.ones(len(ids),bool)
  for row in x[:,ids,:]:
   steps+=1;integral+=abs(row[:,7])*.01;net+=row[:,3]-row[:,0];stand+=(row[:,7]==0)
   ended=(row[:,14]!=0)|(row[:,15]!=0)
   for i in np.flatnonzero(ended):
    # Immutable initial grid, 9m cell centre; reset-entry physical spawn is outside the profile.
    centre=np.floor(spawn[i,0]/9.)*9.+4.5;side=np.sign(spawn[i,0]-centre);toward=-side
    delta=row[i,3:5]-spawn[i];inward=delta[0]*toward
    boundary=(inward>4.)or(inward < -2.)or(abs(delta[1])>2.)
    ends.append(dict(env=int(ids[i]),observed_prefix=int(steps[i]),episode_index=int(episode_index[i]),fully_seen=bool(fully_seen[i]),terminated=bool(row[i,14]),truncated=bool(row[i,15]),stand_controls=int(stand[i]),absolute_command_integral_m=float(integral[i]),signed_toward_root_delta_m=float(inward),root_spawn_xy=spawn[i].tolist(),root_final_xy=row[i,3:5].tolist(),heading_final_before=float(row[i,6]),route_predicate_at_end=bool(boundary),root_center_past_wave_end=bool((row[i,3]-centre)*toward>2.406422727/2.),time_out_candidate=bool(row[i,15] and not boundary),first_prefix_may_have_startup_episode_age=True))
    fully_seen[i]=True;episode_index[i]+=1;steps[i]=0;integral[i]=0;net[i]=0;stand[i]=0
   # Exact next before-physics pose is the only valid new physical episode spawn.
   if ended.any():spawn[ended]=np.nan
   missing=np.isnan(spawn[:,0])
   # patched below: next row refresh before its computations
  total+=len(x)
assert total==2136 and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,checkpoint_SHA=v['own_checkpoint']['sha256'],actual_controls=total,ended_prefixes=ends,maximum_recorded_full_prefix_seconds=max(e['observed_prefix'] for e in ends)*.01,actual_durable=shutil.disk_usage(D)._asdict(),memory_available_bytes=next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')),mounts=Path('/proc/mounts').read_text(),run_manifest=m,checkpoint_lifetime_existing_keys=[k for k in ck if 'life' in k.lower() or 'episode' in k.lower()],CPU_only=True,root_command_proxy_not_contact_or_causal_certificate=True)))
'''
# Reset spawn is sampled at the following before-physics row, including across NPZ files.
CODE=CODE.replace("   steps+=1;integral", "   missing=np.isnan(spawn[:,0]);spawn[missing]=row[missing,:2]\n   steps+=1;integral")
def main():
 assert not (R/'POST153_EPISODE_LIFETIME_CPU_ACTUAL.json').exists()
 own=json.loads(max(R.glob('RESOURCE449_INDEPENDENT_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert own['passed'] and own['closeout_ready']
 n,w=connect_linux_only()
 try:
  with n.open_sftp() as f:
   freeze=json.loads(f.open(ROOT+'/reports/SOURCE_FREEZE.json','rb').read());dest=D/'immutable449_source';assert not dest.exists();dest.mkdir();idx=[]
   for name,sha in freeze['sha256'].items():
    b=f.open(ROOT+'/'+name,'rb').read();assert hashlib.sha256(b).hexdigest()==sha;p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);idx.append(dict(path=str(p.resolve()),remote_path=ROOT+'/'+name,bytes=len(b),sha256=sha))
   save('SOURCE449_IMMUTABLE_LOCAL_FETCH_ACTUAL.json',dict(epoch=time.time(),passed=True,source_count=len(idx),indices=idx,no_GPU_or_replay=True))
  code=CODE.replace('ROOT_TOKEN',repr(ROOT)).replace('OWN_TOKEN',repr(json.dumps(own)))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=240);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('LIFETIME_DIAGNOSIS_REMOTE_ERROR_'+str(time.time_ns())+'.json',dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')));raise RuntimeError('CPU observer failed, original retained')
  v=json.loads(raw);save('POST153_EPISODE_LIFETIME_CPU_ACTUAL.json',v)
  ends=v['ended_prefixes'];print(json.dumps(dict(passed=v['passed'],prefix_count=len(ends),max_seconds=v['maximum_recorded_full_prefix_seconds'],prefix_length_counts={str(k):sum(x['observed_prefix']==k for x in ends) for k in sorted(set(x['observed_prefix'] for x in ends)) if k>=1500},durable=v['actual_durable'],time_out_candidates=sum(x['time_out_candidate'] for x in ends))))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:save('LIFETIME_DIAGNOSIS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
