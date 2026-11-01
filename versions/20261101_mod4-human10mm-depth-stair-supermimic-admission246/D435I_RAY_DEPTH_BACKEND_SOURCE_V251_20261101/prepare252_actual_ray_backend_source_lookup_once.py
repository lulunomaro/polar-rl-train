from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
s=(N/'read251_current_ray_camera_SDK_metadata_once.py').read_text('utf8').replace('251','252')
t=ast.parse(s);node=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='CODE'for v in n.targets));old=ast.get_source_segment(s,node)
code="""from pathlib import Path
import hashlib,importlib.util,importlib.metadata,json,sys,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
rows=[]
for package in ('isaaclab','isaaclab_physx'):
 spec=importlib.util.find_spec(package);assert spec and spec.origin
 root=Path(spec.origin).resolve().parent
 candidates=[p for p in (root/'sensors').rglob('*.py')if p.name in('base_ray_caster_camera.py','ray_caster_camera.py','ray_caster.py')]
 assert len(candidates)<=8
 for p in candidates:
  b=p.read_bytes();assert len(b)<150000
  rows.append(dict(relative=package+'/'+p.relative_to(root).as_posix(),path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),physical_source_byte_reads=1))
assert rows and 'torch'not in sys.modules
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,isaaclab_version=importlib.metadata.version('isaaclab'),source_files=rows,model_assets_raw_GPU_SDK_App_or_account_calls=0)))"""
s=s.replace(old,'CODE='+repr(code));ast.parse(s)
p=N/'read252_actual_ray_backend_SDK_metadata_once.py';p.write_text(s,encoding='utf8')
with(R/'FROZEN252_DISTINCT_CURRENT_PHYSX_RAY_BACKEND_SOURCE_PURPOSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='Resolve actual Factory-dispatched ray-camera implementation and mesh support before changing camera backend. Known SDK sensors folders only, <=8 matchedPY perpackage, no App/GPU/weights/terrain assets.',source251_consumed_no_rerun=True,first250_Vulkan_incompatible_driver_preserved=True,source_SHA=hashlib.sha256(p.read_bytes()).hexdigest()),f,indent=2)
print(json.dumps(dict(passed=True,path=str(p))))
