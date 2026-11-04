"""Eight NEW stdlib SOURCE cases. No old suite, native run or science claim.

The full original metadata modules are imported normally. Only synthetic plain
JSON/protocol fixtures under this NEW package are exercised, never real FINALs.
"""
from pathlib import Path
import ast
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import time
import unittest

import typed_collector_contract as C
import remote_metadata_reader as M
import collect_capture_result as K
import source_pins as P

HERE = Path(__file__).resolve().parent
R = HERE.parent
FIXTURE = HERE/'_SOURCE_ONLY_SYNTHETIC_METADATA_WORKSPACE'
FORBIDDEN = []; OPEN_EVENTS = []; PROFILE_FAILURES = []
BLOCKED = {'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict'}
SOURCE_ENTRY_NAMES = {'main','prepare','preflight_summary','stage','metadata_validate','native_boundary',
    'task_args','validate_group_task','validate_inherited_admission','build_manifest',
    '_pin_original_app_close','_pin_original_app_close_exact','grade_closed_capture_group','evaluate_waited_capture_case'}


def within_own(path):
    try:
        return Path(path).resolve().is_relative_to(HERE)
    except (TypeError, ValueError, OSError):
        return False


def audit(event, args):
    reason = None
    if event == 'import' and str(args[0]).split('.')[0] in BLOCKED:
        reason = 'native import'
    if event in ('subprocess.Popen','os.system','socket.connect','socket.connect_ex','os.kill','os.killpg','fcntl.flock'):
        reason = 'process/network/signal/resource'
    if event == 'open' and args and isinstance(args[0], (str, bytes)):
        path = os.fsdecode(args[0]); normalized = path.lower().replace('\\','/')
        if normalized.endswith(('.pt','.pth','.npz','.npy','.jsonl','.lock')) or '/reports/' in normalized or '/budgets/' in normalized:
            reason = 'actual model/raw/report/budget path'
        if len(args)>1 and type(args[1]) is str and any(c in args[1] for c in 'wax+') and not within_own(path):
            reason = 'write outside NEW SOURCE package'
        OPEN_EVENTS.append((str(Path(path).resolve()), args[1] if len(args)>1 else None))
    if reason:
        FORBIDDEN.append(dict(event=event, reason=reason)); raise AssertionError(reason)


def profile(frame, event, arg):
    if event != 'call': return
    path = Path(frame.f_code.co_filename)
    if frame.f_code.co_name in SOURCE_ENTRY_NAMES and path.is_absolute() and not path.is_relative_to(HERE):
        PROFILE_FAILURES.append(str(path)+':'+frame.f_code.co_name)
        raise AssertionError('old/source producer entry executed')
    if path.is_absolute() and 'test_' in path.name and path != Path(__file__).resolve() and path.is_relative_to(R):
        PROFILE_FAILURES.append(str(path)); raise AssertionError('old test executed')


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_json(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')


def info(raw):
    return dict(status='READ',read_count=1,bytes=len(raw),SHA256=h(raw),whole_JSON_read=True,
                SHA256_is_whole_original_bytes=True,exported_projection_is_not_original_bytes=True,
                published_regular_file_observed=True)


def put(root, name, value):
    target = root/name
    assert target.resolve().is_relative_to(FIXTURE.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    data = raw_json(value); target.write_bytes(data)
    return data


def copy_whole_source(root, *, omit=None):
    root.mkdir(parents=True,exist_ok=False)
    finite = json.loads((R/'source_phase1_typed_native_capture_v1/FINITE_SOURCE_BUNDLE.json').read_bytes())
    for row in finite['full_module_files']:
        if row['install_relative'] == omit: continue
        target = root/row['install_relative']; target.parent.mkdir(parents=True,exist_ok=True)
        data = Path(row['path']).read_bytes()
        assert (len(data), h(data)) == (row['bytes'],row['SHA256'])
        target.write_bytes(data)
    for origin, target in ((R/'source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json', root/'CAPTURE_SOURCE_INDEX.json'),
        (R/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py', root/'phase1_capture_parent_actual_wait_controller_v1.py')):
        target.write_bytes(origin.read_bytes())


def fixture_plan(closure, controls):
    roles = closure['contract'].ROLES
    aliases = ['runtimes/'+role+'/SYNTHETIC_SOURCE_METADATA.py' for role in roles]
    aliases += ['pinned_assets/SYNTHETIC_ASSET.usd','worker_sources/SYNTHETIC_ORIGINAL.py']
    aliases += ['supermimic_vendor_v2/SYNTHETIC_SOURCE_'+str(i)+'.py' for i in range(7)]
    baseline = [dict(relative=name,bytes=13,SHA256=h(('SYNTHETIC_METADATA_ONLY:'+name).encode())) for name in sorted(aliases)]
    origin = [dict(row,input_path='/SYNTHETIC_SOURCE_INPUT_NOT_OPENED/'+row['relative'],bytes_read=row['bytes']) for row in baseline]
    canon = closure['contract'].canonical_digest
    inv = dict(kind='COMPLETE_ORIGINAL_STATIC_TREE_REFERENCE_V1',baseline=baseline,installed=copy.deepcopy(baseline),
        SHA256=canon(baseline),vendor7_SHA256='ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0',
        installed_status='ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES',
        baseline_provenance=dict(kind='INDEPENDENT_COMPLETE_INPUT_TREE_BYTE_INVENTORY_V1',
            original_root='/SYNTHETIC_SOURCE_INPUT_NOT_OPENED',original_plan_SHA256=h(b'SYNTHETIC_PLAN'),
            native_root='/SYNTHETIC_NOT_NATIVE',original_logical_rows=origin,
            original_logical_tree_SHA256=canon(baseline),source_to_retained={},all_original_input_files_read=len(origin)))
    group = M.PREFIX+'SOURCE_ONLY_TYPED_V1'
    return dict(kind=C.PLAN_KIND,typed_producer_schema=C.SCHEMA,batch_purpose=C.PURPOSE,group_id=group,
        GPU_UUID='GPU-0123abcd',capture_controls=controls,requested_roles=['E3'],deferred_roles=list(roles[1:]),
        roles=[dict(role=role,worker='worker_passive_interface_v1.py' if role=='E3' else 'SYNTHETIC_DEFERRED.py') for role in roles],
        worker_files=[dict(relative=row['relative'],bytes=row['bytes'],SHA=row['SHA256']) for row in C.FINITE_ROWS],
        retained_static_inventory=inv,staged=False,source_native_enabled=False,dispatched=False,
        SOURCE_SYNTHETIC_PROTOCOL_ONLY=True)


def fixture_task(closure, plan):
    contract = closure['contract']
    return dict(kind=C.TASK_KIND,purpose=C.PURPOSE,batch_purpose=C.PURPOSE,
        integration=contract.INTEGRATION,policy_variant=contract.POLICY_VARIANT,typed_producer_schema=C.SCHEMA,
        role='E3',requested_roles=['E3'],role_catalog=list(contract.ROLES),num_envs=80,seed=20260928,
        model_PT_reads=0,synthetic_action=[0.,0.,0.,0.,0.,0.],train=False,quality_evaluation=False,
        full_clean35='UNKNOWN',controls=plan['capture_controls'],physics=copy.deepcopy(contract.PHYSICS),
        asset_SHA=contract.USD,contract_SHA=contract.CONTRACT,overall_eight_pass_rate=None,comparison=None,
        group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],absolute_worker_deadline_epoch=1.,
        SOURCE_SYNTHETIC_PROTOCOL_ONLY=True)


def fixture_final(closure, task):
    n = task['controls']
    sensor = dict(kind='PASSIVE_SENSOR_CAPTURE_V3',metadata_retention_complete=True,
        control_ledger=dict(kind='BOUNDED_TYPED_CONTROL_LEDGER_V1',requested_controls=n,recorded_controls=n,
            run_id=task['group_id']+':E3',normal_channel_records=n*10,
            controls=[dict(control=k,payload='SYNTHETIC_NO_REAL_TENSOR') for k in range(n)]),
        incomplete_current_control=None,unknown_sensor_metadata=dict(keep=2**53+17))
    actuation = dict(capture_schema='PHASE1_TYPED_C2_EVENT_WINDOWS_V1',
        windows=dict(seen=n,first=[dict(payload='SYNTHETIC_FIRST_WINDOW')],last=[dict(payload='SYNTHETIC_LAST_WINDOW')]),
        unknown_actuation_metadata='KEEP')
    return closure['contract'].candidate_final(task,completed=n,physics=n*8,feedback=n*2,
        delay_calls=dict(legs=n*8,wheels=n*8),boundary=dict(actions=n,original_step_transitions=n,pending_original_step=False),
        sensor=sensor,actuation=actuation,coverage=dict(deficits=[]),rng_counts={'SOURCE_ONLY_NOT_REAL_RNG':0},
        trace=dict(initial_sensor_memory={'payload':'SYNTHETIC'},initial_actor_original_buffer=['SYNTHETIC_NOISY_NOT_CLEAN']),
        restore=dict(ok=True,order=['actuation','sensor','bridge']),setup=dict(SOURCE_SYNTHETIC_PROTOCOL_ONLY=True))


def fixture_binding(closure, root, fast):
    app = closure['app']; pin = app._APP_PIN
    module = pin.module; class_id = module+'.'+pin.class_name
    source = str((root/'SYNTHETIC_APP_SOURCE_NOT_OPENED.py').resolve())
    value = dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5',actual_class=class_id,
        actual_MRO=[class_id,'builtins.object'],close_owner=class_id,actual_module=module,
        actual_type_name=pin.class_name,close_module=module,close_qualname=pin.class_name+'.close',
        source_file=source,module_file=source,code_filename=source,source_bytes=pin.source_bytes,
        source_SHA256=pin.source_SHA256,close_firstlineno=pin.close_firstlineno,
        exact_class_verified=True,method_self_is_application=True,method_function_is_MRO_definition=True,
        fast_shutdown=fast,no_extra_SDK_getters=True)
    value.update(app._helper_source_receipt())
    return value


def fixture_packet(closure, controls=64):
    plan = fixture_plan(closure, controls); task = fixture_task(closure,plan); worker = fixture_final(closure,task)
    root = M.BASE+'/tasks/'+plan['group_id']
    dispatch = dict(root=root,group_id=plan['group_id'],purpose=C.PURPOSE,parent_source_SHA=M.PARENT_SHA,
        controller=dict(pid=111,linux_start_ticks='1111'),parent=dict(pid=222,linux_start_ticks='2222'),
        actual_native_parent_Popen_calls=1,SDK_scene_or_skill_admission=False)
    source_false = dict(capture_interface_passed=False,exact=False,stage2_GO=False,gate1='UNKNOWN')
    close = dict(kind='REAL_COMPLETE_APP_V6_CONTRACTS_IMPORT_CHECK_V2',passed=True,helper_base_is_actual_imported_contracts=True)
    meta = dict(kind=C.METADATA_KIND,source_derivation_version=1,typed_producer_schema=C.SCHEMA,
        active_bindings=dict(complete_bindings=34,overlay_bindings=32,independent_original_bootstrap_bindings=2,all_complete_source_bytes_verified=True),
        ROOT_equals_HERE=True,passed=True,purpose=C.PURPOSE,requested_roles=['E3'],task_controls=controls,
        canonical7a092_whole_module=True,complete_AppV6_Base=close,native_worker_main_executed=False,
        actual_SDK_binding=None,resource_operations=0,model_reads=0)
    plan_raw = raw_json(plan)
    stage = dict(kind=C.STAGE_KIND,typed_producer_schema=C.SCHEMA,purpose=C.PURPOSE,materialized=True,
        parent_launches=0,group_id=plan['group_id'],root=root,requested_roles=['E3'],capture_controls=controls,files=64,
        GROUP_PLAN_bytes=len(plan_raw),GROUP_PLAN_SHA256=h(plan_raw),baseline_SHA256=plan['retained_static_inventory']['SHA256'],
        source_to_retained={},metadata_validation=meta,source_native_enabled=False,staged=False,dispatched=False,
        actual_SDK_executed=False,model_reads=0,resource_operations=0,**source_false)
    stage_raw = raw_json(stage); dispatch['stage_receipt_SHA256'] = h(stage_raw)
    waited = dict(role='E3',pid=333,actual_waited=True,returncode=0)
    terminal = [dict(waited,passed_execution=True,error=None,semantic=dict(passed_execution=True),data=worker)]
    group = dict(kind=C.GROUP_FINAL_KIND,purpose=C.PURPOSE,group_id=plan['group_id'],passed_execution=True,
        requested_roles=['E3'],terminal=terminal,GO_epoch=123.,**source_false)
    scope = dict(all_own_children_waited=True,original_single_GPU_private_EX_released=True,
        original_global_finite_EX_released=True,canonical_writes=0,errors=[],no_foreign_scope_touched=True,child_waits=[waited])
    grade = dict(kind=C.GRADE_KIND,purpose=C.PURPOSE,passed_closed_capture_execution=True,errors=[],**source_false)
    identity = dict(controller=dispatch['controller'],parent=dispatch['parent'],group_id=plan['group_id'],
        parent_source_SHA=M.PARENT_SHA,actual_native_parent_Popen_calls=1)
    outer = dict(identity,kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1',actual_parent_p_wait_returned=True,
        returncode=0,controller_errors=[],original_parent_resource_close_wait_not_replaced=True,
        controller_resource_SDK_model_C_lock_or_signal_operations=0)
    request = dict(root=root,group_id=plan['group_id'],purpose=C.PURPOSE,stage_receipt_SHA256=dispatch['stage_receipt_SHA256'],
        SDK_scene_or_skill_admission=False,controller_source_SHA=M.CONTROLLER_SHA)
    documents = {'GROUP_PLAN.json':plan,C.COMPLETE:stage,'PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json':request,
        'PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json':dict(kind='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1',
            controller=dispatch['controller'],parent_source_SHA=M.PARENT_SHA,controller_resource_SDK_model_C_lock_or_signal_operations=0),
        'PARENT_STARTED.json':dict(kind='ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1',pid=222,requested_roles=['E3']),
        'PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json':dict(identity,kind='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION',root=root,SDK_scene_or_skill_admission=False),
        M.OUTER:outer,'PARENT_EXIT_SCOPE.json':scope,'PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json':grade,
        'FINAL.json':group,'TERMINAL_ROWS.json':terminal,'cases/E3/FINAL.json':worker,'cases/E3/task.json':task,
        'ACTUAL_GROUP_ADMISSION.json':dict(group_id=plan['group_id'],original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_writes=0),
        'CHILDREN.json':[dict(role='E3',pid=333,root=root+'/cases/E3',worker='worker_passive_interface_v1.py')],
        'GROUP_EVAL_START.json':dict(kind=C.COMMON_START_KIND,purpose=C.PURPOSE,group_id=plan['group_id'],members=['E3'],epoch=123.),
        'cases/E3/WORKER_SCENE_READY.json':dict(kind='PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1',role='E3'),
        'cases/E3/WORKER_EVAL_STARTED.json':dict(kind='PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1',role='E3',GO_epoch=123.)}
    metadata = {name:info(raw_json(value)) for name,value in documents.items()}
    packet = dict(documents=documents,file_metadata=metadata,collector_errors=[],
        metadata_validation=dict(original_capture_plan=True,original_capture_preclose=True,original_app_close_metadata=True,
            typed_materialization_raw_plan_binding=True,errors=[]),closure=closure['receipt'])
    return dispatch, packet


class TypedCollectorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if FIXTURE.exists(): raise AssertionError('exclusive NEW Source fixture path already exists')
        FIXTURE.mkdir(); cls.before_modules = dict(sys.modules); cls.before_path = list(sys.path)
        cls.root = FIXTURE/'whole_metadata_modules'; copy_whole_source(cls.root)
        cls.verified = M.verify_installed_sources(cls.root)
        cls.closure = M.import_complete_metadata_modules(cls.root, cls.verified)

    @classmethod
    def tearDownClass(cls):
        sys.path[:] = cls.before_path
        for name in tuple(sys.modules):
            if name not in cls.before_modules: sys.modules.pop(name,None)
        for name,value in cls.before_modules.items(): sys.modules[name] = value
        target = FIXTURE.resolve()
        assert target.parent == HERE and target.name == '_SOURCE_ONLY_SYNTHETIC_METADATA_WORKSPACE'
        shutil.rmtree(target)

    def test_01_whole_source_inventory_and_unchanged_functions(self):
        inventory = P.build_sources()
        self.assertEqual(inventory['reviewed_mirror']['verified_full_text_inputs'],396)
        self.assertEqual(inventory['independently_checked_unique_source_files'],465)
        self.assertEqual(inventory['finite_active_bindings']['complete'],34)
        self.assertEqual(inventory['sensor_source_manifest']['pin_references'],435)
        self.assertEqual(inventory['sensor_source_manifest']['unique_full_python_sources'],155)
        self.assertEqual(inventory['original_actuation_SOURCE_files'],182)
        self.assertIsNone(inventory['original_B2_reference13']['declared_content_root'])
        self.assertEqual(len(inventory['dependency_packages']['sensor']['members']),21)
        self.assertEqual(len(inventory['dependency_packages']['codec']['members']),7)
        self.assertEqual(len(inventory['dependency_packages']['actuation_clock_scope_v2']['members']),5)
        self.assertEqual(len(inventory['derivation']['complete_reader_functions_identical']),6)
        self.assertEqual(len(inventory['derivation']['complete_cli_functions_identical']),6)
        tree = ast.parse((HERE/'remote_metadata_reader.py').read_text(encoding='utf-8'))
        call = next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='watch')
        self.assertEqual(len(call.args),1)  # Original watch has a keyword-only tail.
        self.assertFalse(FORBIDDEN); self.assertFalse(PROFILE_FAILURES)

    def test_02_real_whole_module_import_and_typed34_negatives(self):
        self.assertEqual(self.verified['source_aliases'],34)
        self.assertEqual(self.verified['overlay_source_aliases'],32)
        self.assertEqual(self.verified['independent_bootstrap_source_aliases'],2)
        self.assertIs(self.closure['app']._base,sys.modules['resume_runtime_contracts_v3'])
        self.assertEqual(Path(self.closure['core'].__file__).read_bytes(),(R/'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py').read_bytes())
        self.assertEqual(Path(self.closure['app'].__file__).read_bytes(),(R/'source_app_close_runtime_compat_v6/app_close_semantics_v6.py').read_bytes())
        missing = FIXTURE/'missing_complete_Base'; copy_whole_source(missing,omit='resume_runtime_contracts_v3.py')
        with self.assertRaises((ValueError,FileNotFoundError)): M.verify_installed_sources(missing)
        index = copy.deepcopy(self.verified['index']); index['dependency_sources'] = index['dependency_sources'][:5]
        abi = json.loads((self.root/'PRODUCER_ABI.json').read_bytes())
        with self.assertRaises(ValueError): C.finite_rows(index,abi)
        with self.assertRaises(ValueError): self.closure['runtime'].validate_installed_root(self.root,self.root)
        self.assertFalse(any(n.split('.')[0] in BLOCKED for n in sys.modules))

    def test_03_real_pure_plan_task_and_materialization64_128(self):
        for controls in (64,128):
            dispatch,packet = fixture_packet(self.closure,controls)
            plan = packet['documents']['GROUP_PLAN.json']; stage = packet['documents'][C.COMPLETE]
            self.closure['contract'].validate_plan(plan,self.verified['index'])
            self.closure['contract'].validate_task(packet['documents']['cases/E3/task.json'])
            self.assertTrue(C.validate_materialization(stage,plan,packet['file_metadata'],dispatch)['typed_materialization_raw_plan_binding'])
            self.assertFalse(stage['staged']); self.assertFalse(stage['source_native_enabled'])
            for key,value in (('kind','SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V1'),('parent_launches',True),('GROUP_PLAN_bytes',True),('GROUP_PLAN_SHA256',h(b'wrong'))):
                bad=copy.deepcopy(stage);bad[key]=value
                with self.assertRaises(ValueError): C.validate_materialization(bad,plan,packet['file_metadata'],dispatch)
            bad=copy.deepcopy(plan);bad['retained_static_inventory'].pop('baseline_provenance')
            with self.assertRaises(ValueError): C.validate_baseline_metadata(bad['retained_static_inventory'])
            bad=copy.deepcopy(plan);bad['capture_controls']=True
            with self.assertRaises(ValueError): C.validate_materialization(stage,bad,packet['file_metadata'],dispatch)
        rejected = P.SourceReader()
        with self.assertRaises(ValueError): rejected.path('R','reports/DO_NOT_STAT.json',(1,h(b'x')))
        with self.assertRaises(ValueError): rejected.path('R','source_phase1_typed_capture_materializer_v1/OTHER.patch',(1,h(b'x')))

    def test_04_explicit_projection_retains_unknown_and_original_cache(self):
        dispatch,packet = fixture_packet(self.closure)
        original = packet['documents']['cases/E3/FINAL.json']; original['future_unknown']={'bigint':2**53+19,'文字':'保留'}
        before = raw_json(original); projected = M.worker_projection(original)
        self.assertEqual(raw_json(original),before)
        marker = projected['_collector_typed_payload_projection']
        self.assertEqual(set(marker['removed_paths']),set(C.REMOVAL_PATHS))
        self.assertEqual(projected['future_unknown'],original['future_unknown'])
        self.assertEqual(projected['sensor']['unknown_sensor_metadata'],original['sensor']['unknown_sensor_metadata'])
        self.assertEqual(projected['actuation']['windows']['seen'],64)
        self.assertNotIn('controls',projected['sensor']['control_ledger'])
        self.assertNotEqual(h(before),h(raw_json(projected)))
        row = {'data':original,'unknown_row_field':{'retained':True}}
        self.assertEqual(M.terminal_projection([row])[0]['unknown_row_field'],row['unknown_row_field'])
        group = {'terminal':[row],'unknown_group_field':'RETAIN'}
        self.assertEqual(M.project('FINAL.json',group)['unknown_group_field'],'RETAIN')
        self.assertEqual(json.loads(raw_json(projected))['future_unknown']['bigint'],2**53+19)

    def test_05_whole_read_once_and_changed_file_hard_error(self):
        root=FIXTURE/'sole_whole_bytes';root.mkdir()
        dispatch,packet=fixture_packet(self.closure);value=packet['documents']['cases/E3/FINAL.json']
        raw=put(root,'cases/E3/FINAL.json',value);reader=M.MetadataReader(root)
        path=str((root/'cases/E3/FINAL.json').resolve());start=len(OPEN_EVENTS)
        first=reader.read('cases/E3/FINAL.json',terminal=True)
        self.assertIs(reader.read('cases/E3/FINAL.json',terminal=True),first)
        self.assertEqual(reader.info['cases/E3/FINAL.json']['read_count'],1)
        self.assertEqual(reader.info['cases/E3/FINAL.json']['SHA256'],h(raw))
        self.assertEqual(sum(p==path and mode=='r' for p,mode in OPEN_EVENTS[start:]),1)
        original_hash=reader.info['cases/E3/FINAL.json']['SHA256']
        put(root,'cases/E3/FINAL.json',{'changed':'DIFFERENT_IMMUTABLE_FILE'})
        self.assertIsNone(reader.read('cases/E3/FINAL.json',terminal=True))
        self.assertEqual(reader.info['cases/E3/FINAL.json']['read_count'],1)
        self.assertEqual(reader.info['cases/E3/FINAL.json']['SHA256'],original_hash)
        self.assertEqual(reader.info['cases/E3/FINAL.json']['status'],'ERROR')
        self.assertIs(reader.cache['cases/E3/FINAL.json'],first)

    def test_06_original_complete_fast_and_returned_binding_helpers(self):
        for fast in (True,False):
            root=FIXTURE/('binding_fast' if fast else 'binding_returned');root.mkdir()
            dispatch,packet=fixture_packet(self.closure)
            task=packet['documents']['cases/E3/task.json'];final=packet['documents']['cases/E3/FINAL.json']
            binding=fixture_binding(self.closure,self.root,fast)
            reader=M.MetadataReader(root)
            for name,value in {'GROUP_PLAN.json':packet['documents']['GROUP_PLAN.json'],'cases/E3/task.json':task,
                    'cases/E3/FINAL.json':final,'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json':binding,
                    'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json':{'closed':True}}.items():
                put(root,name,value);reader.read(name,terminal=name in M.BIG)
            if fast:
                intent=dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',binding=binding,
                    final_SHA=reader.info['cases/E3/FINAL.json']['SHA256'],final_bytes=reader.info['cases/E3/FINAL.json']['bytes'],original_env_close_returned=True)
                name='cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json'
                put(root,name,intent);reader.read(name)
            else:
                name='cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json'
                put(root,name,dict(returned=True,binding=binding));reader.read(name)
            result=M.validate_terminal_cache(reader,dispatch,self.closure)
            self.assertTrue(result.get('original_capture_plan'),result)
            self.assertTrue(result.get('original_capture_preclose'),result)
            self.assertTrue(result.get('original_app_close_metadata'),result)
            if fast:
                original=reader.cache[name];reader.cache[name]=dict(original,final_SHA=h(b'not original'))
            else:
                original=reader.cache[name];reader.cache[name]=dict(returned=False,binding=binding)
            self.assertFalse(M.validate_terminal_cache(reader,dispatch,self.closure)['original_app_close_metadata'])
            reader.cache[name]=original
            changed=dict(binding,capture_metadata_epoch=1.)
            reader.cache['cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json']=changed
            self.assertFalse(M.validate_terminal_cache(reader,dispatch,self.closure)['original_app_close_metadata'])
            self.assertFalse(result['source_grade_function_reexecuted'])

    def test_07_caps_full_packet_LF_and_fake_clock(self):
        root=FIXTURE/'caps';root.mkdir();reader=M.MetadataReader(root)
        target=root/'FINAL.json'
        exact=b'"'+b'x'*(C.BIG_LIMIT-2)+b'"';target.write_bytes(exact)
        self.assertEqual(len(reader.read('FINAL.json',terminal=True)),C.BIG_LIMIT-2)
        self.assertEqual(reader.info['FINAL.json']['bytes'],C.BIG_LIMIT)
        oversized=FIXTURE/'oversized';oversized.mkdir();target=oversized/'FINAL.json'
        with target.open('wb') as stream: stream.seek(C.BIG_LIMIT);stream.write(b'x')
        over=M.MetadataReader(oversized);self.assertIsNone(over.read('FINAL.json',terminal=True))
        self.assertEqual(over.info['FINAL.json']['read_count'],0)
        self.assertTrue(over.info['FINAL.json']['published_regular_file_observed'])
        packet={'pad':''};overhead=len(M.encoded_packet(packet));packet['pad']='a'*(C.EXPORT_LIMIT-overhead)
        self.assertEqual(len(M.encoded_packet(packet)),C.EXPORT_LIMIT)
        packet['pad']+='a'
        with self.assertRaises(ValueError): M.encoded_packet(packet)
        empty=FIXTURE/'clock';empty.mkdir();clock=[0.];sleeps=[]
        def now():return clock[0]
        def sleep(seconds):sleeps.append(seconds);clock[0]+=seconds
        result=M.watch(M.MetadataReader(empty),cap_seconds=45,interval_seconds=20,monotonic=now,sleep=sleep)
        self.assertEqual(sleeps,[20,20,5]);self.assertEqual(result['signals_sent'],0)
        self.assertEqual(result['stop_reason'],'COLLECTOR_CAP_ONLY_NO_NATIVE_TIMEOUT_OR_SIGNAL')
        self.assertFalse(result['native_deadline_extended'])
        with self.assertRaises(ValueError): M.watch(M.MetadataReader(empty),cap_seconds=6001)

    def test_08_qualified_metadata_only_and_wait_EX_ERROR_unknown_negatives(self):
        dispatch,packet=fixture_packet(self.closure)
        M.validate_dispatch(dispatch)
        for name in M.BIG:packet['documents'][name]=M.project(name,packet['documents'][name])
        good=K.summarize(dispatch,packet)
        self.assertTrue(good['passed_closed_capture_execution'],good['errors'])
        self.assertEqual(good['gate1'],'UNKNOWN');self.assertFalse(good['stage2_GO'])
        self.assertIsNone(good['skill_success_rate']);self.assertFalse(good['science_consumer_enabled'])
        for kind in ('old27','missing_outer_wait','missing_inner_wait','missing_private_EX','missing_finite_EX','RC0_but_ERROR','producer_grade_false','missing_whole_hash'):
            bad=copy.deepcopy(packet)
            if kind=='old27':bad['closure']['source_aliases']=27
            elif kind=='missing_outer_wait':bad['documents'][M.OUTER]['actual_parent_p_wait_returned']=False
            elif kind=='missing_inner_wait':bad['documents']['PARENT_EXIT_SCOPE.json']['child_waits'][0]['actual_waited']=False
            elif kind=='missing_private_EX':bad['documents']['PARENT_EXIT_SCOPE.json']['original_single_GPU_private_EX_released']=False
            elif kind=='missing_finite_EX':bad['documents']['PARENT_EXIT_SCOPE.json']['original_global_finite_EX_released']=False
            elif kind=='RC0_but_ERROR':bad['documents']['cases/E3/WORKER_ERROR.json']={'original_error':'SYNTHETIC_PRESERVED_ERROR'}
            elif kind=='producer_grade_false':bad['documents']['PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json']['passed_closed_capture_execution']=False
            else:bad['file_metadata']['cases/E3/FINAL.json']['SHA256']=None
            result=K.summarize(dispatch,bad);self.assertFalse(result['passed_closed_capture_execution'],kind)
            if kind in ('RC0_but_ERROR','producer_grade_false'):self.assertEqual(result['status'],'FAIL_CLOSED_CAPTURE_EXECUTION')
        empty=K.summarize(dispatch,{'documents':{},'file_metadata':{},'collector_errors':[]})
        self.assertIsNone(empty['worker_observed']['controls']);self.assertIsNone(empty['actual_native_parent_Popen_calls'])
        self.assertFalse(FORBIDDEN);self.assertFalse(PROFILE_FAILURES)


def main():
    sys.addaudithook(audit);sys.setprofile(profile)
    output=io.StringIO();runner=unittest.TextTestRunner(stream=output,verbosity=2)
    start=time.monotonic();result=runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(TypedCollectorSourceTests))
    elapsed=time.monotonic()-start;sys.setprofile(None)
    log=output.getvalue();print(log,end='')
    suffix='attempt1'
    log_path=HERE/('SOURCE_TEST_LOG_'+suffix+'.txt')
    report_path=HERE/('SOURCE_TEST_REPORT_'+suffix+'.json')
    with log_path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(log)
    report=dict(kind='EIGHT_NEW_TYPED_COLLECTOR_STDLIB_SOURCE_CASES_V1',tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        passed=result.wasSuccessful() and result.testsRun==8 and not FORBIDDEN and not PROFILE_FAILURES,
        elapsed_seconds=elapsed,old_tests_reexecuted=False,forbidden_operations=FORBIDDEN,forbidden_source_entry_calls=PROFILE_FAILURES,
        full_original_safe_modules_imported=True,AST_cropped_or_stubbed_production_helpers=False,
        fixture_scope='OWN_NEW_SYNTHETIC_JSON_ONLY_NOT_ACTUAL_SDK_OR_TYPED_SCIENCE',
        source_test_module_bytes=len(Path(__file__).read_bytes()),source_test_module_SHA256=h(Path(__file__).read_bytes()),
        log_bytes=len(log_path.read_bytes()),log_SHA256=h(log_path.read_bytes()),
        actual_whole_FINAL_trace_or_report_read=False,actual_SDK_Torch_GPU_C_model_operations=0,
        actual_parent_or_controller_or_materializer_or_collection_entry_executed=False,
        actual_SDK_binding='UNKNOWN',science_consumer_enabled=False,gate1='UNKNOWN',exact=False,capture_interface_passed=False,stage2_GO=False)
    with report_path.open('xb') as stream:stream.write(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False).encode()+b'\n')
    print(json.dumps(dict(tests_run=result.testsRun,passed=report['passed'],failures=len(result.failures),errors=len(result.errors))))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
