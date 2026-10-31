"""ROOT metadata-only Task builder; no checkpoint/asset/network access."""
from pathlib import Path
import argparse,hashlib,json,sys,time
N=Path(__file__).resolve().parent;T=N.parent
sys.path.insert(0,str(N/'source'))
from contract220 import qualified210,original219_binding,read_ref,validate_task,KIND,GENERATION,GPUS


def main():
 p=argparse.ArgumentParser();p.add_argument('--closing',type=Path,required=True);p.add_argument('--new-cpu',type=Path,required=True)
 p.add_argument('--selected-owner-launch',type=Path);p.add_argument('--selected-owner-state',type=Path)
 p.add_argument('--fresh-cnone',type=Path);p.add_argument('--GPU-UUID',choices=sorted(GPUS),required=True)
 p.add_argument('--out-new',type=Path,required=True);a=p.parse_args()
 model=qualified210(a.closing,a.new_cpu)
 if a.selected_owner_launch:
  assert a.selected_owner_state and a.fresh_cnone is None
  binding=original219_binding(a.selected_owner_launch,a.selected_owner_state)
 else:
  assert a.fresh_cnone and a.selected_owner_state is None
  v,ref=read_ref(a.fresh_cnone);assert v['CNone'] and v['generation']==GENERATION and v['active_segment'] is None
  binding=dict(kind='FRESH_CNONE',authority_generation=GENERATION,local_refs=[ref])
 assert not a.out_new.exists();a.out_new.mkdir(parents=True)
 worker=N/'evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py';raw=worker.read_bytes()
 task=dict(kind=KIND,source_status='ROOT_QUALIFIED_MODEL_PENDING_ACTUAL_TARGET_ADMISSION',epoch=time.time(),**model,
  target_host='72',GPU_UUID=a.GPU_UUID,num_envs=1,controls_max=1000,physics_callbacks_max=8000,feedback_samples_max=2000,
  policy_hz=50,physics_dt=.0025,TGS=[32,4],feedback_hz=100,seed=27,worker_seconds=840,parent_wait_seconds=900,
  eval_yaw_range=[0.,0.],vx_range=[-2.1,2.1],height_range=[.12,.15],
  no_optimizer_or_training_or_budget_write=True,model_byte_reads=1,model_decodes=1,model_copies=0,
  current_authority_binding=binding,actual_parent_private_EX_and_authority_admitted=False,
  sdk_python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',worker_SHA=hashlib.sha256(raw).hexdigest(),
  body_geometry_scope='Already-loaded own wheel CollisionAPI mesh points each once, bounded metadata only;UNKNOWN accepted',
  artifact_transfers=0,GUI_requested=False,training_reward_changed=False,full_270_or_population_success_claim=False)
 validate_task(task)
 with (a.out_new/'TASK220.json').open('x',encoding='utf8') as f:json.dump(task,f,indent=2,allow_nan=False)
 names=['evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py','target220_single_N1_parent_UNUSED.py','zonglin2_app_launcher.py']
 files=[]
 for relative in names+['source/'+s for s in ['contract220.py','wheel_geometry220.py','flight_evidence220.py']]:
  data=(N/relative).read_bytes();dst=a.out_new/relative;dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb') as f:f.write(data)
  files.append(dict(relative=relative,bytes=len(data),SHA=hashlib.sha256(data).hexdigest()))
 t=(a.out_new/'TASK220.json').read_bytes();files.append(dict(relative='TASK220.json',bytes=len(t),SHA=hashlib.sha256(t).hexdigest()))
 with (a.out_new/'PACKAGE220_SOURCE_AND_TASK.json').open('x',encoding='utf8') as f:
  json.dump(dict(kind=KIND,files=files,model_metadata_only=model,model_or_asset_copies=0),f,indent=2,allow_nan=False)
 print(json.dumps(dict(source_task_ready=True,new_task=str(a.out_new/'TASK220.json'),model_SHA=model['model_SHA'],
  model_iteration=model['model_iteration'],model_path=model['model_path'],current_authority_kind=binding['kind'],
  target_admitted=False,PT_NPZ_USD_raw_SDK_GPU_SSH_calls=0)))


if __name__=='__main__':main()
