"""New dependency-corrected CPU purpose; preserve V1 missing-rich receipt.
Frozen candidate/core/test unchanged; add existing sealed worker sm_deps sys.path.
"""
from pathlib import Path
import sys,json,time,shlex,hashlib
R=Path(__file__).resolve().parent;src=R/'source_command_review_v1';out=R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V2.json';marker=R/'COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V2_ONCE.json';assert not out.exists()and not marker.exists()
prior=json.loads((R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V1.json').read_bytes());assert prior['returncode']==1 and prior['receipt']['error']=="No module named 'rich'"
names={'command_tracking_torch_candidate_v1.py':'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223','ctx_reward_candidate_v1.py':'c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454','test_command_tracking_core_integration_cpu_v1.py':'348c1494133292fb3905c5e33f5b55c1dc8a0cca10fcfbc5ba48ace7283f45f4'}
files={n:(src/n).read_bytes()for n in names}
for n,raw in files.items():assert hashlib.sha256(raw).hexdigest()==names[n]
for n in ('synthetic_cpu_contract_check.py','native_supermimic_bridge.py'):files[n]=(R/'source_runtime'/n).read_bytes()
pins={n:hashlib.sha256(raw).hexdigest()for n,raw in files.items()};native=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root'];job=native+'/source_checks/COMMAND_CORE_INTEGRATION_CPU_V2_DEPS_'+str(time.time_ns());resultdir=job+'/NEW_SYNTHETIC_RESULT';remoteout=resultdir+'/CORE_INTEGRATION_RECEIPT_V1.json';deps=native+'/roles/E0/worker_sources/sm_deps'
marker.write_text(json.dumps(dict(remote_root=job,source_SHA=pins,purpose='SYNTHETIC_CORE_DEPENDENCY_CORRECTION_NO_SOURCE_HOTPATCH',changed_dependency_path=deps,prior_failure_kept=str(R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V1.json'),native_expert_BPTT_steps=0),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 _,so,se=c.exec_command('mkdir -p '+shlex.quote(job));err=se.read().decode();assert so.channel.recv_exit_status()==0,err
 assert s.stat(deps+'/rich/__init__.py').st_size>0
 for n,raw in files.items():
  with s.open(job+'/'+n,'wb')as f:f.write(raw)
 cmd="CUDA_VISIBLE_DEVICES='' PYTHONPATH="+shlex.quote(deps)+' '+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(job+'/test_command_tracking_core_integration_cpu_v1.py')+' --vendor-parent '+shlex.quote(native+'/roles/E0/worker_sources')+' --fixture '+shlex.quote(job+'/synthetic_cpu_contract_check.py')+' --bridge-source '+shlex.quote(job+'/native_supermimic_bridge.py')+' --candidate-dir '+shlex.quote(job)+' --output-dir '+shlex.quote(resultdir)
 _,so,se=c.exec_command(cmd,timeout=300);stdout=so.read().decode(errors='replace');stderr=se.read().decode(errors='replace');rc=so.channel.recv_exit_status();receipt=None
 try:
  with s.open(remoteout,'rb')as f:receipt=json.loads(f.read())
 except OSError:pass
 value=dict(kind='SYNTHETIC_ACTUAL_CANDIDATE_CORE_CPU_TEST_DEPENDENCY_V2',remote_root=job,source_SHA=pins,dependency_path=deps,prior_failure_preserved=True,returncode=rc,stdout=stdout,stderr=stderr,receipt=receipt,native_expert_BPTT_steps=0,SDK_GPU_PT_C_GO_lock_mutations=0,synthetic_noise_tape_is_not_actual_native_amplitude_or_timing_validation=True)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0
finally:s.close();c.close()
