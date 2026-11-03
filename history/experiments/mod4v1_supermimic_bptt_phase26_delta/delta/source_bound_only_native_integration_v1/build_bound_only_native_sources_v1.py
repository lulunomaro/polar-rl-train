"""Exclusive NEW source generator. No parent/worker/stager/model/native execution."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parent
OLD=PROJECT/'source_frozen_embedded_teacher_native_v1'
V1=PROJECT/'source_bound_only_frozen_probe_v1'
HELPER='bound_only_native_helper_v1'
ROUTE='bound_only_native_route_v1'
GUARD='producer_bound_probe_guard_v1'
RUNTIME='bound_only_native_runtime_v1'
PARENT='single_gpu_e3_w35_bound_only_parent_v1.py'
WORKER='worker_formal_bound_only_v1.py'
STAGER='stage_bound_only_native_v1.py'
INDEX='BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json'
VARIANT='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'
PURPOSE='FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
PLAN='FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_PLAN_V1'
TASK_KIND='FROZEN_ZERO_UPDATE_BOUND_ONLY_N80_TASK_V1'
INTEGRATION='FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_INTEGRATION_V1'
ACTOR='OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE'
INDEX_KIND='SOURCE_ONLY_17_MAPPINGS_ZERO_UPDATE_BOUND_ONLY_NATIVE_V1'


def H(raw): return hashlib.sha256(raw).hexdigest()
def load(path,pin=None):
    raw=path.read_bytes()
    if pin: assert (len(raw),H(raw))==pin,(str(path),len(raw),H(raw))
    return raw.decode('utf-8').replace('\r\n','\n')
def change(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new,1)
def block(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    return ast.get_source_segment(text,node)
def replace_block(text,name,new): return change(text,block(text,name),new)
def emit(name,text):
    path=HERE/name
    if name.endswith('.py'): compile(text,str(path),'exec')
    with path.open('xb') as stream: stream.write(text.encode('utf-8'))
    return path
def info(path):
    raw=path.read_bytes(); return dict(path=str(path),bytes=len(raw),SHA256=H(raw))


def build():
    assert HERE.name=='source_bound_only_native_integration_v1'
    authority=json.loads((OLD/'TEACHER_NATIVE_SOURCE_DELIVERY_V1.json').read_bytes())
    for row in authority['stable_code']:
        path=Path(row['path']); assert path.is_relative_to(OLD)
        raw=path.read_bytes(); assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
    original_index_raw=(OLD/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json').read_bytes()
    assert (len(original_index_raw),H(original_index_raw))==(5685,'cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205')
    original_index=json.loads(original_index_raw)
    for row in original_index['entries']:
        path=Path(row['path']); assert path.is_relative_to(PROJECT) and path.suffix=='.py'
        raw=path.read_bytes(); assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
    patches=[]
    def written(name,before,after):
        emit(name,after)
        patches.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='SEALED_INPUT/'+name,tofile='NEW/'+name))
    old=load(V1/'bound_only_frozen_probe_v1.py',(19125,'4a47700a046d6c7d496223f551745c956d3ff693cd0f02c559354a9627bf61a6'))
    helper=old.replace('A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_RESIDUAL_PROBE_V1',VARIANT).replace('FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_N80_V1',PURPOSE).replace('FROZEN_ZERO_UPDATE_BOUND_ONLY_MEAN_RECEIPT_V1','FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_MEAN_RECEIPT_V1')
    helper=change(helper,'SOURCE-only ZERO_UPDATE tanh-residual probe; no native entry or eager Torch.','Native-capable ZERO_UPDATE tanh actor; capability is NOT actual admission or execution.')
    helper=change(helper,'NATIVE_ENABLED = False','NATIVE_ENABLED = True  # Selected-route CAPABILITY; actual external admission/execution is never inferred.')
    helper=change(helper,"value.get('action_clip') == 6. and value.get('native_enabled') is False","value.get('action_clip') == 6. and value.get('native_enabled') is True")
    helper=change(helper,'source-only probe/container semantics differ','native-capable probe/container semantics differ')
    helper=change(helper,'native_enabled=False, actual_admission_wait_close_or_skill=None','native_enabled=True, actual_admission_wait_close_or_skill=None')
    written(HELPER+'.py',old,helper)
    old=load(V1/'bound_only_frozen_route_v1.py',(3210,'bffc1a3426e7c072176a09140f3edbaaaffb115f88d4dba13736b4271a2eb403'))
    route=old.replace('import bound_only_frozen_probe_v1 as p','import '+HELPER+' as p').replace('SOURCE_ONLY_ZERO_UPDATE_BOUND_PROBE_ADAPTER_V1',INTEGRATION)
    route=change(route,'SOURCE-only adapter route, NOT a runnable native parent/worker or training loop.','Explicit native-capable ZERO_UPDATE route; not a dispatch or training loop.')
    route=change(route,'NATIVE_ENABLED = False','NATIVE_ENABLED = True  # Capability only, not a receipt of actual native admission.')
    route=change(route,"config.get('native_enabled') is False","config.get('native_enabled') is True")
    route=route.replace('NEW explicit SOURCE-only ZERO_UPDATE bound-probe route task required','NEW explicit selected native-capable ZERO_UPDATE bound-probe route task required')
    route=change(route,'class BoundOnlyCheckpointAdapter(base.A1CheckpointAdapter):','class BoundOnlyCheckpointAdapter(base.A1CheckpointAdapter):\n    caller_type = p.BoundOnlyPolicyCaller  # Virtual factory; never build or wrap a loaded mean twice.')
    route=change(route,'self.caller = p.BoundOnlyPolicyCaller(mean, boundary=base.OriginalEpisodeBoundary(mean.t, mean.device))','self.caller = self.caller_type(mean, boundary=base.OriginalEpisodeBoundary(mean.t, mean.device))')
    route=change(route,'approved_RSL_model_source=dict(p.APPROVED_RSL), native_enabled=False','approved_RSL_model_source=dict(p.APPROVED_RSL), native_enabled=True')
    written(ROUTE+'.py',old,route)
    old=load(OLD/'producer_teacher_guard_v1.py',(8902,'855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0'))
    guard=old.replace('ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1',VARIANT).replace('validate_reference_row','validate_bound_probe_row')
    guard=change(guard,'explicit embedded-original-teacher row required','explicit ZERO_UPDATE bound-only actor row required')
    guard=change(guard,"row.get('actor_semantics') == 'EMBEDDED_ORIGINAL_TEACHER_MEAN'","row.get('actor_semantics') == '"+ACTOR+"'")
    guard=change(guard,'reference actor/container semantic identity differs','bound probe effective-actor/container semantic identity differs')
    guard=change(guard,'    return evidence',"    config = row.get('bound_only_probe', {})\n    need(type(config) is dict and config.get('purpose') == '"+PURPOSE+"'\n         and config.get('policy_variant') == POLICY_VARIANT and config.get('zero_update') is True\n         and config.get('native_enabled') is True and type(config.get('collect_action_statistics')) is bool,\n         'explicit native-capable ZERO_UPDATE selection required')\n    expected = "+repr(ast.literal_eval(next(n.value for n in ast.parse(helper).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='QUALIFIED_CONTAINERS' for t in n.targets))))+"\n    need(row.get('role') in expected and row.get('source_SHA') == producer['FINAL']['checkpoint']['SHA'] == expected[row['role']],\n         'bound probe must retain the actual qualified original A1 container')\n    return evidence")
    written(GUARD+'.py',old,guard)
    old=load(OLD/'frozen_embedded_teacher_native_runtime_v1.py',(40728,'17c060dfeed5ccb5e5777554049e4bfe75fcd61b347f26a8646daf5e91ea9c00'))
    runtime=old.replace('frozen_embedded_teacher_native_runtime_v1',RUNTIME).replace('single_gpu_e3_w35_embedded_teacher_parent_v1.py',PARENT).replace('producer_teacher_guard_v1',GUARD).replace('embedded_teacher_reference_v1',HELPER)
    runtime=runtime.replace('ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1',VARIANT).replace('FROZEN_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1',PURPOSE).replace('FROZEN_EMBEDDED_TEACHER_E3_W35_REFERENCE_PLAN_V1',PLAN).replace('FROZEN_EMBEDDED_TEACHER_N80_REFERENCE_TASK_V1',TASK_KIND).replace('FROZEN_EMBEDDED_TEACHER_NATIVE_REFERENCE_INTEGRATION_V1',INTEGRATION)
    runtime=runtime.replace('ACTUAL_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1','ACTUAL_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1').replace('ACTUAL_WAITED_EMBEDDED_ORIGINAL_TEACHER_N80_REFERENCE_SEMANTIC_V1','ACTUAL_WAITED_ZERO_UPDATE_BOUND_ONLY_N80_SEMANTIC_V1').replace('CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1','CLOSED_ZERO_UPDATE_BOUND_ONLY_NATIVE_SOURCE_GRADE_V1')
    runtime=runtime.replace('grade_closed_reference_group','grade_closed_bound_probe_group').replace('passed_closed_reference_source_grade','passed_closed_bound_probe_source_grade').replace('qualified_reference_execution','qualified_bound_probe_execution').replace('validate_reference_row','validate_bound_probe_row')
    runtime=change(runtime,'Embedded ORIGINAL TEACHER reference E3/W35 schema; original plant/barrier/close retained.','ZERO_UPDATE tanh-bound-only E3/W35 schema; original plant/barrier/close retained.')
    runtime=change(runtime,"    '"+HELPER+".py', '"+GUARD+".py', 'resume_runtime_contracts_v3.py',","    '"+HELPER+".py', '"+ROUTE+".py', '"+GUARD+".py', 'resume_runtime_contracts_v3.py',")
    runtime=change(runtime,repr((8902,'855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0')),repr((info(HERE/(GUARD+'.py'))['bytes'],info(HERE/(GUARD+'.py'))['SHA256'])))
    runtime=change(runtime,"_ref = _base._pinned_module('"+HELPER+"', (16333, '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'))","_probe = _base._pinned_module('"+HELPER+"', "+repr((info(HERE/(HELPER+'.py'))['bytes'],info(HERE/(HELPER+'.py'))['SHA256']))+")\n_route = _base._pinned_module('"+ROUTE+"', "+repr((info(HERE/(ROUTE+'.py'))['bytes'],info(HERE/(ROUTE+'.py'))['SHA256']))+")")
    runtime=runtime.replace('explicit original teacher reference policy required','explicit ZERO_UPDATE bounded effective policy required').replace('explicit independent ORIGINAL TEACHER reference purpose required','explicit independent ZERO_UPDATE bound-only purpose required').replace('all sixteen complete reference mappings','all seventeen complete bound-only mappings')
    runtime=runtime.replace('REFERENCE_POLICY_IDENTITY.json','BOUND_PROBE_POLICY_IDENTITY_V1.json').replace('BothRequestedOriginalScenes_EmbeddedOriginalTeacher_N80FullDR_BeforeAnyControlledStep','BothRequestedOriginalScenes_ZERO_UPDATE_BoundOnly_N80FullDR_BeforeAnyControlledStep')
    runtime=change(runtime,'        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))','        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))')
    runtime=change(runtime,'policy_variant=POLICY_VARIANT, reference_not_candidate=True,','policy_variant=POLICY_VARIANT, zero_update_bound_probe=True, native_capable=True, actual_native_enabled=False, actual_staged=False,')
    oldcaller=block(runtime,'ReferenceCaller')
    newcaller='''class BoundProbeCaller(_probe.BoundOnlyPolicyCaller):
    def receipt(self):
        return dict(super().receipt(), paired_reset_protocol=paired_protocol_receipt(), unresolved_evidence=unresolved_evidence())'''
    runtime=change(runtime,oldcaller,newcaller)
    runtime=replace_block(runtime,'A1CheckpointAdapter','''class A1CheckpointAdapter(_route.BoundOnlyCheckpointAdapter):
    """ONE original cache; virtual caller factory, never super().actor then rebuild."""
    caller_type = BoundProbeCaller
    def __init__(self, torch_module, task):
        validate_bound_probe_row(task)
        super().__init__(torch_module, task)
    def receipt(self):
        value = super().receipt()
        value.update(integration=INTEGRATION, batch_purpose=BATCH_PURPOSE,
            actor_semantics='''+repr(ACTOR)+''',
            actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
            original_bootstrap_teacher=dict(self.task['original_bootstrap_teacher']),
            producer_teacher_freeze_evidence=validate_bound_probe_row(self.task),
            old_RSL_actor_checkpoint_loader_used=False,
            approved_reference_provenance=dict(self.task['approved_reference_provenance']),
            admitted_producer_run_id=self.task['a1_producer']['run_id'],
            actual_BPTT_policy_steps=self.task['a1_producer']['FINAL']['actual_BPTT_policy_steps'],
            legacy_source_provenance_aliases_are_historical_not_probe_updates=True,
            actual_eval_RSL_source_binding=(dict(self.caller.mean.source_bindings['rsl_rl.models.MLPModel']) if self.caller is not None else None))
        if self.caller is not None:
            value['bound_only_probe'] = value.pop('frozen_mean')
        return value''')
    start=runtime.index('        evidence = validate_bound_probe_row(role_entry)',runtime.index('def evaluate_waited_eval_case'))
    end=runtime.index("        need((case / 'PRE_CLOSE.json')",start)
    runtime=runtime[:start]+'''        evidence = validate_bound_probe_row(role_entry)
        probe = source.get('bound_only_probe')
        _probe.validate_bound_probe_receipt(probe, expected_role=role, expected_source_sha=checkpoint['SHA'], expected_actor_calls=CONTROLS[role])
        need(probe.get('synthetic_only') is False and source.get('native_enabled') is True
             and source.get('probe_training_updates') == source.get('probe_BPTT_policy_steps') == 0
             and source.get('probe_optimizer_updates') == dict(pi=0, wm=0, aux=0, critic=0)
             and source.get('producer_teacher_freeze_evidence') == evidence and 'frozen_mean' not in source
             and 'embedded_teacher_reference' not in source and source.get('policy_variant') == POLICY_VARIANT
             and source.get('policy_family') == 'zero_update_tanh_postprocess_of_original_full_A1_not_training'
             and source.get('actor_semantics') == '''+repr(ACTOR)+'''
             and source.get('original_bootstrap_teacher') == role_entry['original_bootstrap_teacher'],
             'ZERO_UPDATE effective actor/source/producer identity differs')
        paired = probe.get('paired_reset_protocol')
        need(type(paired) is dict and paired.get('candidate_pose_installed') is True
             and paired.get('protocol') == validate_paired_protocol(role_entry.get('paired_reset_protocol')),
             'shared original pose installer/protocol receipt missing; no matched UID claim')
'''+runtime[end:]
    runtime=change(runtime,"need(final.get('policy_variant') == POLICY_VARIANT and final.get('evaluation_purpose') == BATCH_PURPOSE,","need(final.get('policy_variant') == POLICY_VARIANT and final.get('evaluation_purpose') == BATCH_PURPOSE\n             and final.get('actor_semantics') == "+repr(ACTOR)+", ")
    runtime=runtime.replace('explicit reference FINAL variant/purpose required','explicit bound-probe FINAL variant/purpose required')
    runtime=runtime.replace('reference original semantic gate differs after close','bound-probe original semantic gate differs after close').replace('original reference batch FINAL incomplete or mismatched','original bound-probe batch FINAL incomplete or mismatched')
    runtime=change(runtime,"source20k_DR_history_sliced=False, source20k_histories_physically_applied=False,","source20k_DR_history_sliced=False, source20k_histories_physically_applied=False,\n        probe_training_updates=0, probe_BPTT_policy_steps=0, probe_optimizer_updates=dict(pi=0, wm=0, aux=0, critic=0),")
    written(RUNTIME+'.py',old,runtime)
    old=load(OLD/'worker_formal_embedded_teacher_v1.py',(15282,'2eb7c14229a8a79cc6b511fa249dd4ec230fafed0e0991878e109e51b0f7a221'))
    worker=old.replace('frozen_embedded_teacher_native_runtime_v1',RUNTIME).replace('EMBEDDED ORIGINAL TEACHER MEAN, explicit E3/W35 reference barrier','ZERO_UPDATE BOUND ONLY, explicit E3/W35 probe barrier').replace("actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN'","actor_semantics="+repr(ACTOR))
    written(WORKER,old,worker)
    old=load(OLD/'single_gpu_e3_w35_embedded_teacher_parent_v1.py',(9356,'4d77e137e96c34561976815fc6438c8cef109a42c860ff1c40efff9f3d06f0cd'))
    parent=old.replace('frozen_embedded_teacher_native_runtime_v1',RUNTIME).replace('EMBEDDED ORIGINAL TEACHER reference','ZERO_UPDATE BOUND ONLY probe').replace('ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1','ONEGPU_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1').replace('grade_closed_reference_group','grade_closed_bound_probe_group').replace('reference_parent_entry','bound_probe_parent_entry').replace('REFERENCE_GROUP_CLOSED_SOURCE_GRADE_V1.json','BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json').replace('passed_closed_reference_source_grade','passed_closed_bound_probe_source_grade')
    written(PARENT,old,parent)
    index=copy.deepcopy(original_index)
    index.update(kind=INDEX_KIND,source_variant=VARIANT,actual_staged=False,actual_native_enabled=False,
        source_native_capable=True,actual_qualified_bound_probe_execution=None)
    for row in index['entries']:
        rel=row['relative']
        if rel=='single_gpu_e3_w35_embedded_teacher_parent_v1.py': row.update(path=str(HERE/PARENT),relative=PARENT)
        elif rel=='frozen_embedded_teacher_native_runtime_v1.py': row.update(path=str(HERE/(RUNTIME+'.py')),relative=RUNTIME+'.py')
        elif rel=='worker_sources/parent/worker_five_original_n80.py': row['path']=str(HERE/WORKER)
        elif rel=='embedded_teacher_reference_v1.py': row.update(path=str(HERE/(HELPER+'.py')),relative=HELPER+'.py')
        elif rel=='producer_teacher_guard_v1.py': row.update(path=str(HERE/(GUARD+'.py')),relative=GUARD+'.py')
    index['entries'].append(dict(path=str(HERE/(ROUTE+'.py')),relative=ROUTE+'.py'))
    for row in index['entries']: row.update({k:v for k,v in info(Path(row['path'])).items() if k!='path'})
    index_raw=(json.dumps(index,indent=2)+'\n').encode(); emit(INDEX,index_raw.decode())
    old=load(OLD/'stage_embedded_teacher_native_v1.py',(34156,'e9051dfeb2fd3f08437c4985d2e2f4a6d3229ed75eff870fc3216a7a810e4783'))
    stage=old.replace('single_gpu_e3_w35_embedded_teacher_parent_v1.py',PARENT).replace('frozen_embedded_teacher_native_runtime_v1',RUNTIME).replace('embedded_teacher_reference_v1',HELPER).replace('producer_teacher_guard_v1',GUARD)
    stage=stage.replace('FROZEN_EMBEDDED_TEACHER_E3_W35_REFERENCE_PLAN_V1',PLAN).replace('FROZEN_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1',PURPOSE).replace('ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1',VARIANT).replace('EMBEDDED_ORIGINAL_TEACHER_MEAN',ACTOR)
    stage=stage.replace('SOURCE_ONLY_16_MAPPINGS_EMBEDDED_ORIGINAL_TEACHER_NATIVE_V1',INDEX_KIND).replace('sixteen','seventeen').replace('len(entries) == 16','len(entries) == 17')
    stage=change(stage,"INDEX_PIN = (5685, 'cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205')",'INDEX_PIN = '+repr((len(index_raw),H(index_raw))))
    stage=change(stage,"    '"+HELPER+".py', '"+GUARD+".py'}","    '"+HELPER+".py', '"+ROUTE+".py', '"+GUARD+".py'}")
    stage=change(stage,"'"+RUNTIME+"', '"+HELPER+"', '"+GUARD+"', 'app_close_semantics_v5'","'"+RUNTIME+"', '"+HELPER+"', '"+ROUTE+"', 'frozen_a1_raw35_v1', '"+GUARD+"', 'app_close_semantics_v5'")
    stage=change(stage,"producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]))","producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]),\n                bound_only_probe=dict(purpose="+repr(PURPOSE)+", policy_variant="+repr(VARIANT)+",\n                    zero_update=True, native_enabled=True, collect_action_statistics=collect_action_statistics))")
    stage=change(stage,'*, vendor_pin=VENDOR_PIN):','*, vendor_pin=VENDOR_PIN, collect_action_statistics=False):')
    stage=change(stage,'    original_group_root, new_root = lexical(original_group_root), lexical(new_root)','    need(type(collect_action_statistics) is bool, \'statistics selection must be an explicit bool\')\n    original_group_root, new_root = lexical(original_group_root), lexical(new_root)')
    stage=change(stage,"result.get('reference_not_candidate') is True","result.get('zero_update_bound_probe') is True and result.get('actual_native_enabled') is False")
    stage=stage.replace('EMBEDDED_TEACHER_REFERENCE_V1','BOUND_ONLY_NATIVE_V1').replace('SOURCE_TEACHER_REFERENCE_PREFLIGHT_ONLY_NO_ADMISSION_V1','SOURCE_BOUND_ONLY_NATIVE_PREFLIGHT_NO_ADMISSION_V1').replace('SOURCE_TEACHER_REFERENCE_STAGE_COMPLETE_NOT_DISPATCH_V1','SOURCE_BOUND_ONLY_NATIVE_STAGE_COMPLETE_NOT_DISPATCH_V1')
    stage=stage.replace('Teacher-reference stdlib ONLY:','ZERO_UPDATE bound-only stdlib ONLY:').replace('reference metadata CLI variant differs','bound-only metadata CLI variant differs').replace('complete sixteen reference mappings','complete seventeen bound-only mappings')
    stage=change(stage,"model_stat_hash_open_decode=0, C_lock_SDK_GPU_GO_operations=0, parent_launches=0, staged=False)","model_stat_hash_open_decode=0, C_lock_SDK_GPU_GO_operations=0, parent_launches=0, staged=False, actual_native_enabled=False)")
    stage=change(stage,"receipt = dict(kind='SOURCE_BOUND_ONLY_NATIVE_STAGE_COMPLETE_NOT_DISPATCH_V1', staged=True,","receipt = dict(kind='SOURCE_BOUND_ONLY_NATIVE_STAGE_COMPLETE_NOT_DISPATCH_V1', staged=True, actual_native_enabled=False,")
    stage=change(stage,"    modes = parser.add_mutually_exclusive_group(required=True)","    parser.add_argument('--collect-action-statistics', action='store_true', help='Read-only SAME-forward scalar reductions; default off, host synchronization affects walltime only.')\n    modes = parser.add_mutually_exclusive_group(required=True)")
    stage=change(stage,'args.native_root, args.new_root, args.group_id, args.gpu_uuid)','args.native_root, args.new_root, args.group_id, args.gpu_uuid, collect_action_statistics=args.collect_action_statistics)')
    written(STAGER,old,stage)
    old=load(V1/'remote_cpu_bound_only_synthetic_v1.py',(10730,'54c6852638a52504cda5de9c8e03baab5c3c258cb60d9359f1238a2c248ceb7e'))
    cpu=old.replace('import bound_only_frozen_probe_v1 as p','import '+HELPER+' as p').replace('ACTUAL_SOFTWARE_CPU_ZERO_UPDATE_BOUND_ONLY_PROBE_V1','ACTUAL_SOFTWARE_CPU_NATIVE_CAPABLE_ZERO_UPDATE_BOUND_ONLY_PROBE_V1')
    written('remote_cpu_bound_only_native_synthetic_v1.py',old,cpu)
    emit('BOUND_ONLY_NATIVE_WHITELIST_DIFF_V1.patch',''.join(patches))
    emit('BUILD_BOUND_ONLY_NATIVE_SOURCE_V1.json',json.dumps(dict(source_only=True,actor_math_changed=False,
        source_native_capable=True,actual_native_enabled=False,actual_staged=False,mappings=17,
        files=[info(HERE/n) for n in (HELPER+'.py',ROUTE+'.py',GUARD+'.py',RUNTIME+'.py',PARENT,WORKER,STAGER,INDEX)],
        parent_or_worker_or_stager_or_Torch_executed=False),indent=2)+'\n')
    print(json.dumps(dict(source_only=True,mappings=17,actual_native_enabled=False,actual_staged=False,
        index=info(HERE/INDEX)),indent=2))

if __name__=='__main__': build()
