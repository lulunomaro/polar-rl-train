"""Separate parent-authorized V2 SOURCE review. No production entry or source edits.
Run --phase guard once; only its PASS permits --phase review once.
"""
from pathlib import Path
import argparse
import ast
import builtins
import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

W = Path('F:/RMPOLAR-RL')
R = W / 'mod4v1_supermimic_bptt_20261102'
D = R / 'source_good_holdout_lifecycle_routes_v1'
O = R / 'source_good_holdout_lifecycle_parent_review_v2'
V1 = R / 'source_good_holdout_lifecycle_parent_review_v1'
SELF = O / 'independent_source_review_driver_v2.py'
TP = D / 'test_good_holdout_routes_source.py'
TEST_PIN = (41531, '9b9d780c4281ba3a6462972525509d704d8d2bea6cdb1a3f766387d92560a2c0')
IDENTITY = 'b513c45e1380ffb4200d8a4d208870a2f3b1cfaf4a98b15d4f9ba09d8db4f5a0'
V1_PINS = {'SOURCE_REVIEW.md': (11457, '590a5e836a10289faf336d77089d239cd57a81b9e3078f32ae41723937baffa7'), 'SOURCE_REVIEW.json': (78897, '2788eeab799000d21b3dc1db75306a88b916b3063175e01410452fdaa7a349ff')}
NATIVE = {'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl','paramiko'}
H = lambda b: hashlib.sha256(b).hexdigest()


def put(name, value):
    path = O / name
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def source_key(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def bootstrap():
    original = {}
    for name, pin in V1_PINS.items():
        blob = (V1/name).read_bytes()
        assert (len(blob), H(blob)) == pin
        if name.endswith('.json'):
            prior = json.loads(blob)
        original[source_key(V1/name)] = pin
    expected = {}; raw = {}; n_ast = n_json = 0
    for row in prior['inventory']['current_full_input_inventory']:
        path = Path(row['path'])
        assert path.is_absolute() and path.is_relative_to(W) and '..' not in path.parts
        assert 'reports' not in [p.lower() for p in path.parts]
        assert path.suffix in {'.py','.json','.md','.txt','.patch','.yml','.yaml'} and 'budget' not in path.name.lower()
        assert not path.is_symlink() and path.stat().st_size <= 2*1024*1024
        blob = path.read_bytes(); pin = (row['bytes'], row['SHA256'])
        assert (len(blob), H(blob)) == pin
        if path.suffix == '.py':
            ast.parse(blob.decode('utf-8-sig'), filename=str(path)); n_ast += 1
        if path.suffix == '.json':
            json.loads(blob); n_json += 1
        assert source_key(path) not in expected
        expected[source_key(path)] = pin; raw[path.as_posix()] = blob
    assert (len(expected), n_ast, n_json) == (104, 68, 28)
    records = ''.join(Path(k).relative_to(W).as_posix()+'\t'+str(len(b))+'\t'+H(b)+'\n' for k,b in sorted(raw.items()))
    assert H(records.encode()) == IDENTITY
    seal = json.loads(raw[(D/'SOURCE_SEAL.json').as_posix()])
    assert len(seal['files']) == 12
    assert H(''.join(sorted(x['name']+'\t'+str(x['bytes'])+'\t'+x['SHA256']+'\n' for x in seal['files'])).encode()) == seal['root_SHA256'] == 'a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8'
    for row in seal['files']:
        b = raw[(D/row['name']).as_posix()]; assert (len(b),H(b)) == (row['bytes'],row['SHA256'])
    test_raw = raw[TP.as_posix()]; assert (len(test_raw), H(test_raw)) == TEST_PIN
    compiled = compile(test_raw, str(TP), 'exec')
    return expected, original, raw, compiled


class Denied(AssertionError):
    pass


class Boundary:
    def __init__(self, expected, original, phase):
        self.phase = phase; self.denials = []; self.enabled = True
        self.counts = dict(native_imports=0, model_raw_report_budget_lock_accesses=0,
                           process_network_signal_or_locks=0, writes_outside_NEW=0, nonwhitelisted_read_or_stat=0)
        self.allowed = set(expected) | set(original)
        self.stdlib = Path(sys.base_prefix)
        self.dirs = set()
        for value in list(self.allowed) + [str(self.stdlib), str(O)]:
            for p in Path(value).parents: self.dirs.add(source_key(p))
        self.dirs.update(source_key(p) for p in (W,R,D,O))
        self.real_open = builtins.open; self.real_io = io.open
        self.real_stat = os.stat; self.real_lstat = os.lstat

    def display(self, value):
        if isinstance(value, int): return dict(category='file_descriptor')
        p = Path(os.fsdecode(value)); p = p if p.is_absolute() else W/p
        if p.is_relative_to(R): return dict(category='R_relative', path=p.relative_to(R).as_posix())
        return dict(category='outside_named_R_redacted', suffix=p.suffix.lower())

    def stack(self):
        rows = []; frame = sys._getframe(2)
        for _ in range(7):
            if frame is None: break
            f = frame.f_code.co_filename
            if f.startswith('<'): shown = '<virtual-code>'
            elif Path(f).is_relative_to(R): shown = Path(f).relative_to(R).as_posix()
            else: shown = '<outside_named_R_redacted>'
            rows.append(dict(file=shown, function=frame.f_code.co_name, line=frame.f_lineno)); frame=frame.f_back
        return rows

    def deny(self, counter, operation, value):
        self.counts[counter] += 1
        entry = dict(phase=self.phase, counter=counter, operation=operation,
                     path_type=type(value).__name__, target=self.display(value), stack=self.stack(), blocked_before_IO=True)
        self.denials.append(entry)
        with self.real_io(O/(self.phase+'_BOUNDARY_EVENTS.txt'), 'a', encoding='utf-8') as stream:
            stream.write(json.dumps(entry, ensure_ascii=False)+'\n'); stream.flush()
        raise Denied(counter+': '+operation)

    def check(self, value, operation, *, write=False, metadata=False):
        if not self.enabled or isinstance(value,int): return
        p=Path(os.fsdecode(value)); p=p if p.is_absolute() else W/p
        assert '..' not in p.parts, 'lexical parent path rejected before IO'
        parts=[v.lower() for v in p.parts]; leaf=p.name.lower()
        if p.suffix.lower() in {'.pt','.pth','.ckpt','.safetensors','.onnx','.npz','.npy','.raw','.jsonl','.lock'} or 'reports' in parts or 'budget' in leaf:
            self.deny('model_raw_report_budget_lock_accesses',operation,value)
        if write:
            if not p.is_relative_to(O): self.deny('writes_outside_NEW',operation,value)
        elif not (p.is_relative_to(O) or p.is_relative_to(self.stdlib) or source_key(p) in self.allowed or (metadata and source_key(p) in self.dirs)):
            self.deny('nonwhitelisted_read_or_stat',operation,value)

    def audit(self,event,args):
        if not self.enabled: return
        if event=='import' and str(args[0]).split('.')[0] in NATIVE:
            self.deny('native_imports',event,'<native-module>')
        if event in {'subprocess.Popen','os.system','socket.connect','socket.bind','socket.getaddrinfo','os.kill','os.killpg','fcntl.flock'}:
            self.deny('process_network_signal_or_locks',event,'<process-network-signal-lock>')
        if event=='open' and args:
            wr=(len(args)>1 and isinstance(args[1],str) and any(c in args[1] for c in 'wax+')) or (len(args)>2 and type(args[2]) is int and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            self.check(args[0],'audit:open',write=bool(wr))
        if event in {'os.mkdir','os.rmdir','os.remove','os.unlink','os.truncate'} and args: self.check(args[0],event,write=True)
        if event in {'os.rename','os.replace','os.link','os.symlink'}:
            for value in args[:2]: self.check(value,event,write=True)
        if event in {'os.listdir','os.scandir'} and args: self.check(args[0],event,metadata=True)

    def install(self):
        def op(file,mode='r',*a,**kw): self.check(file,'builtins.open',write=any(c in mode for c in 'wax+')); return self.real_open(file,mode,*a,**kw)
        def ip(file,mode='r',*a,**kw): self.check(file,'io.open',write=any(c in mode for c in 'wax+')); return self.real_io(file,mode,*a,**kw)
        def st(path,*a,**kw): self.check(path,'os.stat',metadata=True); return self.real_stat(path,*a,**kw)
        def ls(path,*a,**kw): self.check(path,'os.lstat',metadata=True); return self.real_lstat(path,*a,**kw)
        builtins.open=op; io.open=ip; os.stat=st; os.lstat=ls
        self.wrappers=(op,ip,st,ls); sys.addaudithook(self.audit)

    def intact(self):
        return (builtins.open,io.open,os.stat,os.lstat)==self.wrappers


def descriptors(code, tree, class_name, method_names, call_attr):
    class_code=next(c for c in code.co_consts if isinstance(c,types.CodeType) and c.co_name==class_name)
    class_ast=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==class_name)
    result={}
    for name in method_names:
        method=next(c for c in class_code.co_consts if isinstance(c,types.CodeType) and c.co_name==name)
        node=next(n for n in class_ast.body if isinstance(n,ast.FunctionDef) and n.name==name)
        calls=[n for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr==call_attr]
        assert len(calls)==1
        codes=[c for c in method.co_consts if isinstance(c,types.CodeType) and c.co_name=='<lambda>']
        sleep=next(c for c in codes if c.co_names==('fail',))
        monotonic=next(c for c in codes if c is not sleep)
        result[name]=dict(method=method,line=calls[0].lineno,monotonic=monotonic,sleep=sleep)
    return result


def authorize(caller,args,specs,globals_dict,reader_type,prefix):
    name=caller.f_code.co_name; assert name in specs, 'wrong caller'
    spec=specs[name]; assert caller.f_code is spec['method'] and caller.f_globals is globals_dict and caller.f_lineno==spec['line'], 'caller identity/line'
    obj=caller.f_locals['self']; reader=args['reader']; root=Path(reader.root)
    assert type(reader) is reader_type and root.is_absolute() and '..' not in root.parts and root.is_relative_to(O), 'not own NEW root'
    assert root==obj.root==Path(obj.scratch.name) and root.parent==O and root.name.startswith(prefix), 'wrong fake root'
    assert isinstance(obj.scratch,tempfile.TemporaryDirectory) and root.is_dir() and not root.is_symlink(), 'not live own tempfile'
    assert args['cap_seconds']==args['interval_seconds']==1
    sleep=args['sleep']; mono=args['monotonic']
    assert type(sleep) is types.FunctionType and sleep.__code__ is spec['sleep'] and sleep.__code__.co_argcount==1
    assert sleep.__globals__ is globals_dict and sleep.__code__.co_filename==caller.f_code.co_filename
    cells=dict(zip(sleep.__code__.co_freevars,sleep.__closure__ or ())); assert cells['self'].cell_contents is obj
    if type(mono) is types.FunctionType:
        assert mono.__code__ is spec['monotonic'] and mono.__code__.co_argcount==0 and mono.__globals__ is globals_dict
        assert mono.__code__.co_filename==caller.f_code.co_filename
        cells=dict(zip(mono.__code__.co_freevars,mono.__closure__ or ()))
        if 'clock' in cells: assert cells['clock'].cell_contents is caller.f_locals['clock']
        clock_kind='same-whole-compilation nested lambda identity'
    else:
        ticks=caller.f_locals.get('ticks'); assert type(ticks) is type(iter(())), 'no bound ticks'
        assert getattr(mono,'__self__',None) is ticks and getattr(mono,'__name__',None)=='__next__' and mono==ticks.__next__, 'wrong bound clock'
        clock_kind='bound tuple iterator.__next__ / caller ticks identity'
    return dict(test=name,line=spec['line'],root=root.relative_to(O).as_posix(),clock=clock_kind,sleep='fixed self.fail lambda',actual_root=False,clock_consumed_by_guard=False)


class FakeReader:
    def __init__(self,root): self.root=root


class ScopeFixture:
    def __init__(self,scratch,specs): self.scratch=scratch; self.root=Path(scratch.name); self.specs=specs; self.mode='normal'
    def fail(self,_): raise AssertionError('fake sleep must never execute')
    def probe(self,reader,*,cap_seconds,interval_seconds,monotonic,sleep):
        return authorize(sys._getframe(1),locals(),self.specs,globals(),FakeReader,'DRIVER_OWN_SCOPE_NOT_STAGE_')
    def case25(self):
        reader=FakeReader(self.root/'wrong' if self.mode=='wrong_root' else self.root)
        mono=time.monotonic if self.mode=='real_clock' else (lambda:0)
        sleeper=time.sleep if self.mode=='real_sleep' else (lambda _:self.fail('never'))
        return self.probe(reader,cap_seconds=1,interval_seconds=1,monotonic=mono,sleep=sleeper)
    def case26(self):
        clock=iter((0,2));ticks=clock; reader=FakeReader(self.root)
        mono=(lambda:next(clock)) if self.mode=='normal' else (ticks.__next__ if self.mode=='bound' else iter((0,2)).__next__)
        before=clock.__reduce__()
        result=self.probe(reader,cap_seconds=1,interval_seconds=1,monotonic=mono,sleep=lambda _:self.fail('never'))
        assert clock.__reduce__()==before, 'guard consumed fake clock'
        return result
    def wrong_caller(self):
        return self.probe(FakeReader(self.root),cap_seconds=1,interval_seconds=1,monotonic=lambda:0,sleep=lambda _:self.fail('never'))


def guard_regressions(expected,original):
    assert not (O/'DRIVER_SCOPE_REGRESSION.json').exists()
    guard=Boundary(expected,original,'guard'); guard.install(); records=[]
    # Actual CLI compilation's class/method/nested code objects, never a recompiled substitute.
    specs={}
    tree=ast.parse(SELF.read_text(encoding='utf-8'))
    cls_ast=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ScopeFixture')
    for name in ('case25','case26'):
        method=getattr(ScopeFixture,name).__code__; node=next(n for n in cls_ast.body if isinstance(n,ast.FunctionDef) and n.name==name)
        call=next(n for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='probe')
        codes=[c for c in method.co_consts if isinstance(c,types.CodeType) and c.co_name=='<lambda>']
        sleeper=next(c for c in codes if c.co_names==('fail',)); mono=next(c for c in codes if c is not sleeper)
        specs[name]=dict(method=method,line=call.lineno,monotonic=mono,sleep=sleeper)
    scratch=tempfile.TemporaryDirectory(prefix='DRIVER_OWN_SCOPE_NOT_STAGE_',dir=O)
    fixture=ScopeFixture(scratch,specs)
    def run(name,fn):
        try: detail=fn(); records.append(dict(name=name,passed=True,detail=detail))
        except BaseException as exc: records.append(dict(name=name,passed=False,error=type(exc).__name__+': '+str(exc)))
    def rejected(fn):
        try: fn()
        except AssertionError: return True
        raise AssertionError('expected scope rejection')
    def clocks():
        fixture.mode='normal'; a=fixture.case25(); b=fixture.case26(); fixture.mode='bound'; c=fixture.case26(); return [a,b,c]
    def wrong_root(): fixture.mode='wrong_root'; return rejected(fixture.case25)
    def wrong_caller(): return rejected(fixture.wrong_caller)
    def real_clock_sleep():
        rows=[]
        for mode,method in [('real_clock',fixture.case25),('real_sleep',fixture.case25),('wrong_bound',fixture.case26)]:
            fixture.mode=mode; rows.append(rejected(method))
        return rows
    def denied_paths():
        before=len(guard.denials)
        for p in (O/'MODEL_FIXTURE.pt',R/'UNLISTED_DRIVER_SCOPE_FIXTURE.py',Path('Z:/OUTSIDE_NAMED_SCOPE_FIXTURE.txt')):
            rejected(lambda p=p:guard.check(p,'SELFTEST:stat',metadata=True))
        events=guard.denials[before:]; assert len(events)==3 and all(e['stack'] and e['blocked_before_IO'] for e in events)
        assert events[1]['target']['category']=='R_relative' and 'path' not in events[2]['target']; assert guard.intact()
        return events
    run('1_legal_fake_lambda_and_bound_clocks_no_consumption',clocks)
    run('2_wrong_root_blocked_before_IO',wrong_root)
    run('3_wrong_caller_identity_blocked',wrong_caller)
    run('4_real_clock_sleep_and_wrong_bound_self_blocked',real_clock_sleep)
    run('5_blocked_path_operation_stack_persist_and_redact',denied_paths)
    assert Path(scratch.name).parent==O; scratch.cleanup()
    receipt=dict(kind='OWN_DRIVER_SCOPE_REGRESSION_V2_NOT_PROJECT_SUITE',tests=5,passed=all(r['passed'] for r in records),cases=records,
                 project_suite_cases_run=0,driver=dict(bytes=SELF.stat().st_size,SHA256=H(SELF.read_bytes())),source_identity_SHA256=IDENTITY,
                 expected_negative_boundary_counters=guard.counts,expected_denials=guard.denials,FS_wrappers_intact=guard.intact())
    put('DRIVER_SCOPE_REGRESSION.json',receipt); print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return 0 if receipt['passed'] else 1


def review(expected,original,raw,compiled):
    regression=json.loads((O/'DRIVER_SCOPE_REGRESSION.json').read_bytes())
    assert regression['passed'] is True and regression['tests']==5 and regression['project_suite_cases_run']==0
    assert regression['driver']==dict(bytes=SELF.stat().st_size,SHA256=H(SELF.read_bytes()))
    assert not (O/'RUN_STARTED.json').exists() and not (O/'RUN_RECEIPT.json').exists()
    put('RUN_STARTED.json',dict(purpose='SEPARATE_V2_REVIEW_NOT_REPLACEMENT_OF_V1_39_1',source_identity_SHA256=IDENTITY,driver_SHA256=H(SELF.read_bytes()),executions=1))
    guard=Boundary(expected,original,'review'); guard.install(); sys.dont_write_bytecode=True; tempfile.tempdir=str(O)
    specs=descriptors(compiled,ast.parse(raw[TP.as_posix()].decode('utf-8')), 'RoutesSourceTests',
                      ('test_25_poll_terminal_once_no_native_deadline_extension','test_26_collector_cap_is_not_a_native_timeout_or_wait_proof'),'watch')
    module=None; modules={}; watches=[]; anomalies=[]; entry_calls=[]; checkpoints=[]; closure=[]; result=None; raised=None; log=io.StringIO()
    forbidden_names={'evaluate_waited_eval_case','grade_closed_reference_group','_validate_zero_update_baseline','_producer_descriptor','validate_reference_row','_metadata','_read_actual_final','main_role','_run_loop','make_task','configure_task','restore_or_build_model','build_teacher_reference','build_frozen_mean_policy','build_bound_only_mean_policy','derive_producer_guard','select_requested_roles'}
    def profile(frame,event,arg):
        try:
            mod=frame.f_globals.get('__name__',''); name=frame.f_code.co_name
            if event=='call':
                forbidden=(mod=='good_holdout_parent_actual_wait_controller_v1' and name in {'main','validate_launch','identity','put','bounded'}) or (mod=='collect_good_holdout_result' and name in {'main','collect','remote_packet','connect_original','atomic_closed'}) or (mod=='good_holdout_remote_reader' and name=='remote_main') or (module is not None and frame.f_globals is module.__dict__ and name=='run') or (name in forbidden_names and mod not in {'__main__','unittest.case','unittest.suite','unittest.runner','unittest.loader'})
                if forbidden:
                    entry_calls.append(dict(module=mod,function=name)); raise Denied('prohibited production entry')
                if mod=='good_holdout_remote_reader' and name=='watch':
                    assert module is not None
                    row=authorize(frame.f_back,frame.f_locals,specs,module.__dict__,modules[mod].MetadataReader,'SOURCE_FAKE_METADATA_NOT_ACTUAL_')
                    assert not any(x['test']==row['test'] for x in watches); watches.append(row)
            if event=='return' and mod=='good_holdout_remote_reader' and name=='load_metadata_closure' and isinstance(arg,dict):
                closure.append(dict(receipt=copy.deepcopy(arg['receipt']),helper_base_is_actual_module=arg['app']._base is arg['base']))
        except BaseException as exc:
            anomalies.append(dict(event=event,function=frame.f_code.co_name,error=type(exc).__name__+': '+str(exc),stack=guard.stack()))
            put('PROFILE_FAILURE_'+str(len(anomalies))+'.json',anomalies[-1]); raise
    def check_profile(where):
        ok=sys.getprofile() is profile and guard.intact(); checkpoints.append(dict(where=where,profile_installed=sys.getprofile() is profile,FS_wrappers_intact=guard.intact()))
        if not ok or anomalies: raise Denied('profile/wrappers coverage lost: '+where)
    class RecordingResult(unittest.TextTestResult):
        def __init__(self,*a,**kw): super().__init__(*a,**kw); self.names=[]
        def startTest(self,test):
            check_profile('start:'+test.id().split('.')[-1]); self.names.append(test.id().split('.')[-1]); super().startTest(test)
        def stopTest(self,test):
            super().stopTest(test)
            try: check_profile('stop:'+test.id().split('.')[-1])
            except Denied: self.stop()
    copied=O/'good_holdout_parent_actual_wait_controller_v1.py'; assert not copied.exists()
    copied.write_bytes(raw[(D/copied.name).as_posix()]); assert copied.read_bytes()==raw[(D/copied.name).as_posix()]
    started=time.perf_counter(); sys.setprofile(profile)
    try:
        check_profile('before_full_module_exec')
        for alias,name in [('good_holdout_contract','good_holdout_contract.py'),('good_holdout_remote_reader','good_holdout_remote_reader.py'),('collect_good_holdout_result','collect_good_holdout_result.py'),('good_holdout_parent_actual_wait_controller_v1','good_holdout_parent_actual_wait_controller_v1.py'),('source_pins','source_pins.py')]:
            p=D/name; obj=types.ModuleType(alias); obj.__file__=str(p); obj.__package__=''; sys.modules[alias]=obj; modules[alias]=obj
            exec(compile(raw[p.as_posix()],str(p),'exec'),obj.__dict__)
        alias='_independent_lifecycle_SOURCE_review_v2'; module=types.ModuleType(alias); module.__file__=str(TP); module.__package__=''; sys.modules[alias]=module
        exec(compiled,module.__dict__); module.HERE=O; tempfile.tempdir=str(O)
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.RoutesSourceTests); assert suite.countTestCases()==40
        result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=RecordingResult).run(suite)
        check_profile('after_full_suite_and_teardown')
    except BaseException as exc:
        import traceback
        raised=''.join(traceback.format_exception(exc))
    finally:
        end_profile=sys.getprofile() is profile; end_wrappers=guard.intact(); sys.setprofile(None)
    elapsed=time.perf_counter()-started
    assert copied.resolve().parent==O and copied.name=='good_holdout_parent_actual_wait_controller_v1.py'; copied.unlink()
    post=[]
    for path,before_raw in raw.items():
        b=Path(path).read_bytes(); assert (len(b),H(b))==expected[source_key(path)]; assert b==before_raw
        post.append((Path(path).relative_to(W).as_posix(),b))
    identity=H(''.join(k+'\t'+str(len(b))+'\t'+H(b)+'\n' for k,b in sorted(post)).encode()); assert identity==IDENTITY
    for path,pin in original.items(): b=Path(path).read_bytes(); assert (len(b),H(b))==pin
    profile_complete=end_profile and end_wrappers and len(checkpoints)==82 and all(c['profile_installed'] and c['FS_wrappers_intact'] for c in checkpoints) and not anomalies
    sealed_audit={} if module is None else dict(module.AUDIT)
    closure_complete=len(closure)==1 and closure[0]['receipt']['source_aliases']==20 and closure[0]['helper_base_is_actual_module'] is True
    all_green=(result is not None and result.testsRun==40 and result.wasSuccessful() and not result.skipped and raised is None and profile_complete and closure_complete and bool(sealed_audit) and all(v==0 for v in sealed_audit.values()) and not entry_calls and len(watches)==2 and not guard.denials and all(v==0 for v in guard.counts.values()))
    receipt=dict(kind='SEPARATE_INDEPENDENT_LIFECYCLE_SOURCE_REVIEW_V2',verdict='SOURCE_REVIEW_PASS_NOT_NATIVE_OR_QUALITY_QUALIFIED' if all_green else 'SOURCE_REVIEW_OR_GUARD_FAILURE_NOT_NATIVE_QUALIFIED',
        purpose='NEW independent V2 driver/scope review; V1 39/1/unknown remains frozen and unsuperseded as history',
        driver=dict(bytes=SELF.stat().st_size,SHA256=H(SELF.read_bytes())),Python=sys.version,flags=['-I','-S','-B'],executions=1,
        tests=0 if result is None else result.testsRun,failures=None if result is None else len(result.failures),errors=None if result is None else len(result.errors),skipped=None if result is None else len(result.skipped),passed=all_green,seconds=elapsed,
        cases=[] if result is None else result.names,failures_detail=[] if result is None else [dict(case=str(t),traceback=s)for t,s in result.failures],errors_detail=[] if result is None else [dict(case=str(t),traceback=s)for t,s in result.errors],driver_exception=raised,
        sealed_audit=sealed_audit,independent_audit=guard.counts,denied_paths=guard.denials,profile_anomalies=anomalies,forbidden_entries=entry_calls,
        profile=dict(checkpoints=checkpoints,installed_at_exit_before_explicit_clear=end_profile,FS_wrappers_intact_at_exit=end_wrappers,complete_40_plus_teardown=profile_complete),
        synthetic_full_watch_calls=len(watches),actual_production_watch_network_calls=0,watch_evidence=watches,whole_original_metadata_closures=closure,
        before_source_identity_SHA256=IDENTITY,after_source_identity_SHA256=identity,source_inputs=104,Python_AST=68,JSON=28,V1_two_files_unchanged=True,
        old_actual_report_stat_read=False,old_tests_or_main_reportwriter_called=False,only_test_HERE_and_tempdir_rebased_in_memory=True,controller_copy_removed=True,
        native='UNKNOWN',quality=None,stage2_GO=False,actual_SSH_SDK_GPU_PT_raw_C_lock_Git=False,actual_parent_or_SDK_close_wait_proof=False)
    put('RUN_RECEIPT.json',receipt)
    with (O/'RUN_LOG.txt').open('x',encoding='utf-8') as stream: stream.write(log.getvalue())
    print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 0 if all_green else 1


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--phase',choices=('guard','review'),required=True); args=parser.parse_args()
    assert Path(__file__).resolve()==SELF and O.parent==R and O.name=='source_good_holdout_lifecycle_parent_review_v2'
    expected,original,raw,compiled=bootstrap()
    return guard_regressions(expected,original) if args.phase=='guard' else review(expected,original,raw,compiled)


if __name__=='__main__':
    try:
        status=main()
    except BaseException as exc:
        frames=[]; tb=exc.__traceback__
        while tb is not None:
            filename=tb.tb_frame.f_code.co_filename
            shown=Path(filename).relative_to(R).as_posix() if not filename.startswith('<') and Path(filename).is_relative_to(R) else '<outside_named_R_redacted>'
            frames.append(dict(file=shown,function=tb.tb_frame.f_code.co_name,line=tb.tb_lineno)); tb=tb.tb_next
        fatal=dict(kind='OWN_V2_DRIVER_FATAL_NO_RETRY',error_type=type(exc).__name__,message=str(exc)[:512],stack=frames,project_suite_rerun=False)
        put('DRIVER_FATAL.json',fatal); print(json.dumps(fatal,ensure_ascii=False,indent=2)); status=1
    raise SystemExit(status)
