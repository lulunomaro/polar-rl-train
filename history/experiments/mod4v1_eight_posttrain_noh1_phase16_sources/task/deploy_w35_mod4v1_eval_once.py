"""New W35/MOD4v1 20k fullstate/no-optimizer32s evaluation; source PT never copied."""
from pathlib import Path
import ast,json,hashlib,datetime,time,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;OLD=R/'staged_sources/W35_MOD4V1_EVAL_V2';D=R/'staged_sources/W35_MOD4V1_EVAL_V3';assert not D.exists();D.mkdir()
for p in OLD.iterdir():
 if p.is_file() and p.name!='SOURCE_INDEX.json':
  raw=p.read_bytes()
  if p.name=='evaluate_mod4v1_w35.py':raw=('\n'.join(line for line in raw.decode('utf-8').splitlines() if not line.strip().startswith(('from guard_latest32 import','guard_uninstall=install_before_main')))+'\n').encode()
  (D/p.name).write_bytes(raw)
assert 'guard_latest32' not in (D/'evaluate_mod4v1_w35.py').read_text(encoding='utf-8')
for p in D.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
base='/home/lc01/Zonglin Li/zonglin2';src=json.loads(sorted((R/'reports').glob('fullDR80_dispatch_*.json'))[-1].read_bytes())['plan']['new_remote_job']
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');job=base+'/tasks/MOD4V1_W35_FULLDR_EVAL_'+stamp+'_'+str(time.time_ns())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files=[(p.name,p) for p in sorted(D.iterdir()) if p.is_file()]+[('w35_eval_parent_v1.py',R/'w35_eval_parent_v1.py')]
shas={rel:H(p) for rel,p in files}
source_job=base+'/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72'
task={'kind':'MOD4V1_W35_LATEST32481_FULLDR_SAMEUID_EVAL_V1','run_id':'MOD4V1_W35_EVAL_'+stamp,'purpose_id':'MOD4V1_W35_NEW_PLANT_FULLDR32S_'+stamp,'runtime_job':job,'qualified_latest227D_job_root':source_job,'model_path':source_job+'/production/model_final_complete.pt','model_SHA':'2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b','model_bytes':17619333,'model_iteration':32481,'Adam17':651260,'actual_saved_LR':.0002562890625000001,'model_new_PPO_updates':77,'num_envs':20000,'controls_max':1600,'physics_max':12800,'feedback_max':3200,'worker_seconds':3600,'parent_seconds':3780,'GPU_UUID':'GPU-16828f91-2b45-b646-8dc0-9481138e2842','no_new_learning_or_GO':True,'asset_USD_SHA':'2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3','asset_contract_SHA':'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','worker_SHA':shas['evaluate_mod4v1_w35.py'],'original_entry_SHA':'bbda08da09bbb12cae8b80e8ff9be2b7a1f19dddd42200d5ec2bdfb6bca45ee2','actual_current_authority_private_shared_resources_admitted':False,'original_eval_parent_holds_private_and_validation_EX':False,'telemetry_producer':{'format':'mod4.227.lossless_fieldset_positional_jsonl.v1','worker_SHA':shas['evaluate_mod4v1_w35.py'],'observer_SHA':shas['rm70_intervals227.py'],'writer_SHA':shas['positional_rows227.py'],'decoder_SHA':shas['decode227_positional.py'],'retained_byte_limit':192*1024**2,'all_original_fields_values_masks_and_union_retained':True,'actual_byte_coverage':'UNKNOWN_UNTIL_ACTUAL_CASE'}}
prepare="""import pathlib,shutil,json
B=pathlib.Path(%r);S=pathlib.Path(%r);assert not B.exists();B.mkdir()
def ignore(path,names):return[n for n in names if n=='__pycache__' or pathlib.Path(n).suffix.lower() in('.pt','.pth','.pyc')]
for name in('runtime','original_field','train','data'):
 if(S/name).is_dir():shutil.copytree(S/name,B/name,ignore=ignore)
for name in('original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):
 p=S/name
 if p.is_file():shutil.copy2(p,B/name)
assert not(B/'kit_isolation').exists()
print(json.dumps({'copied_validated_runtime':True,'source_PT_copies':0,'new_root':str(B)}))
"""%(job,src)
c=connect72();sf=c.open_sftp();report={'task_planned':task,'status':'STAGING','new_job':job}
try:
 i,o,e=c.exec_command(shlex.quote(base+'/run-python.sh')+' -B -c '+shlex.quote(prepare),timeout=180);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);report['prepare']=json.loads(out)
 for rel,p in files:sf.put(str(p),job+'/'+rel)
 package={'files':[{'relative':rel,'bytes':p.stat().st_size,'SHA':H(p)} for rel,p in files],'model_copies':0,'source_byte_decode_max':[1,1]}
 for name,obj in [('TASK_PENDING.json',task),('PACKAGE.json',package)]:
  with sf.open(job+'/'+name,'wx')as f:f.write(json.dumps(obj,indent=2))
 code="import pathlib,subprocess,psutil,json;B=pathlib.Path(%r);log=(B/'PARENT_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'w35_eval_parent_v1.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);q=psutil.Process(p.pid);print(json.dumps({'pid':p.pid,'creation':q.create_time(),'root':str(B),'evaluation_success_not_yet_claimed':True}))"%(job,base+'/run-python.sh')
 i,o,e=c.exec_command(shlex.quote(base+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);report.update(status='PARENT_DISPATCHED',parent=json.loads(out),stderr=err)
finally:sf.close();c.close()
p=R/'reports'/('W35_eval_dispatch_'+stamp+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(report,ensure_ascii=False,indent=2))
