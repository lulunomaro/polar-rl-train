"""Assemble and stage one unused Fudan E3 warm branch; no selected PT/SDK/GO/C operation."""
from pathlib import Path
import sys,time,json,hashlib,ast,shlex
D=Path(__file__).resolve().parent;R=D.parent/'mod4v1_supermimic_bptt_20261102';T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';P=D/'native_payload_v3_admission';assert not P.exists()and not(D/'FDN_W3_STAGE_ONCE.json').exists();P.mkdir();U=P/'uploads';W=U/'worker_sources';W.mkdir(parents=True);H=lambda b:hashlib.sha256(b).hexdigest();kind='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1';run='MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run

def cp(src,dst):
 src=Path(src);assert src.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors');raw=src.read_bytes()
 if src.suffix=='.py':ast.parse(raw.decode('utf8'))
 dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(raw)

def put(p,x):assert not p.exists();p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8')
for name in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):cp(D.parent/'mod4v1_e3_continue_v2_20261104/payload'/name,P/name)
cp(D/'source_original_owner_v2/fudan_original_owner_v1.py',P/'fudan_original_owner_v1.py');cp(D/'stage_fudan_nonpt_v2.py',P/'stage_fudan_nonpt_v2.py');cp(D/'source_original_owner_v2/fudan_worker_close_contract_v1.py',W/'fudan_worker_close_contract_v1.py');cp(D/'source_fudan_seq_ppo_v1/fudan_seq_ppo.py',W/'fudan_seq_ppo.py');cp(D/'source_fudan_native_worker_v2/worker_fudan_sequence_ppo_native_v1.py',W/'worker_fudan_sequence_ppo_native_v1.py');cp(D/'source_task_runtime_v1/e3_fudan_task_runtime_v1.py',W/'e3_fudan_task_runtime_v1.py');cp(D/'CONTRACT_PARITY_AND_POSE_V2.json',U/'fudan_task_pose.json')
for name in('app_close_semantics_v6.py','resume_runtime_contracts_v3.py','pose_cache_runtime_adapter_v4.py'):cp(R/'payload_a1_v6_small_source/source'/name,W/name)
base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_PPO_CONTINUE67EE_W2_SAVENAMESPACE_20261104_142648_1793773608384136500/roles/E3';put(P/'SOURCE_PLAN.json',dict(kind=kind,run_id=run,base_root=base,asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'))
files=[]
for p in P.rglob('*'):
 if p.is_file():raw=p.read_bytes();files.append(dict(path=p.relative_to(P).as_posix(),bytes=len(raw),sha256=H(raw)))
put(D/'FDN_W3_STAGE_ONCE.json',dict(epoch=time.time(),root=root,run_id=run,payload=files,new_native_updates_claim=0));sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp();report=dict(root=root,run_id=run,source_PT_reads=0,SDK_GPU_GO_C_or_lock_operations=0)
def mkdir(p):
 try:s.stat(p)
 except FileNotFoundError:
  parent=p.rsplit('/',1)[0]
  if parent:mkdir(parent)
  s.mkdir(p)
try:
 try:s.stat(root);raise RuntimeError('New unused root required')
 except FileNotFoundError:pass
 mkdir(root)
 for f in files:
  target=root+'/'+f['path'];mkdir(target.rsplit('/',1)[0]);raw=(P/f['path']).read_bytes();assert H(raw)==f['sha256']
  with s.open(target,'wx')as z:z.write(raw)
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/stage_fudan_nonpt_v2.py')+' '+shlex.quote(root);i,o,e=c.exec_command(command,timeout=400);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stdout=stdout,stderr=stderr);assert rc==0,(rc,stderr)
 for name in('OWNER_PLAN.json','STAGE_COMPLETE.json'):
  with s.open(root+'/'+name,'rb')as z:raw=z.read()
  (D/('FDN_W3_'+name)).write_bytes(raw)
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote('import sys,json;sys.path.insert(0,'+repr(root)+');import fudan_original_owner_v1 as m;m.verify_sources(json.loads((m.B/"OWNER_PLAN.json").read_bytes()));print("Original owner source-only preflight passed; SDK/models/GO/C writes0")');i,o,e=c.exec_command(command,timeout=180);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();report.update(owner_source_preflight_rc=rc,owner_source_preflight_stdout=a,owner_source_preflight_stderr=b);assert rc==0,b
finally:
 s.close();c.close();put(D/'FDN_W3_STAGE_RESULT.json',report);print(json.dumps(report,indent=2))
