"""NEW stdlib fakes only. No SDK, Torch, real capture, model or old test runner."""
import ast
import copy
import difflib
from pathlib import Path
import random
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'source_phase1_capture_evidence_verifier_v1'))
import actuation_tap_v2 as c2
import capture_evidence_verifier_v1 as pure


class Asset:
    def __init__(self): self.calls=[]; self.token=object(); self.exc=None
    def set_joint_position_target(self,target,*args,**kwargs):
        self.calls.append(('position',target,args,kwargs))
        if self.exc is not None: raise self.exc
        return self.token
    def set_joint_velocity_target(self,target,*args,**kwargs):
        self.calls.append(('velocity',target,args,kwargs))
        if self.exc is not None: raise self.exc
        return self.token


class Queue:
    def __init__(self):
        self.groups={}; self.calls=[]
        for group,width in c2.GROUPS.items():
            self.groups[group]={k:([[0.]*width for _ in range(3)] if k in ('pending','applied') else
                [False]*3 if k.endswith('valid') else list(range(3)) if k=='lag_steps' else
                [1 if k=='episode' else -1]*3) for k in c2.QUEUE_FIELDS}
    def submit(self,key,target,tick):
        self.calls.append(('submit',key,target,tick))
        if type(tick) is not int or tick<0: raise ValueError('fake original nonnegative issue tick')
        q=self.groups[key]
        for i in range(3):
            q['pending'][i]=target[i][:]; q['pending_valid'][i]=True; q['issued_tick'][i]=tick
            q['due_tick'][i]=tick+q['lag_steps'][i]; q['last_submit_tick'][i]=tick
        return target
    def apply(self,key,tick):
        self.calls.append(('apply',key,tick))
        if type(tick) is not int or tick<0: raise ValueError('fake original nonnegative apply tick')
        q=self.groups[key]
        for i in range(3):
            if q['pending_valid'][i] and q['due_tick'][i]==tick:
                q['applied'][i]=q['pending'][i][:]; q['applied_valid'][i]=True
                q['applied_issue_tick'][i]=q['issued_tick'][i]; q['first_apply_tick'][i]=tick; q['pending_valid'][i]=False
            q['last_apply_tick'][i]=tick
        return q['applied']
    def reset(self,ids):
        for group,width in c2.GROUPS.items():
            q=self.groups[group]
            for i in ids:
                q['episode'][i]+=1; q['pending'][i]=[0.]*width; q['applied'][i]=[0.]*width
                q['pending_valid'][i]=q['applied_valid'][i]=False
                for k in ('issued_tick','due_tick','applied_issue_tick','first_apply_tick','last_submit_tick'): q[k][i]=-1


class Term:
    def __init__(self,env,group,asset):
        self.env,self.group,self._asset=env,group,asset
        self.before=self.after_queue=None; self.apply_calls=self.process_calls=0
        self.token=object(); self.position_for_wheels=False
    def process_actions(self,target):
        self.process_calls+=1; self.env._physics_action_delay.queue.submit(self.group,target,self.env._sim_step_counter)
        return self.token
    def apply_actions(self):
        self.apply_calls+=1; tick=self.env._sim_step_counter-1
        if self.before: self.before()
        target=self.env._physics_action_delay.queue.apply(self.group,tick)
        if self.after_queue: self.after_queue()
        if self.group=='legs' or self.position_for_wheels:
            self._asset.set_joint_position_target(target,joint_ids=(0,1,2,3) if self.group=='legs' else (4,5))
        else: self._asset.set_joint_velocity_target(target,joint_ids=(4,5))
        return self.token


class Holder: pass
class Env:
    def __init__(self,shared=True):
        self._sim_step_counter=0; self.asset=Asset(); self.wheel_asset=self.asset if shared else Asset()
        self._physics_action_delay=Holder(); self._physics_action_delay.queue=Queue()
        self._physics_action_delay.terms={g:Term(self,g,self.asset if g=='legs' else self.wheel_asset) for g in c2.GROUPS}
    @property
    def sensor_getter_trap(self): raise AssertionError('extra getter')
    def reset_idx(self,ids): self._physics_action_delay.queue.reset(ids)


def run_window(env,start=0):
    env._sim_step_counter=start
    for group,width in c2.GROUPS.items():
        term=env._physics_action_delay.terms[group]; target=[[.25]*width for _ in range(3)]
        if term.process_actions(target) is not term.token: raise AssertionError('process return changed')
    for tick in range(start,start+8):
        env._sim_step_counter=tick+1
        for term in env._physics_action_delay.terms.values():
            if term.apply_actions() is not term.token: raise AssertionError('apply return changed')


def functions(tree):
    out={}
    for n in tree.body:
        if isinstance(n,ast.FunctionDef): out[n.name]=ast.dump(n,include_attributes=False)
        if isinstance(n,ast.ClassDef):
            for f in n.body:
                if isinstance(f,ast.FunctionDef): out[n.name+'.'+f.name]=ast.dump(f,include_attributes=False)
    return out


class ClockScopeTests(unittest.TestCase):
    def setUp(self): self.env=Env(); self.tap=c2.ActuationTap(self.env)
    def tearDown(self): self.tap.close()
    def test_01_counter_zero_external_setter_preserved(self):
        target=[[.5,.75]]; ids=[4,5]; selected=[0,2]
        result=self.env.asset.set_joint_position_target(target,joint_ids=ids,env_ids=selected)
        self.assertIs(result,self.env.asset.token); self.assertEqual(len(self.env.asset.calls),1)
        call=self.env.asset.calls[0]; self.assertIs(call[1],target); self.assertIs(call[3]['joint_ids'],ids); self.assertIs(call[3]['env_ids'],selected)
        e=self.tap.drain()[0]; self.assertEqual(e['seq'],0); self.assertEqual(e['raw_stored_counter'],0)
        self.assertEqual(e['tick']['status'],'NOT_APPLICABLE'); self.assertEqual(e['group']['status'],'UNKNOWN')
        self.assertEqual(e['write_scope'],'NON_TERM_SETTER'); self.assertIsNone(e['parent_term_apply_seq'])
        self.assertEqual(e['setter']['joint_ids_source'],'kwargs.joint_ids'); self.assertEqual(e['setter']['joint_ids'],ids)
        target[0][0]=99.; ids[0]=99; self.assertEqual(e['args'][0][0][0],.5); self.assertEqual(e['setter']['joint_ids'],[4,5])
    def test_02_synthetic_gas_preload_and_positive_counter_nonterm(self):
        # Names denote invented auxiliary caller patterns, not an actual path attribution.
        for counter in (0,17):
            self.env._sim_step_counter=counter
            self.env.asset.set_joint_position_target([[.01,.02]],(4,5))
            self.env.asset.set_joint_velocity_target([[.03,.04]])
        rows=self.tap.drain(); self.assertEqual(len(rows),4); self.assertEqual(len(self.env.asset.calls),4)
        self.assertTrue(all(e['group']['status']=='UNKNOWN' and e['tick']['status']=='NOT_APPLICABLE' for e in rows))
        self.assertEqual([e['raw_stored_counter'] for e in rows],[0,0,17,17])
        self.assertEqual(rows[0]['setter']['joint_ids_source'],'positional[1]_UNQUALIFIED_SDK_SIGNATURE')
        self.assertEqual(rows[1]['setter']['joint_ids_source'],'OMITTED')
    def test_03_original_8ticks_4plus2_and_strict_parent_link(self):
        state=random.getstate(); run_window(self.env); rows=self.tap.drain(); byseq={e['seq']:e for e in rows}
        self.assertEqual(random.getstate(),state); self.assertEqual(self.tap.status()['observer_errors'],0)
        metrics=c2.validate_apply_window(rows,0,{g:[1]*3 for g in c2.GROUPS},self.tap.status())
        for group in c2.GROUPS:
            self.assertEqual([r['tick'] for r in metrics['groups'][group]],list(range(8)))
        for e in rows:
            pure.integer(e['tick'],0)
            if e['kind']=='target_write':
                parent=byseq[e['parent_term_apply_seq']]
                self.assertEqual((parent['kind'],parent['group'],parent['tick']),('term_apply',e['group'],e['tick']))
                self.assertEqual(e['write_scope'],'SAME_ASSET_TERM_APPLY_CONTEXT')
        self.assertEqual(len([e for e in rows if e['kind']=='queue_apply']),16); self.assertEqual(self.tap.context,[])
    def test_04_nested_group_comes_from_parent_not_setter_name(self):
        # Dynamic context labels only: this does NOT prove wheels2 physical DOFs,
        # a final target identity, or the real term._joint_ids / SDK method binding.
        legs,wheels=(self.env._physics_action_delay.terms[g] for g in c2.GROUPS)
        wheels.position_for_wheels=True; legs.before=wheels.apply_actions; self.env._sim_step_counter=1
        legs.apply_actions(); rows=self.tap.drain(); writes=[e for e in rows if e['kind']=='target_write']
        self.assertEqual([e['group'] for e in writes],['wheels','legs'])
        self.assertEqual(writes[0]['setter']['method'],'set_joint_position_target')
        self.assertEqual(writes[0]['setter']['discovery_group_hint_NOT_AUTHORITY'],'legs')
        self.assertEqual(self.tap.context,[])
    def test_05_writer_inherits_parent_clock_not_later_counter(self):
        term=self.env._physics_action_delay.terms['legs']; term.after_queue=lambda:setattr(self.env,'_sim_step_counter',99)
        self.env._sim_step_counter=1; term.apply_actions()
        wr=next(e for e in self.tap.drain() if e['kind']=='target_write')
        self.assertEqual((wr['tick'],wr['raw_stored_counter']),(0,99))
    def test_06_nonmatching_asset_context_stays_unknown(self):
        self.tap.close(); self.env=Env(shared=False); self.tap=c2.ActuationTap(self.env)
        term=self.env._physics_action_delay.terms['legs']
        term.before=lambda:self.env.wheel_asset.set_joint_velocity_target([[.2,.3]],joint_ids=(4,5))
        self.env._sim_step_counter=1; term.apply_actions()
        e=next(e for e in self.tap.drain() if e.get('write_scope')=='ACTIVE_TERM_ASSET_MISMATCH')
        self.assertEqual(e['group']['status'],'UNKNOWN'); self.assertEqual(e['tick']['status'],'UNKNOWN')
        self.assertIsNone(e['parent_term_apply_seq']); self.assertEqual(e['active_term_context']['group'],'legs')
    def test_07_same_exception_once_and_finally_context_restored(self):
        error=RuntimeError('synthetic original setter error'); self.env.asset.exc=error; self.env._sim_step_counter=1
        with self.assertRaises(RuntimeError) as caught: self.env._physics_action_delay.terms['legs'].apply_actions()
        self.assertIs(caught.exception,error); self.assertEqual(len(self.env.asset.calls),1); self.assertEqual(self.tap.context,[])
        rows=self.tap.drain(); self.assertEqual(len([e for e in rows if e['kind']=='target_write' and e['outcome']=='RAISED']),1)
        self.env.asset.exc=None; self.env.asset.set_joint_position_target([[0.]])
        self.assertEqual(self.tap.drain()[0]['write_scope'],'NON_TERM_SETTER')
    def test_08_reset_neighbor_original_hook_and_clock_preserved(self):
        q=self.env._physics_action_delay.queue; reset=q.reset.__func__; envreset=self.env.reset_idx.__func__
        run_window(self.env); old=copy.deepcopy(q.groups['legs']); self.tap.drain(); self.env.reset_idx([1]); new=copy.deepcopy(q.groups['legs'])
        edge=c2.validate_reset_edge(old,new); self.assertEqual(edge['selected_env_ids'],[1]); self.assertTrue(edge['unselected_exact'])
        self.assertIs(q.reset.__func__,reset); self.assertIs(self.env.reset_idx.__func__,envreset)
        self.env.asset.set_joint_position_target([[0.]],joint_ids=[0],env_ids=[1])
        self.assertEqual(self.tap.drain()[0]['tick']['status'],'NOT_APPLICABLE')
        run_window(self.env,8); rows=self.tap.drain(); c2.validate_apply_window(rows,8,{g:[1,2,1] for g in c2.GROUPS},self.tap.status())
    def test_09_restore_conflict_not_overwritten(self):
        foreign=lambda *a,**k:None; self.env.asset.set_joint_position_target=foreign
        receipt=self.tap.close(); self.assertFalse(receipt['restored']); self.assertIn('set_joint_position_target',receipt['conflicts'])
        self.assertIs(self.env.asset.set_joint_position_target,foreign)
    def test_10_overflow_unknown_original_calls_retained(self):
        self.tap.close(); self.tap=c2.ActuationTap(self.env,capacity=1)
        for _ in range(3): self.assertIs(self.env.asset.set_joint_position_target([[0.]]),self.env.asset.token)
        self.assertEqual(len(self.env.asset.calls),3); self.assertEqual(len(self.tap.drain()),1)
        self.assertEqual(self.tap.status()['dropped_events'],2); self.assertEqual(self.tap.status()['coverage'],'UNKNOWN')
    def test_11_no_general_negative_float_bool_physics_acceptance(self):
        queue=self.env._physics_action_delay.queue
        for bad in (-1,0.0,True):
            with self.subTest(bad=bad):
                before=len(queue.calls)
                with self.assertRaises(ValueError): queue.apply('legs',bad)
                e=self.tap.drain()[0]; self.assertEqual(type(e['tick']),type(bad)); self.assertEqual(e['tick'],bad)
                self.assertEqual(e['outcome'],'RAISED'); self.assertEqual(len(queue.calls),before+1)
                with self.assertRaisesRegex(ValueError,'typed integer/range'): pure.integer(e['tick'],0)
        with self.assertRaises(ValueError): self.env._physics_action_delay.terms['legs'].apply_actions()
        invalid_parent=next(e for e in self.tap.drain() if e['kind']=='term_apply')
        self.assertEqual(invalid_parent['tick'],-1); self.assertEqual(self.tap.context,[])
        with self.assertRaises(ValueError): pure.integer(invalid_parent['tick'],0)
        self.env.asset.set_joint_position_target([[0.]])
        with self.assertRaises(ValueError): pure.integer(self.tap.drain()[0]['tick'],0)
        run_window(self.env); rows=self.tap.drain(); bad=copy.deepcopy(rows)
        next(e for e in bad if e['kind']=='queue_apply')['tick']=-1
        with self.assertRaises(c2.CaptureUnknown): c2.validate_apply_window(bad,0,{g:[1]*3 for g in c2.GROUPS})
    def test_12_only_patch_changed_AST_complete_diff_and_no_new_native(self):
        old=(HERE.parent/'source_phase1_actuation_capture_v1/actuation_tap.py').read_text(encoding='utf8')
        new=(HERE/'actuation_tap_v2.py').read_text(encoding='utf8'); a,b=functions(ast.parse(old)),functions(ast.parse(new))
        self.assertEqual(a.keys(),b.keys()); self.assertEqual([k for k in a if a[k]!=b[k]],['ActuationTap._patch'])
        expected=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='source_phase1_actuation_capture_v1/actuation_tap.py',tofile='source_phase1_actuation_clock_scope_v2/actuation_tap_v2.py'))
        self.assertEqual((HERE/'C1_TO_C2_SOURCE_DIFF.patch').read_text(encoding='utf8'),expected)
        tree=ast.parse(new); self.assertEqual([(n.module,[a.name for a in n.names]) for n in tree.body if isinstance(n,ast.ImportFrom)],[('functools',['wraps'])])
        self.assertFalse(any(isinstance(n,ast.Import) for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in ('cpu','tolist','numpy','synchronize','manual_seed','randn','rand','_reset_idx') for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('open','eval','exec','__import__') for n in ast.walk(tree)))


if __name__=='__main__': unittest.main()
