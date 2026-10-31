"""ROOT saved-metadata Task builder only. No model/raw/assets/SDK/remote access."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,time
MODEL='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
N=Path(__file__).resolve().parent


def read(p):return json.loads(Path(p).read_bytes())
def main():
 p=argparse.ArgumentParser();p.add_argument('--closing',type=Path,required=True);p.add_argument('--new-cpu',type=Path,required=True)
 p.add_argument('--GPU-UUID',required=True);p.add_argument('--out-new',type=Path,required=True);a=p.parse_args()
 c=read(a.closing);u=read(a.new_cpu);r=c['roles']['w35_72'];f=c['formals']['w35_72'];q=u['roles']['w35_72']
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert c['owner_closed']['cohort_final']['original_cost_settled'] and c['owner_closed']['owner_exit']['original_cost_settled']
 assert r['qualified_formal'] and r['errors']==[] and r['private_EX_free'] and r['actual_material_limit_error_count']==0
 assert r['original_node_terminal']['row']['returncode']==0 and r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released']
 assert u['passed'] and u['old_model_reads']==0 and q['passed'] and q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present'] and q['save_at_or_after_requested_deadline']
 assert f['SHA']==r['final']['final']['SHA']==q['SHA']==MODEL and f['bytes']==17619269
 assert q['saved_iteration']==32404 and q['Adam17_step']==649720 and q['new_PPO_updates']==68
 model=PurePosixPath(f['source']);assert model.name=='model_final_complete.pt' and model.parent.name=='production'
 assert a.GPU_UUID in ('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
 assert len(q['actual_saved_optimizer_LR'])==1
 a.out_new.mkdir(parents=True,exist_ok=False);rows=[]
 for name in ('evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py','rm70_intervals222.py'):
  raw=(N/name).read_bytes()
  with (a.out_new/name).open('xb') as out:out.write(raw)
  rows.append(dict(relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 task=dict(kind='NEW222_W35_CLOSED_FULL_RM70_SKILL_ONLY',epoch=time.time(),model_SHA=MODEL,model_bytes=17619269,
  model_path=str(model),qualified219_job_root=str(model.parent.parent),model_iteration=32404,Adam17=649720,model_new_PPO_updates=68,
  actual_saved_LR=q['actual_saved_optimizer_LR'][0],num_envs=20000,controls_max=1600,seconds_max=32.,physics_max=12800,feedback_max=3200,
  GPU_UUID=a.GPU_UUID,no_new_learning_or_GO=True,worker_seconds=1680,parent_seconds=1800,
  actual_current_CNone_private_shared_resources_admitted=False,
  worker_SHA=rows[0]['SHA'],model_physical_byte_reads=1,model_decodes=1,model_copies=0,
  old_5039_or_other_raw_reads=0,source_CPU_old_model_reads=0,default_JSONL_or_NPZ_transfer=False,
  current_authority='FRESH canonicalCNone/current exact LOCAL CIM and original selectedGPU private/shared/resource checks required by ROOT;old219 active binding is historical',
  threshold_source='189 frozen original max(.03,.1V) along/cross + .2 signedyaw;actual roughV=abs original BODYvx,not E2world.5',
  sampler='Original20%stand/BODYvx[-.3,.3]/vy=yaw0/12..16s;no forced directed trials or new reward',
  full_expert_skill='UNKNOWN;this original domain cannot expose retained flat/world spin skills',
  formal_qualification_refs=[dict(path=str(x),SHA=hashlib.sha256(x.read_bytes()).hexdigest()) for x in (a.closing,a.new_cpu)])
 with (a.out_new/'TASK222_PENDING_CURRENT_ADMISSION.json').open('x',encoding='utf8') as out:json.dump(task,out,indent=2,allow_nan=False)
 with (a.out_new/'SOURCE222_INSTALL.json').open('x',encoding='utf8') as out:json.dump(dict(files=rows,model_metadata_only=True,original_runtime_reused=str(model.parent.parent/'runtime')),out,indent=2)
 print(json.dumps(dict(source_task_created=True,current_target_admission=False,model_or_asset_reads=0)))


if __name__=='__main__':main()
