from pathlib import Path
import sys,os,json,time,hashlib,shlex
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_linux_runtime_cpu_once import S
D=Path(__file__).resolve().parent
def main():
    assert not (D/'reports/LINUX20K_DISPATCH_ACTUAL_RECEIPT.json').exists()
    local=json.loads((D/'TARGET_SOURCEFREEZE_CPU_ACTUAL.json').read_bytes())
    assert local['cpu']['passed'] and local['available_RAM_B']>=55000000000 and local['durable_free_B']>=30000000000
    actual=json.loads((D/'windows_manifest_actual.json').read_bytes())['TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json']
    m=dict(actual)
    m.update(num_envs=20000,seed=20260928,approved_for_new_Linux4090_scope=True,source=dict(path=S+'/source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt',sha256='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9',bytes=1770679),target_CPU_receipt=dict(path=S+'/TARGET_FULLSTATE_CPU_PASSED.json'),sourcefreeze_files=local['sourcefreeze'],max_formal_updates=256,capacity_benchmark_only=False,explicit_Windows512_to_Linux20000_fullstate_dimension_and_ABI_migration=True,repeated_parent_slots_and_future_vector_RNG_layout_change_disclosed=True,backend_PhysX_equivalence_claimed=False,original_20k_D05_DR_not_spliced_into_learned_policy=True,resource_guards=dict(RAM_available_bytes=55000000000,durable_free_bytes=30000000000,GPU_free_bytes=22000000000))
    m['root_review_actual']=dict(GPU_lease_explicitly_granted=True,human_Linux_normal_training_and_Windows_output_authorized=True,laptop_GPU_paused=True,remote3060_eval_only=True,all_new_native_fullrestore_admission_required_before_PPO=True)
    m['source_environment'].pop('RM_RESCUE_DEADLINE',None)
    # Buffer capacity is a resource allocation, not a solver/model tolerance.
    # 1024 actual Windows demand was ~162MiB; preserve generous 4GiB20k headroom.
    m['temporary_small_batch_capacities']['gpu_collision_stack_size']=4294967296
    m['admitted_Windows20k_GPU_buffer_capacities']['gpu_collision_stack_size']=4294967296
    m['temporary_small_batch_capacities']['gpu_max_rigid_contact_count']=8388608
    m['admitted_Windows20k_GPU_buffer_capacities']['gpu_max_rigid_contact_count']=8388608
    m['resource_capacity_disclosure']=dict(collision_stack_bytes=4294967296,rigid_contact_capacity=8388608,solver_TGS32_4_unchanged=True,no_contact_query_COM_health_tolerance_changes=True,new_native_physical_capacity_pass_required=True,Windows20GB_temp_limit_not_applied_to_authorized_fullscale_Linux=True)
    c=connect_linux_only()
    try:
        sf=c.open_sftp();p=D/'linux_resume_parent_guard005_reviewed.py';sf.put(str(p),S+'/payload_v2/'+p.name)
        m['sourcefreeze_files'].append(dict(path=S+'/payload_v2/'+p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        localmanifest=D/'LINUX_SCOPE_MANIFEST_PREPARED.json';localmanifest.write_text(json.dumps(m,indent=2),encoding='utf8');sf.put(str(localmanifest),S+'/LINUX_SCOPE_MANIFEST.json');sf.close()
        script=r'''
from pathlib import Path
import subprocess,os,json,time,hashlib,fcntl
P=Path;R=P(S);M=json.loads((R/'LINUX_SCOPE_MANIFEST.json').read_bytes());assert not (R/'SEQUENCE_ONCE_CONSUMED.json').exists() and not (R/'DISPATCH_RECEIPT.json').exists()
for row in M['sourcefreeze_files']:
 h=hashlib.sha256()
 with P(row['path']).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 assert h.hexdigest()==row['sha256'],row['path']
budget=json.loads(P('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());assert budget['active_segment'] is None and budget['authorized_training_seconds']==1188000
assert len(budget['budget_extensions'])==7 and 36000+sum(x['additional_training_seconds'] for x in budget['budget_extensions'])==1188000
job=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True);assert not job.stdout.strip(),job.stdout
argv=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-u',str(R/'payload_v2/linux_resume_parent_guard005_reviewed.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
stat=P('/proc')/str(p.pid)/'stat';tail=stat.read_text().split(') ',1)[1].split()
receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),argv=argv,cwd=str(R),new_independent_sequence=True,initial_phase='native_pending_actual',PPO_claimed=False,original_budget_SHA=hashlib.sha256(P('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes()).hexdigest())
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
        si,so,se=c.exec_command('python3 -',timeout=35);si.write('S='+repr(S)+'\n'+script);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
        receipt=dict(code=rc,stdout=out.decode(),stderr=err.decode(),single_authorized_Linux_dispatch=True)
        q=D/'reports/LINUX20K_DISPATCH_ACTUAL_RECEIPT.json';q.write_bytes(json.dumps(receipt,indent=2).encode());assert rc==0,str(q);print(out.decode())
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
