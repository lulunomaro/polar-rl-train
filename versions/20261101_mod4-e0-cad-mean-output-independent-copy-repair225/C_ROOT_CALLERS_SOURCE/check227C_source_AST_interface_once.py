"""New C source/embedded-code AST+interface checks only. No caller imports."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

N=Path(__file__).resolve().parent


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 purpose=json.loads((N/'reports/CPU227C_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/CPU227C_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=purpose['ID']))
 trees={};texts={}
 for r in purpose['sources']:
  p=Path(r['path']);b=p.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
  trees[p.name]=ast.parse(b,filename=str(p));texts[p.name]=b.decode('utf8')
 code_count=0
 for name in ('remote227C_payloads.py','remote227C_additions.py'):
  for node in trees[name].body:
   if isinstance(node,ast.Assign):
    code=ast.literal_eval(node.value);ast.parse(code,filename=name+':'+node.targets[0].id);code_count+=1
 for node in ast.walk(trees['collect227C_original_W35_formal_cost_normal900_UNUSED_once.py']):
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('COLLECT_NODE','code') for t in node.targets) and isinstance(node.value,ast.Constant):
   ast.parse(node.value.value);code_count+=1
 launcher=texts['launch227C_install_original_solo_W35_FIRST_UNUSED_once.py']
 assert "sf.file(remote,'wx')" in launcher and "target.POSTCOPY_NO_MODEL" in launcher
 assert "A/'prepare227_Task_manifest_Ready_SOURCE_ONLY.py'" in launcher
 assert launcher.index('qualification=qualified(')<launcher.index('cim=exact_cim(')<launcher.index('wrapper=module(')
 assert "N.parents[1]" in texts['collect227C_original_W35_formal_cost_normal900_UNUSED_once.py']
 remote_values={node.targets[0].id:ast.literal_eval(node.value) for node in trees['remote227C_payloads.py'].body if isinstance(node,ast.Assign)}
 assert 'POSTCOPY_AND_SOURCE_COPY' not in remote_values and "v['source']" not in remote_values['POSTCOPY_NO_MODEL']
 assert "os.chdir(v['root'])" in remote_values['SPAWN']
 assert 'time.time()+850' in remote_values['FIRST'] and '649720' in remote_values['FIRST'] and '649740' in remote_values['FIRST'] and '32405' in remote_values['FIRST']
 normal=texts['collect227C_original_W35_formal_cost_normal900_UNUSED_once.py']
 assert 'nominal-time.time()<=900' in normal and 'end=time.time()+850' in normal and 'end=time.time()+180' in normal
 assert 'rawsum=sum(fees.values())' in normal and "actual_source_host_SHA=sha" in normal
 cpu=texts['review227C_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py']
 assert '649720+20*updates' in cpu and "ck['iter']==32404+updates" in cpu
 assert "os.environ['CUDA_VISIBLE_DEVICES']=''" in cpu and 'torch.load(io.BytesIO(raw)' in cpu
 assert 'weights_only=False' in cpu and 'same_RM70_course_assignment_and_command_fullstate_restored' in cpu
 put(N/'reports/CPU227C_SOURCE_AST_INTERFACE_ACTUAL.json',dict(passed=True,ID=purpose['ID'],
  source_AST_count=len(trees),embedded_remote_AST_count=code_count,
  four_ROOT_entrypoints_source_complete=True,source_A_B_frozen_bytes_unmodified=True,
  actual_Task_Ready_fresh_CNone_CIM_resources_and_ROOT_execution='PENDING',
  selected343e_installer_model_open_stat_copy_hash_decode=0,
  production_selected_source_byte_read=1,production_selected_source_decode=1,
  old_fixture_replays=0,PT_NPZ_USD_actualraw_Torch_SDK_GPU_SSH_Git_calls=0))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/CPU227C_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
