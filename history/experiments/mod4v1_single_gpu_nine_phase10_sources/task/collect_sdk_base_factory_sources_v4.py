"""FollowactualfacaderelativeBaseimports. backendmoduleisnotonpreAppsys.path; noSDKimporttoforceit."""
from pathlib import Path
import json,hashlib,posixpath
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1';origin=json.loads((D/'ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json').read_bytes());base=origin['search_locations'][0];root=posixpath.dirname(posixpath.dirname(base));out=D/'BASE_FACTORY_SOURCE_READ_V4.json';assert not out.exists();e=D/'PHYSX_TOPLEVEL_SPEC_UNAVAILABLE_PREAPP_ERROR_V3.json';assert not e.exists();e.write_text(json.dumps({'kind':'PREAPP_PHYSX_MODULE_SPEC_UNAVAILABLE_NOT_RUNTIME_SDK_FAILURE','error':'AssertionError on top-level isaaclab_physx find_spec is not None','job':'pwsh-7e5a9e97f46a4a92','meaning':'Factory TYPE_CHECKING reference does not makebackend discoverableinplainCPUbeforeSim extensionloader. Do notstartSDKtoguess. FollowknownBaseandFactorysourceandinspectSDKsource-scopeddirectorymetadataonly.','PT_raw_App_GPUdriver_budget':0},indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();rows=[]
try:
 for rel in('assets/articulation/base_articulation_data.py','utils/backend_utils.py'):
  remote=base+'/'+rel
  with s.open(remote,'rb')as f:raw=f.read()
  p=D/'base_factory_v4'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);rows.append({'remote_path':remote,'local_copy':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'exactbytes':True})
 names=s.listdir(root);related=[n for n in names if any(x in n.lower()for x in('physx','newton','isaaclab'))]
finally:s.close();c.close()
v={'kind':'EXACT_ACTIVE_BASE_GETTER_FACTORY_SOURCES_NO_SDKIMPORT','base_package':base,'SDK_source_scope':root,'SDK_source_related_directory_names_only':related,'files':rows,'PT_raw_App_GPUdriver_canonical_calls':0};out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
