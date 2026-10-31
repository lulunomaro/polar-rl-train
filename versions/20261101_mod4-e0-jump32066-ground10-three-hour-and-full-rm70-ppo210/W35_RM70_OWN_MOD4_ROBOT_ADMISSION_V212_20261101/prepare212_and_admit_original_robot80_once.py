"""ROOT typed original RM70/own MOD480env0PT admission, corrected SDKxyzw."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,posixpath,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_RM70_OWN_ROBOT_20261101v212/robot_admission'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args();assert args.root_lease_label.startswith('ROOT212_EXCLUSIVE_ROBOT_')
 assert H(S/'INDEX208_FROZEN.json')=='e4f5df8fbee2cf1c232e65dbf2068f0f72556aa075b47104ca1c49195bda920a'
 assert H(S/'adapter_v3/INDEX208_ROBOT_XYZW_V3.json')=='e46f930dac40aaf0976740c934932bdc128d4baf2b1a030d402ef8756369035a'
 inputs=read(S/'reports/INSTALL208_SOURCE_INPUTS.json');rows={}
 for r in inputs['base_rows']+inputs['all_binaries_metadata_only']:
  rel=r['installed_relative'];p=Path(r['local_path']);assert p.stat().st_size==r['bytes']
  if p.suffix.lower() not in ('.usd','.usda','.usdc','.npz','.pt'):assert H(p)==r['SHA'],str(p)
  rows[rel]=dict(relative=rel,local=str(p),bytes=r['bytes'],SHA=r['SHA'])
 for folder in (S/'source',S/'adapter_v3'):
  for p in sorted(folder.glob('*.py')):
   rel='runtime/isaac/mod4/'+p.name;ast.parse(p.read_bytes(),filename=str(p))
   rows[rel]=dict(relative=rel,local=str(p),bytes=p.stat().st_size,SHA=H(p))
 for relative,sha,size in [('assets/arena_collision.usdc','9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b',635933),('data/arena_collision.npz','f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954',528810)]:
  p=W/'rmuc2026_training'/relative;assert p.stat().st_size==size
  rows['original_field/'+relative]=dict(relative='original_field/'+relative,asset_relative=relative,local=str(p),bytes=size,SHA=sha)
 rows=list(rows.values());assert all(Path(r['relative']).suffix!='.pt' for r in rows)
 worker='runtime/isaac/mod4/robot0pt208_v3.py';worker_SHA=next(r['SHA'] for r in rows if r['relative']==worker)
 assert worker_SHA=='c5d2cce7b9d00c35b26e327fe6b9f577c8825caa01852718908ea8b32ebdb3b1'
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'prepare212_and_admit_original_robot80_once|install211_|launch210_|install209_|launch209_|install208_|launch208_|collect197_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);cim=json.loads(p.stdout) if p.stdout.strip() else [];cim=cim if isinstance(cim,list) else [cim]
 own=[x for x in cim if x['ProcessId']==os.getpid()];others=[x for x in cim if x['ProcessId']!=os.getpid()]
 put('ROOT212_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=cim,others=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT212_ROBOT0PT_PURPOSE_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),root_lease_label=args.root_lease_label,files=rows,worker_SHA=worker_SHA,
  model_reads=0,actor_critic_optimizer=0,old_raw_reads=0,original_RESET_COLLISION_BANK_constructor_npz_loads=1,new_CAD_query_npz_loads=1,
  source_asset_postcopy_hash_passes=1,num_envs=80,controls=8,physics_callbacks=64,feedback=16,max_original_parent_wait=720,
  old_wxyz_source_not_executed=True,new_xyzw_source='adapter_v3 exact frozen source',no_account_write=True))
 # Reuse only the already-owned finite subprocess/FD mechanics as source.
 src=read_text=(T/'W35_RM70_ORIGINAL_CAD_SCENE_ADMISSION_V211_20261101/install211_scene_source_zeroPT_once.py').read_text('utf8')
 tree=ast.parse(src);node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(z,ast.Name) and z.id=='REMOTE_CODE' for z in n.targets));code=ast.literal_eval(node.value)
 start=code.index("task=dict(kind='NEW208_ORIGINAL_CAD_SCENE_ZERO_PT'");end=code.index('\nlock=',start)
 code=code[:start]+'''task=dict(kind='NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V3',num_envs=80,controls=8,physics_callbacks=64,feedback_samples=16,
 model_opens=0,actor_calls=0,optimizer_updates=0,max_worker_seconds=600,original_manifest_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb',
 actual_parent_exclusive_control_GPU_private_shared_admission=True,GPU_UUID=gpu,worker_SHA=v['worker_SHA'])'''+code[end:]
 code=code.replace("put('SCENE0PT208_TASK.json',task)","put('ROBOT0PT208_V3_TASK.json',task)")
 code=code.replace("str(B/'scene0pt211.py')","str(B/'runtime/isaac/mod4/robot0pt208_v3.py')")
 code=code.replace('p.wait(timeout=300)','p.wait(timeout=720)')
 code=code.replace("B/'scene0pt208/SCENE0PT208_ACTUAL.json'","B/'robot0pt208_v3/OWN_MOD4_ROBOT0PT208_V3_ACTUAL.json'")
 code=code.replace("(B,B/'scene0pt208')","(B,B/'robot0pt208_v3')")
 code=code.replace("value.get('passed_scene_and_route_ground_query')","value.get('passed')")
 code=code.replace('SCENE211','ROBOT212')
 ast.parse(code)
 with (N/'ROOT212_REMOTE_FROZEN_CODE.txt').open('x',encoding='utf8',newline='\n') as f:f.write(code)
 wrapper=module('robot212_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('robot212_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import json,hashlib,time
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
print(json.dumps(dict(passed=True,epoch=time.time(),CNone=True,SHA=hashlib.sha256(raw).hexdigest(),no_C_write=True)))"""
  put('ROOT212_FRESH72_CNONE_BEFORE_ROBOT.json',d.code(client,d.PY72,auth,{},timeout=45))
  create="""from pathlib import Path
import json
B=Path(v['root']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,new_root=str(B))))"""
  put('ROOT212_NEW_NAMESPACE_CREATED.json',d.code(client,d.PY72,create,dict(root=J),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in rows:
    cur=J
    for bit in row['relative'].split('/')[:-1]:
     if not bit:continue
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(row['local'],J+'/'+row['relative'])
  finally:sf.close()
  result=d.code(client,d.PY72,code,dict(job=J,files=rows,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',worker_SHA=worker_SHA),timeout=850)
  put('ROOT212_ORIGINAL_RM70_OWN_ROBOT80_ZERO_PT_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=result['passed'],returncode=result['returncode'],waited=result['all_own_children_waited'],private_EX_released=result['private_EX_released'],parent_error=result['parent_error'],result=result['result'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT212_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT212_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
