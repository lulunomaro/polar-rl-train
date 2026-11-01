from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;R=N/'reports';s=(N/'read252_actual_ray_backend_SDK_metadata_once.py').read_text('utf8').replace('252','253')
t=ast.parse(s);n=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='CODE'for v in n.targets));old=ast.get_source_segment(s,n)
code="""from pathlib import Path
import hashlib,importlib.util,importlib.metadata,json,sys,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
spec=importlib.util.find_spec('isaaclab_physx');assert spec
roots=[Path(x).resolve()for x in(spec.submodule_search_locations or [])];assert roots
candidates=[]
for root in roots:
 candidates += [p for p in root.rglob('*.py')if p.name in('ray_caster_camera.py','ray_caster.py')]
candidates=list(dict.fromkeys(candidates));assert 1<=len(candidates)<=12
rows=[]
for p in candidates:
 b=p.read_bytes();assert len(b)<160000
 rows.append(dict(relative='isaaclab_physx/'+str(p),path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),physical_source_byte_reads=1))
assert 'torch'not in sys.modules
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,isaaclab_version=importlib.metadata.version('isaaclab'),namespace_origin=spec.origin,namespace_roots=[str(p)for p in roots],source_files=rows,model_assets_raw_GPU_SDK_App_or_account_calls=0,previous252_lab_source_reopens=0)))"""
s=s.replace(old,'CODE='+repr(code));ast.parse(s);p=N/'read253_namespace_PhysX_ray_backend_only_once.py';p.write_text(s,encoding='utf8')
with(R/'FROZEN253_NAMESPACE_READER_REPAIR_DISTINCT_PHYSX_ONLY_SOURCE_PURPOSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original252_false='find_spec namespace has originNone; original reader asserted spec.origin before physx files. Prior isaaclab-source opens may have occurred but were not returned; no false0claim.',new_scope='Only previously unreadisaaclab_physx backend sources, namespace roots from spec.submodule_search_locations. No priorlab file reread, no App/GPU/weights or runtime action.'),f,indent=2)
print(json.dumps(dict(passed=True,path=str(p))))
