"""Explicit one-shot launch, token generated in memory, never cfg/TASK/disk/argv."""
from pathlib import Path
import json,os,secrets,subprocess,sys,time,traceback
from flat90_bound_cfg_v1 import bound_cfgs,logical_argv,expected_exec,OWNER_NAME,NODE_NAME
from flat90_protocol_v1 import JOB,validate_payload,load_actual_flat_preinstalled_CPU
B=Path(__file__).resolve().parent
def save(name,value):
 with (B/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def own(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
def start(cfg,root,name):
 args=logical_argv(root,name);env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
 result=subprocess.run(args,input=json.dumps(cfg),capture_output=True,text=True,env=env,timeout=30)
 assert result.returncode==0,(result.returncode,result.stderr)
 value=json.loads(result.stdout);identity=own(value['detached_pid']);expected=expected_exec(args)
 assert all(identity[k]==expected[k] for k in ('exe','argv','root'))
 save(('OWNER' if cfg['role']=='owner' else 'NODE')+'_EXACT_LAUNCHED_IDENTITY.json',identity)
 return identity
def main():
 request=json.loads(sys.stdin.readline());assert 'token' not in request
 assert not (B/'FLAT90_LAUNCH_ENTERED_ACTUAL.json').exists() and not (Path(JOB)/'job0/GO_PRODUCTION.json').exists() and not (Path(JOB)/'job0/production').exists()
 token=secrets.token_hex(32);owner_cfg,node_cfg=bound_cfgs(request,token)
 validate_payload(node_cfg,request['node_root']);load_actual_flat_preinstalled_CPU(node_cfg,request['node_root'])
 save('FLAT90_LAUNCH_ENTERED_ACTUAL.json',dict(epoch=time.time(),launcher=own(os.getpid()),request_without_secret=request,
  one_owner_one_real_h1_flat90_node=True,token_memory_stdin_only=True,no_cfg_Task_or_report_token_write=True))
 owner=start(owner_cfg,request['owner_root'],OWNER_NAME);node=start(node_cfg,request['node_root'],NODE_NAME)
 token=None;owner_cfg=None;node_cfg=None
 value=dict(epoch=time.time(),owner=owner,node=node,token_not_written=True,source_CPU_reused_without_model_reload=True,
  actual_GO_worker_CUDA_native_outcome_not_claimed_by_launcher=True)
 save('FLAT90_SINGLE_OWNER_NODE_LAUNCH_RETURNED_ACTUAL.json',value);print(json.dumps(value))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('FLAT90_LAUNCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_force_kill_or_account_clear=True));raise
