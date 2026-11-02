"""Firstactualposttrainpair E3+CURB878, original twoGPU singlewriter. StageonlynonPT; noselectedmodelread until original parent admission/GO."""
from pathlib import Path
import json,hashlib,datetime,time,sys,ast,shlex
D=Path(__file__).resolve().parent;R=D.parent;sys.path.insert(0,str(R));from project_connector import connect72
marker=D/'PAIR3_V1_DISPATCH_ONCE.json';assert not marker.exists();stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());run='MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR3_V1_'+stamp;remote='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;payload=D/('PAIR3_V1_SOURCE_PAYLOAD_'+stamp);payload.mkdir();USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';H=lambda raw:hashlib.sha256(raw).hexdigest();parent=D/'parent_source/eight_posttrain_original_owner_v1.py';ast.parse(parent.read_text(encoding='utf-8'));(payload/parent.name).write_bytes(parent.read_bytes());base=D/'parent_source/original_budget_and_asset_refs'
for n in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):(payload/n).write_bytes((base/n).read_bytes())
summary=json.loads((R/'reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json').read_bytes());pins={x['role']:x for x in summary['rows']};m={x['role']:x for x in json.loads((D/'source_e1/PARENT_RUNTIME_CLONE_MAP_V1.json').read_bytes())['rows']};entries=[]
def addfiles(role,paths):
 out=payload/'roles'/role;out.mkdir(parents=True,exist_ok=True)
 for p in paths:(out/p.name).write_bytes(p.read_bytes())
 for rel in('NEW_ASSET_NATIVE_ACTUAL.json','RM70_SCOPE_REUSE_ACTUAL.json'):
  p=out/'evidence'/rel;p.parent.mkdir(exist_ok=True);p.write_bytes((base/'evidence'/rel).read_bytes())
 return out
# E3 exact source child minimalcompletebundle + pure constructor (stdlib, notGO issuer).
fam=D/'source_e0_e2_e3';descriptor=json.loads((fam/'E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json').read_bytes());out=addfiles('E3',[fam/n for n in('posttrain_fullstate_common_v1.py','worker_posttrain_e3_v1.py','E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json','construct_source_task_go_v1.py')]);proof=R/'reports/E3_1cd_no_update_final_20261102_031620/COLLECTION.json';collection=json.loads(proof.read_bytes());n=collection['files']['FINAL.json']['rows'][0]['data'];assert collection['files']['FINAL.json']['passed']and collection['files']['PARENT_EXIT_SCOPE.json']['all_own_children_waited']and n['passed']and n['source_SHA']==pins['E3']['source_SHA']and n['num_envs']==20000 and n['controls']==24 and n['core_actor_critic_STD17Adam_before_after_exact'];g=n['new_nominal_guard'];assert g['usd_sha256']==USD and g['contract_sha256']==CONTRACT;v={'source_SHA':n['source_SHA'],'asset_SHA':g['usd_sha256'],'contract_SHA':g['contract_sha256']};(out/'evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json').write_bytes(proof.read_bytes());norm=dict(actual_not_mock=True,source_SHA=v['source_SHA'],asset_USD_SHA=v['asset_SHA'],asset_contract_SHA=v['contract_SHA'],num_envs=20000,whole_state_restore_passed=True,all_own_children_waited=True,raw_reference='ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',raw_SHA=H(proof.read_bytes()),historical_reference_not_newtrainpass=True);(out/'evidence/PRIOR_FULL20K_REFERENCE.json').write_text(json.dumps(norm,indent=2),encoding='utf-8');entries.append(dict(role='E3',role_key='posttrain_e3_72',source_family='e0_e2_e3',base_root=descriptor['historical_actual_full20k_stage_without_models'],job_root=remote+'/roles/E3',source_SHA=pins['E3']['source_SHA'],task_template={},go_template={},max_additional_updates=20,num_envs=20000,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',actual_prior_full20k_proof_file='evidence/PRIOR_FULL20K_REFERENCE.json',native3pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',target_source_SDK_receipt_file='evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',historical_geometry_evidence_file='evidence/RM70_SCOPE_REUSE_ACTUAL.json',source_contract_AST_MOCK_passed=True,source_contract_not_SDK_pass_claim=True,worker_argv=['{JOB}/worker_posttrain_e3_v1.py','--mode','train','--num-envs','20000','--run-id','{RUN}','--out','{JOB}/production'],final_file='production/FINAL.json',stop_relative='production/STOP_AFTER_SAVE.json',final_updates_key='actual_new_PPO_updates'))
# TheseexactrootmetadataaresealedE3overlaydependencies,notsyntheticSDKproofs.
for n in('MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):(out/n).write_bytes((Path(descriptor['exact_sealed_overlay'])/n).read_bytes())
# Curb878 exact own full20k runtime, not any80 allocationoverlay.
fam=D/'source_e1';mp=m['SLOPE135'];out=addfiles('SLOPE135',[fam/'runtime_bundle'/n for n in('worker_e1_posttrain_full20k_original_ppo_v1.py','e1_posttrain_contract.py','e1_posttrain_state_tools.py')]+[fam/'e1_posttrain_make_task.py']);template=json.loads(Path(mp['fixed_source_descriptor']['path']).read_bytes());template.update(new_job_root=remote+'/roles/SLOPE135',asset_dir=remote+'/roles/SLOPE135/runtime/assets');proof=Path(mp['local_original_full20k_actual_proof']['path']);v=json.loads(proof.read_bytes());assert v['new_typed_source']['SHA']==pins['SLOPE135']['source_SHA']and v['STD17Adam_LR_iteration_beforeafter_exact']and v['controls']==24 and v['ONEoriginalreset']==1 and v['closewait_originalEX_finiteSH_release']['all_own_children_waited'];(out/'evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json').write_bytes(proof.read_bytes());norm=dict(actual_not_mock=True,source_SHA=v['new_typed_source']['SHA'],asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,num_envs=20000,whole_state_restore_passed=True,all_own_children_waited=True,raw_reference='ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',raw_SHA=H(proof.read_bytes()),historical_reference_not_newtrainpass=True);(out/'evidence/PRIOR_FULL20K_REFERENCE.json').write_text(json.dumps(norm,indent=2),encoding='utf-8');entries.append(dict(role='SLOPE135',role_key='posttrain_slope135_72',source_family='e1',base_root=mp['remote_original_native_runtime_clone_root'],job_root=remote+'/roles/SLOPE135',source_SHA=pins['SLOPE135']['source_SHA'],task_template=template,go_template={'source_iteration':template['source_iteration'],'input_Adam':template['source_Adam_step'],'source_qualification_kind':template['kind']},max_additional_updates=20,num_envs=20000,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',actual_prior_full20k_proof_file='evidence/PRIOR_FULL20K_REFERENCE.json',native3pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',target_source_SDK_receipt_file='evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',historical_geometry_evidence_file='evidence/RM70_SCOPE_REUSE_ACTUAL.json',source_contract_AST_MOCK_passed=True,source_contract_not_SDK_pass_claim=True,worker_argv=['{JOB}/worker_e1_posttrain_full20k_original_ppo_v1.py','--job-root','{JOB}','--task','{JOB}/TASK.json','--out','{JOB}/production'],final_file='production/FINAL.json',stop_relative='STOP_AFTER_SAVE.json',final_updates_key='completed_actual_updates'))
assets=R.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets'
for role in('E3','SLOPE135'):
 for n,h in(('robot.usd',USD),('import_contract.json',CONTRACT)):
  raw=(assets/n).read_bytes();assert H(raw)==h;q=payload/'roles'/role/'runtime/assets'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
plan=dict(run_id=run,H1_excluded=True,entries=entries,other_six_unconsumed_roles=['E2','E3','W35','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'],source_stage_not_training_pass=True);(payload/'OWNER_PLAN_TEMPLATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(payload/'SCHEDULE_PUBLIC.json').write_text(json.dumps({'experts':{e['role_key']:{'max_parent_seconds':3900,'GPU_UUID':['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][i]}for i,e in enumerate(entries)}},indent=2),encoding='utf-8')
remote_code="""from pathlib import Path
import json,shutil,hashlib,ast,sys
B=Path(%r);p=json.loads((B/'OWNER_PLAN_TEMPLATE.json').read_bytes());assert not(B/'STAGE_COMPLETE.json').exists();copies=[]
for e in p['entries']:
 src=Path(e['base_root']);dst=Path(e['job_root']);dst.mkdir(parents=True,exist_ok=True)
 def ignore(path,names):
  return [n for n in names if n=='__pycache__'or n.endswith(('.pt','.pth','.pyc','.zip','.jsonl','.log'))]
 for name in('runtime','lib','original_field','new_assets'):
  if(src/name).exists():shutil.copytree(src/name,dst/name,ignore=ignore,dirs_exist_ok=True)
 forbidden=('OWNER','PARENT','WORKER','READY','TASK','GO_','FINAL','ERROR','EXIT','WAIT','PRE_CLOSE','APP_','RESOURCE','N20K_','NATIVE24_','NOUPDATE_','GROUP_')
 for f in src.iterdir():
  if f.is_file()and(f.suffix=='.py'or(f.suffix=='.json'and not any(f.name.upper().startswith(x)for x in forbidden)))and f.name not in('STAGE_COMPLETE.json','COLLECTION.json'):shutil.copy2(f,dst/f.name)
 # Sourcepayloadalreadyuploaded contains only new source/evidence and wins over originalsourcefiles.
 for f in(B/'uploads'/e['role']).rglob('*'):
  if f.is_file():target=dst/f.relative_to(B/'uploads'/e['role']);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
 required=['original_run_manifest.json']+(['MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json']if e['source_family']=='e0_e2_e3'else['E1_CANONICAL_SOURCE_METADATA.json'])
 assert all((dst/n).is_file()for n in required),{'role':e['role'],'missing_immutable_root_dependencies':[n for n in required if not(dst/n).is_file()]}
 for n,expected in(('robot.usd',%r),('import_contract.json',%r)):
  raw=(dst/'runtime/assets'/n).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 files=[]
 for f in sorted(dst.rglob('*')):
  if f.is_file():
   assert f.suffix not in('.pt','.pth','.pyc','.jsonl','.log'),str(f);raw=f.read_bytes();files.append({'relative':str(f.relative_to(dst)),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
 m={'kind':'MOD4V1_POSTTRAIN_ACTUAL_NONPT_INSTALL','source_PT_copied':False,'source_model_metadata':{'SHA':e['source_SHA']},'asset_USD_SHA':%r,'asset_contract_SHA':%r,'files':files};(dst/e['manifest_file']).write_text(json.dumps(m,indent=2));mh=hashlib.sha256((dst/e['manifest_file']).read_bytes()).hexdigest()
 if e['source_family']=='e0_e2_e3':
  sys.path.insert(0,str(dst));from construct_source_task_go_v1 import build_task_go
  h=lambda n:hashlib.sha256((dst/n).read_bytes()).hexdigest();e['task_template'],e['go_template']=build_task_go(e['role'],job_root=str(dst),run_id=p['run_id'],role_key=e['role_key'],GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',worker_SHA=h('worker_posttrain_'+e['role'].lower()+'_v1.py'),common_SHA=h('posttrain_fullstate_common_v1.py'),descriptor_SHA=h(e['role']+'_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json'),manifest_SHA=mh,root_admission_SHA='0'*64,owner_parent_pid=0,learning_started_epoch=0.)
 copies.append({'role':e['role'],'nonPTfiles':len(files),'source_root':str(src),'new_job':str(dst)})
(B/'OWNER_PLAN.json').write_text(json.dumps(p,indent=2));(B/'STAGE_COMPLETE.json').write_text(json.dumps({'nonPT_runtime_clones':copies,'models_stat_hash_decode':0,'SDK_GO_canonical_writes':0},indent=2));print(json.dumps({'root':str(B),'staged_nonPT':copies,'source_models_opened':0,'SDK_GO_canonical_writes':0}))
"""%(remote,USD,CONTRACT,USD,CONTRACT)
marker.write_text(json.dumps({'run_id':run,'root':remote,'roles':['E3','SLOPE135'],'source_stage_only_until_parent_actual_admission':True},indent=2),encoding='utf-8');c=connect72();s=c.open_sftp()
def mkdir(path):
 try:s.stat(path)
 except FileNotFoundError:
  parent=str(Path(path).parent).replace('\\','/');
  if parent and parent!=path:mkdir(parent)
  s.mkdir(path)
try:
 mkdir(remote)
 for f in payload.rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(payload);dest=remote+('/uploads/'+rel.as_posix()[6:]if rel.parts[0]=='roles'else'/'+rel.as_posix());mkdir(dest.rsplit('/',1)[0])
  with s.open(dest,'wb')as z:z.write(f.read_bytes())
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(remote_code);i,o,er=c.exec_command(command,timeout=300);i.close();stdout=o.read().decode();stderr=er.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);print(stdout)
 # Original parent alone does actual resource locks/canonical reservation/GO; thislauncher touches no selectedPT.
 command="import subprocess,json,time;from pathlib import Path;B=Path("+repr(remote)+");f=(B/'ORIGINAL_PARENT_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(["+repr('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+",'-u','-B',str(B/'eight_posttrain_original_owner_v1.py')],cwd=B,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);f.close();print(json.dumps({'parent_pid':p.pid,'root':str(B),'dispatched_only_not_trainingpass':True}))";i,o,er=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(command),timeout=45);i.close();txt=o.read().decode();err=er.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);parent_info=json.loads(txt);report={'kind':'POSTTRAIN_PAIR3_ORIGINAL_OWNER_DISPATCH_NOT_RESULTS','source_stage_stdout':stdout,'parent':parent_info,'run_id':run,'root':remote,'H1_excluded':True,'other_six_pending':plan['other_six_unconsumed_roles']};out=D/'PAIR3_V1_STAGE_DISPATCH_RESULT.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(out);print(json.dumps(report,indent=2))
finally:s.close();c.close()
