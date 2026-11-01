from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_RAY_DEPTH_LINK_BINDING_V256_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
err=json.loads((B/'reports/ROOT256_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes())
original=next(x['UTF8']for x in err['full_UTF8']if x['path'].endswith('/ORIGINAL256_ERROR.json'));assert 'Invalid mesh prim path: /World/ground' in original
for p in (B/'source').glob('*.py'):
 s=p.read_text('utf8').replace('256','257')if p.name!='depth_stair247.py'else p.read_text('utf8')
 if p.name.startswith('evaluate'):
  a=s.index(" text='#usda 1.0");b=s.index(' cfg.scene.ground=AssetBaseCfg',a)
  s=s[:a]+''' from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf
 stage=Usd.Stage.CreateNew(str(ground_file));UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z);UsdGeom.SetStageMetersPerUnit(stage,1.)
 root_prim=UsdGeom.Xform.Define(stage,'/Ground').GetPrim();stage.SetDefaultPrim(root_prim)
 mesh=UsdGeom.Mesh.Define(stage,'/Ground/mesh');mesh.CreatePointsAttr([Gf.Vec3f(*p)for p in points]);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr([i for f in faces for i in f]);mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
 UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());mat=UsdShade.Material.Define(stage,'/Ground/Material');pm=UsdPhysics.MaterialAPI.Apply(mat.GetPrim());pm.CreateStaticFrictionAttr(.5);pm.CreateDynamicFrictionAttr(.5);pm.CreateRestitutionAttr(.5);UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat,materialPurpose='physics')
 stage.GetRootLayer().Save();del stage
 raw=ground_file.read_bytes();check=Usd.Stage.Open(str(ground_file));assert check.GetPrimAtPath('/Ground/mesh').IsA(UsdGeom.Mesh);del check
 put('ACTUAL257_GENERATED_TERRAIN_METADATA.json',dict(path=str(ground_file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),producer_readback=1,physical_and_ray_mesh_same_USD=True,plane0_and270mm_box=True,not_privileged_heightmap=True,source_repair='Explicit UsdGeom mesh child and its exact ray target path; previous256 false retained.'))
''' +s[b:]
  s=change(s,"mesh_prim_paths=['/World/ground']","mesh_prim_paths=['/World/ground/mesh']")
 (S/p.name.replace('256','257')).write_text(s,encoding='utf8')
s=(B/'run_ROOT256_NEW240_mean_regression_once.py').read_text('utf8').replace('256','257');s=change(s,"pattern='run_ROOT257_|","pattern='run_ROOT257_|run_ROOT256_|")
(N/'run_ROOT257_NEW240_mean_regression_once.py').write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT257_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT257_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original256_false_preserved=True,original_error=original,mesh_source='new generated USD via pxr.UsdGeom, same physical and ray triangle points',model_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX257_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_EXPLICIT_USD_MESH_RAY_SENSOR_BINDING',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
