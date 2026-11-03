"""NEW bound-only parent source callers, cloned from actual-wait reference plumbing.
This builder does not connect remotely, run stager/parent, or touch any model.
"""
from pathlib import Path
import json,ast,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/BOUND_ONLY_NATIVE_PARENT_CALLERS_SOURCE_V1.json';assert not out.exists()
changes=[
 ('payload_embedded_teacher_native_v1','payload_bound_only_native_v1'),
 ('source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py','source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'),
 ('stage_embedded_teacher_native_v1.py','stage_bound_only_native_v1.py'),
 ('EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json','BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json'),
 ('EMBEDDED_TEACHER_NATIVE16_LOCAL_SOURCE_PAYLOAD_V1.json','BOUND_ONLY_NATIVE17_LOCAL_SOURCE_PAYLOAD_V1.json'),
 ('EMBEDDED_TEACHER_E3_W35_V1','BOUND_ONLY_E3_W35_V1'),
 ('MOD4V1_EMBEDDED_TEACHER_E3_W35_REF_V1_','MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_'),
 ('STAGE_COMPLETE_EMBEDDED_TEACHER_REFERENCE_V1.json','STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json'),
 ('single_gpu_e3_w35_embedded_teacher_parent_v1.py','single_gpu_e3_w35_bound_only_parent_v1.py'),
 ('reference_parent_actual_wait_controller_v1.py','bound_probe_parent_actual_wait_controller_v1.py'),
 ('4d77e137e96c34561976815fc6438c8cef109a42c860ff1c40efff9f3d06f0cd','63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80'),
 ('len(raw)==9356','len(raw)==9348'),
 ("PARENT=(9356,","PARENT=(9348,"),
 ('34156','34960'),('e9051dfeb2fd3f08437c4985d2e2f4a6d3229ed75eff870fc3216a7a810e4783','74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40'),
 ('5685','6085'),('cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205','d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a'),
 ("len(manifest['files'])==16","len(manifest['files'])==17"),
 ('REFERENCE_POLICY_IDENTITY.json','BOUND_PROBE_POLICY_IDENTITY_V1.json'),
 ('REFERENCE_','BOUND_PROBE_'),
 ('passed_closed_reference_source_grade','passed_closed_bound_probe_source_grade'),
 ('qualified_reference_execution','qualified_bound_probe_execution'),
 ('sole_reference_metadata_observer','sole_bound_probe_metadata_observer'),
 ('ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1','A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'),
 ('EMBEDDED_ORIGINAL_TEACHER_REFERENCE','A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'),
 ('EMBEDDED_TEACHER_REFERENCE_METADATA_NOT_SKILL_GRADUATION','ZERO_UPDATE_BOUND_PROBE_METADATA_NOT_TRAINING_OR_SKILL_GRADUATION')]
items=[
 ('upload_preflight_embedded_teacher_e3_w35_v1_once.py','upload_preflight_bound_only_e3_w35_v1_once.py'),
 ('stage_embedded_teacher_e3_w35_after_preflight_once.py','stage_bound_only_e3_w35_after_preflight_once.py'),
 ('dispatch_embedded_teacher_e3_w35_original_parent_once.py','dispatch_bound_only_e3_w35_original_parent_once.py'),
 ('collect_embedded_teacher_e3_w35_metadata_once.py','collect_bound_only_e3_w35_metadata_once.py'),
 ('reference_parent_actual_wait_controller_v1.py','bound_probe_parent_actual_wait_controller_v1.py')]
rows=[]
for old,new in items:
 dest=R/new;assert not dest.exists();text=(R/old).read_text(encoding='utf-8')
 for a,b in changes:text=text.replace(a,b)
 text=text.replace('original-teacher reference','zero-update bound-only probe').replace('original teacher reference','zero-update bound-only probe').replace('Full sixteen','Full seventeen').replace('cached pi.teacher reference','same learned pi with .05*tanh residual; no optimizer updates').replace('reference-parent lifecycle','bound-probe-parent lifecycle').replace('sealed reference parent','sealed bound-probe parent').replace('sole reference','sole bound-probe').replace('own reference','own bound-probe')
 if new.startswith('dispatch_'):
  start=text.index('w=json.loads(');end=text.index("root=stage['root']",start)
  gate="quality=json.loads((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes());assert quality['qualified_reference_execution']and quality['qualified_candidate_execution'];"
  text=text[:start]+gate+text[end:]
  text=text.replace('release_witness_SHA','prior_qualified_quality_screen_SHA').replace('RELEASE_SHA','PRIOR_SCREEN_SHA').replace('reports/FROZEN_V2_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json','reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json')
 # A historical reference root/schema must never accidentally select the old policy.
 assert 'single_gpu_e3_w35_embedded_teacher_parent_v1.py'not in text
 assert 'STAGE_COMPLETE_EMBEDDED_TEACHER_REFERENCE'not in text
 assert 'qualified_reference_execution'not in text or new.startswith('dispatch_')
 ast.parse(text);dest.write_text(text,encoding='utf-8',newline='\n');raw=dest.read_bytes();rows.append(dict(path=str(dest),source_template=old,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
value=dict(kind='NEW_ZERO_UPDATE_BOUND_ONLY_PARENT_CALLER_SOURCES',files=rows,probe_training_updates=0,stats_default=False,original_parent_resources_or_deadlines_modified=False,remote_native_model_SDK_C_operations=0)
out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
