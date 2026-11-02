"""Read bounded source references for Warp buffers/kernel and SimulationApp.close.
No SDK import/instance, GPU/teacher checkpoint/raw/canonical access.
"""
from pathlib import Path
import sys,json,ast,hashlib
R=Path(__file__).resolve().parent;D=R/'discovery/sdk_warp_buffer_appclose_v3';out=R/'reports/SDK_WARP_BUFFER_APPCLOSE_SOURCE_V3.json';assert not D.exists()and not out.exists();D.mkdir(parents=True)
prior=json.loads((R/'reports/SDK_RESET_CACHE_BACKEND_SOURCE_V2.json').read_bytes());backend=next(x['remote']for x in prior['files']if x['remote'].endswith('/assets/articulation/articulation.py')).split('/assets/')[0];base=next(x['remote']for x in prior['files']if x['remote'].endswith('/envs/manager_based_env.py')).split('/envs/')[0];appbase=prior['top_level_specs']['isaacsim']['locations'][0]
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();rows=[]
def fetch(local,remote):
 try:
  with s.open(remote,'rb')as f:raw=f.read()
 except FileNotFoundError as e:rows.append(dict(remote=remote,status='source_missing',error=str(e)));return None
 assert len(raw)<2_000_000
 dest=D/local;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append(dict(remote=remote,local=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),status='source_only'));return raw
try:
 raw=fetch('buffers/package_init.py',base+'/utils/buffers/__init__.py')
 if raw:
  for node in ast.walk(ast.parse(raw)):
   if isinstance(node,ast.ImportFrom)and any(a.name=='TimestampedBufferWarp'for a in node.names):
    assert node.level==1 and node.module and'..'not in node.module
    fetch('buffers/'+node.module.replace('.','/')+'.py',base+'/utils/buffers/'+node.module.replace('.','/')+'.py')
 fetch('backend/kernels.py',backend+'/assets/kernels.py')
 bounded_names=[]
 for container in ('exts','extscache'):
  parent=appbase+'/'+container
  try:names=sorted(n for n in s.listdir(parent)if n.startswith('isaacsim.simulation_app'))
  except FileNotFoundError:names=[]
  assert len(names)<=8
  for i,n in enumerate(names):
   assert '/'not in n and'\\'not in n
   remote=parent+'/'+n+'/isaacsim/simulation_app/simulation_app.py';bounded_names.append(remote);fetch('app/'+container+'_'+str(i)+'_simulation_app.py',remote)
 value=dict(kind='LINKED_WARP_AND_APPCLOSE_SOURCE_ONLY',files=rows,app_bounded_candidates=bounded_names,SDK_GPU_PT_raw_C_GO_or_mutation_operations=0,actual_previous_worker_close_method_or_fast_shutdown_configuration=None)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:s.close();c.close()
