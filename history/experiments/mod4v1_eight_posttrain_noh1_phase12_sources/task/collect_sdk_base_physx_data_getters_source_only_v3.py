"""FollowexactFactoryimports toBaseArticulationData+isaaclab_physx moduleSPEC; noSDKimport/App/model/driver."""
from pathlib import Path
import json,hashlib,shlex,base64
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1';origin=json.loads((D/'ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json').read_bytes());base=origin['search_locations'][0];out=D/'BASE_PHYSX_FACTORY_SOURCE_READ_V3.json';assert not out.exists();B='/home/lc01/Zonglin Li/zonglin2';code="""import importlib.util,sys,json,hashlib,base64
from pathlib import Path
assert 'isaaclab_physx'not in sys.modules;s=importlib.util.find_spec('isaaclab_physx');assert s is not None and 'isaaclab_physx'not in sys.modules
bases=list(s.submodule_search_locations or[]);assert len(bases)==1;root=Path(bases[0]);base=Path(%r)
paths=[base/'assets/articulation/base_articulation_data.py',base/'utils/backend_utils.py',root/'assets/articulation/articulation_data.py',root/'assets/articulation/articulation.py'];files=[]
for p in paths:
 raw=p.read_bytes();assert len(raw)<4*1024**2;files.append({'path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'bytes_base64':base64.b64encode(raw).decode()})
assert 'isaaclab_physx'not in sys.modules and 'isaaclab'not in sys.modules
print(json.dumps({'kind':'FOLLOW_FACTORY_BASE_AND_PHYSX_SOURCE_WITHOUT_IMPORT_SDK','spec_origin':s.origin,'search_locations':bases,'SDK_imported':False,'files':files,'PT_raw_App_GPUdriver_canonical_calls':0}))
"""%base
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
for n,row in enumerate(v['files']):
 raw=base64.b64decode(row.pop('bytes_base64'));assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];p=D/'base_physx_factory_v3'/str(n)/Path(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_copy']=str(p)
out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
