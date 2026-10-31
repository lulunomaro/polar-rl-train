"""Source-only derivation of ROOT actual219V3 lifecycle callers. No execution."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

N=Path(__file__).resolve().parent
P=N.parent
T=P.parent
OLD=T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101'
A=P/'A_PPO_SOURCE'


def write(p,b):
 with p.open('xb') as f:f.write(b)
def put(p,v):write(p,json.dumps(v,indent=2,allow_nan=False).encode())
def ref(p):
 b=p.read_bytes();return dict(local_path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def once(text,old,new):
 assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)


def main():
 purpose=json.loads((N/'reports/DERIVE227C_PURPOSE_FROZEN.json').read_bytes())
 for r in purpose['source_inputs']:
  assert ref(Path(r['local_path']))==r
 remote=OLD/'source/remote219_payloads.py'
 payload={}
 for node in ast.parse(remote.read_bytes()).body:
  if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
   payload[node.targets[0].id]=ast.literal_eval(node.value)
 payload['CREATE']=payload['CREATE'].replace("J/'control219'","J/'control227'")
 original_post=payload.pop('POSTCOPY_AND_SOURCE_COPY')
 stop=original_post.index("src=Path(v['source']['original_target_path'])")
 payload['POSTCOPY_NO_MODEL']=original_post[:stop]+'''raw=(B/'RM70_BINARY_INSTALL_ACTUAL.json').read_bytes()
generated=[dict(relative='RM70_BINARY_INSTALL_ACTUAL.json',bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())]
print(json.dumps(dict(passed=True,source_asset_postcopy_passes=1,files=len(rows),selected_model_stat_hash_copy_open_decode=0,generated_metadata_rows=generated,no_GPU_or_account_write=True)))'''
 payload['SPAWN']="import os\nos.chdir(v['root'])\n"+payload['SPAWN']
 payload['FIRST']=payload['FIRST'].replace('control219','control227').replace('PREDELEGATE218','PREDELEGATE227')
 for old,new in [('648360','649720'),('648380','649740'),('32337','32405')]:
  payload['FIRST']=payload['FIRST'].replace(old,new)
 write(N/'remote227C_payloads.py',('"""ROOT-only original219V3 remote payloads, narrow227 source/cwd changes."""\n'+
       '\n\n'.join(k+' = '+repr(v) for k,v in payload.items())+'\n').encode())
 normal_path=OLD/'collect219V3_original_W35_formal_cost_normal900_UNUSED_once.py'
 normal=normal_path.read_text(encoding='utf8')
 normal=normal.replace('ROOT219V3','ROOT227C').replace('control219','control227').replace('current_closed219_models','current_closed227_models')
 normal=once(normal,'import hashlib,importlib.util,json,os,subprocess,sys,time,traceback','import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback')
 normal=once(normal,"N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'", "N=Path(__file__).resolve().parent;T=N.parents[1];W=T.parent;R=N/'reports'")
 normal=once(normal,'def main():\n', '''def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);parser.add_argument('--auth-provider',type=Path,required=True);parser.add_argument('--additional-control-pattern',required=True);parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 assert args.root_lease_label.startswith('ROOT227C_EXCLUSIVE_NORMAL900_') and args.additional_control_pattern
 from launch227C_install_original_solo_W35_FIRST_UNUSED_once import verify_index
 verify_index(N/'INDEX227C_FROZEN.json',args.caller_index_SHA)
''')
 start=normal.index(" query=r'''")
 end=normal.index('\n p=subprocess.run',start)
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'CONTROL_PATTERN' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 normal=normal[:start]+" pattern='collect227C_|launch227C_|review227C_|collect219V3_|launch219_|launch210_|prepare212_|install211_|install209_|launch209_|human196_194_one_saved|collect194_original|start195_literal|collect195_original|install195_literal|'+args.additional_control_pattern\n query="+repr(query)+".replace('CONTROL_PATTERN',pattern.replace(\"'\",\"''\"))"+normal[end:]
 normal=once(normal,"sec=module('normal210_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')", "sec=module('normal227C_auth',args.auth_provider)")
 write(N/'collect227C_original_W35_formal_cost_normal900_UNUSED_once.py',normal.encode())
 cpu_path=OLD/'review219V3_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py'
 cpu=cpu_path.read_text(encoding='utf8')
 cpu=cpu.replace('ROOT219V3','ROOT227C').replace('current_closed219_models','current_closed227_models')
 cpu=once(cpu,'import hashlib,io,json,time,traceback','import argparse,hashlib,io,json,time,traceback')
 cpu=once(cpu,'def main():\n', '''def main():
 parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 from launch227C_install_original_solo_W35_FIRST_UNUSED_once import verify_index
 verify_index(N/'INDEX227C_FROZEN.json',args.caller_index_SHA)
''')
 for old,new in [('ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f','343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'),
                 ('648360','649720'),('32336','32404'),('MOD4_W35_FULL_RM70_MATERIAL_SHARED214','MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'),('.00011390625000000003','.00017085937500000009')]:
  cpu=cpu.replace(old,new)
 cpu=once(cpu,"assert t['policy_hz']==50 and t['nominal_gas_N_each']==400 and t['root_quaternion_order']=='xyzw'", "assert t['policy_hz']==50 and t['nominal_gas_N_each']==400 and t['root_quaternion_order']=='xyzw'\n assert t['same_RM70_course_assignment_and_command_fullstate_restored'] and t['source_prior_new_PPO_updates']==68\n assert updates==r['final']['actual_new_PPO_updates']==r['formal']['actual_new_PPO_updates']\n assert ck['iter']==r['formal']['saved_iteration'] and min(steps)==r['formal']['Adam_min']==r['formal']['Adam_max']")
 write(N/'review227C_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py',cpu.encode())
 controls=[dict(relative=p.name,**ref(p)) for p in sorted((A/'control227').glob('*.py'))]
 put(N/'reports/CONTROL227C_A_FROZEN_BINDINGS.json',dict(status='BYTE_REUSE_FROZEN227A_CONTROLS',
  A_INDEX_SHA='b71e3df7327b93c3849eb1ced2ba002e004d714e69b444b0ab08914d18676ed6',
  files=controls,original_owner_HMAC_twofcntl_charge_budget_caps_STOP_save_close_wait_terminal_ACK_unchanged=True))
 put(N/'reports/DERIVE227C_SOURCE_BINDINGS_ACTUAL.json',dict(epoch=time.time(),status='SOURCE_ONLY_NO_ROOT_EXECUTION',
  source_inputs=purpose['source_inputs'],actual219V3_original_rawfee_normal900_and_newCPU_templates_reused=True,
  changes=['A contract/generator/INSTALL;343e32404Adam649720LR.00017085937500000009',
           'Model copy/stat/hash/decode removed from installer;original runtime+asset postcopy retained',
           'Remote spawn prefixes os.chdir(root),owner/node separate;original node worker cwd=job retained',
           'FIRST counters649720->649740/32405;original850 wait',
           'Normal report/control namespace and required ROOT auth/lease/currentCIM pattern fields;850/180+rawfees unchanged',
           'NEWformal CPU counter/typedkind/inputLR and actual-final consistency join;no old model reads'],
  PT_NPZ_USD_actualraw_Torch_SDK_GPU_SSH_Git_calls=0))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/DERIVE227C_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
