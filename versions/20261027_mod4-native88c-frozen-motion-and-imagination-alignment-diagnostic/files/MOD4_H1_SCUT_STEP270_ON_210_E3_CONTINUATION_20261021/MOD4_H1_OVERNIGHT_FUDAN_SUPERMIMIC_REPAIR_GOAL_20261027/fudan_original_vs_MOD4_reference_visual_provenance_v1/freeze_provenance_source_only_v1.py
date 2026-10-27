"""Source/JSON/XML provenance only. Never opens NPZ/NPY/STL/URDF/PT/ONNX."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;T=D.parent.parent
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';A=J/'agent_reference_retarget_cpu'
FILES={
 'capture_producer':J/'fudan_original_jump_headless_CPU_reference_v1.py',
 'original_source':J/'source/mujoco/python_tools/onnx_mj_chuanlian.py',
 'original_XML':J/'source/mujoco/assert_now/infantry_binglian_yuntai/infantry_V2/meshes/mjmodel.xml',
 'asset_plan':J/'reports/PINNED_FOREIGN_REFERENCE_ASSET_DOWNLOAD_PLAN_SOURCE_ONLY_ACTUAL.json',
 'original_receipt':J/'reports/FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json',
 'capture_summary':J/'actual_72_reference_text/reference_capture/BOUNDED_FUDAN_JUMP_REFERENCE_CASES_CPU_ACTUAL.json',
 'retarget_v2':A/'retarget_saved_canonical_actual_Fudan_CPU_v2.py',
 'declare_v3':A/'declare_actual_reference_partial_step270_phase_V3_CPU.py',
 'canonical':A/'ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json',
 'reference_v3':A/'ACTUAL_PARTIAL_STEP270_PHASE_V3_1793006590678125700/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json',
 'reference9223':T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1/source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json',
}
def H(x):return hashlib.sha256(x).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
src={};lineage={}
for key,p in FILES.items():
 assert p.suffix in ('.py','.json','.xml')
 raw=p.read_bytes();src[key]=raw.decode('utf-8-sig');row=dict(path=str(p),bytes=len(raw),SHA=H(raw))
 if p.suffix=='.py':row['definitions']=[dict(name=n.name,line=n.lineno,end_line=n.end_lineno) for n in ast.walk(ast.parse(src[key])) if isinstance(n,ast.FunctionDef)]
 lineage[key]=row
def ev(key,anchor):
 hits=[i for i,line in enumerate(src[key].splitlines(),1) if anchor in line];assert hits,(key,anchor)
 return dict(path=lineage[key]['path'],SHA=lineage[key]['SHA'],lines=hits,anchor=anchor)
receipt=json.loads(src['original_receipt']);summary=json.loads(src['capture_summary']);plan=json.loads(src['asset_plan'])
canonical=json.loads(src['canonical']);v3=json.loads(src['reference_v3']);r=json.loads(src['reference9223']);m=r['metadata']
xml=ET.fromstring(src['original_XML']);bodies=['world']+[b.get('name') for b in xml.findall('.//worldbody//body')]
fields=next(ast.literal_eval(n.value) for n in ast.parse(src['capture_producer']).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FIELDS' for t in n.targets))
assets=[x for x in receipt['assets'] if x['path'].lower().endswith(('.xml','.stl','.urdf'))]
artifact_rows=receipt['small_artifacts']
report=dict(schema='mod4.fudan_original_vs_own_reference.visual_provenance.v1',scope='source/JSON/XML only; binary motion/weights/meshes not opened or rehashed',
 upstream=dict(repository=plan['repository'],commit=plan['revision'],new_SuperMimic_demo_project_identity_not_established=True,original_source_SHA_from_existing_producer=summary['pinned_source_full_SHA'],
  local_source_SHA=lineage['original_source']['SHA'],same_pinned_source=summary['pinned_source_full_SHA']==lineage['original_source']['SHA']),
 original_motion_artifacts=artifact_rows,binary_artifact_metadata_reused_without_open_stat_or_hash=True,
 original_array_schema=dict(format='np.savez_compressed field dictionary; no separate raw schema version',fields=fields,
  body_order=bodies,body_order_basis='include-free original MJCF preorder plus world; matches producer d.xpos.copy()/d.xquat.copy()',
  body_pose_quaternion='wxyz',time_basis='saved simulation time; not nominal policy_dt label',
  native_default_capture_interval_source_inference_s=.002*2,
  source_default_sim_dt_variable_s=.005,actual_default_MJCF_step_s=.002,
  time_warning='Producer retained script steps_per_policy2 while original MJCF dt.002; use NPZ time array for exact playback, not assumed100Hz/400Hz.'),
 cases=summary['cases'],
 original_geometry=dict(local_XML=lineage['original_XML'],local_URDF_found_in_J=False,
  local_XML_mesh_folder_entries=[p.name for p in FILES['original_XML'].parent.iterdir()],
  exact_mesh_geometry_available_in_local_XML_folder=False,
  previously_transferred_remote_assets=assets,
  world_geoms=[g.attrib for g in xml.find('worldbody').findall('geom')],
  base_authored_spawn=xml.find('.//worldbody/body').attrib,
  interpretation='MJCF has stairs/ramp/platform geometry, but selected command0 standing-jump capture starts baseX-2.8 over landing_box top.3m. Existing summary initial wheel support≈.298m. This is not a recorded270mm step-ascent demonstration.'),
 retarget_lineage=dict(canonical_schema=canonical['schema'],canonical_source=canonical['source'],v3_schema=v3['schema'],
  v3_path=str(FILES['reference_v3']),v3_phase=v3['metadata'].get('partial_phase_contract'),
  v3_phase_evidence=v3['metadata'].get('partial_phase_source_evidence'),
  v2_crop_source_s=[1.,3.6],v2_limb_excursion_factor=.1,
  phase_mapping='native age100 -> cropped reference.5s -> original simulation1.5s trigger; age0..49 holds initial retarget pose, age50 begins source1.0s; apex aroundage136.',
  interpretation='Canonical body/wheel paths are measured original-robot simulation, not hardware motion capture. Retargeted MOD4 q30 is static own closed-chain IK, not measured foreign q or dynamically executed own motion.90% limb excursion attenuation is explicit.'),
 own9223=dict(path=str(FILES['reference9223']),SHA=lineage['reference9223']['SHA'],schema=r['schema'],
  reference_role=m['reference_role'],first_touch_age=m['first_touch_age'],support_age=m['support_age'],
  source_air_preserved=m['source_air_Z_R_q_vertical_velocity_angular_velocity_qd_literal_preserved_before_touch'],
  own_forward_profile=m['horizontal_reference_profile'],
  source_contact_used_as_own_contact=m['source_contact_used_as_own_contact'],
  actual_own_contact_or_dynamic_qualification=m['actual_own_contact_or_dynamic_qualification'],
  reference_teacher_source=m['reference_teacher_source'],
  authored_portion='RootX/VX are newly authored own task timing (flightvx.9, physical command remains.8); aftertouch145, own staticIK contact/support/splice toward standing on270mm platform atage165, then braking/hold. These are goals, not original Fudan measured step ascent or actual MOD4 contact.',
  no_airborne_plus270mm=m['no_airborne_plus270mm_height']),
 visualization=dict(without_actor_or_physics=True,
  faithful_available='Use saved original body_position/body_quaternion_wxyz/time for complete original source motion; originalXML provides body names/tree and primitive wheel/terrain transforms. No new FK/simulation is required for body pose reconstruction.',
  limitation='Local original mesh folder has XML only. Exact mesh silhouette/collider geometry requires separately bound already-produced assets, not guessed boxes. A body-tree/wheel primitive view must be labelled schematic, not exact mesh collider.',
  required_labels=['originalFudan saved standing-jump simulation (not270mm step-ascent)', 'MOD4 converted own step GOAL (static IK/authored timing, not trained motion)','actualC frozen single policy attempt (separate actual outcome)'],
  cannot_claim='A saved standing-jump capture or synthetic own target animation is not footage of Fudan or MOD4 physically jumping onto270mm step.',
  initial_pose='0.01s of native/own goal is before request/trigger. Full original6s includes settling before1.5s trigger, so show full or honestly label cropped time; do not force crouch pose atframe0.'),
 evidence=[ev('capture_producer','FIELDS='),ev('capture_producer','d.time)>=1.5'),ev('capture_producer','float(d.time)<6.0'),ev('capture_producer','d.xpos.copy(),d.xquat.copy()'),
  ev('original_source','RECOVER_2500_ONNX_PATH ='),ev('original_source','sim_dt = 0.005'),ev('retarget_v2','crop_start_source_s=1.'),
  ev('retarget_v2','common_limb_excursion_attenuation=.1'),ev('retarget_v2','initial_hold_until_own_age_control=50'),
  ev('declare_v3','source_flat_return_preserved_as_raw_evidence_but_excluded_from_elevated_landing_supervision=True')])
put('PROVENANCE_SOURCE_AND_EXISTING_METADATA_ACTUAL.json',report)
put('SOURCE_JSON_XML_SHA_INDEX_ACTUAL.json',lineage)
put('SOURCE_READER_LIMITATIONS_ACTUAL.json',dict(source_output_truncations_retained=True,
 description='Initial path listing and metadata excerpts exceeded tool output budget; required fields were selected into this new report. Original source/raw/reports untouched.',
 no_raw_NPZ_or_NPY_read=True,no_weights_or_mesh_binary_read=True,new_actor_physics_or_download=False))
put('HANDOFF.md',f'''# FROZEN: original Fudan versus converted MOD4 visual provenance

The available measured source is a **saved original-robot MuJoCo standing jump**, not a verified270mm step-ascent. Upstream repository `{plan['repository']}`, pinned commit `{plan['revision']}`. Producer original `onnx_mj_chuanlian.py` SHA `{summary['pinned_source_full_SHA']}`. Capture adapter source SHA `{lineage['capture_producer']['SHA']}`. This teacher capture is not established to be the newly supplied native SuperMimic demo/project; keep the two sources distinct until its link/source is identified.

Primary full-motion input for root's declared new-purpose single binary read:
`{artifact_rows[1]['local_path']}`
Existing transfer metadata:1991407B, SHA `{artifact_rows[1]['SHA']}`. This helper did not open/stat/hash it.1501 saved control rows, original MJCF dt.002; retained script sim_dt.005/steps_per_policy2 implies roughly4ms saved spacing. **Use saved time array**, not an assumed100Hz/400Hz. Entire6s capture includes initial settle, trigger at1.5s, original jump-mode duration and return policy. The summary reports peak wheel height.3366786m above initial support and967 postjump dual-contact rows; neither proves obstacle ascent. Two other captures exist with declared5ms dt (standing command0 and forward command.8); preserve their separate labels/results rather than selecting largest peak.

NPZ schema is the exact producer `FIELDS` tuple: time/root_position/root_quaternion_wxyz/full_qpos/full_qvel/body_position/body_quaternion_wxyz/wheel_bottom_world_z/wheel_normal_contact_N/wheel_partner_geom/raw_action6/executed_action6/actuator_torque6/obs25/obs_history125/jump_mode. It contains **all body world poses**, so reconstructing source skeleton/primitive-wheel side view requires neither actor nor physics nor a new FK run. Body order is world + original include-free MJCF preorder (16total), supplied in report. Do not use MOD4 body order.

Original local geometry source:
`{FILES['original_XML']}`
SHA `{lineage['original_XML']['SHA']}`. The scene contains20/35cm steps,30cm platforms and ramp, but base spawnX=-2.8 is on landing_box top.3m; observed initial support≈.298m agrees. Command0 capture is standing jump on that support, not a whole step traversal. `上台阶3_angz+.onnx` is the source **recover/plane** policy filename; filename alone is not evidence the saved trajectory ascended a step. This helper never opened ONNX.

No URDF exists in inspectedJ source. Local original mesh folder contains only `mjmodel.xml`; exact STLs were previously transferred/verified on72 under the receipt's `vendor/fudan_rl_wheel_leg/...` paths. Their existing sourcepath/SHA metadata is recorded, no new download/read. For immediate no-physics visualization, use saved body poses + tree/wheel primitives with a clear schematic label. Do not call guessed body boxes exact collider geometry. Exact mesh view needs its separately approved/pinned geometry availability.

V2/V3 are **own static retarget**, not rawFudan animation: original source crop1.0..3.6s, limb excursion factor.1, own closed-chain IK/q30, sourcewheel=.06/own geometry conversion. Native age100 corresponds to original1.5s trigger; ages0..49 hold initial retarget pose, sourcecrop begins atage50. V3 only adds truthful partial ascent/height supervision; original returns to its original surface and does not supply a270mm landing.

Current9223 `{r['schema']}` table is explicitly `{m['reference_role']}`. Beforetouch145, source-derived ownZ/R/q/vZ/omega/qd are preserved; X/VX are authored own ballistic timing (flight.9m/s versus physicalcommand.8). Contact/support145..165 is new own IK splice to270mm platform, then braking/hold. Original contacts are foreign phase markers; no actual own contact/dynamics/skill was proved. Therefore an animation of9223 is **MOD4 goal design**, not evidence of Fudan stepping or learned MOD4 motion.

The user's0.01s objection is resolved by showing the complete timeline: that frame is before the request100/trigger, not necessarily the crouch/takeoff phase. Keep source-time labels and the full initial preparation; do not move firstframe into a staged crouch or insert a step under the foreign standing jump. Show original saved jump and own designed goal separately if both are useful. ActualC's early terminated learned attempt is a third distinct result.

All exact source anchors, geometry/body order, three existing artifact receipts and case summaries are in `PROVENANCE_SOURCE_AND_EXISTING_METADATA_ACTUAL.json`; full source/JSON/XML SHA index is separate. No NPZ/npy/model/mesh binary was read, no actor/physics/SDK/GPU/SSH/download/Git ran. Original frozen dirs unchanged. OrdinaryGit supplementation/root visualization remains pending; no new trial/tag or runtime claim.
''')
put('FREEZE_STATUS_ACTUAL.json',dict(frozen_UTC=datetime.now(timezone.utc).isoformat(),complete=True,source_only=True,binary_inputs_not_read=True,Git_supplementation='PENDING_ROOT'))
rows=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name!='INDEX.json':
  raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
put('INDEX.json',dict(files=rows,self_excluded='INDEX.json'))
print(json.dumps(dict(frozen=True,directory=str(D),INDEX_SHA=H((D/'INDEX.json').read_bytes()),source_SHA_verified=report['upstream']['same_pinned_source'],body_count=len(bodies))))
