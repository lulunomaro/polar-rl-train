"""EmitNOT_READY descriptor templates forparentgroupcomposition, no run/GO/SDK."""
from pathlib import Path
import argparse,hashlib,json
from e1_group_scope import KIND
B=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--group-id',default='PARENT_NEW_GROUP_ID');p.add_argument('--gpu-uuid',default='PARENT_FRESH_ACTUAL_GPU_UUID');p.add_argument('--group-root',default='PARENT_GROUP_ROOT');a=p.parse_args();a.out.mkdir(exist_ok=False);contracts=json.loads((B/'ROLE_CONTRACTS.json').read_bytes());rows=[]
 for role,c in contracts.items():
  n=c['controls'];case=Path(a.group_root)/role
  v=dict(kind=KIND,purpose=KIND,role=role,group_id=a.group_id,GPU_UUID=a.gpu_uuid,source_path=c['source']['path'],source_SHA=c['source']['SHA'],source_bytes=c['source']['bytes'],source_iteration=c['core']['original_iteration'],source_Adam17=c['core']['original_17Adam_step'],source_LR=c['core']['original_LR'],asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',runtime_root='PARENT_INSTALLED_OWN_'+role+'_RUNTIME_ROOT',runtime_source_root=c['own_runtime_source_root'],asset_dir='PARENT_EXACT_2C_BAE_NEW_ASSET_DIR',num_envs=80,seed=20260928,controls=n,physics_callbacks=n*8,feedback_samples=n*2,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_N=400,stiffness_N_m=2000,fresh_fullDR_cohort=True,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,optimizer_updates=0,absolute_worker_deadline_epoch=0,actual_group_admission=dict(group_id=a.group_id,GPU_UUID=a.gpu_uuid,source_SDK_admitted=False,private_GPU_EX_held=False,global_finite_EX_held=False,inherited_lock_fds=[]),sourceonly_NOT_READY=True,not_an_actual_task_or_resource_admission=True,worker_basename=c['worker_basename'],worker_SHA=hashlib.sha256((B/c['worker_basename']).read_bytes()).hexdigest(),common_source_index='PARENT_TO_PIN_FINAL_E1_INDEX_SHA',CLI=['python','-B',c['worker_basename'],'--task',str(case/'task.json'),'--group-root',a.group_root],output_basenames=['WORKER_SCENE_READY.json','FINAL.json','WORKER_ERROR.json','PRE_CLOSE.json','OWN_NEW_SKILL_RAW.npz','OWN_PARTIAL_SKILL_RAW.npz'],accepted_original_scope=c['scope'])
  target=a.out/(role+'_TASK_SOURCE_ONLY_NOT_READY.json')
  with target.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
  rows.append(dict(role=role,path=str(target),SHA=hashlib.sha256(target.read_bytes()).hexdigest()))
 with (a.out/'SOURCE_ONLY_DESCRIPTOR_EMISSION_INDEX.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='ONLY_TEMPLATE_EMISSION_NOT_ACTUAL',rows=rows,SDK_model_or_GO_calls=0),f,indent=2)
 print(json.dumps(dict(templates=4,sourceonly=True,SDK_PT_operations=0),indent=2))
if __name__=='__main__':main()
