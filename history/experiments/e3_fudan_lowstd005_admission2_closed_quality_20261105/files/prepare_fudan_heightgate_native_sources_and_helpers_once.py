"""Metadata-only fresh-branch adapters around unchanged Fudan/native/owner machinery."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent
old_branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8';branch=old_branch+'_HEIGHTGATE'
old_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8';kind=old_kind+'_heightgate'
old_sha='386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2'
overlay=D/'source_task_runtime_v3_lowheightgate/e3_fudan_task_runtime_v1.py';raw=overlay.read_bytes();sha=hashlib.sha256(raw).hexdigest();size=len(raw)
N=D/'source_fudan_native_worker_v6_lowheightgate';O=D/'source_original_owner_v6_lowheightgate'
stager=D/'stage_fudan_nonpt_v6_lowheightgate.py'
helper_names=('prepare_stage_fudan_heightgate_w9_once.py','dispatch_fudan_heightgate_w9_original_owner_once.py','collect_fudan_heightgate_w9_window_once.py')
assert not N.exists()and not O.exists()and not stager.exists()and all(not(D/n).exists()for n in helper_names)
def change(s):return s.replace(old_branch,branch).replace(old_kind,kind).replace(old_sha,sha)
files={}
old=(D/'source_fudan_native_worker_v5_fresh1cd_timeout8/worker_fudan_sequence_ppo_native_v1.py').read_text(encoding='utf8');new=change(old);assert new.count('version=4')==7;new=new.replace('version=4','version=5');assert new.count('TASK_RUNTIME_BYTES = 8571')==1;new=new.replace('TASK_RUNTIME_BYTES = 8571','TASK_RUNTIME_BYTES = '+str(size))
normalized=new.replace(branch,old_branch).replace(kind,old_kind).replace(sha,old_sha).replace('version=5','version=4').replace('TASK_RUNTIME_BYTES = '+str(size),'TASK_RUNTIME_BYTES = 8571')
assert ast.dump(ast.parse(normalized))==ast.dump(ast.parse(old))
files[N/'worker_fudan_sequence_ppo_native_v1.py']=new;worker_sha=hashlib.sha256(new.encode('utf8')).hexdigest()
old_owner=(D/'source_original_owner_v5_fresh1cd_timeout8/fudan_original_owner_v1.py').read_text(encoding='utf8');new_owner=change(old_owner)
assert ast.dump(ast.parse(new_owner.replace(kind,old_kind).replace(sha,old_sha)))==ast.dump(ast.parse(old_owner))
files[O/'fudan_original_owner_v1.py']=new_owner
c=(D/'source_original_owner_v5_fresh1cd_timeout8/fudan_worker_close_contract_v1.py').read_text(encoding='utf8');c=change(c).replace('fresh_version4=','fresh_version5=');assert c.count("intent['version']==4")==1;c=c.replace("intent['version']==4","intent['version']==5");assert c.count('==8571')==1;c=c.replace('==8571','=='+str(size));files[O/'fudan_worker_close_contract_v1.py']=c
s=change((D/'stage_fudan_nonpt_v5_fresh1cd_timeout8.py').read_text(encoding='utf8')).replace('e3_fudan_seq_n20000_timeout8_fresh1cd_25','e3_fudan_seq_n20000_timeout8_fresh1cd_heightgate_25');files[stager]=s
current_guard='''previous=json.loads((D/'reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/CLOSED_RESULT.json').read_bytes());m=previous['metadata'];f=m['FDN_FINAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];end=m['OWNER_EXIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json']
assert previous['closed']is True and end['errors']==[]and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0 and outer['controller_pid']==1626919 and outer['original_owner_pid']==1626926
assert m['FDN_PARENT_WAIT_QUALIFICATION.json']['qualified']is True and latest==f['latest_complete_save']and latest['sha256']=='246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2'and latest['bytes']==146165047 and f['counters']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)
assessment=json.loads((D/'FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json').read_bytes());assert assessment['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_246AC_PROMOTION'and assessment['original_N80']['execution_qualified']is True and assessment['original_N80']['actual_original_parent_qualified']is True
'''
old_stage=(D/'prepare_stage_fudan_fresh1cd_w8_admission2_once.py').read_text(encoding='utf8');a=old_stage.index('previous_admission=json.loads(');b=old_stage.index('source=dict(',a);stage=old_stage[:a]+'__CURRENT_CLOSED_GUARD__\n'+old_stage[b:]
def namespace(s):return s.replace('FDN_N20000_W8_FRESH1CD_ADMISSION2_','FDN_N20000_W9_LOWHEIGHTGATE_').replace('native_payload_v8_n20000_fresh1cd25_admission2','native_payload_v9_lowheightgate25').replace('FRESH1CD25_W8_ADMISSION2_','FRESH1CD25_HEIGHTGATE_W9_')
stage=namespace(stage).replace('source_fudan_native_worker_v5_fresh1cd_timeout8',N.name).replace('source_original_owner_v5_fresh1cd_timeout8',O.name).replace('stage_fudan_nonpt_v5_fresh1cd_timeout8.py',stager.name).replace('source_task_runtime_v2_lowtimeout8','source_task_runtime_v3_lowheightgate').replace(old_sha,sha).replace('len(overlay_raw)==8571','len(overlay_raw)=='+str(size)).replace('e4d5df2827a2d07d7c880f72bd09e483d4987072c005253c7f93e6b2cccfdeb5',worker_sha)
stage=stage.replace('__CURRENT_CLOSED_GUARD__\n',current_guard)
files[D/helper_names[0]]=stage
files[D/helper_names[1]]=namespace((D/'dispatch_fudan_fresh1cd_w8_admission2_original_owner_once.py').read_text(encoding='utf8'))
files[D/helper_names[2]]=namespace((D/'collect_fudan_fresh1cd_w8_admission2_window_once.py').read_text(encoding='utf8'))
for path,s in files.items():ast.parse(s);compile(s,str(path),'exec')
for path,s in files.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding='utf8',newline='\n')
print(json.dumps(dict(task_overlay=dict(bytes=size,sha256=sha),worker=dict(bytes=len(files[N/'worker_fudan_sequence_ppo_native_v1.py'].encode('utf8')),sha256=worker_sha),files=[str(x)for x in files],source_only_AST_and_metadata_normalized_worker_owner_equivalence=True,worker_owner_core_math_resource_lifecycle_unchanged=True,model_SDK_SSH_GPU_C_operations=0),indent=2))
