"""New corrected-constructor CPU software purpose; V1 failure retained, core unchanged."""
from pathlib import Path
import sys,json,time,shlex,hashlib,ast
R=Path(__file__).resolve().parent;out=R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V2.json';marker=R/'LEGACY_A0_A1_FULL_RESUME_CPU_V2_ONCE.json';assert not out.exists()and not marker.exists()
previous=json.loads((R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json').read_bytes());assert previous['returncode']==1 and'fresh_env.calls == fresh_env.fresh_initializations == 0'in previous['stderr']
paths={
 'test_resume_legacy_torch_cpu_v2.py':(R/'source_resume_torch_validation_v1/test_resume_legacy_torch_cpu_v2.py','4a4141259410702d2103952a828be31a7ddaf28057272b69bbf8a8bde3109e55'),
 'synthetic_cpu_contract_check.py':(R/'source_runtime/synthetic_cpu_contract_check.py','4de256764f7fec0dac6fbb624a7a4189d7a686dc9d28bd5570a9a43f8afce10d'),
 'native_supermimic_bridge.py':(R/'source_runtime/native_supermimic_bridge.py','8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'),
 'ctx_reward_full_resume_candidate_v2.py':(R/'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py','8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac'),
 'resume_runtime_contracts_v3.py':(R/'source_resume_runtime_v2/resume_runtime_contracts_v3.py','dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7'),
 'command_tracking_torch_candidate_v1.py':(R/'source_command_review_v1/command_tracking_torch_candidate_v1.py','bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223')}
files={};pins={}
for name,(path,expected)in paths.items():
 raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==expected,(name,sha);ast.parse(raw.decode('utf-8-sig'));files[name]=raw;pins[name]=dict(local_source=str(path),bytes=len(raw),SHA=sha)
native=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root'];job=native+'/source_checks/LEGACY_A0_A1_FULL_RESUME_CPU_V2_'+str(time.time_ns());resultdir=job+'/NEW_SYNTHETIC_RESULT';deps=native+'/roles/E0/worker_sources/sm_deps';vendor=native+'/roles/E0/worker_sources'
value=dict(kind='CORRECTED_CONSTRUCTOR_SYNTHETIC_LEGACY_FULL_RESUME_CPU_V2',remote_root=job,source_pins=pins,dependency_path=deps,prior_failure_preserved=str(R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json'),core_worker_contracts_unchanged=True,native_expert_BPTT_steps=0,original_PT_SDK_GPU_C_GO_lock_mutations=0)
marker.write_text(json.dumps(value,indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 s.mkdir(job)
 for name,raw in files.items():
  with s.open(job+'/'+name,'wb')as f:f.write(raw)
 args=[job+'/test_resume_legacy_torch_cpu_v2.py','--vendor-parent',vendor,'--dependency-path',deps,'--fixture',job+'/synthetic_cpu_contract_check.py','--bridge-source',job+'/native_supermimic_bridge.py','--payload-core',job+'/ctx_reward_full_resume_candidate_v2.py','--resume-contracts',job+'/resume_runtime_contracts_v3.py','--raw35-source',job+'/command_tracking_torch_candidate_v1.py','--output-dir',resultdir]
 cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+' '.join(shlex.quote(x)for x in args)
 i,so,se=c.exec_command(cmd,timeout=300);i.close();stdout=so.read().decode(errors='replace');stderr=se.read().decode(errors='replace');rc=so.channel.recv_exit_status();receipt=None
 try:
  with s.open(resultdir+'/SYNTHETIC_TORCH_RESUME_RECEIPT_V2.json','rb')as f:receipt=json.loads(f.read())
 except OSError:pass
 value.update(returncode=rc,stdout=stdout,stderr=stderr,receipt=receipt)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,stderr)
finally:s.close();c.close()
