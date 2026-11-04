"""Fresh D7 seed30 controller/collector callers; original native body unchanged."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_D7_SEED20260930_LIFECYCLE_CALLER_SOURCE_V1.json';assert not out.exists();rows=[]
for oldname,newname in [('dispatch_good_holdout_d6_seed29_original_parent_once.py','dispatch_good_holdout_d7_seed30_original_parent_once.py'),('collect_good_holdout_d6_seed29_closed_metadata_once.py','collect_good_holdout_d7_seed30_closed_metadata_once.py')]:
 src=R/oldname;dst=R/newname;assert not dst.exists();raw=src.read_bytes();t=raw.decode('utf8');tree=ast.parse(t)
 for a,z in [('source_good_holdout_lifecycle_routes_v4','source_good_holdout_lifecycle_routes_v5'),('GOOD_HOLDOUT_D6_SEED20260929','GOOD_HOLDOUT_D7_SEED20260930'),("2975,'4ca6cdf8e6f86d25ca3ebedb0ad92bb9252e536846c9677b2a2539bc67c22396'","2446,'ddfa3f19c4be7961003207ac6e6c79f96f8befad97a91a2477e0589c37e0ab6d'"),('20260929','20260930')]:
  assert a in t,a;t=t.replace(a,z)
 if oldname.startswith('dispatch'):
  assert 'GOOD_LIFECYCLE_V4_SOURCE'in t;t=t.replace('GOOD_LIFECYCLE_V4_SOURCE','GOOD_LIFECYCLE_V5_SOURCE')
  oldcode=[x.value for x in ast.walk(tree)if isinstance(x,ast.Constant)and type(x.value)is str and'subprocess.Popen'in x.value];newcode=[x.value for x in ast.walk(ast.parse(t))if isinstance(x,ast.Constant)and type(x.value)is str and'subprocess.Popen'in x.value];assert len(oldcode)==1 and oldcode==newcode
 ast.parse(t)
 with dst.open('x',encoding='utf8',newline='\n')as f:f.write(t)
 rows.append(dict(source=str(dst),bytes=len(t.encode()),SHA256=hashlib.sha256(t.encode()).hexdigest(),old_source_SHA256=hashlib.sha256(raw).hexdigest()))
v=dict(kind='D7_SEED30_FRESH_LIFECYCLE_CALLERS_SOURCE_NOT_EXECUTED',epoch=time.time(),files=rows,whole_remote_original_Popen_body_equal=True,source_changes='CFF_V5_EXACT_SEAL_NAMESPACE_SEED30_SOURCE_OPS_PATH_ONLY',actual_parent_or_SDK_or_model_C_or_resource_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
