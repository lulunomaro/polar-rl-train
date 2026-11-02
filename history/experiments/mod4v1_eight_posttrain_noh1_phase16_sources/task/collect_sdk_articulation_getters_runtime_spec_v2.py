"""Actualtop-levelmoduleSPECwithoutimportSDK. direct_urleditablehistoricalpathwasmissing; preservefailure."""
from pathlib import Path
import json,hashlib,base64,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1';out=D/'ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json';assert not out.exists();e=D/'EDITABLE_DIRECT_URL_MISSING_SOURCE_ERROR_V1.json';assert not e.exists();e.write_text(json.dumps({'kind':'METADATA_EDITABLE_DIRECT_URL_STALE_OR_MISSING_NOT_ACTUAL_MODULE_ORIGIN','attempted_source':'/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/assets/articulation/articulation_data.py','error':'FileNotFoundError [Errno2]','job':'pwsh-dbe6989a2066443c','no_PT_SDK_App_GPUdriver_budget':True,'followup':'Findactualtop-levelisaaclabModuleSpecwithoutimportSDK; metadatafileURLaloneisnotruntimeoriginproof'},indent=2),encoding='utf-8');B='/home/lc01/Zonglin Li/zonglin2';code="""import importlib.util,sys,json,hashlib,base64
from pathlib import Path
assert 'isaaclab'not in sys.modules;s=importlib.util.find_spec('isaaclab');assert s is not None and 'isaaclab'not in sys.modules
bases=list(s.submodule_search_locations or[]);assert bases;files=[]
for base in bases:
 root=Path(base)
 for p in sorted(root.rglob('articulation*.py')):
  if p.name not in('articulation_data.py','articulation.py'):continue
  raw=p.read_bytes();assert len(raw)<4*1024**2;files.append({'path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'bytes_base64':base64.b64encode(raw).decode()})
assert 'isaaclab'not in sys.modules
print(json.dumps({'kind':'TOP_LEVEL_SDK_SPEC_WITHOUT_PACKAGE_IMPORT_ACTUAL_SOURCE_BYTES','spec_origin':s.origin,'search_locations':bases,'SDK_imported':False,'files':files,'PT_raw_App_GPUdriver_canonical_calls':0}))
"""
c=connect72()
try:
 i,o,err=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();text=o.read().decode();stderr=err.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);v=json.loads(text)
finally:c.close()
for n,row in enumerate(v['files']):
 raw=base64.b64decode(row.pop('bytes_base64'));assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];p=D/'actual_module_spec_v2'/str(n)/Path(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_copy']=str(p)
out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
