"""One explicit mixed launch; no model/SDK/CPU rerun; token only memory/stdin."""
from pathlib import Path
import json,os,secrets,subprocess,sys,time,traceback
from mixed72_next_bound_cfg_v1 import bound_cfgs,logical_argv,expected_exec,validate_owner_sources,OWNER_NAME,W35_NODE_NAME
from mixed72_next_protocol_v1 import validate_both_preinstalled
from W35_mixed72_protocol_v1 import H,JOB as W35_JOB
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
 label='OWNER' if cfg['role']=='owner' else 'NODE_'+cfg['key'].upper()
 save(label+'_EXACT_LAUNCHED_IDENTITY.json',identity)
 return identity

def main():
 request=json.loads(sys.stdin.readline());validate_owner_sources(B,request['owner_manifest_SHA'])
 assert str(B)==request['owner_root'] and not (B/'MIXED_LAUNCH_ENTERED_ACTUAL.json').exists() and not (B/'owner_CONSOLE.log').exists()
 token=secrets.token_hex(32);owner_cfg,h1_cfg,w35_cfg=bound_cfgs(request,token)
 h1node=Path(request['h1_node_root']);w35node=Path(request['w35_request']['node_root'])
 assert H(h1node/request['h1_node_filename'])==request['h1_node_SHA']
 assert H(w35node/W35_NODE_NAME)==request['w35_node_SHA']
 assert not (Path(h1_cfg['job_root'])/'job0/GO_PRODUCTION.json').exists() and not (Path(W35_JOB)/'GO_PRODUCTION.json').exists() and not (Path(W35_JOB)/'adaptation').exists()
 closed=validate_both_preinstalled(h1_cfg,w35_cfg,h1node,w35node)
 save('MIXED_LAUNCH_ENTERED_ACTUAL.json',dict(epoch=time.time(),launcher=own(os.getpid()),request_without_secret=request,registered_real_slots=['h1','w35'],source_CPU_JSON_only_no_weight_reload=True,token_memory_stdin_only=True,no_privateheld_READY_fabrication=True))
 owner=start(owner_cfg,B,OWNER_NAME)
 h=start(h1_cfg,h1node,request['h1_node_filename']);w=start(w35_cfg,w35node,W35_NODE_NAME)
 token=None;owner_cfg=None;h1_cfg=None;w35_cfg=None
 value=dict(epoch=time.time(),owner=owner,nodes={'h1':h,'w35':w},token_not_written=True,all_real_nodes_launched=True,actual_READY_GO_GPU_CUDA_PPO_not_claimed_by_launcher=True)
 save('MIXED_SINGLE_OWNER_TWO_NODES_LAUNCH_RETURNED_ACTUAL.json',value);print(json.dumps(value))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('MIXED_LAUNCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_forcekill_ledgerclear_retry_or_other_writer=True));raise
