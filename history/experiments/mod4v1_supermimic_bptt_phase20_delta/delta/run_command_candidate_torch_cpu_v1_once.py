"""Execute frozen two-file SYNTHETIC CPU software purpose, no expert counts."""
from pathlib import Path
import sys,json,hashlib,time,shlex
R=Path(__file__).resolve().parent;src=R/'source_command_review_v1';out=R/'reports/COMMAND_CANDIDATE_TORCH_CPU_V1.json';marker=R/'COMMAND_CANDIDATE_TORCH_CPU_V1_ONCE.json'
assert not out.exists()and not marker.exists()
expected={'command_tracking_torch_candidate_v1.py':'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223','test_command_tracking_torch_cpu_v1.py':'3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703'}
blobs={name:(src/name).read_bytes()for name in expected}
for name,raw in blobs.items():assert hashlib.sha256(raw).hexdigest()==expected[name]
dispatch=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes());print('dispatch_keys',list(dispatch))
root=dispatch.get('root')or dispatch.get('remote_root')or dispatch.get('job_root');assert root and root.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_')
job=root+'/source_checks/COMMAND_TRACKING_TORCH_CPU_V1_'+str(time.time_ns());remoteout=job+'/TORCH_SOFTWARE_RECEIPT_V1.json';marker.write_text(json.dumps(dict(remote_root=job,source_SHA=expected,purpose='SYNTHETIC_COMPONENT_SOFTWARE_TEST_ONLY',native_expert_BPTT_optimizer_steps=0,epoch=time.time()),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 command='mkdir -p '+shlex.quote(job);_,so,se=c.exec_command(command);err=se.read().decode();assert so.channel.recv_exit_status()==0,err
 for name,raw in blobs.items():
  with s.open(job+'/'+name,'wb')as f:f.write(raw)
 command="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(job+'/test_command_tracking_torch_cpu_v1.py')+' --output '+shlex.quote(remoteout)
 _,so,se=c.exec_command(command,timeout=240);stdout=so.read().decode(errors='replace');stderr=se.read().decode(errors='replace');rc=so.channel.recv_exit_status();receipt=None;receipt_error=None
 try:
  with s.open(remoteout,'rb')as f:receipt=json.loads(f.read())
 except OSError as e:receipt_error=type(e).__name__+':'+str(e)
 result=dict(kind='SYNTHETIC_CPU_TORCH_COMPONENT_TEST',remote_root=job,source_SHA=expected,returncode=rc,stdout=stdout,stderr=stderr,receipt=receipt,receipt_read_error=receipt_error,native_expert_BPTT_optimizer_steps=0,SDK_GPU_sourcePT_raw_C_GO_or_lock_mutations=0)
 out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(out);print(json.dumps(result,indent=2));assert rc==0
finally:s.close();c.close()
