"""No network. Finish two already received official PEP658 byte witnesses."""
from pathlib import Path
from email.parser import BytesParser
from packaging.requirements import Requirement
import hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports';base=json.loads((R/'OFFICIAL_TORCH211_VISION026_PRIMARY_PIN_CANDIDATES_ACTUAL.json').read_bytes());rows=[]
for p in base['pins']:
 path=R/(p['package']+'_EXACT_CU128_WHEEL_FULL_METADATA_UTF8.txt');raw=path.read_bytes();expected=p['index_metadata_attributes']['data-core-metadata'].split('=',1)[1];assert hashlib.sha256(raw).hexdigest()==expected
 m=BytesParser().parsebytes(raw);assert m['Name']==p['package'] and m['Version']==p['version'];requires=m.get_all('Requires-Dist',[])
 if p['package']=='torchvision':
  req=[Requirement(x) for x in requires if Requirement(x).name=='torch'];assert len(req)==1 and str(req[0].specifier)=='==2.11.0' and req[0].specifier.contains('2.11.0+cu128')
 if p['package']=='torch':assert any('12.8.1' in x for x in requires) and not any('cu13' in x for x in requires)
 rows.append(dict(**p,exact_metadata_path=str(path),exact_metadata_bytes=len(raw),exact_metadata_SHA=expected,exact_wheel_requires_dist=requires,metadata_published_SHA_passed=True))
v=dict(epoch=time.time(),passed=True,pins=rows,default_PyPI_torch_metadata_is_not_the_selected_CUDA128_build=True,old_local_selector_failed_on_legal_parenthesized_Requires_Dist=True,original_error_preserved='EXACT_CU128_METADATA_ONLY_EXEC_FULL.log',no_metadata_refetch_or_wheel_download=True,actual_newhost_joint_resolve_install_pipcheck_SDK_and_fullrestore_pending=True)
with (R/'EXACT_CU128_TORCH211_VISION026_PEP658_METADATA_PINS_ACTUAL_V2.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(passed=True,pins=[dict(package=x['package'],version=x['version'],published_SHA=x['published_SHA'],metadata_SHA=x['exact_metadata_SHA']) for x in rows])))
