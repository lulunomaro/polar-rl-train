"""Exactvariant fresh80 or nextnew typed20kNoUpdate on ONLYGPU1; no PTstage reads."""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,shlex,sys,time,traceback,zipfile
B=Path(__file__).resolve().parent;T=B.parent;C=T/'E1_three_variants_CPU_actual_v1';sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2';UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';ASSETS=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets');NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
def execute(c,code,timeout=240):
 i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=timeout);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();return rc,out,err

def main():
 p=argparse.ArgumentParser();p.add_argument('--variant',choices=['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50'],required=True);p.add_argument('--mode',choices=['fresh80','n20k'],required=True);a=p.parse_args();name=a.variant;mode=a.mode;locator=B/(name+'_CURRENT_'+mode.upper()+'_CASE_V1.json');assert not locator.exists()
 cpu=json.loads((C/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());audit=json.loads((C/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')).read_bytes());assert cpu['passed'] and audit['all_actual_rootkeys_mapped'] and not audit['unmapped_active_or_schema_fields'] and not audit['missing_source_reference_files'];typed=cpu['new_typed_source']
 source=B/(name+'_ACTUAL_TYPED_SOURCE_V1');stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_E1_'+name+'_GPU1_'+mode.upper()+'_'+stamp
 complete='E1_FRESH80_COMPLETE.json' if mode=='fresh80' else 'E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json';error='E1_FRESH80_ORIGINAL_ERROR.json' if mode=='fresh80' else 'E1_NATIVE24_ORIGINAL_ERROR.json';worker='worker_fresh80_noPT.py' if mode=='fresh80' else 'worker_n20k_typed_noupdate.py';tree=ast.parse((source/worker).read_bytes());puts={n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant)};assert {complete,error,'ENV_CLOSE_RETURNED.json','APP_CLOSING.json'}<=puts
 if mode=='n20k':assert 'VARIANT_FIRST_BEFORE_CONTROL.json' in puts
 report=dict(kind='EXPLICIT_VARIANT_GPU1_BOUND_STAGE_DISPATCH',variant=name,mode=mode,root=root,typed_source=typed,CPU_nested_owners_unknown=[],source_PT_reads_by_stage=0,canonical_or_PPO_or_productionGO=False);client=sf=None
 try:
  client=connect72();sf=client.open_sftp()
  if mode=='fresh80':
   join=json.loads((source/'EXACT_EXECUTED_SOURCE_PACKAGE_JOIN_V1.json').read_bytes());npzr=next(r for r in join['binary_metadata_only'] if r['original_relative'].endswith('MOD4_RESET_COLLISION_BANK.npz'));npz=Path(join['upstream_manifest']).parent/npzr['original_relative'];assert npzr['saved_SHA']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
   entries={}
   for p in source.rglob('*'):
    if p.suffix.lower() in NO:raise ValueError('Model in nonPTsource bundle')
    if p.is_file():entries[p.relative_to(source).as_posix()]=p
   entries['runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz']=npz
   for p in ASSETS.rglob('*'):
    if p.suffix.lower() in NO:raise ValueError('Model in newasset dependencies')
    if p.is_file():entries['new_assets/'+p.relative_to(ASSETS).as_posix()]=p
   entries['supervise_e1_actual.py']=B/'supervise_variant_gpu1_actual.py';archive=B/(name+'_NONPT_STAGE_'+stamp+'.zip');rows=[]
   with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
    for rel,p in sorted(entries.items()):
     raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
     if rel.endswith('MOD4_RESET_COLLISION_BANK.npz'):assert sha==npzr['saved_SHA']
     if rel=='new_assets/robot.usd':assert sha=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
     if rel=='new_assets/import_contract.json':assert sha=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
     z.writestr(rel,raw);rows.append(dict(relative=rel,bytes=len(raw),sha256=sha,local_dependency_path=str(p)))
   ah=hashlib.sha256(archive.read_bytes()).hexdigest();report['archive']=dict(path=str(archive),bytes=archive.stat().st_size,SHA=ah);report['files']=rows;sf.mkdir(root);sf.put(str(archive),root+'/NONPT_STAGE.zip')
   with sf.open(root+'/NONPT_STAGE_INDEX.json','wx') as f:f.write(json.dumps(dict(files=rows,archive_SHA=ah),indent=2))
   code="""from pathlib import Path
import hashlib,json,zipfile
B=Path(%r);j=json.loads((B/'NONPT_STAGE_INDEX.json').read_bytes());assert hashlib.sha256((B/'NONPT_STAGE.zip').read_bytes()).hexdigest()==j['archive_SHA']
with zipfile.ZipFile(B/'NONPT_STAGE.zip') as z:
 for r in j['files']:
  rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'};raw=z.read(r['relative']);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(raw)
print(json.dumps({'root':str(B),'actualnonPTfiles':len(j['files']),'NPZ_newasset_actual_verified':True,'model_reads':0}))
"""%root
   rc,stdout,stderr=execute(client,code);report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0
   task=dict(kind='E1_CANONICAL_ACTUAL_FRESH80_NO_PT_V1',canonical=name,num_envs=80,controls=24,no_checkpoint_or_actor=True,parent_limit_s=720)
  else:
   oldloc=json.loads((B/(name+'_CURRENT_FRESH80_CASE_V1.json')).read_bytes());oldroot=oldloc['remote_root']
   code="""from pathlib import Path
import json,hashlib
S=Path(%r);B=Path(%r);assert not B.exists();final=json.loads((S/'FINAL.json').read_bytes());closed=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes());assert final['passed'] and closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors'];old=json.loads((S/'E1_ACTUAL_PLAN.json').read_bytes());assert old['canonical']==%r and old['GPU_UUID']==%r;B.mkdir();rows=[]
for r in old['files']:
 rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors'};raw=(S/rel).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
 rows.append(r)
(B/'N20K_NONPT_STAGE_INDEX.json').write_text(json.dumps({'files':rows,'priorfresh_final':final,'priorfresh_closed':closed,'model_reads':0},indent=2));print(json.dumps({'root':str(B),'freshtruePASS_closewaitrelease':True,'files':len(rows),'model_reads':0}))
"""%(oldroot,root,name,UUID)
   rc,stdout,stderr=execute(client,code);report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'Originalfresh truePASS +closewaitrelease required'
   with sf.open(root+'/N20K_NONPT_STAGE_INDEX.json','r') as f:rows=json.load(f)['files']
   task=dict(kind='E1_MOD4V1_N20K_NATIVE24_ACTUAL_PARENT_TASK_V1',separate_actual_SDK_permission=True,canonical=name,num_envs=20000,controls=24,no_optimizer_update=True,source_read_purpose='NEW_TYPED_'+name+'_GPU1_NATIVE24_'+stamp,selected_typed_source_path=typed['path'],source_SHA=typed['SHA'],source_bytes=typed['bytes'],original_source_SHA=cpu['original_source']['SHA'],asset_dir=root+'/new_assets',source_saved_iteration=cpu['actual_source_metadata']['original_iteration'],source_saved_LR=cpu['actual_source_metadata']['original_LR'],source_saved_Adam17=cpu['actual_source_metadata']['original_17Adam_step'],seed=20260928,worker_limit_s=900,parent_limit_s=1200,no_PPO_or_productionGO=True)
  plan=dict(kind='EXPLICIT_VARIANT_GPU1_BOUND_EVAL_PLAN_V1',canonical=name,mode=mode,GPU_index=1,GPU_UUID=UUID,controls=24,worker=worker,complete_basename=complete,error_basename=error,files=rows,task=task,original_privateEX_finiteSH_only=True,no_PPO_or_canonical_or_productionGO=True)
  with sf.open(root+'/E1_ACTUAL_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e1_actual.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'GPU_UUID':%r,'dispatched_only':True}))"%(root,BASE+'/run-python.sh',UUID)
  rc,stdout,stderr=execute(client,start,60);assert rc==0,(rc,stderr);report.update(status='PARENT_DISPATCHED_ONLY',parent=json.loads(stdout))
  with locator.open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],canonical=name,mode=mode,GPU_UUID=UUID,typed_source=typed),f,indent=2)
 except BaseException:report.update(status='ORIGINAL_STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/(name+'_GPU1_'+mode+'_dispatch_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),variant=name,mode=mode,root=root,parent=report.get('parent'),report=str(dest),PT_reads_by_stage=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('VARIANT_STAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),source_PT_reads_by_stage=0,no_auto_replay=True),f,indent=2)
  raise
