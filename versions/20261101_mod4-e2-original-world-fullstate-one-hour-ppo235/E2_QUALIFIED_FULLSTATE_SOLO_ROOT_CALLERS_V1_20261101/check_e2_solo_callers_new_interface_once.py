"""NEW caller ABI/AST purpose only;no old fixtures or transport/runtime."""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,time,traceback
from caller_common import *

def literals(p):
 return {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
def main():
 purpose=read(R/'CPU_E2_CALLERS_PURPOSE_FROZEN.json');assert purpose['executions']==1
 put('CPU_E2_CALLERS_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixture_replays=0))
 files=sorted(N.glob('*.py'));assert len(files)==8
 texts={p.name:p.read_text(encoding='utf8') for p in files}
 for s in texts.values():ast.parse(s)
 payload=literals(N/'remote_e2_solo_payloads.py');add=literals(N/'remote_e2_solo_additions.py')
 embedded=dict(payload,**add)
 normal_tree=ast.parse(texts['collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py'])
 embedded['COLLECT_NODE']=next(ast.literal_eval(x.value) for x in normal_tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='COLLECT_NODE' for t in x.targets))
 embedded['NORMAL_OWNER']=next(x.value for x in ast.walk(normal_tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and 'segments=[s for s in c' in x.value)
 assert len(embedded)==10
 for s in embedded.values():ast.parse(s)
 prohibited=[]
 for name,s in dict(texts,**embedded).items():
  for node in ast.walk(ast.parse(s)):
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('kill','terminate','send_signal'):prohibited.append(name)
 assert not prohibited
 for name,s in texts.items():
  if name.startswith(('launch_','collect_','review_','remote_')):assert 'W35' not in s and 'RM70' not in s,name
 g=dict(run_id='SYNTHETIC_NEW_CALLER_INTERFACE_ONLY',role_key=ROLE,source_model_SHA=SHA,source_SHA=SHA,
  source_iteration=ITER,input_Adam=ADAM,source_saved_LR=LR,genuine_original_E2_WORLD_MOVING_SIGNED4=True,one_original_writer=True,
  max_parent_seconds=3900,exit_headroom_seconds=300,learning_started_epoch=1000.,save_deadline=4600.,nominal_end_epoch=4900.)
 assert validate_original_go(g,g['run_id'])
 rejected=0
 for key,value in [('role_key','w35_72'),('source_model_SHA','0'*64),('source_iteration',ITER+1),('input_Adam',ADAM+1),
  ('source_saved_LR',LR*2),('max_parent_seconds',4000),('genuine_original_E2_WORLD_MOVING_SIGNED4',False),('save_deadline',4601.)]:
  bad=dict(g);bad[key]=value
  try:validate_original_go(bad,g['run_id'])
  except AssertionError:rejected+=1
  else:raise AssertionError('New caller rejection failed: '+key)
 assert not normal900_eligible(g,3999.99,False) and normal900_eligible(g,4000.,False) and normal900_eligible(g,0,True)
 launch=texts['launch_e2_solo_install_FIRST_ROOT_ONLY_once.py'];lt=ast.parse(launch)
 stage=next(x for x in lt.body if isinstance(x,ast.FunctionDef) and x.name=='stage')
 env={'PurePosixPath':PurePosixPath};exec(compile(ast.Module(body=[stage],type_ignores=[]),'<new wx stage interface>','exec'),env)
 class File:
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def write(self,b):assert b==b'new metadata only'
  def flush(self):pass
 class SFTP:
  def __init__(self):self.modes=[]
  def mkdir(self,p):pass
  def file(self,p,mode):self.modes.append(mode);return File()
 sf=SFTP();env['stage'](sf,'/new/e2/meta.json',b'new metadata only');assert sf.modes==['wx']
 assert 'prepare_e2_solo_Task_manifest_Ready_SOURCE_ONLY.py' in launch and "'--scoped-actual232'" in launch and "'--fresh-admission'" in launch
 assert "'--install',str(FINITE/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json')" in launch and "completed.returncode==0" in launch
 assert "dict(passed=True,kind=" not in launch and "ready=read(staging/'ADMISSION_E2_SOLO_READY.json')" in launch
 assert 'verify_index(FINITE/' in launch and 'verify_index(SOURCE/' in launch and 'verify_index(N/INDEX' in launch
 assert launch.index('qualified_cpu(cpu')<launch.index('wrapper.install()') and launch.index('scoped232(scope)')<launch.index('wrapper.install()')
 assert "root=O,module='e2_solo_finite_owner_authority72.py'" in launch and "root=J+'/control_e2_solo',module='e2_solo_fullstate_slot_node.py'" in launch
 assert launch.count('expected_control_cwd=CONTROL_CWD')==2 and 'os.chdir(' not in payload['SPAWN']
 assert "Path.cwd().resolve()==Path(v['expected_control_cwd']).resolve()" in payload['SPAWN']
 assert 'time.time()+850' in payload['FIRST'] and "==859300" in payload['FIRST'] and '==859320' in payload['FIRST'] and '==42823' in payload['FIRST']
 assert 'NATIVE24_E2_ORIGINAL_ACTUAL.json' in payload['FIRST'] and 'E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json' in payload['FIRST']
 assert "or closed,'Original signed remote900" in embedded['NORMAL_OWNER'] and "normal900_eligible(go['e2']" in texts['collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py']
 assert 'time.time()+850' in embedded['NORMAL_OWNER'] and 'time.time()+180' in embedded['COLLECT_NODE']
 assert 'source_readcounts_before_Appclose=counts' in embedded['COLLECT_NODE'] and 'counts[\'source_decodes\']==1' in embedded['COLLECT_NODE']
 d=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE'
 oldpayload=literals(d/'remote227D_payloads.py')
 assert payload['AUTH']==oldpayload['AUTH'] and payload['SPAWN']==oldpayload['SPAWN'] and payload['OWNER_STATE']==oldpayload['OWNER_STATE']
 oldnormal=ast.parse((d/'collect227D_original_W35_formal_cost_normal900_UNUSED_once.py').read_bytes())
 oldcode=next(x.value for x in ast.walk(oldnormal) if isinstance(x,ast.Constant) and isinstance(x.value,str) and 'segments=[s for s in c' in x.value)
 a=oldcode[oldcode.index('segments=[s for s in c'):oldcode.index('texts=[]')]
 b=embedded['NORMAL_OWNER'][embedded['NORMAL_OWNER'].index('segments=[s for s in c'):embedded['NORMAL_OWNER'].index('texts=[]')]
 assert a==b,'Original independent rawfee/sumonce/shared-release body byte reused'
 install=read(FINITE/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json')
 w=next(x for x in install['files'] if x['relative']=='worker_e2_original_fullPPO.py')
 assert w['SHA']=='d7aa9a57e90eb93ff51b332e1a4d1e7d290fbaf0c25d643639d44f5f5d7569f1'
 assert all(not x['relative'].endswith(('.pt','.partial','.active')) for x in install['files'])
 cpu=texts['review_e2_solo_NEW_formal_initial_whole_CPU_ROOT_ONLY_once.py'];ct=ast.parse(cpu)
 loads=[x for x in ast.walk(ct) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='torch' and x.func.attr=='load']
 assert len(loads)==1 and 'weights_only=False' in cpu and 'typed_E2_original_world_PPO_task' in cpu
 assert '859300+20*updates' in cpu and '42822+updates' in cpu and 'actual_saved_optimizer_LR' in cpu and "saved>=go['save_deadline']" in cpu
 assert cpu.index("os.environ['CUDA_VISIBLE_DEVICES']=''")<cpu.index(' import torch')
 put('CPU_E2_SOLO_CALLERS_NEW_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=len(files),embedded_remote_AST=len(embedded),
  groups=['exact_E2_source_role_V2_generator_and_current_authority','wx_and_cwd_original_owner_node_control','FIRST_850_and_normal900_AND_remote_850_180_original_rawfee','NEWformal_only_read_decode1_typed_DR_command_counts_LR'],
  new_GO_refusals=rejected,new_normal900_boundary_cases=3,new_wx_inmemory_case=1,original_charge_body_byte_reused=True,
  original_AUTH_SPAWN_OWNER_STATE_byte_reused=True,selected_V2_worker_SHA=w['SHA'],model_asset_raw_Torch_SDK_network_Git=0,old_fixture_replays=0,ROOT_actual_calls='UNUSED_PENDING'))
if __name__=='__main__':
 try:main()
 except BaseException:put('CPU_E2_CALLERS_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
