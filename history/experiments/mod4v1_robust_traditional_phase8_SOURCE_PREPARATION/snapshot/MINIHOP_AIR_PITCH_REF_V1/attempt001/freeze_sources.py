"""Precode small-source lock only; no project/physics imports or raw access."""
from pathlib import Path
import hashlib,json,datetime
D=Path(__file__).resolve().parent;R=D.parent;O=R.parent/'traditional_control_20261101'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=['MINIHOP_V1/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_POSITION_TRIGGER_V1/controller.py','ground_controller_v4.py','sensor_core_v4.py','sensor_core_jump_v1.py','sensor_core.py','run_manual_position_v4.py','run_minihop_landing_v4.py','MINIHOP_AUDIT_V2/provenance_v2.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_flat_v2.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py','MANUAL_FIRST_BAR_V1/grade_rows.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py','streamed_trace_rows_v1.py','MODEL_AUDIT/mod4v1_usd_source_aligned.xml','JUMP270_V1/GAIN_BANK.json','TALL_ROUGH_BANK_V1/gain_delta20.json','TALL_ROUGH_BANK_V1/gain_delta0.json','physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py']
paths=[R/p for p in rel]+[O/p for p in ['kinematics.py','model_parameters.json','reports/model_manifest.json']]
for p in paths:assert p.is_file(),p
assert not(D/'controller.py').exists() and not(D/'run_manual_air_pitch_ref_v1.py').exists()
obj=dict(kind='PRECODE_SMALL_SOURCE_LOCK_NO_MODEL_ASSET_OR_RAW_HASH',at=datetime.datetime.now().astimezone().isoformat(),method_SHA=sha(D/'METHOD.json'),architecture_SHA=sha(D/'ARCHITECTURE.md'),sources=[dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=sha(p))for p in paths],parent_fixed_hypothesis_not_gain_fit=True,source_limit_warning='crouch hip .45417412979711813 + .10 exceeds XML .50000000583640236; evaluate original 51 points and retain failure, no range/gain/limit changes',PH7_pending=True)
with(D/'SOURCE_LOCK.json').open('x',encoding='utf-8')as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(sources=len(paths),method_SHA=obj['method_SHA'],architecture_SHA=obj['architecture_SHA'],source_lock_SHA=sha(D/'SOURCE_LOCK.json'),physics_imports=0,raw_scans=0,old_writes=0),indent=2))
