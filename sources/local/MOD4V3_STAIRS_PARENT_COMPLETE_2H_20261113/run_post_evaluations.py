"""Post-round frozen paired native evaluations; no training or demo recollection."""
from pathlib import Path
import sys,json,subprocess,time,shlex,hashlib,os
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());source=selected['source_file'];teacher_root=json.loads((T.parent/'MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113/PLAN.json').read_text())['root']
models={'parent':REMOTE+'/frozen_best_parent.pt','student':REMOTE+'/train120m_parent_r1/'+source};E=T/'evidence/post_native';E.mkdir(exist_ok=False)
c=connect()
try:
 sf=c.open_sftp();assert sf.stat(REMOTE+'/train120m_parent_r1/SAFE_CLOSED.json')
 assert execute(c,'sha256sum -- '+shlex.quote(models['student'])).split()[0]==selected['sha256']
 for name in ['native_student_pair.py','rough_retention_replay.py']:sf.put(str(T/name),REMOTE+'/'+name)
 try:sf.mkdir(REMOTE+'/retention_eval_terrain')
 except OSError:pass
 for f in (T/'retention_eval_terrain').glob('*'):
  if f.is_file():sf.put(str(f),REMOTE+'/retention_eval_terrain/'+f.name)
 with sf.open(REMOTE+'/POST_MODELS.json','w') as f:f.write(json.dumps(models))
finally:c.close()
jobs=[('stairs', [P['python'],'-B','-u',REMOTE+'/native_student_pair.py','--plan',REMOTE+'/PLAN.json','--support',REMOTE+'/support','--models',REMOTE+'/POST_MODELS.json','--out',REMOTE+'/native_student_pair_r1'])]
for skill in ['traverse','gyro','landing']:
 jobs.append(('retained_'+skill,[P['python'],'-B','-u',REMOTE+'/rough_retention_replay.py','--plan',REMOTE+'/PLAN.json','--support',REMOTE+'/support','--models',REMOTE+'/POST_MODELS.json','--out',REMOTE+'/native_retained_'+skill+'_l9_r1','--version','specialist_student_parentdb6','--level','9','--skill',skill]))
records=[]
for label,cmd in jobs:
 out=cmd[cmd.index('--out')+1];local=E/label;local.mkdir();c=connect()
 try:
  busy=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip();assert not busy,'Another compute owner still running:'+busy
  code="from pathlib import Path;import subprocess,os,json,time;root=Path("+repr(REMOTE)+");out=Path("+repr(out)+");assert not out.exists();env=dict(os.environ);env.update(CUDA_VISIBLE_DEVICES='0',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',XDG_CACHE_HOME=str(root/'cache'),WARP_CACHE_PATH=str(root/'cache/warp'),TMPDIR=str(root/'tmp'));log=(root/"+repr('post_'+label+'.log')+").open('xb',buffering=0);child=subprocess.Popen("+repr(cmd)+",cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True);print(json.dumps(dict(pid=child.pid,epoch=time.time(),job=str(out))))"
  receipt=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));(local/'LAUNCH.json').write_text(json.dumps(receipt,indent=2)+'\n');print('POST_NATIVE_STARTED '+label+' '+str(receipt['pid']),flush=True)
 finally:c.close()
 last_step=-1
 while True:
  c=connect()
  try:
   sf=c.open_sftp()
   try:names=[p.filename for p in sf.listdir_attr(out)]
   except FileNotFoundError:names=[]
   closed='SAFE_CLOSED.json' in names
   for name in ['PROGRESS.json','ERROR.json','SAFE_CLOSED.json']:
    if name in names:sf.get(out+'/'+name,str(local/name))
   if (local/'PROGRESS.json').exists():
    progress=json.loads((local/'PROGRESS.json').read_text());step=progress.get('step',0)
    if step!=last_step:last_step=step;print('POST_NATIVE_PROGRESS '+label+' '+json.dumps(progress),flush=True)
   if closed:
    for name in names:
     if name.endswith(('.json','.npz','.pt')):sf.get(out+'/'+name,str(local/name))
    sf.get(REMOTE+'/post_'+label+'.log',str(local/'stdout.log'))
    # app.close may take a moment after writing the safe-close marker.
    owner=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip()
    if owner:closed=False
   if closed:
    if (local/'ERROR.json').exists():raise RuntimeError('Native '+label+' failed; see preservedERROR.json')
    assert (local/'RESULT.json').exists();records.append(dict(label=label,remote=out,result=str(local/'RESULT.json')));break
  finally:c.close()
  time.sleep(10)
 (E/'STATUS.json').write_text(json.dumps(dict(completed=records,pending=[j[0] for j in jobs if j[0] not in [r['label'] for r in records]]),indent=2)+'\n')
 print('POST_NATIVE_COMPLETE '+label,flush=True)
(E/'COMPLETE.json').write_text(json.dumps(dict(completed=records,selected=selected,all_closed=True),indent=2)+'\n');print('ALL_POST_NATIVE_COMPLETE',flush=True)
