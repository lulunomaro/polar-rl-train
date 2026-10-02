"""Seal the new model and validate loading from an independent extraction."""
from pathlib import Path
import ast,json,hashlib,zipfile,datetime,subprocess,sys
import numpy as np
import mujoco
from pxr import Usd,Sdf,UsdUtils,UsdGeom,UsdPhysics
sys.stdout.reconfigure(encoding='utf8')
WORK=Path(__file__).parent;ROOT=WORK.parent/'chassis_mod4'
ZIP=WORK.parent/'chassis_mod4_mjcf_usd_20260910.zip'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((ROOT/'reports/cad_source.json').read_text(encoding='utf8'))
assert sha(Path(r'C:\Users\lulu\Downloads\底盘_MOD4.STEP'))==source['source_sha256'],'Source STEP changed during conversion'
reports=['validation_report.json','model_parity_audit.json','import_guard_tests.json','operating_clearance.json','cad_axis_audit.json']
for f in reports:assert json.loads((ROOT/'reports'/f).read_text(encoding='utf8'))['status']=='PASS',f
ppo=json.loads((ROOT/'reports/ppo_smoke_report.json').read_text(encoding='utf8'))
assert ppo['numerical_failures']==0 and ppo['policy_parameters_updated'] and ppo['actual_steps']==4096
assert sha(ROOT/'scene_training.xml')==ppo['model_sha256']
for p in ROOT.rglob('*.py'):
    if '__pycache__' not in p.parts:ast.parse(p.read_text(encoding='utf8'),filename=str(p))

files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'runs' not in p.relative_to(ROOT).parts and p.name!='DELIVERY_MANIFEST.json')
manifest={'package':'MOD4_MJCF_USD','version':'2026-09-10','source':source,
 'physics_runtime_verified':'MuJoCo 3.12.0 only','isaac_physx_runtime_tested':False,
 'primary_mjcf':'scene_training.xml','primary_usd':'isaac/robot.usd','usd_preview_scene':'isaac/scene.usda',
 'report_files':reports+['ppo_smoke_report.json'],
 'files':{str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}}
(ROOT/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
files.append(ROOT/'DELIVERY_MANIFEST.json')
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())

test=WORK/('unpack_check_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));test.mkdir()
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    for name in z.namelist():
        target=(test/name).resolve()
        assert target.is_relative_to(test.resolve()),name
    z.extractall(test)
unpacked=test/ROOT.name
for name,info in manifest['files'].items():assert sha(unpacked/name)==info['sha256'],name

models={}
for f in ['scene.xml','scene_training.xml','scene_headless.xml','robot_hifi.xml']:
    m=mujoco.MjModel.from_xml_path(str(unpacked/f));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    assert (m.nq,m.nv,m.nu,m.neq)==(29,28,6,10)
    assert np.max(np.abs(d.efc_pos[:d.ne]))<1e-8
    baseline=mujoco.MjModel.from_xml_path(str(ROOT/f))
    for a in ['body_mass','body_inertia','body_parentid','jnt_axis','jnt_range','eq_data','actuator_ctrlrange']:
        assert np.array_equal(getattr(m,a),getattr(baseline,a)),(f,a)
    models[f]={'nq':m.nq,'nv':m.nv,'nu':m.nu,'equalities':m.neq,'mesh_count':m.nmesh}

stages={}
for name in ['isaac/robot.usd','isaac/scene.usda']:
    stage=Usd.Stage.Open(str(unpacked/name));assert stage and stage.GetDefaultPrim()
    layers,assets,missing=UsdUtils.ComputeAllDependencies(str(unpacked/name))
    assert not missing,(name,missing)
    for l in layers:assert Path(l.realPath).resolve().is_relative_to(unpacked.resolve()),l.realPath
    stages[name]={'layer_count':len(layers),'missing_dependencies':list(map(str,missing)),
                 'rigid_bodies':sum(p.HasAPI(UsdPhysics.RigidBodyAPI) for p in stage.Traverse()),
                 'joints':sum(p.IsA(UsdPhysics.Joint) for p in stage.Traverse())}
    assert stages[name]['rigid_bodies']==23 and stages[name]['joints']==28
    if name.endswith('scene.usda'):
        bound=UsdGeom.BBoxCache(0.,['default']).ComputeWorldBound(stage.GetPrimAtPath('/World/Ground')).ComputeAlignedRange()
        assert abs(bound.GetMax()[2])<1e-7

subprocess.run([sys.executable,str(unpacked/'isaac/audit_import.py')],check=True)
result={'status':'PASS','archive':str(ZIP),'archive_bytes':ZIP.stat().st_size,'sha256':sha(ZIP),
 'file_count':len(files),'all_manifest_hashes_verified':True,'original_step_unchanged':True,
 'isolated_mjcf_loads':models,'isolated_usd_loads':stages,'physx_runtime_tested':False,
 'usd_crate_version':str(Sdf.CrateInfo.Open(str(unpacked/'isaac/robot.usd')).GetFileVersion())}
ZIP.with_suffix('.verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
ZIP.with_suffix('.sha256').write_text(f"{result['sha256']}  {ZIP.name}\n",encoding='ascii')
print(json.dumps(result,indent=2,ensure_ascii=False))
