"""Human requested host/task lookup, current WM authority exact; no execution."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';B=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101/reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 binding=read(B/'KNOWN_ACTIVE276V3_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 pattern='read_ROOT278_|launch276_|collect276_|close276|read276_|run_ROOT274_|run_ROOT272_|collect270_exact_|run_ROOT267_|collect240_|start240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout)if p.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT278_HUMAN_LQR_HOST_LOOKUP_PURPOSE_AND_FRESH_LOCAL_CIM.json',dict(epoch=time.time(),exact_LOCAL_CIM=rows,human_selected_DSH_session='session-5ee9dc9d-5a3d-49a8-ae31-5c022b269a22',purpose='Read actual72 hostname and existing LQR task text/paths; current WM owner exact; no health watcher/replay/GPU/model/raw/account',expected_current_owner=binding['owner'],expected_run=binding['run_id']))
 client=transport=previous=secret=None
 try:
  transport,previous=module('root278_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root278_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None;peer=client.get_transport().getpeername()
  code="""from pathlib import Path
import hashlib,json,psutil,socket,time
b=v['binding'];o=b['owner'];O=Path(o['root']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
current=json.loads((O/'OWNER_CURRENT.json').read_bytes());assert current['go']==b['original_full_GO']and set(current['go'])=={'jump_72'};g=current['go']['jump_72'];assert g['run_id']==b['run_id']and g['original_owner_pid']==o['pid']and g['original_owner_creation']==o['creation']
if c['active_segment']is not None:
 p=psutil.Process(o['pid']);assert p.create_time()==o['creation']and p.exe()==o['exe']and p.cmdline()==o['argv']and p.cwd()==o['cwd']and c['active_segment']['owner_parent_pid']==o['pid']
 assert c['active_segment']['experts']['jump_72']['started_epoch']==g['learning_started_epoch'];authority='exact_current276V3_active'
else:
 final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes());assert final['go']==b['original_full_GO']and final['original_cost_settled']and exit['original_cost_settled'];authority='same276V3_actually_closed_and_fresh_CNone'
P=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101');assert P.is_dir();rows=[]
for name in('README.md','RESULTS_20261101.md','run.sh','run_case.py','full_lqr.py','linear_mpc.py','hybrid_trial.py','nominal_candidate.json','results/FINAL_FULLDR_MATCHED_V2/summary.json','results/FINAL_EVIDENCE_V2/manifest.json','FINAL_METRICS.json'):
 p=P/name;assert p.is_file();row=dict(path=str(p),bytes=p.stat().st_size)
 if name in('README.md','RESULTS_20261101.md'):
  raw=p.read_bytes();row.update(SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'))
 else:row['content']='METADATA_ONLY_NOT_EXECUTED'
 rows.append(row)
print(json.dumps(dict(passed=True,epoch=time.time(),hostname=socket.gethostname(),task_root=str(P),fresh_authority=authority,owner_run_GO_exact=True,rows=rows,SDK_model_weights_raw_trajectories_GPU_process_scan=0,simulation_replays=0,task_account_training_writes=0)))"""
  result=d.code(client,d.PY72,code,dict(binding=binding),timeout=50);result['actual_pinned_SSH_peer']=list(peer);put('ROOT278_ACTUAL72_LQR_TASK_AND_SOURCE_TEXT_RETURNED.json',result)
  print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT278_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT278_LOOKUP_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_training_change=True));raise
