from pathlib import Path
import json,time,hashlib,sys,msvcrt,psutil
D=Path(__file__).resolve().parent;G=D/'geometry_pose';R=D/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 case=sys.argv[1];agent=sys.argv[2];body=int(sys.argv[3]);world=int(sys.argv[4]);steps=int(sys.argv[5]);factor=sys.argv[6]
 assert agent in ('geometry_pose_factor','forward_reverse_evidence','io_dr_factor') and body in (-1,1) and world in (-1,1) and steps in (120,300,600,1500) and factor in ('baseline','policy','feedback')
 assert case.replace('-','').replace('_','').isalnum()
 proof=json.loads((R/'TRAINING_HANDOFF_FULLSAVE_CPU_ACTUAL.json').read_bytes());assert proof['passed']
 cp=Path(proof['checkpoint']['path']);assert H(cp)==proof['checkpoint']['sha256']
 for prior in (D/'leases').glob('*.json'):
  if prior.name.endswith('_CLOSED_ACTUAL.json'):continue
  data=json.loads(prior.read_bytes());assert (D/'leases'/(data['case_id']+'_CLOSED_ACTUAL.json')).exists(),'prior actual lease not closed'
 lock=D.parent/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock'
 with lock.open('r+b') as stream:
  stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1);stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
 gpu_python=[]
 for p in psutil.process_iter(['name','cmdline','create_time']):
  if p.pid==__import__('os').getpid():continue
  argv=p.info['cmdline'] or []
  if any('local_scope_worker.py' in x or 'paired_geometry_pose.py' in x for x in argv):gpu_python.append(dict(pid=p.pid,argv=argv,creation=p.info['create_time']))
 assert not gpu_python,'owned GPU worker still active'
 worker=G/'paired_geometry_pose.py';runtime=G/'factor_runtime.py';parent=G/'run_factor_once.py'
 expected={'worker':'8efad28f373947e8024b2d0424a5eb61ecc89adc36ec410f4ae8216f782d5d09','runtime':'1dcd103cd9b0a1604bec85b8ac258aef360a721a4a13ccabcf4f38f0cbf68688','parent':'6c910cd23ac8ff7615b99b89f7f4e460bc202c1057b587024c234c595afdbc91'}
 assert H(worker)==expected['worker'] and H(runtime)==expected['runtime'] and H(parent)==expected['parent']
 params=dict(steps=steps,num_envs=8,seed=20260928,body_sign=body,world_sign=world,pitch_deg=0.,roll_deg=0.,height_m=.25,entry_margin=.4,sensor_clean=False,feedback_current=factor=='feedback',policy_factor=factor=='policy',speed=.3,headless=True,device='cuda:0')
 path=D/'leases'/(case+'.json');assert not path.exists();path.write_text(json.dumps(dict(epoch=time.time(),case_id=case,owner_agent=agent,checkpoint_path=str(cp),checkpoint_sha256=H(cp),GPU_lease_granted_by_root=True,owned_training_actual_exit_and_shared_lock_free_verified=True,worker_sha256=expected['worker'],factor_runtime_sha256=expected['runtime'],parent_sha256=expected['parent'],case_parameters=params,shared_native_lock=str(lock),one_GPU_process=True,diagnostic_only_no_PPO=True,new_scope_not_oldjob_replay=True,initialstate_DR_pairing_pending_actual_CPU_check=True),indent=2),encoding='utf8')
 print(json.dumps(dict(passed=True,lease=str(path),case_id=case,owner=agent,params=params)))
if __name__=='__main__':main()
