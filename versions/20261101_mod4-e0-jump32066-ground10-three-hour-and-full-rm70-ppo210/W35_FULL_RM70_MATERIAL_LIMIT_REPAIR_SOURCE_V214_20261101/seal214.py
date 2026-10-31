"""Freeze material failure evidence and candidate;no target or model read."""
from pathlib import Path
import hashlib,json,time

H=Path(__file__).resolve().parent;T=H.parent;W=T.parent;S=H/'source';R=H/'reports'
P=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
OLD=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4'


def read(path):return json.loads(path.read_bytes())
def row(path):
    if path.suffix not in ('.json','.py','.md','.txt'):raise ValueError('No binary inputs in214seal')
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def write(name,value):
    with (R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False)


def main():
    cpu=read(R/'CPU214_ACTUAL.json');assert cpu['passed']
    frozen=read(R/'CPU214_PURPOSE_FROZEN.json')
    for r in frozen['source_rows']:
        raw=Path(r['path']).read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']
    comparison=R/'ROOT214_E0_SAVED_UPDATES_SOURCE_COMPARISON_ACTUAL.json'
    first=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_W35_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'
    write('MATERIAL214_CAUSE_SCOPE_AND_PRESERVED_FAILURE.json',dict(
        schema='mod4.W35.material214.source_diagnosis.v1',epoch=time.time(),
        actual_failure=dict(source='root provided actual first/error report',path=str(first),
            bytes_metadata_only=first.stat().st_size,child_did_not_read_large_stdout=True,
            last_observed_error='2026-10-31T16:31:57Z [445,121ms] [Error] PhysX PxPhysics::createMaterial: limit of64K materials reached',
            worker_pid=990366,worker_creation=1793463868.49,
            fullrestore_native24_FIRST_not_captured=True,sole_cause_of_no_FIRST_not_proven=True),
        original_stop_scope=dict(root_receipt=str(T/'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101/reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json'),
            source='parent/root actual receipt;not rechecked by214child',
            human_authorized_only_W35_fault_process=True,
            STOP_SIGINT_no_exit_then_exact_identity_TERM_necessaryKILL=True,
            original_postsignal_exit_race_RC1_preserved=True,
            independent_readonly_followup_workerOUT_nodewait_minus9_privateEXreleased_ownerACK=True,
            E0_not_signalled_or_changed=True,no_child_signal_or_account_action=True),
        consumed_E0_comparison=dict(report=row(comparison),
            actual_comparison_repeated_by_child=False,
            root_reported_mildDR_byte_identical=True,
            root_snapshot_E0_new_PPO_updates=67,root_snapshot_transitions=32160000,
            root_snapshot_timeouts=32037,root_snapshot_orientation_resets=66,root_snapshot_closure_perenv_resets=6,
            same_sampler_code_alone_not_established_global_64K_cause=True,
            E0_root_or_flight_statistics_not_jump_acceptance=True),
        original_sources=dict(robot_config=row(OLD/'mod4_task.py'),mildDR=row(OLD/'mild_dr.py'),
            original_CAD_authoring=row(W/'rmuc2026_work/build_assets.py'),
            original_field_layout=row(P/'source/field208.py')),
        source_facts=[
            'Robot UsdFileCfg already copy_from_source=False;do not revert it or copy all CAD meshes/materials perenv',
            'MildDR already uses33exact triples:nominal.9 and32uniform-bucket values inwhite_v3 .7..1;bothwheel μ equal,rest0;sampling and bothRNG unchanged',
            'Oldfield208 references complete/Asset perenv,includingmesh and physics_material sibling;20k composition can expand material paths,but USDpaths/value counts are not PhysXhandles',
            'Original CAD authoring material .9static/.8dynamic/0rest;oldgenerator config also carries its originalgroundmaterial settings;do not invent replacementcoefficients',
            'Original fullrestore sensor path restores physical namedRNG then originalenv.reset;D5/D6/D7 loadmethods issue existing physical parameter setters',
            'MildDR originally has no state_dict method for all physicalvalues;214model-free probe owns an explicit samepopulation snapshot and one extra same-value material reapply as disclosedstress,not a claim about a preexisting productionloader'],
        candidate='geometry-only prototype reference to original/Asset/mesh;one shared reference to original/Asset/physics_material inside layout defaultroot,strong inheritedphysicsbinding',
        actual_PhysX_capacity_or_material_interning_proven=False,
        no_geometry_wave_slope_DR_guard_or_budget_change=True))
    probe=row(S/'material0pt214.py')
    write('TARGET214_REQUIRED_20K_ZERO_PT_PURPOSE.json',dict(
        schema='mod4.W35.material214.20k_zeroPT_task.v1',status='SOURCE_CPU_PASSED_ACTUAL_TARGET_NOT_RUN',
        purpose_id='RM70_SHARED_ORIGINAL_MATERIAL20K_OWN_RESTORE214_NEW_UNUSED',
        entry=probe,command='ACTUAL_SDK_PYTHON -B -X utf8 runtime/isaac/mod4/material0pt214.py --job-root NEW_UNUSED_JOB',
        task_file='MATERIAL0PT214_TASK.json',
        task_fields=dict(kind='NEW214_RM70_SHARED_MATERIAL_20K_OWN_RESTORE_ZERO_PT',num_envs=20000,controls=8,
            physics_callbacks=64,feedback_samples=16,model_opens=0,actor_calls=0,optimizer_updates=0,
            max_worker_seconds=1680,original_manifest_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb',
            worker_SHA=probe['SHA'],GPU_UUID='root actual c27 selected UUID only after actual exclusive lease',
            actual_parent_exclusive_control_GPU_private_shared_admission='ACTUAL true only'),
        additional_root_admission=dict(current_authority='E0 originalowner210 may still beactive;fresh exactactualowner/run/go binding,never fabricatedCNone',
            original72_readonly_then_CLOSE72_before_target=True,
            fresh_LOCAL_exact_CIM_and_global_serial_SSH=True,
            selected_c27_original_faultworker_OUT_and_EXactuallyFREE_required=True,
            original_startup_light='4090free>15669MiB/util<=30/RAM>32GiB/disk>25GiB,originalshared/privateguards;nonemptycomputeUUIDallowed',
            parent_original_supervisor_seconds=1800,worker_seconds=1680,
            parent_must_bound_App_startup_and_wait_all_children_and_closeSDK=True,
            no_PPO_or_ledger_or_newwriter_or_grant=True,no_E0_signal_or_hotpatch=True),
        exact_scope=[
            'Original complete CAD geometry,20k original robots/35obs38critic6actions/400N50/TGS32/4',
            'Fresh20k env construction and originalfreshreset with allsourceμ33buckets',
            'Own same20k snapshot in memory,no PT/NN or20k-to-small projection',
            'Own μ/mass/inertia/motor values andRNG restore with explicitly extra same-value actualmaterial reapply',
            'Original D1-D7 ownload_state_dict paths and physical parameter setters,command/global+namedRNG restore',
            'Original newepisode reset once,originalparameter audit,then8controls64physics16feedback64legs+64wheels queue'],
        required_material_evidence=['before/after construction,originalMildDR materialcache read,eachactual project set_material_properties APIcall,ownrestore/newreset/native8phase markers',
            'Full terrain USDinstanceproxy MaterialAPI paths,distinctcomputed boundpaths andmaterialattribute signatures;never label them PhysXhandlecounts',
            'Cached property value triplecounts andoriginalmu33bucket sampling evidence;no extra materialgetter added bysetterobserver',
            'One shared originalmaterial reference withno authoredfriction/restitution/combineoverride;record actualboundattributes',
            'Parent scans original ownedstdout/stderr for PxPhysics::createMaterial / limitof64Kmaterials reached;ANY match preventspromotion evenif OSRC0 or nativefunction passed'],
        observer_scope='mild_dr214.py instruments onlyexisting reset setter;restore214 one extra same-value write is explicit probe-only;SDK internal allocator handles remainUNKNOWN',
        output_reports=['material0pt214/MATERIAL214_PHASE_AND_SETTER_EVENTS.jsonl (newsmallMETADATA report,notteacher/rawtrajectory;explicitpurpose permits rootmetadata retrieval)',
            'material0pt214/new_layout/MATERIAL214_COMPOSITION_PLAN.json',
            'material0pt214/MATERIAL0PT214_NATIVE_RETURNED_ACTUAL.json',
            'originalstdout/stderr fullownedlog andoriginal parentwait/SDKclose/EXrelease'],
        acceptance='actual20k complete/requiredphase evidence/originalμ+parameterchecks/native8/0 knownmateriallimiterrors/allownwaitout;notmaterial-onlyRC0,not80env extrapolation',
        not_covered=['Exact sourcePPO17Adam/STD/fullstate restore','ActualfirstnewPPO update/fullsave','CompleteRM70skill','Unique cause of oldmissingFIRST'],
        original_native160k_and_old213_CPU_not_replayed=True,
        binary_inputs_metadata_only='Reuse original robot700Ngeometry+400Nlayer/importcontract/resetbank andoriginalarena .usdc/.npz installation receipts;214child reads none',
        install='All214source .py undernewjob runtime/isaac/mod4;reuse exact originalW35 runtime+208xyzwlearning/reset/launcher/sourcecache dependencies fromfrozenV3;do not edit original210job',
        actual_target_executed_by_child=False))
    write('NEXT214_AFTER_PROBE_PRODUCTION_SOURCE_CONTRACT.json',dict(
        status='UNUSED_SOURCE_CANDIDATE_ONLY_CAPACITY_PASS_AND_ROOT_JOIN_REQUIRED',
        worker=row(S/'worker_full214.py'),entry=row(S/'train_full214.py'),config=row(S/'config214_training.py'),
        kind='MOD4_W35_FULL_RM70_MATERIAL_SHARED214',
        originalCLI='--mode train --num-envs 20000 --run-id RUN --out NEW_JOB/production',
        source_model_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
        source_bytes=17619013,source_iteration=32336,Adam17=648360,LR=.00011390625000000003,
        original_task_go_and_FULLSTATE_FIRST_FINAL_ABI='samefrozen208V3;saveiter32336+actualupdates andAdam648360+20updates;sourcephysicalread1/decode1',
        new_required_task_fields=dict(actual_shared_material20k0PT_passed='actualtrueonly',actual_material_limit_error_count=0),
        production_uses_original_mildDR_class_not_probe_observer=True,
        production_extra_own_snapshot_reapply=False,
        only_production_material_change='field214geometry-onlyprototype+singlesharedORIGINALmaterial',
        original_3900_save3600_exit300_and_solecanonical_writer_unchanged=True,
        no_hotadd_currentowner210=True,root_next_original_owner_window_only=True,
        not_ready_for_GO_before_actual_capacity_and_actual_all_other_startup_checks=True,
        failed_originalW35_job_or_partialweights_not_promoted=True,
        no_new_modelCPU_read_for_stats_or_Git=True))
    write('MATERIAL214_SCOPE_ERRORS_AND_RECORDING.json',dict(
        CPU_actual=cpu,source_derivation_executions=['NEW214_MATERIAL_SHARING_SOURCE_DERIVATION_V1',
            'NEW214_20K_MATERIAL_OWN_RESTORE_PROBE_SOURCE_V1','NEW214_AFTER_CAPACITY_PROBE_TRAINING_SOURCE_ONLY'],
        extra_reader_error='feedback_delay_training_env.py guessed lookup ENOENT;actual originalstate provider is feedback_delay_runtime.py;no SDK orrobotfailure',
        combined_source_tool_output_truncated_once='narrow exactsource slices read;no conclusion from clipped text',
        source214core_frozen_CPU_rows=frozen['source_rows'],
        after_CPU_training_delta='source-only textualderivative ofexistingV3 forfutureuse;no extra CPUfixture replay orSDKexecution',
        all_V3_210_material_errors_andoriginalterminationrace_retained=True,
        no_sole_cause_claim=True,root_saved_comparison_purpose_consumed_not_rerun=True,
        child_PT_NPZ_USD_SDK_GPU_SSH_Git_Go_automation_or_goal_calls=0,
        all_new_reports_sources_pending_root_Git=True))
    with (H/'HANDOFF214.md').open('x',encoding='utf8')as f:f.write('''# W35 material214 candidate

SOURCE/CPU ONLY. No PT,NPZ,USD,SDK,GPU,SSH,Git,GO,account,Goal orautomation action bythischild. The originalW35 failure andtermination receipts remain unchanged. E0 comparison alreadydone byroot:identicalmild_dr source andongoing67updates/manyresets refutes treating μsampler codealone asestablishedglobalcause.64K is observed,not proven sole reason for missingFIRST.

Candidate field214.py references ONLY originalCAD/Asset/mesh in a sharedgeometryprototype;layout defaultroot contains ONE reference to original/Asset/physics_material andstrong inheritedphysicsbinding. No materialcoefficients are invented:originalCAD authoring is.9static/.8dynamic/0rest,andactualboundattributes must be recorded. Originalfullwave/slope/points/faces/contactoffsets are retained. Originalrobot copy_from_source=False andoriginal33wheelμbucket sampler/RNG remain. USDprim/valuecounts are not PhysXhandlecounts.

New214 CPU purpose passed3groups/3refusals at20k plainCPUvaluebuffers:exact old/new reset method sampling,mass,motor,nominal,μ andbothRNG preserved across2resets;candidate adds one disclosedsame-value ownstate reapply withoutdraws. This is not USDcomposition or PhysX64K capacity proof. No old213/208fixture was rerun.

Use reports/TARGET214_REQUIRED_20K_ZERO_PT_PURPOSE.json for exactnextrootentry material0pt214.py,Task/sourceSHA/resources/dependencies andpromotionrule. It requires FULL20k freshconstruction→freshreset→own20kstate materialreapply + originalD1-D7load physicalsetters→originalone newepisode reset→8controls(64physics16feedback,64perqueuegroup),0PT/NN0.1680worker/1800originalparentbound. CurrentE0owner210 isactive:rootmust usefresh exactknownowner/run/go binding,close72 beforetarget,c27actualEXfree andoriginalsharedguards. No fakeCNone,newlearning/secondwriter orE0interference.

Everyprojectactualmaterialsetter hasbefore/aftermarkers pluscachedvalues,terrain MaterialAPIprim/boundpath/attribute census. Rootmust rejectANYknown64Kerror inownedstdout/stderr evenif OSRC0/nativefunctionreportpassed. Only a complete actual20k cleanmaterial/native/ownwait+out result permits laterproductionreview;N1/80 success cannot cover this limit.

Unusedfutureworker_full214.py/train_full214.py/config214_training.py keep originalMildDR(noobserver orprobe-extra-reapply),alloriginalPPO/guard/fullstatecache/parentFIRST/FINALcontracts andselectedad504fec…formal. Theychange onlyfieldmaterialorganization andrequireactual20k0PTzero64Klogs. No hotadd toowner210;futureoriginalownerwindow+actualTaskGOJOIN needed. Fullrestore/native24/FIRST andRM70skill remainseparate.

Alloriginalerrors,newsource/reports/rootcomparisonandCPUproof awaitrootunique214/actualprobe Gitphase. Nothinglocal-only is called Git-recorded.
''')
    files=[]
    for p in sorted(H.rglob('*')):
        if p.is_file():files.append(dict(**row(p),relative=p.relative_to(H).as_posix()))
    index=H/'INDEX214_FROZEN.json'
    with index.open('x',encoding='utf8')as f:json.dump(dict(
        schema='mod4.W35.material214.complete_source_index.v1',epoch=time.time(),files=files,
        status='SOURCE_CPU_PASSED_ACTUAL_20K_CAPACITY_PROBE_PENDING',
        selected_probe=probe,CPU_actual=cpu,old_failure_and_roottermination_unchanged=True,
        actual_repaired_training_or_skill_claimed=False,all_new_reports_Git_pending_root=True),f,indent=2)
    print(json.dumps(dict(index=row(index),files=len(files),probe=probe)))


if __name__=='__main__':main()
