"""After actualCPUpass stage exactcanonical nonPT+realNPZ+fullnewasset, fresh80only."""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,shlex,sys,time,traceback,zipfile
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2';ASSETS=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets');NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--canonical',choices=['CURB141','SLOPE135'],required=True);a=p.parse_args();name=a.canonical
 assert not (B/(name+'_CURRENT_FRESH80_CASE.json')).exists();cpu=json.loads((B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());assert cpu['passed']
 source=B/(name+'_ACTUAL_TYPED_SOURCE_V1');assert source.is_dir();stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_E1_'+name+'_FRESH80_'+stamp
 # Known exact savedE1 source-map dependency; same78af in canonical404/424.
 npz=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload'/('job1' if name=='SLOPE135' else 'job0')/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
 entries={}
 for f in source.rglob('*'):
  if f.suffix.lower() in NO:raise ValueError('Modelbinary in nonPT source package')
  if f.is_file():entries[f.relative_to(source).as_posix()]=f
 entries['runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz']=npz
 for f in ASSETS.rglob('*'):
  if f.suffix.lower() in NO:raise ValueError('Model in assetdependency tree')
  if f.is_file():entries['new_assets/'+f.relative_to(ASSETS).as_posix()]=f
 entries['supervise_e1_actual.py']=B/'supervise_e1_actual_bounded_v1.py'
 for n in ['worker_fresh80_noPT.py','worker_n20k_typed_noupdate.py']:
  tree=ast.parse((source/n).read_bytes());names={x.args[0].value for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='put' and x.args and isinstance(x.args[0],ast.Constant)}
  expected='E1_FRESH80_COMPLETE.json' if n.startswith('worker_fresh') else 'E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json';error='E1_FRESH80_ORIGINAL_ERROR.json' if n.startswith('worker_fresh') else 'E1_NATIVE24_ORIGINAL_ERROR.json';assert expected in names and error in names and 'ENV_CLOSE_RETURNED.json' in names and 'APP_CLOSING.json' in names
 archive=B/(name+'_FRESH80_NONPT_BUNDLE_'+stamp+'.zip');rows=[]
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for rel,f in sorted(entries.items()):
   assert f.suffix.lower() not in NO;raw=f.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if rel.endswith('MOD4_RESET_COLLISION_BANK.npz'):assert sha=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
   if rel=='new_assets/robot.usd':assert sha=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
   if rel=='new_assets/import_contract.json':assert sha=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
   z.writestr(rel,raw);rows.append(dict(relative=rel,bytes=len(raw),sha256=sha,local_dependency_path=str(f)))
 ash=hashlib.sha256(archive.read_bytes()).hexdigest();report=dict(kind='E1_ACTUAL_EXACT_NONPT_NPZ_NEWASSET_STAGE_FRESH80_DISPATCH',canonical=name,remote_root=root,CPU_actual_pass_first=True,original_or_typed_PT_reads_in_stage=0,archive=dict(path=str(archive),bytes=archive.stat().st_size,SHA=ash),files=rows);client=sf=None
 try:
  client=connect72();sf=client.open_sftp();sf.mkdir(root);sf.put(str(archive),root+'/NONPT_STAGE.zip')
  with sf.open(root+'/NONPT_STAGE_INDEX.json','wx') as f:f.write(json.dumps(dict(files=rows,archive_SHA=ash,NPZ_actual_source_SHA_verified=True,newasset_all_actualfiles_verified=True),indent=2))
  code="""from pathlib import Path
import zipfile,json,hashlib
B=Path(%r);j=json.loads((B/'NONPT_STAGE_INDEX.json').read_bytes());assert hashlib.sha256((B/'NONPT_STAGE.zip').read_bytes()).hexdigest()==j['archive_SHA']
with zipfile.ZipFile(B/'NONPT_STAGE.zip') as z:
 for r in j['files']:
  rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
  raw=z.read(r['relative']);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(raw)
print(json.dumps({'remote_root':str(B),'actual_nonPT_files':len(j['files']),'actual_NPZ_newasset_verified':True,'model_reads':0}))
"""%root
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'ExactE1nonPT stage failed'
  task=dict(kind='E1_CANONICAL_ACTUAL_FRESH80_NO_PT_V1',canonical=name,num_envs=80,controls=24,parent_limit_s=720,no_checkpoint_or_actor=True)
  plan=dict(kind='E1_CANONICAL_BOUNDED_VALIDATION_PLAN_V1',canonical=name,mode='fresh80',GPU_index=1,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',controls=24,worker='worker_fresh80_noPT.py',complete_basename='E1_FRESH80_COMPLETE.json',error_basename='E1_FRESH80_ORIGINAL_ERROR.json',files=rows,task=task,resource_wait_interval_s=45,resource_wait_cap_s=1800,no_PPO_or_production_GO_or_canonical=True)
  with sf.open(root+'/E1_ACTUAL_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e1_actual.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_only':True}))"%(root,BASE+'/run-python.sh')
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='FRESH80_PARENT_DISPATCHED_ONLY',parent=json.loads(stdout))
  with (B/(name+'_CURRENT_FRESH80_CASE.json')).open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],canonical=name,CPU_actual_receipt=str(B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json'))),f,indent=2)
 except BaseException:report.update(status='STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/(name+'_fresh80_stage_dispatch_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),canonical=name,root=root,parent=report.get('parent'),report=str(dest),NPZ_actual_copy_SHA_verified=True,PT_reads_in_stage=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E1_STAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),expected_NPZ_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',original_or_typed_PT_reads_by_stage=0,no_auto_replay=True),f,indent=2)
  raise
