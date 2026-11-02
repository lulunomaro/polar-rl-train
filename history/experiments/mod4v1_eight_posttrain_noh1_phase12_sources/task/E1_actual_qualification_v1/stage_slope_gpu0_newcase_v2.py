"""Newunused GPU0case after actual ownGPU1metadatawaiter cancellation. No PTread."""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2';UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842'

def main():
 transition=json.loads((B/'SLOPE135_GPU0_PERMISSION_TRANSITION_METADATA.json').read_bytes())['actual'];assert transition['own_metadata_waiter_cancelled'] and transition['no_SDK_token_or_child_at_frozen_cancel'] and transition['own_process_waited'] and transition['new_GPU0_identity_only']['UUID']==UUID
 assert not (B/'SLOPE135_CURRENT_FRESH80_GPU0_V2.json').exists();source=transition['own_root'];stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_E1_SLOPE135_GPU0_FRESH80_'+stamp
 s=(B/'supervise_e1_actual_bounded_v1.py').read_text(encoding='utf-8');s=s.replace("plan['GPU_index']==1","plan['GPU_index']==0",1).replace("assert uuid=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","assert uuid=='"+UUID+"'",1);compile(s,'GPU0scopedsupervisor','exec');supervisor=B/'supervise_e1_actual_gpu0_bounded_v2.py'
 with supervisor.open('x',encoding='utf-8') as f:f.write(s)
 code="""from pathlib import Path
import hashlib,json
S=Path(%r);B=Path(%r);assert not B.exists();cancel=json.loads((S/'OWN_METADATA_WAIT_CANCELLED_FOR_NEW_GPU0_PERMISSION.json').read_bytes());assert cancel['own_metadata_waiter_cancelled'] and cancel['no_SDK_token_or_child_at_frozen_cancel'] and cancel['own_process_waited'];assert not (S/'SDK_DISPATCH_ONCE.json').exists() and not (S/'CHILDREN.json').exists()
old=json.loads((S/'E1_ACTUAL_PLAN.json').read_bytes());rows=[];B.mkdir()
for r in old['files']:
 rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors'}
 if str(rel)=='supervise_e1_actual.py':continue
 raw=(S/rel).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
 rows.append(r)
(B/'GPU0_NEW_NONPT_STAGE_INDEX.json').write_text(json.dumps({'files':rows,'oldGPU1case_not_hotpatched':True,'oldGPU1SDKdispatched':False,'PT_reads':0},indent=2))
print(json.dumps({'root':str(B),'files':len(rows),'source_PT_reads':0}))
"""%(source,root)
 report=dict(kind='SLOPE135_NEW_GPU0_FRESH80_UNUSEDCASE_V2',remote_root=root,old_cancelled_root=source,GPU_UUID=UUID,sourcePT_reads=0);client=sf=None
 try:
  client=connect72();i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0
  sf=client.open_sftp()
  with sf.open(root+'/GPU0_NEW_NONPT_STAGE_INDEX.json','r') as f:rows=json.load(f)['files']
  sf.put(str(supervisor),root+'/supervise_e1_actual.py');raw=supervisor.read_bytes();rows.append(dict(relative='supervise_e1_actual.py',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),local_dependency_path=str(supervisor)))
  plan=dict(kind='E1_CANONICAL_GPU0_BOUNDED_VALIDATION_PLAN_V2',canonical='SLOPE135',mode='fresh80',GPU_index=0,GPU_UUID=UUID,controls=24,worker='worker_fresh80_noPT.py',complete_basename='E1_FRESH80_COMPLETE.json',error_basename='E1_FRESH80_ORIGINAL_ERROR.json',files=rows,task=dict(kind='E1_CANONICAL_ACTUAL_FRESH80_NO_PT_V1',canonical='SLOPE135',num_envs=80,controls=24,parent_limit_s=720,no_checkpoint_or_actor=True),no_PPO_or_canonical_or_productionGO=True)
  with sf.open(root+'/E1_ACTUAL_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e1_actual.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'GPU_UUID':%r,'dispatched_only':True}))"%(root,BASE+'/run-python.sh',UUID)
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='GPU0_FRESH80_PARENT_DISPATCHED_ONLY',parent=json.loads(stdout))
  with (B/'SLOPE135_CURRENT_FRESH80_GPU0_V2.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],GPU_UUID=UUID,mode='fresh80',canonical='SLOPE135'),f,indent=2)
 except BaseException:report.update(status='GPU0_NEW_STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/('SLOPE135_GPU0_fresh80_newcase_v2_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),root=root,parent=report.get('parent'),report=str(dest),source_PT_reads=0),indent=2))
if __name__=='__main__':main()
