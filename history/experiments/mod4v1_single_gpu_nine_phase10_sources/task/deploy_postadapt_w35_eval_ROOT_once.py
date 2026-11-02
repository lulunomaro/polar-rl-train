"""ROOT use only AFTER current finite owner is fully saved/settled/waited/released.
One new saved-source read purpose; no old source2d contract reuse or learning.
"""
from pathlib import Path
import json,hashlib,ast,datetime,time,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'staged_sources/W35_MOD4V1_POSTADAPT_EVAL_V1';dispatch=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());producer=dispatch['new_job'];base='/home/lc01/Zonglin Li/zonglin2'
for p in D.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
c=connect72();sf=c.open_sftp();record={'kind':'ROOT_POSTADAPT_SAVEDMODEL_EVAL_ONLY','producer_root':producer,'source_PT_opens_parent':0,'new_budget_seconds':0};stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');job=base+'/tasks/MOD4V1_W35_POSTADAPT_EVAL_'+stamp+'_'+str(time.time_ns())
try:
 def read_json(rel):
  with sf.open(producer+'/'+rel,'rb')as f:return json.loads(f.read())
 exit=read_json('OWNER_EXIT_ACTUAL.json');cohort=read_json('COHORT_FINAL.json');final=read_json('production/FINAL.json')
 assert exit['all_own_children_waited'] and exit['original_cost_settled'] and exit['own_original_two_fcntl_released_if_held'] and exit['private_finite_leases_released'] and exit['error'] is None
 assert cohort['passed_execution'] and final['passed'] and final['actual_new_PPO_updates']>0
 source=final['final'];assert source['source_SHA']=='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b' and source['actual_new_PPO_updates']==final['actual_new_PPO_updates'] and source['Adam_min']==source['Adam_max']==651260+20*source['actual_new_PPO_updates']
 assert source['path']==producer+'/production/model_final_complete.pt'
 # Reserve a NEW purpose token after the genuine saved and waited boundary, never retry it automatically.
 with sf.open(producer+'/POSTADAPT_EVAL_PURPOSE_CONSUMED.json','wx')as f:f.write(json.dumps({'new_eval_job':job,'source_SHA':source['SHA'],'source_bytes':source['bytes'],'parent_metadata_read_only':True},indent=2))
 prepare="""from pathlib import Path
import shutil,json
B=Path(%r);S=Path(%r);assert not B.exists();B.mkdir()
def ignore(path,names):return[n for n in names if n=='__pycache__' or Path(n).suffix.lower() in('.pt','.pth','.pyc')]
for name in('runtime','original_field','train','data'):
 if(S/name).is_dir():shutil.copytree(S/name,B/name,ignore=ignore)
for name in('original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):
 if(S/name).is_file():shutil.copy2(S/name,B/name)
assert not(B/'kit_isolation').exists();print(json.dumps({'new_job':str(B),'runtime_source':str(S),'PT_copies':0}))
"""%(job,producer)
 i,o,e=c.exec_command(shlex.quote(base+'/run-python.sh')+' -B -c '+shlex.quote(prepare),timeout=180);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);record['prepare']=json.loads(text)
 files=[(p.name,p)for p in D.iterdir()if p.is_file()]+[('w35_eval_parent_v1.py',R/'w35_eval_parent_v1.py')];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sha={rel:H(p)for rel,p in files}
 for rel,p in files:sf.put(str(p),job+'/'+rel)
 task={'kind':'MOD4V1_W35_POSTADAPT_SAVEDMODEL_FULL32_EVAL_V1','run_id':'MOD4V1_W35_POSTADAPT_EVAL_'+stamp,'purpose_id':'POSTADAPT_NEW_SAVEDMODEL_'+source['SHA'][:16]+'_'+stamp,'producer_job_root':producer,'runtime_job':job,'model_path':source['path'],'model_SHA':source['SHA'],'model_bytes':source['bytes'],'model_iteration':source['saved_iteration'],'Adam17':source['Adam_min'],'actual_saved_LR':None,'saved_LR_binding':'One cached selected-source optimizer paramgroup, strict fulloptimizer exact restore; old sourceLR is not assumed','model_new_PPO_updates':source['actual_new_PPO_updates'],'num_envs':20000,'controls_max':1600,'physics_max':12800,'feedback_max':3200,'worker_seconds':3600,'parent_seconds':3780,'GPU_UUID':'GPU-16828f91-2b45-b646-8dc0-9481138e2842','no_new_learning_or_GO':True,'asset_USD_SHA':'2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3','asset_contract_SHA':'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','worker_SHA':sha['evaluate_mod4v1_w35.py'],'original_entry_SHA':'bbda08da09bbb12cae8b80e8ff9be2b7a1f19dddd42200d5ec2bdfb6bca45ee2','actual_current_authority_private_shared_resources_admitted':False,'original_eval_parent_holds_private_and_validation_EX':False,'telemetry_producer':{'format':'mod4.227.lossless_fieldset_positional_jsonl.v1','worker_SHA':sha['evaluate_mod4v1_w35.py'],'observer_SHA':sha['rm70_intervals227.py'],'writer_SHA':sha['positional_rows227.py'],'decoder_SHA':sha['decode227_positional.py'],'retained_byte_limit':192*1024**2,'all_original_fields_values_masks_and_union_retained':True,'actual_byte_coverage':'UNKNOWN_UNTIL_ACTUAL_CASE'}}
 package={'files':[{'relative':rel,'bytes':p.stat().st_size,'SHA':H(p)}for rel,p in files],'models_copied':0,'purpose':'Actual new complete saved source after settled parent boundary'}
 for name,obj in [('SOURCE_PRODUCER_METADATA.json',source),('TASK_PENDING.json',task),('PACKAGE.json',package)]:
  with sf.open(job+'/'+name,'wx')as f:f.write(json.dumps(obj,indent=2))
 code="import pathlib,subprocess,psutil,json;B=pathlib.Path(%r);log=(B/'PARENT_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'w35_eval_parent_v1.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);q=psutil.Process(p.pid);print(json.dumps({'pid':p.pid,'creation':q.create_time(),'root':str(B),'actual_eval_pass_not_yet_claimed':True}))"%(job,base+'/run-python.sh')
 i,o,e=c.exec_command(shlex.quote(base+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);record.update(status='PARENT_DISPATCHED',new_job=job,parent=json.loads(text),new_source_model=source,task_planned=task,stderr=err)
finally:sf.close();c.close()
p=R/'reports'/('W35_postadapt_eval_dispatch_'+stamp+'.json');p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(record,ensure_ascii=False,indent=2))
