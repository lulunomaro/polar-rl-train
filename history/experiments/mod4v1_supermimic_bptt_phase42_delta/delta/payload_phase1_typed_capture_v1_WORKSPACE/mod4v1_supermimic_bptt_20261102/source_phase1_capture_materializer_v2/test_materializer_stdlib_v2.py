"""SOURCE / actual text PINs / stdlib fake static trees / whole AST only.
Never call prepare(), stage(), CLI main, native parent/worker or old test scripts.
"""
from pathlib import Path
import ast
import builtins
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
R=HERE.parent
MODEL_SUFFIXES={'.pt','.pth','.ckpt','.safetensors','.onnx','.pt2','.pkl','.pickle'}
BLOCKED={'torch','numpy','isaacsim','isaaclab','omni','pxr','warp','psutil','fcntl','paramiko'}
AUDIT=dict(model_stat_lstat_open=0,native_imports=0,process_network_lock=0,escaped_writes=0,real_raw_reads=0)
OLD_STAT,OLD_LSTAT=os.stat,os.lstat


def is_model(value):
    return isinstance(value,(str,bytes,os.PathLike)) and Path(os.fsdecode(value)).suffix.lower() in MODEL_SUFFIXES


def checked_stat(function):
    def call(path,*a,**kw):
        if is_model(path):AUDIT['model_stat_lstat_open']+=1;raise RuntimeError('test blocks model stat/lstat')
        return function(path,*a,**kw)
    return call


def audit(event,args):
    if event=='import' and args and str(args[0]).split('.')[0] in BLOCKED:
        AUDIT['native_imports']+=1;raise RuntimeError('test blocks native/resource import')
    if event in ('subprocess.Popen','os.system','os.spawn','os.exec') or event.startswith('socket.'):
        AUDIT['process_network_lock']+=1;raise RuntimeError('test blocks process/network')
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]));name=path.name.lower()
        if is_model(path):AUDIT['model_stat_lstat_open']+=1;raise RuntimeError('test blocks model open')
        if path.suffix.lower()=='.lock' or 'budget' in name:
            AUDIT['process_network_lock']+=1;raise RuntimeError('test blocks C/lock file')
        if path.suffix.lower() in ('.npy','.npz') and not (path.is_relative_to(HERE) and any(p.startswith('fake_source_') for p in path.parts)):
            AUDIT['real_raw_reads']+=1;raise RuntimeError('only own explicit fake static bank markers allowed')
        mode=args[1] if len(args)>1 else None;flags=args[2] if len(args)>2 else 0
        writing=(isinstance(mode,str) and any(v in mode for v in 'wax+')) or bool(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and not path.is_relative_to(HERE):AUDIT['escaped_writes']+=1;raise RuntimeError('writes confined to NEW test directory')


sys.addaudithook(audit);os.stat=checked_stat(OLD_STAT);os.lstat=checked_stat(OLD_LSTAT)
tempfile.tempdir=str(HERE)  # stdlib's normal scratch routing; no production PIN bypass hook
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
import stage_phase1_capture_v2 as m


def H(raw):return hashlib.sha256(raw).hexdigest()


def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():path.read_bytes()  # observe own fixture before replacing
    path.write_bytes(raw)


def put_json(path,value):put(path,(json.dumps(value,indent=2,allow_nan=False)+'\n').encode())


def whole_ast(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.FunctionDef)}


def sealed_snapshots():
    result={}
    for folder,seal_name in ((R/'source_good_expert_holdout_subset_v1','GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'),
          (R/'source_stage_good_expert_holdout_v1','SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json'),
          (R/'source_phase1_capture_worker_v1','SOURCE_SEAL.json'),
          (R/'source_phase1_capture_materializer_v1','SOURCE_SEAL.json'),
          (R/'source_phase1_capture_worker_v2','SOURCE_SEAL.json')):
        raw=(folder/seal_name).read_bytes();result[str(folder/seal_name)]=H(raw);seal=json.loads(raw)
        for row in seal['files']:
            path=folder/row.get('name',row.get('relative'));data=path.read_bytes()
            assert (len(data),H(data))==(row['bytes'],row.get('SHA256',row.get('sha256')))
            result[str(path)]=H(data)
    return result


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=sealed_snapshots()
        cls.bundle=m.load_sources(R)  # real pinned text ONLY, never actual input/tree preflight
        cls.original_raw=(R/'source_bound_only_native_integration_v1/stage_bound_only_native_v1.py').read_bytes()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='fake_source_',dir=HERE);self.root=Path(self.temp.name)

    def tearDown(self):
        assert self.root.parent==HERE and self.root.name.startswith('fake_source_')
        self.temp.cleanup()

    def originals(self):
        values={}
        names=['pinned_assets/robot.usd','worker_sources/parent/original_metadata.py']
        for role in m.ROLES:names+=['runtimes/'+role+'/runtime/source.py','runtimes/'+role+'/banks/FAKE_STATIC_MARKER.npz']
        for rel in names:
            path=self.root/rel
            raw=b'FAKE_STATIC_MARKER_NOT_REAL_RAW\n' if path.suffix=='.npz' else b'# FAKE ORIGINAL TREE ONLY\n'
            put(path,raw);values[rel]=(path,m.identity(path))
        for leaf in ('__init__.py','learner.py','networks.py','geometry.py','replay.py','contract.py','FAKE_SEVENTH_ONLY.py'):
            rel='supermimic_vendor_v2/'+leaf
            if rel in self.bundle['sources']:values[rel]=self.bundle['sources'][rel]
            else:
                path=self.root/rel;put(path,b'"""FAKE STATIC VENDOR MEMBER NOT ACTUAL VENDOR7."""\n');values[rel]=(path,m.identity(path))
        # These actual alias forms will differ when original V8 bytes are overlaid.
        for rel in ('worker_sources/e1/e1_parallel_worker_safe.py','worker_sources/e1/e1_fresh_runtime_bridge.py','worker_sources/parent/worker_five_original_n80.py'):
            path=self.root/rel;put(path,b'# FAKE OLD UNOVERLAID ORIGINAL BYTES\n');values[rel]=(path,m.identity(path))
        # Actual complete stdlib helper sources from the consumed V1 inventory.
        # Positive cases never substitute a storage/capacity stub or invoke constructors.
        for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values():
            path=R/row['source_relative'];values[row['relative']]=(path,m.identity(path))
        return values

    def fixture(self,controls=64):
        original=self.originals();materials,inventory=m.retain_originals(original,self.bundle['sources'],original_root=self.root,
            original_plan_SHA='1'*64,native_root=self.root/'FAKE_NATIVE_NOT_ADMISSION')
        plan=dict(kind='PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1',batch_purpose=m.PURPOSE,group_id=m.ROOT_PREFIX+'FAKE',GPU_UUID='GPU-0000-abcd',
            requested_roles=['E3'],deferred_roles=list(m.ROLES[1:]),capture_controls=controls,paired_reset_protocol=m.paired_plan(),roles=[],
            retained_static_inventory=inventory,worker_files=[dict(relative=k,**i) for k,(_,i) in sorted(materials.items())])
        for role in m.ROLES:
            plan['roles'].append(dict(role=role,worker='worker_passive_interface_v1.py' if role=='E3' else 'DEFERRED_NOT_CONSTRUCTED.py',
                controls=m.CONTROLS[role],runtime_root=str(self.root/'FAKE_OUTPUT'/'runtimes'/role),asset_dir=str(self.root/'FAKE_OUTPUT'/'runtimes'/role/'runtime/assets')))
        return dict(self.bundle,originals=original,materials=materials),plan

    def test_01_final_worker13_root_and_fixed_INDEX_actual_bytes(self):
        self.assertEqual(self.bundle['receipt']['worker']['content_root_sha256'],m.WORKER_ROOT_SHA)
        self.assertEqual(self.bundle['receipt']['index_SHA256'],m.WORKER_INDEX_PIN[1])
        self.assertEqual(self.bundle['receipt']['source_mappings'],27)
        self.assertEqual(self.bundle['receipt']['actual_original_C_source_pins'],182)
        self.assertEqual({k:v['members'] for k,v in self.bundle['receipt']['dependency_seals'].items()},dict(worker=13,sensor=13,actuation=8,adapter=10,partition=9))

    def test_02_corrupt_sealed_worker_member_rejected(self):
        folder=self.root/'worker'
        source=R/m.WORKER_FOLDER
        for row in json.loads((source/'SOURCE_SEAL.json').read_bytes())['files']:
            put(folder/row['relative'],(source/row['relative']).read_bytes())
        put(folder/'SOURCE_SEAL.json',(source/'SOURCE_SEAL.json').read_bytes())
        path=folder/'phase1_capture_contract.py';put(path,path.read_bytes()+b'\n# CHANGED_FAKE\n')
        with self.assertRaisesRegex(ValueError,'sealed member differs'):
            m.verify_package(folder,m.WORKER_SEAL_PIN[1],13,worker=True)

    def test_03_full_real_safe_metadata_import_and_task64(self):
        bundle,plan=self.fixture();result=m.metadata_validate(bundle,plan)
        self.assertTrue(result['passed']);self.assertEqual(result['task_controls'],64)
        self.assertEqual(result['negative_tasks_rejected'],4)
        self.assertTrue(result['complete_AppV6_Base']['helper_base_is_actual_imported_contracts'])
        self.assertFalse(result['native_worker_main_executed']);self.assertEqual(result['gate1'],'UNKNOWN')

    def test_04_task128_same_protocol_no_training_or_skill(self):
        bundle,plan=self.fixture(128);result=m.metadata_validate(bundle,plan)
        self.assertEqual(result['task_controls'],128);self.assertEqual(result['model_reads'],0)
        self.assertFalse(result['capture_interface_passed'])

    def test_05_missing_real_Base_not_stubbed(self):
        bundle,plan=self.fixture();bundle=dict(bundle,sources={k:v for k,v in bundle['sources'].items() if k!='resume_runtime_contracts_v3.py'})
        with self.assertRaises(FileNotFoundError):m.metadata_validate(bundle,plan)
        self.assertNotIn('phase1_capture_runtime',sys.modules)

    def test_06_collision_keeps_old_bytes_active_alias_unmodified(self):
        bundle,plan=self.fixture();inventory=plan['retained_static_inventory'];moves=inventory['baseline_provenance']['source_to_retained']
        self.assertEqual(set(moves),{'worker_sources/e1/e1_parallel_worker_safe.py','worker_sources/e1/e1_fresh_runtime_bridge.py','worker_sources/parent/worker_five_original_n80.py'})
        for old,retained in moves.items():
            self.assertEqual(retained,m.RETAIN_PREFIX+old)
            self.assertEqual(bundle['materials'][retained][1],bundle['originals'][old][1])
            self.assertEqual(bundle['materials'][old][1],bundle['sources'][old][1])
            self.assertNotEqual(bundle['materials'][old][1],bundle['materials'][retained][1])
        self.assertTrue(m.validate_preservation(inventory,bundle['materials'],originals=bundle['originals']))

    def test_07_identical_overlay_creates_no_duplicate_backup(self):
        original=self.originals();sources={k:v for k,v in original.items() if k.startswith('worker_sources/')}
        materials,inventory=m.retain_originals(original,sources,original_root=self.root,original_plan_SHA='2'*64,native_root=self.root)
        self.assertEqual(inventory['baseline_provenance']['source_to_retained'],{})
        self.assertEqual(len(materials),len(original))

    def test_08_two_equal_forged_lists_not_sufficient(self):
        bundle,plan=self.fixture();inventory=copy.deepcopy(plan['retained_static_inventory'])
        inventory['baseline'].pop();inventory['installed']=copy.deepcopy(inventory['baseline']);inventory['SHA256']=m.canonical(inventory['baseline'])
        with self.assertRaisesRegex(ValueError,'baseline is incomplete'):
            m.validate_preservation(inventory,bundle['materials'],originals=bundle['originals'])

    def test_09_incomplete_input_provenance_or_wrong_read_path_rejected(self):
        bundle,plan=self.fixture();inventory=copy.deepcopy(plan['retained_static_inventory'])
        inventory['baseline_provenance']['original_logical_rows'][0]['input_path']='INVENTED_PATH'
        with self.assertRaisesRegex(ValueError,'input path/read-byte provenance'):
            m.validate_preservation(inventory,bundle['materials'],originals=bundle['originals'])
        with self.assertRaisesRegex(ValueError,'complete independently read input tree'):
            m.validate_preservation(plan['retained_static_inventory'],bundle['materials'],originals=dict(list(bundle['originals'].items())[1:]))

    def test_10_missing_or_corrupt_retained_byte_and_wrong_relocation_rejected(self):
        bundle,plan=self.fixture();inventory=plan['retained_static_inventory'];old,alias=next(iter(inventory['baseline_provenance']['source_to_retained'].items()))
        bad=dict(bundle['materials']);bad[alias]=(bad[alias][0],dict(bytes=0,SHA='0'*64))
        with self.assertRaisesRegex(ValueError,'original byte lost/changed'):
            m.validate_preservation(inventory,bad,originals=bundle['originals'])
        inv=copy.deepcopy(inventory);inv['baseline_provenance']['source_to_retained'][old]='worker_sources/FAKE_WRONG_ALIAS.py'
        with self.assertRaisesRegex(ValueError,'only exact retained-original'):
            m.validate_preservation(inv,bundle['materials'],originals=bundle['originals'])

    def test_11_observed_stream_hash_not_preflight_list_is_required(self):
        bundle,plan=self.fixture();inventory=plan['retained_static_inventory'];observed={k:i for k,(_,i) in bundle['materials'].items()}
        self.assertTrue(m.validate_preservation(inventory,bundle['materials'],originals=bundle['originals'],observed=observed))
        alias=inventory['baseline'][0]['relative'];observed=dict(observed);observed[alias]=dict(bytes=42,SHA='0'*64)
        with self.assertRaisesRegex(ValueError,'installed retained bytes differ'):
            m.validate_preservation(inventory,bundle['materials'],originals=bundle['originals'],observed=observed)

    def test_12_exact17_whole_original_helper_AST(self):
        original=whole_ast(R/'source_bound_only_native_integration_v1/stage_bound_only_native_v1.py')
        helper=whole_ast(HERE/'static_source_helpers_v1.py')
        self.assertEqual(len(helper),17)
        for name,node in helper.items():self.assertEqual(node,original[name],name)
        self.assertNotIn('producer_final',helper)

    def test_13_complete_fake_static_NPZ_NPY_deps_not_AST_subset(self):
        folder=self.root/'STATIC';put(folder/'banks/a.npz',b'FAKE_STATIC_MARKER_NOT_REAL_RAW')
        put(folder/'banks/b.npy',b'FAKE_STATIC_MARKER_NOT_REAL_RAW');put(folder/'deps/mesh.usd',b'FAKE_STATIC_ASSET')
        put(folder/'deps/config.yaml',b'FAKE_STATIC_DEPENDENCY');put(folder/'source.py',b'# complete fake source\n')
        result=m.tree(folder)
        self.assertEqual(set(result),{'banks/a.npz','banks/b.npy','deps/mesh.usd','deps/config.yaml','source.py'})

    def test_14_denied_name_skipped_before_classification(self):
        class DeniedEntry:
            name='NEVER_OPEN_OR_STAT.pt'
            def is_symlink(self):raise AssertionError('PT classified before name filter')
            def is_dir(self,**kw):raise AssertionError('PT classified')
            def is_file(self,**kw):raise AssertionError('PT classified')
        class Entries:
            def __enter__(self):return iter([DeniedEntry()])
            def __exit__(self,*a):return False
        original=m.os.scandir;m.os.scandir=lambda p:Entries()
        try:self.assertEqual(m.tree(self.root),{})
        finally:m.os.scandir=original

    def test_15_source_path_traversal_and_unknown_provenance_rejected(self):
        for value in ('../../escape.py','/absolute.py','F:/outside/evil.py'):
            with self.assertRaises(ValueError):m.reference_path(R,value)
        path=m.reference_path(R,'F:/RMPOLAR-RL/'+m.R_NAME+'/source_phase1_capture_worker_v1/phase1_capture_contract.py')
        self.assertEqual(path,R/'source_phase1_capture_worker_v1/phase1_capture_contract.py')

    def test_16_full8_H1_absent_and_missing_native_layer_is_hard_PIN(self):
        bundle,plan=self.fixture();self.assertEqual([r['role'] for r in plan['roles']],list(m.ROLES));self.assertNotIn('H1_normal',[r['role'] for r in plan['roles']])
        self.assertEqual(len([r for r in bundle['materials'] if r.startswith('supermimic_vendor_v2/')]),7)
        self.assertIn('native_supermimic_bridge.py',bundle['sources'])
        native=Path(bundle['sources']['native_supermimic_bridge.py'][0]).read_bytes()
        self.assertEqual((len(native),H(native)),(13125,'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'))
        self.assertNotIn('native_supermimic_bridge',sys.modules)

    def test_17_preflight_summary_no_root_creation_no_materialization(self):
        bundle,plan=self.fixture();new=self.root/'NEW_ROOT_ABSENT'
        prepared=dict(plan=plan,new_root=new,materials=bundle['materials'],source_bundle=bundle,boundary={'FAKE_METADATA_ONLY':True},metadata_validation={'FAKE_SOURCE_ONLY':True})
        result=m.preflight_summary(prepared)
        self.assertFalse(new.exists());self.assertFalse(result['materialized']);self.assertEqual(result['parent_launches'],0)
        self.assertEqual(result['purpose'],m.PURPOSE);self.assertEqual(result['requested_roles'],['E3'])

    def test_18_real_prepare_only_AST_complete_tree_native_proof_no_producer(self):
        text=(HERE/'stage_phase1_capture_v2.py').read_text();nodes={n.name:n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        body=ast.get_source_segment(text,nodes['prepare'])
        for needed in ("for role in ROLES:","tree(runtime)","('worker_sources','pinned_assets')","old.get('worker_files')","VENDOR_PIN","retain_originals","original_capacity_helper"):
            self.assertIn(needed,body)
        self.assertNotIn('producer_final',text);self.assertNotIn('subprocess',text);self.assertNotIn('Popen',text)
        self.assertIn("len(rows)==9",body);self.assertIn("'H1_normal'",body)
        self.assertEqual(m.ROOT_PREFIX,'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')

    def test_19_stage_only_AST_streaming_and_receipt_controller_interface(self):
        text=(HERE/'stage_phase1_capture_v2.py').read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        body=ast.get_source_segment(text,node)
        for token in ("target.open('xb')","incoming.read(1024*1024)","observed=written","ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES","materialized=True,parent_launches=0","purpose=PURPOSE","put_json(root/COMPLETE_NAME,receipt)"):
            self.assertIn(token,body)
        self.assertEqual(m.COMPLETE_NAME,'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json')
        self.assertIn('root_consumed_no_same_root_retry=True',body)
        self.assertIn('source_native_enabled=False,staged=False,dispatched=False,actual_SDK_executed=False',body)

    def test_20_original_parent_physics_gate_blocks_stay_sealed(self):
        old=(R/'source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py').read_text().splitlines(keepends=True)
        new=(R/m.WORKER_FOLDER/'single_gpu_passive_capture_parent_v1.py').read_text().splitlines(keepends=True)
        for first,last in ((17,44),(46,78)):self.assertEqual(old[first-1:last],new[first-1:last])
        bundle,plan=self.fixture();self.assertEqual(plan['roles'][0]['controls'],160);self.assertEqual(plan['capture_controls'],64)
        self.assertEqual(plan['paired_reset_protocol']['candidate_planned_protocol']['seed'],20260928)
        self.assertEqual(plan['paired_reset_protocol']['candidate_planned_protocol']['physics_dt'],.0025)

    def test_21_missing_originals_cannot_be_filled_from_self_reported_baseline(self):
        bundle,plan=self.fixture();bundle=dict(bundle);bundle.pop('originals')
        with self.assertRaises(KeyError):m.metadata_validate(bundle,plan)

    def test_22a_unicode_static_alias_uses_actual_contract_digest(self):
        bundle,plan=self.fixture();original=dict(bundle['originals'])
        alias='runtimes/E3/banks/保留的静态元数据.json';path=self.root/alias;put_json(path,{'FAKE_STATIC_METADATA_ONLY':True})
        original[alias]=(path,m.identity(path))
        materials,inventory=m.retain_originals(original,self.bundle['sources'],original_root=self.root,original_plan_SHA='3'*64,native_root=self.root)
        bundle=dict(bundle,originals=original,materials=materials);plan['retained_static_inventory']=inventory
        self.assertEqual(inventory['SHA256'],H(json.dumps(inventory['baseline'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()))
        self.assertTrue(m.metadata_validate(bundle,plan)['passed'])

    def test_22_all_old_sealed_files_unchanged_and_no_native_loaded(self):
        self.assertEqual(sealed_snapshots(),self.before)
        self.assertFalse(any(n.split('.')[0] in BLOCKED for n in sys.modules))
        self.assertEqual(AUDIT,dict.fromkeys(AUDIT,0))


    def source_view(self,bundle):
        root=self.root/'WHOLE_SAFE_SOURCE_VIEW_NOT_STAGE'
        for alias,(path,info) in bundle['sources'].items():
            raw=path.read_bytes();self.assertEqual((len(raw),H(raw)),(info['bytes'],info['SHA']))
            put(root/alias,raw)
        for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values():
            path,info=bundle['originals'][row['relative']];raw=path.read_bytes()
            self.assertEqual((len(raw),H(raw)),(row['bytes'],row['SHA256']))
            put(root/row['relative'],raw)
        return root

    def test_23_same_bootstrap_whole_modules_without_parent_search_path(self):
        bundle,plan=self.fixture();root=self.source_view(bundle);parent=str(root/'worker_sources/parent')
        before=list(sys.path);self.assertNotIn(parent,sys.path)
        result=m.metadata_validate(bundle,plan,actual_root=root)
        origin=result['original_helper_bootstrap'];self.assertEqual(origin['source_version'],2)
        self.assertEqual(origin['parent_five_storage_calls'],0);self.assertEqual(origin['capacity_ctor_calls'],0)
        self.assertEqual(origin['SDK_constructor_calls'],0);self.assertFalse(origin['resource_admission'])
        self.assertEqual({row['relative'] for row in origin['sources']},{row['relative'] for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values()})
        for row in origin['sources']:
            self.assertEqual(Path(row['actual_source_file']),root/row['relative'])
            self.assertTrue(row['actual_module_and_function_code_verified'])
        self.assertEqual(sys.path,before)
        self.assertNotIn('launch_storage_contract',sys.modules);self.assertNotIn('n80_gpu_capacity',sys.modules)
        self.assertFalse((root/'kit_isolation').exists())

    def test_24_missing_storage_or_capacity_actual_module_rejected(self):
        for name,row in m.BOOTSTRAP_ORIGINAL_SOURCES.items():
            with self.subTest(module=name):
                # Each missing-source case gets a distinct pure-source view.
                bundle,plan=self.fixture();root=self.source_view(bundle)
                path=root/row['relative'];self.assertEqual(path.parent,root/'worker_sources/parent')
                self.assertTrue(path.is_relative_to(self.root));path.unlink()
                with self.assertRaisesRegex(ValueError,'complete original bootstrap source required'):
                    m.metadata_validate(bundle,plan,actual_root=root)
                self.assertNotIn(name,sys.modules)
                # Explicit checked cleanup makes another view in this same fake case possible.
                assert root.parent==self.root and root.name=='WHOLE_SAFE_SOURCE_VIEW_NOT_STAGE';shutil.rmtree(root)

    def test_25_wrong_storage_or_capacity_PIN_rejected(self):
        for name,row in m.BOOTSTRAP_ORIGINAL_SOURCES.items():
            with self.subTest(module=name):
                bundle,plan=self.fixture();root=self.source_view(bundle)
                path=root/row['relative'];put(path,path.read_bytes()+b'\n# FAKE CORRUPT HELPER ONLY\n')
                with self.assertRaisesRegex(ValueError,'original bootstrap source bytes/SHA differ'):
                    m.metadata_validate(bundle,plan,actual_root=root)
                assert root.parent==self.root and root.name=='WHOLE_SAFE_SOURCE_VIEW_NOT_STAGE';shutil.rmtree(root)

    def test_26_poisoned_cached_module_origin_is_not_sanitized_into_pass(self):
        import types
        bundle,plan=self.fixture();root=self.source_view(bundle);name='launch_storage_contract'
        cached=types.ModuleType(name);cached.__file__=str(self.root/'WRONG_SOURCE_NOT_IMPORTED.py')
        before=sys.modules.get(name);sys.modules[name]=cached
        try:
            with self.assertRaisesRegex(ValueError,'cached bootstrap module origin differs'):
                m.metadata_validate(bundle,plan,actual_root=root)
            self.assertIs(sys.modules[name],cached)
        finally:
            if before is None:sys.modules.pop(name,None)
            else:sys.modules[name]=before

    def test_27_actual_whole_module_with_changed_cached_function_rejected(self):
        bundle,plan=self.fixture();root=self.source_view(bundle);name='launch_storage_contract';path=root/m.BOOTSTRAP_ORIGINAL_SOURCES[name]['relative']
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        original=module.parent_five_storage;module.parent_five_storage=lambda *a,**k:None
        before=sys.modules.get(name);sys.modules[name]=module
        try:
            with self.assertRaisesRegex(ValueError,'actual cached/bootstrap function code differs'):
                m.metadata_validate(bundle,plan,actual_root=root)
        finally:
            module.parent_five_storage=original
            if before is None:sys.modules.pop(name,None)
            else:sys.modules[name]=before

    def test_28_actual_whole_module_with_wrong_spec_origin_rejected(self):
        bundle,plan=self.fixture();root=self.source_view(bundle);name='n80_gpu_capacity';path=root/m.BOOTSTRAP_ORIGINAL_SOURCES[name]['relative']
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        origin=module.__spec__.origin;module.__spec__.origin=str(self.root/'WRONG_SPEC_ORIGIN.py')
        before=sys.modules.get(name);sys.modules[name]=module
        try:
            with self.assertRaisesRegex(ValueError,'actual imported bootstrap module origin differs'):
                m.metadata_validate(bundle,plan,actual_root=root)
        finally:
            module.__spec__.origin=origin
            if before is None:sys.modules.pop(name,None)
            else:sys.modules[name]=before

    def test_29_decoy_search_directory_does_not_win_without_parent_dir(self):
        bundle,plan=self.fixture();root=self.source_view(bundle);decoy=self.root/'DECOY_NOT_ORIGINAL'
        put(decoy/'launch_storage_contract.py',b'raise AssertionError("DECOY_BOOTSTRAP_RESOLVED")\n')
        before=list(sys.path);sys.path.insert(0,str(decoy))
        try:
            result=m.metadata_validate(bundle,plan,actual_root=root)
            self.assertEqual(result['original_helper_bootstrap']['path_inserted'],str(root/'worker_sources/parent'))
        finally:sys.path[:]=before

    def test_30_V2_whitelist_preserves_V1_entire_functions_and_wire_names(self):
        old_path=R/'source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py';new_path=HERE/'stage_phase1_capture_v2.py'
        old=whole_ast(old_path);new=whole_ast(new_path)
        self.assertEqual(set(old),set(new))
        self.assertEqual({n for n in old if old[n]!=new[n]},{'load_sources','metadata_validate','preflight_summary','stage'})
        self.assertEqual(old['native_boundary'],new['native_boundary'])
        self.assertEqual(old['retain_originals'],new['retain_originals'])
        self.assertEqual(old['validate_preservation'],new['validate_preservation'])
        self.assertEqual(old['prepare'],new['prepare'])
        oldtext=old_path.read_text();newtext=new_path.read_text()
        oldstage=next(n for n in ast.parse(oldtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        newstage=next(n for n in ast.parse(newtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        self.assertEqual(ast.get_source_segment(oldtext,oldstage).replace("kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V1'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2'"),ast.get_source_segment(newtext,newstage))
        self.assertEqual(m.ROOT_PREFIX,'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
        self.assertEqual(m.COMPLETE_NAME,'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json')
        self.assertEqual(m.SOURCE_DERIVATION_VERSION,2)

    def test_31_worker_main_reuses_actual_bootstrap_before_storage_and_native(self):
        path=R/m.WORKER_FOLDER/'worker_passive_interface_v1.py';text=path.read_text();tree=ast.parse(text)
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        bootstrap=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bootstrap_original_helpers')
        forbidden={'parent_five_storage','capacity_ctor','constructor','Mod4Env','build_env','mkdir'}
        for node in ast.walk(bootstrap):
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else None
                self.assertNotIn(name,forbidden)
        calls=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='bootstrap_original_helpers']
        self.assertEqual(len(calls),1)
        storage=min(n.lineno for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='parent_five_storage')
        native=min(n.lineno for n in ast.walk(main) if isinstance(n,ast.Import) and any(a.name=='torch' for a in n.names))
        self.assertLess(calls[0].lineno,storage);self.assertLess(calls[0].lineno,native)
        runtime=(R/m.WORKER_FOLDER/'phase1_capture_runtime.py').read_text()
        self.assertIn('core()._validate_returned_app_binding(binding, helper)',runtime)
        self.assertNotIn('core()._validate_returned_app_binding(binding)',runtime)

    def test_32_original_material_binding_required_not_helper_source_overlay(self):
        bundle,plan=self.fixture();name='launch_storage_contract';row=m.BOOTSTRAP_ORIGINAL_SOURCES[name]
        bad=dict(bundle,sources=dict(bundle['sources']));bad['sources'][row['relative']]=bundle['originals'][row['relative']]
        # Positive provenance is always original bytes, never a source-overlay fallback.
        with self.assertRaisesRegex(ValueError,'bootstrap must use complete original baseline, not an overlay'):
            m.metadata_validate(bad,plan)


def main():
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    print(stream.getvalue())
    report=dict(kind='PHASE1_MATERIALIZER_SOURCE_REAL_TEXT_PIN_WHOLE_BOOTSTRAP_FAKE_STATIC_AST_ONLY_V2',passed=result.wasSuccessful(),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),audit=AUDIT,actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,
        native_worker_or_parent_calls=0,real_static_root_or_vendor7_integrity_tested=False,
        fake_static_marker_files_not_actual_raw=True,source_native_enabled=False,materialized=False,staged=False,dispatched=False,
        capture_interface_passed=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
    path=HERE/'TEST_REPORT.json'
    if path.exists():path.read_bytes()
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(report,sort_keys=True))
    if not result.wasSuccessful():raise SystemExit(1)


if __name__=='__main__':main()
