"""After actualGPU0freshPASS+closewaitrelease: NEW f2btyped N20kNoUpdate purpose.
No sourcePTtransport/stat/hash/load bystage. Onlyactualworker onecachepurpose.
"""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2';UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842'

def main():
 assert not (B/'SLOPE135_CURRENT_N20K_GPU0_V1.json').exists();loc=json.loads((B/'SLOPE135_CURRENT_FRESH80_GPU0_V2.json').read_bytes());source=loc['remote_root'];cpu=json.loads((B/'SLOPE135_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').read_bytes());assert cpu['passed'];typed=cpu['new_typed_source']
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_E1_SLOPE135_GPU0_TYPED_N20K_NATIVE24_NOUPDATE_'+stamp;purpose='NEW_F2B_TYPED_SLOPE135_GPU0_N20K_NATIVE24_'+stamp
 worker=(B/'SLOPE135_ACTUAL_TYPED_SOURCE_V1/worker_n20k_typed_noupdate.py').read_bytes();tree=ast.parse(worker);names={n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant)}
 complete='E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json';error='E1_NATIVE24_ORIGINAL_ERROR.json';assert all(n in names for n in [complete,error,'E1_CORE_BEFORE.json','E1_CORE_AFTER.json','E1_SOURCE_FINAL_READ_COUNTS.json','ENV_CLOSE_RETURNED.json','APP_CLOSING.json'])
 code="""from pathlib import Path
import json,hashlib
S=Path(%r);B=Path(%r);assert not B.exists();final=json.loads((S/'FINAL.json').read_bytes());closed=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes());assert final['passed'] is True and closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors']
actual=json.loads((S/'gpu1/out/E1_FRESH80_COMPLETE.json').read_bytes());assert actual['passed'] and actual['controls']==24 and actual['physics_callbacks']==192 and actual['feedback_samples']==48
old=json.loads((S/'E1_ACTUAL_PLAN.json').read_bytes());assert old['GPU_index']==0 and old['GPU_UUID']==%r;rows=[];B.mkdir()
for r in old['files']:
 rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors'}
 raw=(S/rel).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
 rows.append(r)
(B/'N20K_NONPT_STAGE_INDEX.json').write_text(json.dumps({'files':rows,'fresh_actual_final':final,'fresh_closed':closed,'sourcePT_reads':0},indent=2));print(json.dumps({'root':str(B),'freshPASS_cleanrelease':True,'nonPTfiles':len(rows),'sourcePT_reads':0}))
"""%(source,root,UUID)
 report=dict(kind='SLOPE135_GPU0_TYPED_F2B_N20K_NOUPDATE_NEW_PURPOSE',remote_root=root,source_read_purpose=purpose,source_PT_reads_by_stage=0);client=sf=None
 try:
  client=connect72();i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'FreshactualPASS/cleanrelease required; no actual20k before it'
  sf=client.open_sftp()
  with sf.open(root+'/N20K_NONPT_STAGE_INDEX.json','r') as f:rows=json.load(f)['files']
  task=dict(kind='E1_MOD4V1_N20K_NATIVE24_ACTUAL_PARENT_TASK_V1',separate_actual_SDK_permission=True,canonical='SLOPE135',num_envs=20000,controls=24,no_optimizer_update=True,source_read_purpose=purpose,selected_typed_source_path=typed['path'],source_SHA=typed['SHA'],source_bytes=typed['bytes'],original_source_SHA=cpu['original_source']['SHA'],asset_dir=root+'/new_assets',source_saved_iteration=cpu['actual_source_metadata']['original_iteration'],source_saved_LR=cpu['actual_source_metadata']['original_LR'],source_saved_Adam17=cpu['actual_source_metadata']['original_17Adam_step'],seed=20260928,worker_limit_s=900,parent_limit_s=1200,no_PPO_or_production_GO=True)
  plan=dict(kind='E1_CANONICAL_GPU0_BOUNDED_VALIDATION_PLAN_V2',canonical='SLOPE135',mode='n20k',GPU_index=0,GPU_UUID=UUID,controls=24,worker='worker_n20k_typed_noupdate.py',complete_basename=complete,error_basename=error,files=rows,task=task,no_PPO_or_canonical_or_productionGO=True)
  with sf.open(root+'/E1_ACTUAL_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e1_actual.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'GPU_UUID':%r,'dispatched_only':True}))"%(root,BASE+'/run-python.sh',UUID)
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='SLOPE135_GPU0_N20K_PARENT_DISPATCHED',parent=json.loads(stdout))
  with (B/'SLOPE135_CURRENT_N20K_GPU0_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],GPU_UUID=UUID,canonical='SLOPE135',mode='n20k',source_read_purpose=purpose,typed_source=typed),f,indent=2)
 except BaseException:report.update(status='N20K_STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/('SLOPE135_GPU0_N20K_dispatch_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),root=root,parent=report.get('parent'),report=str(dest),sourcePT_stage_reads=0),indent=2))
if __name__=='__main__':main()
