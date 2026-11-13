"""Collect complete successful expert episodes after PPO closes; prepare data only, no new training."""
try:
 from pathlib import Path
 import sys,json,time,shlex,hashlib
 import torch
 S=Path(__file__).resolve().parents[1];N=S/'next_full_episode';T=S.parent/'MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113';sys.path.insert(0,str(S));from remote_run import connect,execute,P,REMOTE
 teacher_root=json.loads((T/'PLAN.json').read_text())['root'];out=REMOTE+'/native_teacher_full_episode_r1';E=S/'evidence/full_episode_native_r1';E.mkdir(exist_ok=False)
 c=connect()
 try:
  sf=c.open_sftp();sf.put(str(N/'native_teacher_full_episode.py'),REMOTE+'/native_teacher_full_episode.py')
  with sf.open(REMOTE+'/FULL_EPISODE_MODELS.json','w') as f:f.write(json.dumps({'parent':REMOTE+'/frozen_best_parent.pt','teacher':teacher_root+'/train040m_specialist_r1/model_final.pt'}))
  assert not execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip(),'PPO/evaluation GPU still active'
  cmd=[P['python'],'-B','-u',REMOTE+'/native_teacher_full_episode.py','--plan',REMOTE+'/PLAN.json','--support',teacher_root+'/support','--models',REMOTE+'/FULL_EPISODE_MODELS.json','--out',out]
  code="from pathlib import Path;import subprocess,os,json,time;root=Path("+repr(REMOTE)+");out=Path("+repr(out)+");assert not out.exists();env=dict(os.environ);env.update(CUDA_VISIBLE_DEVICES='0',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',XDG_CACHE_HOME=str(root/'cache'),WARP_CACHE_PATH=str(root/'cache/warp'),TMPDIR=str(root/'tmp'));log=(root/'full_episode_teacher_data.log').open('xb',buffering=0);child=subprocess.Popen("+repr(cmd)+",cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True);print(json.dumps(dict(pid=child.pid,epoch=time.time(),job=str(out))))"
  launch=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));(E/'LAUNCH.json').write_text(json.dumps(launch,indent=2)+'\n');print('FULL_EPISODE_NATIVE_STARTED '+str(launch['pid']),flush=True)
 finally:c.close()
 last=-1
 while True:
  c=connect()
  try:
   sf=c.open_sftp()
   try:names=[p.filename for p in sf.listdir_attr(out)]
   except FileNotFoundError:names=[]
   for name in ['PROGRESS.json','ERROR.json','SAFE_CLOSED.json']:
    if name in names:sf.get(out+'/'+name,str(E/name))
   if (E/'PROGRESS.json').exists():
    j=json.loads((E/'PROGRESS.json').read_text());step=j.get('step',0)
    if step!=last:last=step;print('FULL_EPISODE_NATIVE_PROGRESS '+str(step),flush=True)
   closed='SAFE_CLOSED.json' in names
   if closed:
    for name in names:
     if name.endswith(('.json','.npz','.pt')):sf.get(out+'/'+name,str(E/name))
    sf.get(REMOTE+'/full_episode_teacher_data.log',str(E/'stdout.log'));closed=not execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip()
   if closed:
    assert not (E/'ERROR.json').exists(),'Full-episode native collector failed; preserve evidence';break
  finally:c.close()
  time.sleep(10)
 mu=S/'evidence/full_episode_mujoco_r1/success_demos.pt';assert mu.is_file(),'Full successfulMuJoCo collection must finish first'
 parts=[torch.load(E/'teacher_success_full_episode_demos.pt',map_location='cpu',weights_only=False),torch.load(mu,map_location='cpu',weights_only=False)];sha=P['teacher_retention']['stair_teacher_sha256'];assert all(d['metadata']['teacher_sha256']==sha for d in parts)
 x=torch.cat([d['policy'] for d in parts]);y=torch.cat([d['actions'] for d in parts]);assert x.shape[1]==35 and y.shape==(len(x),6) and bool(torch.isfinite(x).all()) and bool(torch.isfinite(y).all())
 meta=dict(teacher_sha256=sha,retains_initial_preparation=True,first_recorded_endpoint=0,observations=len(x),native_frames=len(parts[0]['policy']),mujoco_frames=len(parts[1]['policy']),native_successful_full=parts[0]['metadata']['native_successful_full'],mujoco_successful_full=parts[1]['metadata']['successful_full_episodes'],policy_dim=35,action_dim=6,only_complete_two_step_success=True,same_movement_onset3s=True,current_student_training_not_modified=True,no_new_training=True,source_metadata=[d['metadata'] for d in parts])
 output=N/'successful_teacher_full_episode_demos.pt';torch.save(dict(policy=x.float(),actions=y.float(),phase=torch.cat([d['phase'] for d in parts]),env_id=torch.cat([d['env_id'] for d in parts]),endpoint=torch.cat([d['endpoint'] for d in parts]),source_engine=torch.cat([torch.full((len(d['policy']),),i,dtype=torch.long) for i,d in enumerate(parts)]),metadata=meta),output)
 data_sha=hashlib.sha256(output.read_bytes()).hexdigest();nextplan=json.loads((S/'PLAN.json').read_text());nextroot=REMOTE.removesuffix('_r1')+'_full_episode_r2';nextplan.update(root=nextroot,phase='PREPARED_NOT_STARTED_full_successful_episode_guidance',source_experiment='Only fix complete-success demonstration coverage; current40m outcome preserved');nextplan['teacher_retention'].update(dataset=nextroot+'/teacher_success_full_episode_demos.pt',dataset_sha256=data_sha);nextplan['specialist_transfer']['teacher_data']={'sha256':data_sha,'frames':len(x),'successful_whole_episodes':meta['native_successful_full']+meta['mujoco_successful_full'],'native_frames':meta['native_frames'],'MuJoCo_frames':meta['mujoco_frames'],'includes_preparation_from_endpoint0':True};nextplan['teacher_retention']['stair_domain']='Complete verified successful frozen-teacher first episodes from endpoint0, including height raise/preparation; no failed or mid-start data';nextplan['next_recipe']={'status':'prepared, not launched','only_change':'Complete successful demonstrations from endpoint0 instead of>=3s; no reward/DR/PPO/asset/controller change','parent_sha256':P['parent_sha256'],'support_reused_from_frozen_current_recipe':P['support'],'dataset_file':str(output),'dataset_sha256':data_sha,'teacher_native_fullDR_still_not_graduated':True}
 (N/'PLAN_NEXT_NOT_STARTED.json').write_text(json.dumps(nextplan,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(N/'DATA_COMPLETE.json').write_text(json.dumps(dict(meta,dataset_sha256=data_sha,bytes=output.stat().st_size),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('FULL_EPISODE_DATA_PREPARED_NO_TRAINING '+json.dumps(dict(frames=len(x),native=meta['native_frames'],MuJoCo=meta['mujoco_frames'],sha256=data_sha)),flush=True)
except BaseException:
 import traceback
 from pathlib import Path
 import json,time
 (Path(__file__).resolve().parent/'DATA_PREPARATION_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n')
 raise
