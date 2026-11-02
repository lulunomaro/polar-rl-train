"""Read only linked SDK backend/reset cache source; no package or SDK import."""
from pathlib import Path
import sys,json,hashlib,shlex
R=Path(__file__).resolve().parent;D=R/'discovery/sdk_reset_cache_backend_v2';out=R/'reports/SDK_RESET_CACHE_BACKEND_SOURCE_V2.json';assert not D.exists()and not out.exists();D.mkdir(parents=True)
old=json.loads((R.parent/'mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json').read_bytes());lab=old['search_locations'][0];source=lab.rsplit('/isaaclab/isaaclab',1)[0]
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();rows=[]
try:
 specs_code="import importlib.util,json;names=['isaaclab_physx','isaacsim'];out={};\nfor name in names:\n spec=importlib.util.find_spec(name);out[name]=None if spec is None else dict(origin=spec.origin,locations=list(spec.submodule_search_locations or []))\nprint(json.dumps(out))"
 _,so,se=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(specs_code),timeout=45);text=so.read().decode();err=se.read().decode();rc=so.channel.recv_exit_status();assert rc==0,(rc,err);specs=json.loads(text)
 backend=(specs.get('isaaclab_physx')or{}).get('locations')or[source+'/isaaclab_physx/isaaclab_physx'];root=backend[0]
 wanted=[('backend/articulation.py',root+'/assets/articulation/articulation.py'),('backend/articulation_data.py',root+'/assets/articulation/articulation_data.py'),('base/manager_based_env.py',lab+'/envs/manager_based_env.py'),('base/timestamped_buffer.py',lab+'/utils/buffers/timestamped_buffer.py')]
 if specs.get('isaacsim')and specs['isaacsim'].get('origin'):wanted.append(('isaacsim/package_init.py',specs['isaacsim']['origin']))
 for local,remote in wanted:
  try:
   with s.open(remote,'rb')as f:raw=f.read()
  except FileNotFoundError as e:rows.append(dict(local=local,remote=remote,status='source_missing',error=str(e)));continue
  assert len(raw)<2_000_000
  dest=D/local;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append(dict(remote=remote,local=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),status='source_read_only'))
 value=dict(kind='TOP_LEVEL_PACKAGE_SPEC_AND_LINKED_BACKEND_SOURCE_ONLY_NOT_LIVE_BINDING',top_level_specs=specs,files=rows,SDK_GPU_PT_raw_C_GO_or_mutation_operations=0,backend_in_actual_previous_worker=None,old_canonical_not_reopened=True)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:s.close();c.close()
