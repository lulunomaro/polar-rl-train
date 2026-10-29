"""NEW109 source only; own-geometry supported extension shaping, no model/raw/SDK."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=L/'native109_ground_supported_extension_calibration_source_v1';assert not B.exists();B.mkdir();(B/'reports').mkdir()
src=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
H=lambda x:hashlib.sha256(x).hexdigest()
rname='mod4_fudan_contact_phase_reward_candidate_v2.py';qname='OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json';aname='native_fudan_step_adapter_candidate_v2.py'
old=(src/rname).read_bytes();a=b"    takeoff=ground*torch.sigmoid((root_vz-.15)/.05)";b=b"    takeoff=ground  # NEW109 supported extension does not require prior upward velocity"
assert old.count(a)==1;new=old.replace(a,b);assert new.replace(b,a)==old;ast.parse(new)
refold=(src/qname).read_bytes();ra=b'"extension_length_m": 0.31';rb=b'"extension_length_m": 0.346'
assert refold.count(ra)==1;refnew=refold.replace(ra,rb);assert refnew.replace(rb,ra)==refold
doc=json.loads(refnew);meta=doc['metadata'];assert meta['episode_seconds']==20 and meta['request_age_ticks']==200 and meta['request_end_exclusive']==2000
assert meta['physical270_success_unchanged'] and not meta['source_is_measured_successful_Fudan_joint_motion']
assert doc['metadata']['bound_own_step_reward']['extension_length_m']==.346
for name,data in [(rname,new),(qname,refnew),(aname,(src/aname).read_bytes())]:
 (B/name).write_bytes(data)
contract=dict(kind='SOURCE_ONLY_NATIVE107_TO109_SUPPORTED_EXTENSION_CALIBRATION_V1',epoch=time.time(),
 source_native107=dict(SHA='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef',bytes=256234249,iteration=17272,WM=172720,Pi=16632),
 source_files=[dict(path=str(src/name),bytes=(src/name).stat().st_size,SHA=H((src/name).read_bytes())) for name in (rname,qname,aname)],
 candidate_files=[dict(relative=name,bytes=(B/name).stat().st_size,SHA=H((B/name).read_bytes())) for name in (rname,qname,aname)],
 changes=[dict(field='contact_and_step_modes.takeoff',old='ground*sigmoid((root_vz-.15)/.05)',new='ground',reason='Remove prior-upward-velocity self-gate on the extension term. Active request and near/flight jump mixture remain original.'),
 dict(field='reference.bound_own_step_reward.extension_length_m',old=.31,new=.346,reason='Use observed own late standing sagittal hip-wheel length, not the Fudan robot length. Engineering shaping reference, not measured maximum extension or an airborne reference.')],
 exact_inverse_reward_and_reference_bytes=True,adapter_bytes_unchanged=True,
 preserved=['20s/2000controls and request200..1999','private4096/age_seconds/horizon32/goal10/taskfocus50percent/max8/fallback',
 'all other reward formulas/weights/clipping/dt/topquiet/softdone/real270acceptance','all networks/normalizers/threeoptimizers/counters/architecture/learner',
 'native100Hz/400N/2.5msTGS32/4/FP32/PD/actionclip6/queue/DR/reset/sourceSDK'],
 limits=['This jointly changes a support gate and a geometry target; no isolated causal attribution.',
 'It supplies supported extension shaping; it does not add a separate crouch phase or promise a complete jump.',
 'Near-edge blend still attenuates the jump component far from the edge. Existing forward tracking remains unchanged.',
 'Observed0.346m is not proof of maximum mechanical reach, dynamic launch feasibility, a force curve, a teacher motion, or270mm skill.',
 'Candidate has no scripted action/force/airborne reset, no added state/phase/RNG stream.',
 'No payload/producer/Task/GO/sourceSDK/fullstate/resource/canonical admission or GPU training done. Do not install into old namespaces.'],
 geometry_evidence_path=str(T/'H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029/reports/NEW108_REWARD_BLEND_GATE_AND_LEG_TARGET_SOURCE_CPU_ACTUAL.json'),
 exact_input_schema_and_producer_binding_pending=True,source_only=True,saved_model_reads=0,raw_reads=0,remote_calls=0,successful_skill=False)
(B/'SOURCE_DELTA_TYPED_CONTRACT_109_V1.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(source_only_prepared=True,path=str(B),reward_SHA=H(new),reference_SHA=H(refnew),no_model_raw_or_remote=True)))

