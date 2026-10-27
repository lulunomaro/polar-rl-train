"""Bounded source/report inventory, never an NPZ/PT/RAW data reader or trainer."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;W=T.parent
N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';B=N/'payloads/h1'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads'
S3=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'
C=W/'MOD4_HOST72_E1_CURB_SLOPE_TRAINING_ASSIGNMENT_20261016'
MOE=T/'MOE_SMALL_CURB_CONTACT_REPLAY_20261024'
FILES={
 'migration80_79c':T/'MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026/reports/CLOSED81O_FOR82Q_OLD80_79C_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',
 'migration81O_82Q':T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/reports/CLOSED82Q_FOR83_81O_82Q_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',
 'migration80_81O_83B':T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026/reports/CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',
 'actual_TLS_HMAC_receiver':T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/reports/CLOSED82Q_FOR83_CURRENT82Q_MINIMAL_RECEIVER_FULL_TEXT_ALL_OUT_ACTUAL.json',
 'old_H1_trace':P/'h1/h1_production_control_prefix_trace_v1.py',
 'current_H1_trace':B/'h1_production_control_prefix_trace_v1.py',
 'current_retention':B/'h1_prefix_pair_retention_v1.py',
 'current_bridge':B/'source/native_wheel_leg_bridge_v4.py',
 'h1_400_retention_index':N/'current_native88_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json',
 'recovery_400_retention_index':N/'current_native88_closed_text/recovery/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json',
 'frozen400_driver':S3/'code/native88C_frozen_acceptance_driver_v1.py',
 'frozen400_receipt':S3/'reports/FROZEN_NATIVE88C_SOURCE210_SINGLE_FINITE_RETURNED_ACTUAL.json',
 'E2_worker':P/'e2/production_worker.py',
 'E2_frame':P/'e2/job0/runtime/isaac/mod4/e2_h1_flat_environment_v1.py',
 'E3_worker':P/'recovery/recovery_worker.py',
 'E0_W35_contact_worker':MOE/'small_curb_actual_contact_worker_v3.py',
 'W35_contact_receipt':MOE/'actual_contact_V3_4090/out/W35_vx_0p8_COMPLETE.json',
 'E0_contact_receipt':MOE/'actual_contact_V3_4090/out/E0_vx_0p8_COMPLETE.json',
 'CURB_SLOPE_worker':C/'payload/host72_original_backend_native_worker_v2_prefix_durable.py',
 'CURB_SLOPE_unused_preparation':C/'reports/NATIVE_WORKER_V2_UNUSED_PREFIX_DURABILITY_REPAIR_ACTUAL.json',
}
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
src={};lineage={}
for k,p in FILES.items():
 assert p.suffix in ('.json','.py')
 raw=p.read_bytes();src[k]=raw.decode('utf-8-sig');row=dict(path=str(p),bytes=len(raw),SHA=H(raw))
 if p.suffix=='.py':row['definitions']=[dict(name=n.name,line=n.lineno,end_line=n.end_lineno) for n in ast.walk(ast.parse(src[k])) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
 lineage[k]=row
def ev(k,fragment):
 hits=[i for i,line in enumerate(src[k].splitlines(),1) if fragment in line];assert hits,(k,fragment)
 return dict(source=k,path=lineage[k]['path'],report_or_source_SHA=lineage[k]['SHA'],lines=hits,anchor=fragment)

retained=[]
for key in ('migration80_79c','migration81O_82Q','migration80_81O_83B'):
 r=json.loads(src[key]);assert r['passed'] and r['all_full_SHA_retained_on72']
 for batch in r['batches']:
  for f in batch['files']:
   assert f['target_full_SHA_verified'] and f['target_path'].startswith('/home/lc01/')
   retained.append(dict(stage=batch['source_stage'],authoritative_latest_retained_path=f['target_path'],
    former_producer_path=f['path'],bytes=f['bytes'],producer_SHA=f['SHA'],
    transfer_report=str(FILES[key]),transfer_report_SHA=lineage[key]['SHA'],
    target_full_SHA_verified_in_original_actual_receipt=True,new_file_read_stat_or_hash=False,
    no_claim_former210_path_still_exists=True))
assert len({x['authoritative_latest_retained_path'] for x in retained})==len(retained)==14
ack=json.loads(src['actual_TLS_HMAC_receiver']);complete=json.loads(ack['texts']['RECEIVER_COMPLETE_ACTUAL.json'])
assert complete['passed'] and complete['TLS_pin_HMAC_and_full_SHA'] and ack['all_receiver_processes_actual_out']
ackproof=dict(report=str(FILES['actual_TLS_HMAC_receiver']),report_SHA=lineage['actual_TLS_HMAC_receiver']['SHA'],
 actual_TLS_pin_HMAC_full_SHA=True,all_receiver_processes_out=True,
 transport_source_SHA=H(ack['texts']['forensic_tls_peer_transfer_V96_V5_NINTH.py'].encode()),
 scope='Explicitly inspected actual82Q receiver COMPLETE+saved transport source. Other moved files use their original successful composite fullSHA receipts; no HMAC key/signature bytes are exported or regenerated.')
current={}
for role in ('h1','recovery'):
 k=role+'_400_retention_index';r=json.loads(src[k]);ss=r['retention_status'];rows=[]
 for i,row in enumerate(r['index']):
  if ss[i]['raw_retained']:
   rows.append(dict(index=i,path=row['path'],bytes=row['bytes'],producer_SHA=row['SHA'],controls=row['controls'],
      preupdate_model_metadata_reference_only=row.get('preupdate_source',{}).get('path')))
 current[role]=dict(completed_controls=r['controls'],num_envs=4096,retained=rows,
  retained_snapshot_controls=sum(x['controls'] for x in rows),retained_env_control_snapshots=sum(x['controls'] for x in rows)*4096,
  middle_pruned=True,actual_remote_fresh_existence_not_requeried=True,
  index_report=str(FILES[k]),index_report_SHA=lineage[k]['SHA'])
assert current['h1']['retained_snapshot_controls']==72 and current['recovery']['retained_snapshot_controls']==67

def matching_rows(value,fragment):
 result=[]
 def walk(x):
  if isinstance(x,dict):
   if any(isinstance(x.get(k),str) and fragment in x[k] for k in ('path','local_path','remote_path','filename')):
    result.append({k:v for k,v in x.items() if not isinstance(v,(list,dict))})
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(value);return result
frozen_receipt=json.loads(src['frozen400_receipt'])
frozen_paths=matching_rows(frozen_receipt,'ACTUAL_100HZ_CONTROLS.jsonl')
frozen_candidate=dict(local_expected_path=str(S3/'actual210/seed_20260928/episode/ACTUAL_100HZ_CONTROLS.jsonl'),
 producer_source=str(FILES['frozen400_driver']),producer_source_SHA=lineage['frozen400_driver']['SHA'],
 actual_receipt=str(FILES['frozen400_receipt']),actual_receipt_SHA=lineage['frozen400_receipt']['SHA'],
 matching_existing_receipt_artifact_rows=frozen_paths,controls_from_already_qualified_actual_single_case=61,num_envs=1,
 schema=['packed127_for_action','xi31_for_action','terminal_packed127_same_point','terminal_pre_reset.state.executed6','actual_original_done','control','age_for_action'],
 direct_candidate_scope='Same400 source layout and explicit s/action/terminal-s1/staticxi; must perform one newly declared schema/value extraction before actual dataset admission.61 failure transitions in one episode, not skill or diversity evidence.',
 raw_content_not_read=True)

old_fields=['policy35','critic38','root13','q30','joint_velocity','applied_torque','executed6','history5ms','impulse','closure','mimic','public_request','episode','done','raw_sampled6','reward/events']
classes=[
 dict(family='current400_H1native_two_training_roots',plant='nominal400N,k2000,upperL200',clock='100Hz control/2.5ms physics/4callbacks',
  category='same400_partial_raw_not_yet_full127_direct',evidence=current,fields=old_fields,
  missing=['persisted processed queueApplied6','per-episode staticxi31 across resets','source env origin/joint order join for replay pack'],
  note='Private bridge aux/static memory exists at runtime but original27-column trace does not save those additional fields; do not confuse runtime availability with dataset persistence.'),
 dict(family='current400_C_frozen_single_h1',plant='same qualified400C',clock='100Hz/2.5ms/4',category='same400_full_field_direct_candidate_pending_single_extraction',evidence=frozen_candidate,
  missing=['new declared data extraction/content admission only; no inference/retry required'],note='Source explicitly saves same-point terminalstate before original auto-reset. Failure/terminal sample is useful dynamics evidence, not a success demo.'),
 dict(family='old700_H1_PPO_79c_80_81O_82Q_83B',plant='old nominal700 spring recipe and upperlimit; exact asset/source version per manifest required',clock='H1 production100Hz/2.5ms/4',
  category='old700_same_clock_separate_domain_pretraining_or_explicit_plant_condition',artifact_count=len(retained),fields=old_fields,
  missing=['queueApplied6 not stored; possible exact boundary reconstruction requires processed target mapping/queue proof','staticxi31 not stored; matching old DR source snapshots required and post-reset unknowns excluded','env origins/ordered30names/source reset semantics join'],
  note='No reward/actor data needed for WM regression, but plant/source/DR/action semantics are mandatory. Restored model weights or Adam states are not transition datasets.'),
 dict(family='old700_H1_native85_86_87R5',plant='old700',clock='laterH1 native100Hz/2.5ms/4; earlier versions require their own manifests',
  category='same_old_domain_field_audit_pending_not_blanket_all_experts',
  fields='Original H1 trace family; full native checkpoints save model/DR state but do not imply full replay retention',
  missing=['exact existing raw retention index/producer pins for each additional stage; not scanned across allW','same raw omissions as current H1 trace'],
  note='No old native/PT or training raw opened. CurrentC frozen reader evidence does not certify all older datasets.'),
 dict(family='normal_E2_production',plant='old700/source-specific own MOD4',clock='normal policy50Hz/2.5ms/8; source-bound',category='multi_rate_and_field_coverage_required',
  evidence=[ev('E2_worker','def persist'),ev('E2_worker',"if phase=='native':")],
  note='Production PPO branch primarily saves model/log reports, not the native144 prefix. E2 native144 source is a distinct100Hz diagnostic exception (assert4callbacks), not proof of50Hz transition capture.',
  native144_fields=['root13','q30','joint_vel','applied_torque','history','executed6','done','command','physical_wheel_force','policy35','critic38','raw6','reward'],
  missing=['episode/reset IDs and staticxi/queueApplied/origin mapping; actual native-prefix artifact receipt per selected run']),
 dict(family='normal_E3_recovery',plant='old700/source-specific own MOD4',clock='50Hz/2.5ms/8;100Hz feedback2/control',category='report_only_for_inspected50Hz_native24_and_production_branch',
  evidence=[ev('E3_worker','policy_hz=50'),ev('E3_worker','for i in range(24):')],
  note='Inspected worker native24 collects callback/check rows, not a root/q/qdot transition table; a persist helper definition alone is not proof it ran. Older336/native-full runs are separate sources, pending bounded artifact/schema join.'),
 dict(family='E0_W35_MuJoCo_contact_replay_V3',plant='own MOD4 exported MuJoCo collider/actuator plant, not automatically same IsaacPhysX400',clock='100Hz control/.5ms physics/20callbacks',
  category='different_backend_asset_clock_explicit_condition_or_separate_pretrain',
  evidence=[ev('E0_W35_contact_worker',"for variant in ('auto','E0','W35')"),ev('E0_W35_contact_worker','np.savez_compressed')],
  receipts={k:json.loads(src[k]) for k in ('W35_contact_receipt','E0_contact_receipt')},
  fields=['qpos','qvel','action','initial_qpos_qvel','observation','choice/logits','per-physicscontact frame/wrench','physics ctrl/actuatorforce/velocity'],
  missing=['map MuJoCo qpos/qvel and actuator motor order to own30+root physical convention','current SDK appliedTorque30/contact18/processedQueue6 semantics not equal raw MuJoCo ctrl/contactwrench','xi31 DR definition/backend and plant condition','exact successful/fault/reset sequence interpretation'],
  note='Saved qpos/qvel/action/contact make this more than obs-only, but do not silently zero-fill current auxiliary/static inputs or call it current400 groundtruth. Contact V3 report includes extreme forces; retain original fault/health classifications, do not invent a new exclusion gate.'),
 dict(family='CURB_SLOPE_old_native_assignment',plant='older own source-specific geometry/DR; exact source contracts needed',clock='original manifest, not inferred from worker filename; pending',
  category='insufficient_full_state_and_actual_artifact_evidence_in_bounded_scope',
  evidence=[ev('CURB_SLOPE_worker','rows.append(dict(policy35='),dict(report=str(FILES['CURB_SLOPE_unused_preparation']),SHA=lineage['CURB_SLOPE_unused_preparation']['SHA'])],
  fields=['root','q30','policy35','raw6','done','reward','closure','mimic'],
  missing=['qdot/contact18/torque30/queueApplied6/xi31/reset/origin/actual clock','V2 was syntax-prepared and target_uploadFalse; do not invent native120 data existence'],
  note='This is a bounded pending classification, not a claim no useful CURB/SLOPE history exists anywhere. Need one existing actual artifact receipt and its executed producer per branch before any binary read.'),
 dict(family='Fudan_foreign_reference',category='exclude_from_MOD4_WM_groundtruth',clock='foreign2ms/derived4ms or declared5ms variants, different robot',
  note='Taskspace/reference goals only. Do not mix foreign full_qpos/actions/torques/body transitions as own MOD4 dynamics labels.',
  provenance_existing_frozen_index='fudan_original_vs_MOD4_reference_visual_provenance_v1/INDEX.json'),
]
plan=dict(schema='mod4.historical_WM_data_preparation.plan.v1',not_executed=True,
 target_layout=dict(packed_state=127,aux=54,staticxi=31,action=6,physical_joints=30,control_dt_s=.01,physics_dt_s=.0025,substeps=4),
 required_row_fields=['source_artifact_SHA_and_original_receipt','host_current_path','source_recipe/asset/plant/backend/clock','ordered_joint30/motor6/body/contact order','env_id','episode_id','global_control_id','s127','xi31_for_s','executed6','terminal_pre_reset_s1_127','done/term/timeout','reset_join_status','origin_transform'],
 preparation_steps=[
  'Materialize this metadata catalog first. Use latest verified72 retained_path for migratedNPZ. Do not try original210paths, transfer/cleanup again or regenerate hashes in this inventory.',
  'Root declares one new-purpose bounded extraction per selected artifact. Inspect fields/dtypes/shapes/order and original recipe metadata once; retain failures and original data. No actor, physics, policy retraining or replay rerun is needed.',
  'Start with same400 frozenC61 explicit transitions. Validate s127,xi31,executed6 and terminalpacked127/done same-point fields directly; retain failed episode label. It is small coverage, not convergence evidence.',
  'For H1 postcontrol trace, pair previous postcontrol state s with CURRENT row executed6 and current terminal state s1 only when controls contiguous, previousdoneFalse and episode identity matches. Never pair current action with the following state (off-by-one), across holes, or terminalstate with autoreset nextinitial.',
  'Restore only source-metadata/staticDR mapping evidence, not environment/actor. If source preupdate fullsave DR is available under a separately authorized read, use it only until selected reset changes thatenv; do not assume xi stays known after reset. Unknown xi is masked/unadmitted, never replaced by0/1.',
  'QueueApplied6 may be exactly recoverable at nonreset end-of-control because maxlag5ms<10ms, but ONLY after source-specific processed target offset/scale/clip/motor order and queue scheduling/reset proof. It is not equal raw6 or actuator torque. Do not claim reconstruction already performed.',
  'Subtract source env origins and bind ordered joints before current terrain-relative WM features. FullworldXY from20k environment grids cannot be treated as local H1 X. No guessed origin or axis change.',
  'Split train/holdout by episode and source/run before sampling overlapping windows; enforce actual contiguous windows and original terminal masks. Avoid leakage from duplicated/migrated SHA and two copies of the same motion.',
  'Old700 and current400 both encode spring factor relative to their own nominal, so xi31ratio1 aliases k3500 and2000. Use separate-domain pretraining→400-only calibration or explicitly version plant/dt/backend conditioning and model interface. No unconditional mixed training in current127/xi31 source.',
  'For50Hz data do not relabel20ms as10ms or interpolate pseudo nextstates. Use typed dt-conditioned dynamics or explicitly verified two10ms held-action rollout loss; adapt context/controller-delay semantics and declare architecture/admission changes.',
  'Missing-field sources may support a separately declared partial/base-state pretraining objective; do not pass them through existing full127 WM API by fake static/dynamic defaults. Preserve observed masks and provenance. No learner modification or training is executed here.',
  'Write immutable admitted_dataset_manifest with actual admitted transition counts by domain/phase/reset/coverage. Landing journal event0/32 or training32M transition counters are only pointers; they do not establish saved full-field samples. Root owns next actual data preparation and training protocol.'],
 current_source_directly_qualified_sample_count=0,
 note='Candidate means source/metadata suitability. No binary row was inspected in this task, so no dataset is marked actually installed/admitted.')
put('LATEST_VERIFIED72_MIGRATED_H1_NPZ_METADATA_CATALOG_ACTUAL.json',dict(artifacts=retained,total_files=len(retained),total_bytes_from_original_receipts=sum(x['bytes'] for x in retained),actual_signed_TLS_ack_evidence=ackproof,binary_files_not_accessed=True))
put('HISTORICAL_EXPERT_WM_REUSE_SOURCE_INVENTORY_ACTUAL.json',dict(schema='mod4.historical_WM_inventory.source_only.v1',families=classes,current400_retained=current,
 old_trace_and_current_trace_source_byteexact=lineage['old_H1_trace']['SHA']==lineage['current_H1_trace']['SHA'],
 important_limits=['bounded20coretextsources, not exhaustive allW inventory','source schema is not actual binary field/content qualification','all retained-path claims are as-of original actual signed/verified receipts; no new remote availability query','no old PT/NPZ/raw/ONNX/mesh content or stat/hash performed'],
 source_evidence=[ev('current_H1_trace','self.frame=dict('),ev('current_retention','protected=set('),ev('frozen400_driver','packed127_for_action=s[0]'),ev('E2_frame','self._own_flat_frame=dict(')]))
put('DATA_PREPARATION_TYPED_PLAN_ACTUAL.json',plan)
put('CORE20_SOURCE_REPORT_SHA_INDEX_ACTUAL.json',lineage)
put('SOURCE_READER_ERRORS_AND_SCOPE_ACTUAL.json',dict(errors=[
 dict(kind='filename_discovery_permission_error',path=str(W/'rmuc2026_work/unpack_verify_4zomhj13'),scope='initial rg filename-only discovery',followup='Skipped unrelated inaccessible path; bounded searches narrowed to knownMOD4 task directories. No binary read.'),
 dict(kind='source_output_truncation',scope='several path/source excerpts exceeded tool output token budgets',followup='Required fields parsed into this inventory; original source/error reports unchanged.')],
 no_binary_or_runtime_failure=True,no_datasets_actually_admitted=True))
put('HANDOFF.md',f'''# FROZEN bounded historical expert WM data reuse inventory

This is20-core-source/report metadata work only. No NPZ/npy/raw/PT/ONNX or mesh content/stat/hash, actor/WM forward, physics/SDK/GPU, SSH/download, transfer/cleanup, training, budget or Git operation occurred. All old frozen dirs stay unchanged. OrdinaryGit supplementation is root-owned.

The history can help WM, but expert names/weights/skill counts are not transition data. No dataset is actually admitted here. Field-complete same400 candidate: the newly saved frozenC H1 single episode, source producer explicitly writes `packed127_for_action`, `xi31_for_action`, `terminal_packed127_same_point`, terminal executed6 anddone.61controls/N1 only; a useful failed-trajectory candidate, not skill/diversity. Root must perform one newly declared content/schema extraction before admission. Its rawJSONL was not read here.

Current400 training prefixes retain **h1 72controls×4096={current['h1']['retained_env_control_snapshots']} postcontrol snapshots**, **recovery67×4096={current['recovery']['retained_env_control_snapshots']}** (latest partial19). Original complete counts7944/3235 are not saved sample counts. Middle was pruned. First24+latest48 applies h1; recovery is first24+latest43. There are gaps; cannot concatenate them as a continuous episode. Rawtrace retains root13/q30/qdot/contact18/torque30/executed6/done/episode, but omits persistedqueueApplied6 andxi31. Private bridge runtime state existing in memory does not mean savedNPZ contains it.

Old79c/80/81O/82Q/83B:14NPZs, {sum(x['bytes'] for x in retained)}B from original receipts, exact latest72 paths/bytes/producerSHAs in `LATEST_VERIFIED72_MIGRATED_H1_NPZ_METADATA_CATALOG_ACTUAL.json`. They are already minimally moved and verified. **Use target_path**, never assume old210path still present.82Q actualreceiver COMPLETE explicitly asserts TLS_pin_HMAC_and_full_SHA; the saved transport source SHA and report SHA are included. Other batches' original successful composite fullSHA receipts remain linked. No signatures/keys are regenerated, no retransfer/cleanup/hash. Additional signed-ack detail, if needed, must reuse original receipt, not reruntransport.

OldH1700N100Hz data is valuable same-robot pretraining evidence, but conditional plant meaning differs: currentxi spring factor1 means nominalk2000 while oldfactor1 means3500, and upperlimit changed. Unconditional mixing aliases dynamics even if input widths match. Separate old700 domain pretraining→400-only calibration, or explicit versioned plant conditioning/model interface is required. Missingxi cannot be faked. Matching preupdate DR snapshots may recover nonreset spans under a new authorized source-state read; after reset parameters unknown until evidenced. Queue-applied targets might be reconstructed exactly at nonreset control boundaries if original processing/lag/reset source proves it, not assumed from rawaction.

Transition alignment matters: H1 trace row stores **post-action terminal state**. Pair previous row state + current row executedaction -> current row state, only if previousdoneFalse and sameepisode/contiguouscontrol. Drop gap/reset boundaries and unsupported initial rows. Preserve true terminal labels and mask rules; do not pair terminal with automatically reset initialstate. Recover source env origins (20k world grid) and actual joint/motor orders before current terrain-relative features.

NormalE2/E3 production is50Hz/8callbacks, not H1100Hz/4. Inspected E2 native144 is a distinct100Hz diagnostic (4callback assert) and saves more physical state; do not mislabel all E2 archives50Hz. Inspected E3 native24 only saves clock checks, while production branch mainly saves PPO checkpoints/logs. A `persist()` definition is not evidence of a dataset; older336/nativefull E3 sources remain pending their actual artifact/producer join.20ms data cannot be relabelled10ms or pseudo-interpolated; consider typed dt dynamics or source-proved two-step held-action loss later.

E0/W35 existing contactV3 MuJoCo reports really index qpos/qvel/actions and per0.5ms contacts/wrenches; it is more than obs-only. Representative E0/W35 actualpaths/SHAs and source field lists are included. Backend/asset/order/torque/contact/queue/DR semantics differ from IsaacPhysX400; require explicit mapping/domain conditioning or separate pretraining. Keep original force/fault reports unchanged, no new exclusion gate. Other obs/reward/router/health-only logs cannot synthesize qdot/root/contact/DR.

CURB/SLOPE inspected historicalworker writes only root/q30/action/obs/done/reward/closure/mimic; qdot/contact18/torque30/queue/xi/reset data absent. ItsV2 report says target_uploadFalse, so the prepared source does not prove native120 raw ran. This bounded inventory does **not** claim no useful CURB/SLOPE data exists elsewhere: one already-existing actual artifact receipt+executed producer per branch is the next necessary metadata join. No allW scan or binary search was performed. Landingjournal0/32 event counts likewise are leads only, not datasets.

Fudan foreign transitions remain excluded from own MOD4 WM groundtruth. Foreign reference goals may be used for task semantics, never as own plant transitions.

`DATA_PREPARATION_TYPED_PLAN_ACTUAL.json` gives an executable preparation sequence and immutable output-row contract: source recipe/domain/clock, origins/order, env/episode/control IDs, s127/xi31/executed6/terminal-s1/done/reset. This script already materializes the metadata manifest; root's next bounded extractor can consume that catalog without transport or rollout. No actual samples or training benefit are claimed. Split by episode/source before overlapping windows, deduplicateSHA, and report actual admitted counts/coverage rather than all-time32M updates. Model architecture, reward, physics and budget are untouched.

All20 files have exact source/report SHA+lineanchors in `CORE20_SOURCE_REPORT_SHA_INDEX_ACTUAL.json`; all read errors/output truncations are retained. This is an ordinary source-only supplementation, not newtrial/tag or live admission.
''')
put('FREEZE_STATUS_ACTUAL.json',dict(frozen_UTC=datetime.now(timezone.utc).isoformat(),complete=True,source_metadata_only=True,core_text_files=len(FILES),dataset_samples_actually_admitted=0,Git_supplementation='PENDING_ROOT'))
rows=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name!='INDEX.json':
  raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
put('INDEX.json',dict(files=rows,self_excluded='INDEX.json'))
print(json.dumps(dict(frozen=True,directory=str(D),INDEX_SHA=H((D/'INDEX.json').read_bytes()),core_sources=len(FILES),migrated_files=len(retained),current400_snapshot_controls=[current[k]['retained_snapshot_controls'] for k in ('h1','recovery')],frozen_case_receipt_rows=len(frozen_paths))))
