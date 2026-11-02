"""NewoneGPU9x80 evaluationgroup. CopyonlydeclarednonPTsource/asset/bank; sourceweightsstayexistingpaths. Oncegroupdispatch."""
from pathlib import Path
import json,hashlib,datetime,time,zipfile,shlex,ast,traceback
from project_connector import connect72
R=Path(__file__).resolve().parent;S=R/'NINE_N80_PARALLEL_SOURCE_V1';E=R/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1';BASE='/home/lc01/Zonglin Li/zonglin2';USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
def main():
 once=R/'NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V1.json';assert not once.exists();assert(S/'PARENT_FIVE_SOURCE_INDEX_V2.json').exists();child=json.loads((R/'E1_N80_FRESH_FULLDR_PARALLEL_FOUR_WORKERS_SOURCE_HANDOFF_V1.json').read_bytes());contracts=json.loads((E/'ROLE_CONTRACTS.json').read_bytes());origins=json.loads((S/'FOUR_REMOTE_RUNTIME_ROOTS.json').read_bytes());v=json.loads((R/'EXPERT_NORMALIZATION_REGISTRY_v7.json').read_bytes());reg={r['expert']:r for r in v['selected_formals']};stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_'+stamp;groupid='MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_'+stamp;report={'kind':'NINE_SINGLE_GPU_STAGE_DISPATCH_NO_MODEL_COPY','group_id':groupid,'root':root,'GPU_UUID':GPU,'old_goal_paused_no_automatic_resume_work_is_direct_user_task':True};roles=[]
 parent_origins={'E0':BASE+'/tasks/MOD4V1_E0_FRESH80_FULLDR_20261102_013149_1793554309234206700','E2':BASE+'/tasks/MOD4V1_E2_FRESH80_FULLDR_20261102_023610_1793558170021229000','E3':BASE+'/tasks/MOD4V1_E3_FRESH80_FULLDR_20261102_030504_1793559904510076900','H1_normal':BASE+'/tasks/MOD4V1_H1_NORMAL_FRESH80_20261102_042702_1793564822209508600','W35':BASE+'/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000'}
 for role,controls in [('E0',1000),('E2',1200),('E3',160),('H1_normal',1000),('W35',1600)]:
  row=reg['H1_normal_PPO86B'if role=='H1_normal'else role];model=row.get('source_remote');sha=row.get('expected_source_SHA256',row.get('source_SHA'));size=row['source_bytes'];iteration=row['source_iteration'];adam=row.get('source_Adam_step',row.get('source_17Adam'));lr=row['source_LR']
  if role=='H1_normal':model=BASE+'/tasks/H1_TYPED71DB_EXACT_TRANSPORT_20261102_040952_1793563792484126600/NORMAL_H1_TYPED71DB_PRESERVED_SOURCE.pt'
  if role=='W35':model=parent_origins[role]+'/production/model_final_complete.pt';sha='8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54';size=17620037;iteration=32643;adam=654500;lr=1.0000000000000004e-05
  roles.append(dict(role=role,worker='worker_sources/parent/worker_five_original_n80.py',runtime_origin=parent_origins[role],runtime_root=root+'/runtimes/'+role,source_path=model,source_SHA=sha,source_bytes=size,source_iteration=iteration,source_Adam17=adam,source_LR=lr,controls=controls,asset_dir=root+'/runtimes/'+role+('/new_assets'if role=='H1_normal'else'/runtime/assets')))
 for role,contract in contracts.items():
  core=contract['core'];src=contract['source'];roles.append(dict(role=role,worker='worker_sources/e1/'+contract['worker_basename'],runtime_origin=origins[role],runtime_root=root+'/runtimes/'+role,source_path=src['path'],source_SHA=src['SHA'],source_bytes=src['bytes'],source_iteration=core['original_iteration'],source_Adam17=core['original_17Adam_step'],source_LR=core['original_LR'],controls=contract['controls'],asset_dir=root+'/runtimes/'+role+'/new_assets'))
 assert len(roles)==9 and all(r['source_path']and r['source_SHA']for r in roles);entries={'single_gpu_group_supervisor.py':S/'single_gpu_group_supervisor.py'}
 for p in S.glob('*.py'):
  if p.name!='single_gpu_group_supervisor.py':entries['worker_sources/parent/'+p.name]=p
 for row in child['runtime_files_to_stage_same_directory']:
  p=Path(row['path']);raw=p.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];entries['worker_sources/e1/'+p.name]=p
 for p in (R/'..'/'mod4_usd_scut_fudan_20261101/candidates/v1/assets').resolve().rglob('*'):
  if p.is_file():entries['pinned_assets/'+p.relative_to((R/'..'/'mod4_usd_scut_fudan_20261101/candidates/v1/assets').resolve()).as_posix()]=p
 archive=R/('NINE_N80_SINGLE_GPU_NONPT_SOURCE_'+stamp+'.zip');files=[]
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=2)as z:
  for rel,p in sorted(entries.items()):
   assert p.suffix.lower()not in{'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc'};raw=p.read_bytes()
   if p.suffix=='.py':ast.parse(raw.decode('utf-8'))
   z.writestr(rel,raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 plan=dict(kind='SINGLE_GPU_NINE_FRESH80_SKILL_EVAL_PLAN',group_id=groupid,GPU_UUID=GPU,asset_SHA=USD,contract_SHA=CONTRACT,roles=roles,worker_files=files,copy_models=False,PPO_BPTT_newledger=False);report['plan']=plan;c=s=None
 try:
  c=connect72();s=c.open_sftp();s.mkdir(root);s.put(str(archive),root+'/NONPT_GROUP_SOURCE.zip');s.open(root+'/GROUP_PLAN.json','wx').write(json.dumps(plan,indent=2));code="""from pathlib import Path
import json,hashlib,zipfile,shutil,ast
B=Path(%r);P=json.loads((B/'GROUP_PLAN.json').read_bytes());NO={'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc'}
with zipfile.ZipFile(B/'NONPT_GROUP_SOURCE.zip')as z:
 for r in P['worker_files']:
  rel=Path(r['relative']);assert not rel.is_absolute()and '..'not in rel.parts and rel.suffix.lower()not in NO;raw=z.read(r['relative']);assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA'];p=B/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
indices=[]
for role in P['roles']:
 src=Path(role['runtime_origin']);dst=Path(role['runtime_root']);assert src.is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))and src.is_dir()and dst.is_relative_to(B/'runtimes')and not dst.exists();dst.mkdir(parents=True);rows=[]
 dirs=('runtime','lib','new_assets','original_field','job0/runtime')
 paths=[]
 for d in dirs:
  q=src/d
  if q.is_dir():paths.extend(p for p in q.rglob('*')if p.suffix.lower()not in NO and p.is_file())
 paths.extend(p for p in src.glob('*.py')if p.is_file())
 for name in('original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_DERIVATION_INDEX.json','E1_CANONICAL_SOURCE_METADATA.json'):
  p=src/name
  if p.exists():paths.append(p)
 p=src/'job0/original_run_manifest.json'
 if p.exists():paths.append(p)
 for p in sorted(set(paths)):
  assert p.suffix.lower()not in NO and not p.name.upper().startswith('TRAINING_BUDGET');rel=p.relative_to(src);raw=p.read_bytes();out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);rows.append({'relative':rel.as_posix(),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
 asset=Path(role['asset_dir']);asset.mkdir(parents=True,exist_ok=True)
 for p in(B/'pinned_assets').rglob('*'):
  if p.is_file():out=asset/p.relative_to(B/'pinned_assets');out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes())
 assert hashlib.sha256((asset/'robot.usd').read_bytes()).hexdigest()==P['asset_SHA']and hashlib.sha256((asset/'import_contract.json').read_bytes()).hexdigest()==P['contract_SHA'];indices.append({'role':role['role'],'origin':str(src),'runtime_root':str(dst),'files':rows,'selected_model_copies':0})
with(B/'ACTUAL_NONPT_RUNTIME_STAGE_INDEX.json').open('x')as f:json.dump({'staged':True,'models_or_canonical_access':False,'rows':indices},f,indent=2)
print(json.dumps({'staged':True,'root':str(B),'roles':len(indices),'runtime_nonPT_files':sum(len(r['files'])for r in indices),'source_PT_opens':0,'SDK_started':False}))
"""%root
  i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_returncode=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,(rc,stderr)
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'GROUP_SUPERVISOR_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'single_gpu_group_supervisor.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_only':True}))"%(root,BASE+'/run-python.sh');i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='ALLNINE_SINGLEGPU_GROUP_PARENT_DISPATCHED_ONCE_NOT_RESULTS',parent=json.loads(stdout));once.write_text(json.dumps(report,indent=2),encoding='utf-8')
 except BaseException:report.update(status='STAGE_OR_GROUP_DISPATCH_ERROR_NO_AUTOMATIC_REPLAY',error=traceback.format_exc());raise
 finally:
  if s:s.close()
  if c:c.close()
  p=R/'reports'/('NINE_SINGLE_GPU_GROUP_STAGE_'+stamp+'.json');p.write_text(json.dumps(report,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({k:v for k,v in report.items()if k not in('plan',)},indent=2))
if __name__=='__main__':main()
