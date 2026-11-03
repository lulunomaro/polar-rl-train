"""NEW stdlib synthetic regressions, never imports/opens an actual capture."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'source_phase1_capture_evidence_verifier_v1'))
import capture_evidence_verifier_v1 as pure
import queue_failure_locator_v1 as locator


def synthetic():
    events=[]; seq=0
    def event(kind,group,tick,pre,post,args,**extra):
        nonlocal seq
        e=dict(seq=seq,kind=kind,group=group,tick=tick,pre=copy.deepcopy(pre),post=copy.deepcopy(post),
               args=copy.deepcopy(args),kwargs={},outcome='RETURNED',**extra)
        events.append(e); seq+=1; return e
    for group,width in pure.GROUPS.items():
        q={k:([[0.]*width for _ in range(80)] if k in ('pending','applied') else
              [False]*80 if k.endswith('valid') else [0 if k=='lag_steps' else 1 if k=='episode' else -1]*80) for k in pure.QUEUE}
        before=copy.deepcopy(q); target=[[.25]*width for _ in range(80)]
        for i in range(80):
            q['pending'][i]=target[i][:]; q['pending_valid'][i]=True
            for k in ('issued_tick','due_tick','last_submit_tick'): q[k][i]=0
        event('issue',group,0,before,q,[[[0.]*width for _ in range(80)]])
        event('queue_submit',group,0,before,q,[group,target,0])
        for tick in range(8):
            before=copy.deepcopy(q)
            for i in range(80):
                if tick==0:
                    q['applied'][i]=q['pending'][i][:]; q['applied_valid'][i]=True
                    q['applied_issue_tick'][i]=0; q['first_apply_tick'][i]=0; q['pending_valid'][i]=False
                q['last_apply_tick'][i]=tick
            term=event('term_apply',group,tick,before,q,[])
            event('queue_apply',group,tick,before,q,[group,tick],selected_target=copy.deepcopy(q['applied']))
            event('target_write',group,tick,q,q,[q['applied']],parent_term_apply_seq=term['seq'])
    return dict(controls=1,actuation=dict(status=dict(dropped_events=0,observer_errors=0,missing_hooks=[],restore_conflicts=[])),
                bounded_trace=dict(actuation=dict(control_windows_seen=1,retained_window_bound=4,
                first=[dict(control_index=0,events=events)],last=[])),
                private_payload={'unrelated':'DO_NOT_EXPORT_'+('WHOLE_TRACE_SECRET_'*1000)})


def frames(r,name): return [x for x in r['frames'] if x['function']==name]
def events(f): return f['bounded_trace']['actuation']['first'][0]['events']


class LocatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.template=synthetic()
    def setUp(self): self.f=copy.deepcopy(self.template)
    def run_locator(self):
        before=pure.digest(self.f); keys=set(vars(pure)); funcs={k:vars(pure)[k] for k in locator.API_LINES}
        r=locator.locate_queue_failure(self.f,pure)
        self.assertEqual(before,pure.digest(self.f)); self.assertTrue(r['input_unchanged'])
        self.assertEqual(r['canonical_before_SHA256'],r['canonical_after_SHA256'])
        self.assertEqual(keys,set(vars(pure))); self.assertTrue(all(vars(pure)[k] is v for k,v in funcs.items()))
        self.assertEqual(r['gate1'],'UNKNOWN'); self.assertFalse(r['exact']); self.assertFalse(r['stage2_GO'])
        return r
    def test_01_positive_original_component_no_admission(self):
        self.assertEqual(pure.actuation_component(self.f)['first_transition_latency_us'],{'legs':[0],'wheels':[0]})
        r=self.run_locator(); self.assertEqual(r['status'],'NO_EXCEPTION'); self.assertEqual(r['frames'],[])
    def test_02_tick_negative_float_bool_not_coerced(self):
        for x in (-1,0.0,True):
            with self.subTest(x=x,type=type(x).__name__):
                self.f=copy.deepcopy(self.template); events(self.f)[0]['tick']=x
                r=self.run_locator(); self.assertEqual(r['exception']['message'],'typed integer/range')
                integer=frames(r,'integer')[0]['integer']
                self.assertEqual(integer['x'],{'python_type':type(x).__name__,'value':x})
                self.assertEqual(integer['low'],{'python_type':'int','value':0})
                act=frames(r,'actuation_component')[0]; self.assertEqual(act['line'],381)
                self.assertEqual(act['integer_callsite_fields'],['event.tick'])
                self.assertEqual(act['event']['tick'],integer['x']); self.assertEqual(act['window_control_index']['value'],0)
    def test_03_original_low_minus_one_contract(self):
        self.assertEqual(pure.integer(-1,-1),-1)
        for x in (-2,-1.0,True):
            with self.subTest(x=x):
                with self.assertRaisesRegex(ValueError,'typed integer/range'): pure.integer(x,-1)
    def test_04_sequence_listcomp_original_frame_only(self):
        events(self.f)[2]['seq']=-1; r=self.run_locator()
        self.assertEqual(frames(r,'integer')[0]['integer']['x']['value'],-1)
        self.assertTrue(all(x['function'] in {*locator.API_LINES,'<listcomp>','<genexpr>'} for x in r['frames']))
        self.assertNotIn('locate_queue_failure',[x['function'] for x in r['frames']])
        act=frames(r,'actuation_component')[0]; self.assertEqual(act['line'],378)
        witnesses=[x.get('event') for x in r['frames'] if x.get('event')]
        self.assertTrue(any(e['seq']['value']==-1 for e in witnesses))
        # A later window restores the PREVIOUS window's e on 3.14: never trust it.
        self.f=copy.deepcopy(self.template); self.f['controls']=2
        trace=self.f['bounded_trace']['actuation']; trace['control_windows_seen']=2
        second=copy.deepcopy(trace['first'][0]); second['control_index']=1; second['events'][2]['seq']=-1
        trace['first'].append(second); r=self.run_locator()
        act=frames(r,'actuation_component')[0]
        self.assertEqual(act['window_control_index']['value'],1); self.assertEqual(act['event']['seq']['value'],-1)
        self.assertEqual(act['event_local'],'recovered_seq_identity_witness')
    def test_05_status_retention_and_window_callsite_fields(self):
        cases=[('status',367),('seen',369),('bound',369),('window',372)]
        for key,line in cases:
            with self.subTest(key=key):
                self.f=copy.deepcopy(self.template); trace=self.f['bounded_trace']['actuation']
                if key=='status': self.f['actuation']['status']['observer_errors']=0.0
                elif key=='seen': trace['control_windows_seen']=1.0
                elif key=='bound': trace['retained_window_bound']=4.0
                else: trace['first'][0]['control_index']=0.0
                r=self.run_locator(); self.assertEqual(frames(r,'actuation_component')[0]['line'],line)
                self.assertEqual(frames(r,'integer')[0]['integer']['x']['python_type'],'float')
                if key=='bound': self.assertEqual(frames(r,'integer')[0]['integer']['low']['value'],None)
    def test_06_queue_vector_scalar_and_original_field(self):
        sub=next(e for e in events(self.f) if e['kind']=='queue_submit'); sub['pre']['episode'][7]=1.0
        r=self.run_locator(); self.assertEqual(r['exception']['message'],'decoded scalar type')
        q=frames(r,'queue_state')[0]; self.assertEqual(q['queue_state_current_loop_field']['value'],'episode')
        vec=frames(r,'vector')[0]['vector']; self.assertEqual(vec['index'],7)
        self.assertEqual(vec['v'],{'python_type':'float','value':1.0})
        act=frames(r,'actuation_component')[0]; self.assertEqual(act['event_local'],'sub')
        self.assertEqual(act['event']['kind']['value'],'queue_submit')
    def test_07_UNKNOWN_dict_bounded_metadata_only(self):
        sub=next(e for e in events(self.f) if e['kind']=='queue_submit')
        sub['pre']['lag_steps']={'status':'UNKNOWN','reason':'synthetic unavailable','payload':'SECRET_NOT_EXPORTED'}
        r=self.run_locator(); self.assertEqual(r['exception']['python_type'],'Missing'); self.assertEqual(r['validator_status'],'UNKNOWN')
        field=frames(r,'field')[0]; self.assertEqual(field['field_key']['value'],'lag_steps')
        self.assertEqual(set(field['field_value']['metadata']),{'status','reason'})
        self.assertNotIn('SECRET_NOT_EXPORTED',json.dumps(r))
    def test_08_UNKNOWN_string_and_missing_field_preserved(self):
        for missing in (False,True):
            with self.subTest(missing=missing):
                self.f=copy.deepcopy(self.template)
                if missing: del events(self.f)[0]['tick']
                else: events(self.f)[0]['tick']='UNKNOWN'
                r=self.run_locator(); self.assertEqual(r['exception']['python_type'],'Missing')
                self.assertEqual(frames(r,'field')[0]['field_key']['value'],'tick')
                self.assertEqual(r['exception']['message'],('missing field: tick' if missing else 'explicit UNKNOWN: tick'))
    def test_09_no_payload_locals_or_getters_exported(self):
        events(self.f)[0]['tick']=-1; r=self.run_locator(); text=json.dumps(r)
        for token in ('WHOLE_TRACE_SECRET_','private_payload','selected_target','f_locals','"pending"','"pre"','"post"','"args": [0.25'):
            self.assertNotIn(token,text)
        self.assertLess(len(text),6000)
        class Trap:
            @property
            def status(self): raise AssertionError('getter touched')
        self.f['trap']=Trap()
        with self.assertRaisesRegex(TypeError,'decoded builtins only'): locator.locate_queue_failure(self.f,pure)
    def test_10_passed_module_API_shape_and_nonmonkeypatch(self):
        for module in (object(),types.ModuleType('not_pure')):
            with self.subTest(module=type(module).__name__):
                with self.assertRaises((TypeError,ValueError)): locator.locate_queue_failure(self.f,module)
        self.assertEqual(pure.integer(3),3)
    def test_11_stdlib_source_no_IO_target_import_or_formatter(self):
        tree=ast.parse((HERE/'queue_failure_locator_v1.py').read_text(encoding='utf8'))
        self.assertEqual([n.names[0].name for n in tree.body if isinstance(n,ast.Import)],['hashlib','json','types'])
        forbidden={'open','eval','exec','compile','getattr','setattr','delattr','print','__import__'}
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in ('format_exc','format_exception','getsource','read_text','read_bytes','settrace','setprofile') for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and '__name__' in ast.unparse(n.test) for n in tree.body))


if __name__=='__main__': unittest.main()
