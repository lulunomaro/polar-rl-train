"""Produce a portable hardware-corrected release ZIP once, not models/weights for status or Git."""
from pathlib import Path
import json,hashlib,zipfile,time
D=Path(__file__).resolve().parent;C=D/'candidates/HW300N60';P=C/'package';out=D/'MOD4v2_HW300N60_P0.zip';index=D/'DELIVERY_INDEX.json';assert not out.exists()and not index.exists()
validation=json.loads((C/'VALIDATION.json').read_bytes());runtime=json.loads((C/'RUNTIME_TARGET_CPU_VALIDATION.json').read_bytes());build=json.loads((C/'BUILD_RECEIPT.json').read_bytes());assert validation['passed']is True and runtime['passed']is True and all(validation['checks'].values())and all(runtime['checks'].values())
spec=D/'MECHANICAL_LIMITS_SPEC_V2_HW300N60.json';copy=C/spec.name;assert not copy.exists();copy.write_bytes(spec.read_bytes())
manifest=C/'RELEASE_STATUS.json';assert not manifest.exists();manifest.write_text(json.dumps(dict(version='MOD4v2-HW300N60',software_status='BUILT_AND_LOCAL_ENGINE_AND_TARGET_ALGORITHM_REGRESSION_PASS',hardware_stroke_user_confirmed_m=[.14,.20],nominal_extension_force_N=300,force_curve_calibrated=False,active_and_follower_continuous=True,CAD_stop_implementation='equivalent_relative_one_sided_joint_bounds_not_new_mesh_contact',native_PhysX_executed=False,native_feedback100Hz_verified=False,hardware_dynamic_qualified=False,production_environment_switched=False,new_expert_training_started=False,old400N_package='superseded historical not selected',old_v1_checkpoints_Registry_changed=False,validation_checks=len(validation['checks']),CPU_target_checks=len(runtime['checks'])),indent=2),encoding='utf8')
rows=[]
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for path in sorted(C.rglob('*')):
  rel=path.relative_to(C)
  if 'attempts'in rel.parts or '__pycache__'in rel.parts or not path.is_file():continue
  if path.suffix in('.pyc','.pyo'):continue
  raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest();arc='MOD4v2-HW300N60/'+rel.as_posix();z.writestr(arc,raw);rows.append(dict(path=rel.as_posix(),bytes=len(raw),sha256=sha))
raw=out.read_bytes();result=dict(kind='MOD4V2_HW300N60_DELIVERY_INDEX_V1',artifact=str(out),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),archive_root='MOD4v2-HW300N60/',file_count=len(rows),files=rows,physical_target_PhysX_verified=False,hardware_force_curve_calibrated=False,production_hot_replacement=False,old_models_Registry_or_budget_modified=False,model_weights_read=False,source_assets_packaged_for_genuine_delivery=True)
index.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in result.items()if k!='files'},indent=2))
