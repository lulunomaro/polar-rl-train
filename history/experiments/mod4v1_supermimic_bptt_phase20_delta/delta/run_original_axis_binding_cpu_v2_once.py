"""New purpose CPU-only original pending C113 protocol software test, no native install."""
from pathlib import Path
import sys,json,time,shlex,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/ORIGINAL_C113_AXIS_BINDING_CPU_V2.json';marker=R/'ORIGINAL_C113_AXIS_BINDING_CPU_V2_ONCE.json';assert not out.exists()and not marker.exists()
files={n:(R/'source_runtime'/n).read_bytes()for n in ('original_role_command_binding_candidate_v2.py','synthetic_cpu_original_axis_binding_v2.py')};files['independent_expert_axis_v1.py']=(R/'discovery/reward_command_audit_v1/CURB_INDEPENDENT113/runtime/isaac/mod4/independent_expert_axis_v1.py').read_bytes();pins={n:hashlib.sha256(raw).hexdigest()for n,raw in files.items()}
root=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root']+'/source_checks/ORIGINAL_AXIS_BINDING_CPU_V2_'+str(time.time_ns());remoteout=root+'/SOFTWARE_RESULT_V2.json';marker.write_text(json.dumps(dict(remote_root=root,source_SHA=pins,native_expert_BPTT_steps=0,not_deployed=True),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 _,so,se=c.exec_command('mkdir -p '+shlex.quote(root));err=se.read().decode();assert so.channel.recv_exit_status()==0,err
 for name,raw in files.items():
  with s.open(root+'/'+name,'wb')as f:f.write(raw)
 cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/synthetic_cpu_original_axis_binding_v2.py')+' '+shlex.quote(remoteout)
 _,so,se=c.exec_command(cmd,timeout=180);stdout=so.read().decode(errors='replace');stderr=se.read().decode(errors='replace');rc=so.channel.recv_exit_status();receipt=None
 try:
  with s.open(remoteout,'rb')as f:receipt=json.loads(f.read())
 except OSError:pass
 value=dict(kind='SYNTHETIC_CPU_ORIGINAL_BINDING_V2',source_SHA=pins,remote_root=root,returncode=rc,stdout=stdout,stderr=stderr,receipt=receipt,native_expert_BPTT_steps=0,SDK_GPU_PT_C_GO_lock_mutations=0,active_or_pending_role_sources_modified=False)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0
finally:s.close();c.close()
