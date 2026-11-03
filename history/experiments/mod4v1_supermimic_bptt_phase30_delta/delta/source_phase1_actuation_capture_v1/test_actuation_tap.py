"""Deterministic fake contracts only. No imports/execution of original/native task."""
from copy import deepcopy
from types import SimpleNamespace as NS
from unittest import TestCase, main
from unittest.mock import patch
from pathlib import Path
import ast
import datetime
import hashlib
import io
import json
import sys
import unittest

import actuation_tap as tapmod
from actuation_tap import (install_actuation_tap, queue_snapshot, snapshot_static,
                          validate_apply_window, validate_reset_edge, validate_static_snapshot,
                          CaptureUnknown, CaptureViolation)
from source_pins import verify_source_pins, verify_old_seal

HERE=Path(__file__).resolve().parent


class FakeQueue:
    def __init__(self,n,leglag,wheellag):
        self.n=n;self.groups={};self.counts={"submit":0,"apply":0,"reset":0};self.token=object();self.error=None
        for group,width in tapmod.GROUPS.items():
            self.groups[group]={name:([0]*n if name in ("lag_steps","episode") else [[0.0]*width for _ in range(n)] if name in ("pending","applied") else [False]*n if name.endswith("valid") else [-1]*n) for name in tapmod.QUEUE_FIELDS}
            self.reset(group,list(range(n)),leglag if group=="legs" else wheellag)
    def reset(self,group,ids,lag):
        self.counts["reset"]+=1;g=self.groups[group];width=tapmod.GROUPS[group]
        for i in ids:
            g["episode"][i]+=1;g["lag_steps"][i]=lag
            for f in ("pending","applied"):g[f][i]=[.25 if group=="legs" else 0.0]*width
            for f in ("pending_valid","applied_valid"):g[f][i]=False
            for f in ("issued_tick","due_tick","applied_issue_tick","first_apply_tick","last_submit_tick"):g[f][i]=-1
    def submit(self,key,x,tick):
        self.counts["submit"]+=1
        if self.error:raise self.error
        g=self.groups[key]
        for i in range(self.n):
            if g["last_submit_tick"][i]==tick:
                assert g["pending"][i]==x[i];continue
            assert not g["pending_valid"][i]
            assert g["last_apply_tick"][i]<tick
            assert g["last_submit_tick"][i]<0 or tick-g["last_submit_tick"][i]==8
            g["pending"][i]=deepcopy(x[i]);g["pending_valid"][i]=True
            g["issued_tick"][i]=tick;g["due_tick"][i]=tick+g["lag_steps"][i];g["last_submit_tick"][i]=tick
        return self.token
    def apply(self,key,tick):
        self.counts["apply"]+=1
        if self.error:raise self.error
        g=self.groups[key]
        for i in range(self.n):
            old=g["last_apply_tick"][i]
            assert old<0 or old in (tick-1,tick)
            if old!=tick and g["pending_valid"][i] and g["due_tick"][i]<=tick:
                assert g["due_tick"][i]==tick
                g["applied"][i]=deepcopy(g["pending"][i]);g["applied_valid"][i]=True
                g["applied_issue_tick"][i]=g["issued_tick"][i];g["first_apply_tick"][i]=tick;g["pending_valid"][i]=False
            g["last_apply_tick"][i]=tick
        return deepcopy(g["applied"])


class FakeAsset:
    def __init__(self):
        self.calls={"legs":0,"wheels":0};self.targets={};self.token=object();self.error=None
    def set_joint_position_target(self,target,*args,**kwargs):
        self.calls["legs"]+=1
        if self.error:raise self.error
        self.targets["legs"]=deepcopy(target);return self.token
    def set_joint_velocity_target(self,target,*args,**kwargs):
        self.calls["wheels"]+=1
        if self.error:raise self.error
        self.targets["wheels"]=deepcopy(target);return self.token
    @property
    def data(self):raise AssertionError("Observer must not fetch SDK/physical data")


class FakeTerm:
    def __init__(self,env,group,asset):
        self.env=env;self.group=group;self._asset=asset;self._processed_actions=None
        self.calls={"process":0,"apply":0,"reset":0};self.token=object();self.error=None
    def process_actions(self,actions):
        self.calls["process"]+=1
        if self.error:raise self.error
        self._processed_actions=[[v*2+(.25 if self.group=="legs" else 0) for v in row] for row in actions]
        self.env._physics_action_delay.queue.submit(self.group,deepcopy(self._processed_actions),self.env._sim_step_counter)
        return self.token
    def apply_actions(self):
        self.calls["apply"]+=1
        if self.error:raise self.error
        original=self._processed_actions
        value=self.env._physics_action_delay.queue.apply(self.group,self.env._sim_step_counter-1)
        self._processed_actions=value
        try:
            writer=self._asset.set_joint_position_target if self.group=="legs" else self._asset.set_joint_velocity_target
            writer(value,joint_ids=[0,1,2,3] if self.group=="legs" else [4,5])
        finally:self._processed_actions=original
        return self.token
    def reset(self,*args):self.calls["reset"]+=1


def make_env(leglag=0,wheellag=0,n=2):
    env=NS(_sim_step_counter=0,_reset_idx=lambda ids:None,termination_hook=lambda:None)
    q=FakeQueue(n,leglag,wheellag);env._physics_action_delay=NS(queue=q,terms={})
    asset=FakeAsset()
    env._physics_action_delay.terms={g:FakeTerm(env,g,asset) for g in tapmod.GROUPS}
    motors={g:NS(episode_scale=[[1.01]*w for _ in range(n)],step_scale=[[1.0]*w for _ in range(n)]) for g,w in tapmod.GROUPS.items()}
    env._mild_dr=NS(profile="white_v3",factor=[1.02]*n,mu=[.9]*n,nominal=[False]*n,reset_count=[1]*n,output={g:m.episode_scale for g,m in motors.items()})
    env._explicit_pd=NS(**motors,component=NS(factor={"leg_kp":[[1.0]*4 for _ in range(n)],"leg_kd":[[1.0]*4 for _ in range(n)],"wheel_kd":[[1.0]*2 for _ in range(n)]},episode=[1]*n))
    env._chassis_com=NS(component=NS(delta_m=[[.001,0.0,-.001] for _ in range(n)],episode=[1]*n))
    for name in ("_spring_pressure","_gas_damping"):setattr(env,name,NS(component=NS(factor=[[1.0,1.0] for _ in range(n)],episode=[1]*n)))
    return env,q,asset


def run_control(env,start=0,value=.1):
    env._sim_step_counter=start
    terms=env._physics_action_delay.terms
    returns=[]
    for g,w in tapmod.GROUPS.items():returns.append(terms[g].process_actions([[value]*w for _ in range(env._physics_action_delay.queue.n)]))
    for tick in range(start,start+8):
        env._sim_step_counter=tick+1
        for term in terms.values():returns.append(term.apply_actions())
    return returns


class ActuationTests(TestCase):
    def test_all_nine_lag_pairs_and_eight_physics_ticks(self):
        for a in range(3):
            for b in range(3):
                with self.subTest(legs=a,wheels=b):
                    e,q,asset=make_env(a,b);t=install_actuation_tap(e)
                    returns=run_control(e);events=t.drain()
                    receipt=validate_apply_window(events,0,{g:[1,1] for g in tapmod.GROUPS},t.status())
                    for g,lag in (("legs",a),("wheels",b)):
                        self.assertEqual(receipt["groups"][g][-1]["envs"][0]["first_transition_latency_us"],lag*2500)
                        self.assertEqual(receipt["groups"][g][-1]["envs"][0]["held_command_age_us"],17500)
                    self.assertTrue(all(x is e._physics_action_delay.terms["legs" if i%2==0 else "wheels"].token for i,x in enumerate(returns)))
                    self.assertEqual(q.counts,{"submit":2,"apply":16,"reset":2});self.assertEqual(asset.calls,{"legs":8,"wheels":8})
                    self.assertFalse(receipt["exact"]);self.assertEqual(receipt["physical_readback"],"UNKNOWN");t.close()
    def test_requested_vs_processed_vs_selected_not_conflated(self):
        e,q,a=make_env(2,2);t=install_actuation_tap(e);run_control(e);ev=t.drain()
        issue=next(x for x in ev if x["kind"]=="issue" and x["group"]=="legs")
        submit=next(x for x in ev if x["kind"]=="queue_submit" and x["group"]=="legs")
        first=next(x for x in ev if x["kind"]=="target_write" and x["group"]=="legs")
        self.assertEqual(issue["args"][0][0][0],.1);self.assertEqual(submit["args"][1][0][0],.45)
        self.assertEqual(first["args"][0][0][0],.25)
    def test_submit_return_identity_and_original_argument_identity(self):
        e,q,a=make_env();t=install_actuation_tap(e);value=[[.3]*4]*2
        self.assertIs(q.submit("legs",value,0),q.token)
        self.assertEqual(t.drain()[0]["args"][1],value)
    def test_forwarded_args_kwargs_identity_no_rebinding(self):
        e,q,a=make_env();seen={};sentinel=object()
        def original(key,x,tick,*,metadata):
            seen.update(key=key,x=x,tick=tick,metadata=metadata);return sentinel
        q.submit=original;t=install_actuation_tap(e);x=[[.1]*4]*2;metadata={"tag":object()}
        self.assertIs(q.submit("legs",x,0,metadata=metadata),sentinel)
        self.assertIs(seen["x"],x);self.assertIs(seen["metadata"],metadata)
    def test_writer_and_queue_output_return_identity(self):
        e,q,a=make_env();seen={};original=q.apply
        def apply(key,tick):
            value=original(key,tick);seen["result"]=value;return value
        q.apply=apply;t=install_actuation_tap(e)
        self.assertIs(q.apply("legs",0),seen["result"])
        self.assertIs(a.set_joint_position_target([[.1]*4]*2),a.token)
    def test_second_control_held_age_not_first_latency(self):
        e,q,a=make_env(2,2);t=install_actuation_tap(e);run_control(e);t.drain();run_control(e,8,.2)
        r=validate_apply_window(t.drain(),8,{g:[1,1] for g in tapmod.GROUPS})
        for group in tapmod.GROUPS:
            self.assertEqual(r["groups"][group][0]["envs"][0]["first_transition_latency_us"],5000)
            self.assertEqual(r["groups"][group][0]["envs"][0]["held_command_age_us"],20000)
            self.assertEqual(r["groups"][group][2]["envs"][0]["held_command_age_us"],5000)
    def test_episode_mixing_inside_window_is_unknown(self):
        e,q,a=make_env();t=install_actuation_tap(e);run_control(e);ev=t.drain()
        next(x for x in ev if x["kind"]=="queue_apply")["post"]["episode"][0]+=1
        with self.assertRaises(CaptureUnknown):validate_apply_window(ev,0,{g:[1,1] for g in tapmod.GROUPS})
    def test_original_exception_identity_unchanged(self):
        e,q,a=make_env();t=install_actuation_tap(e);err=RuntimeError("same original error");q.error=err
        with self.assertRaises(RuntimeError) as caught:q.submit("legs",[[0]*4]*2,0)
        self.assertIs(caught.exception,err);self.assertEqual(q.counts["submit"],1)
        self.assertEqual(t.drain()[0]["exception_identity"],id(err))
    def test_nested_target_exception_and_processed_restore(self):
        e,q,a=make_env();t=install_actuation_tap(e);term=e._physics_action_delay.terms["legs"]
        term.process_actions([[.2]*4]*2);old=term._processed_actions;e._sim_step_counter=1;err=ValueError("writer failed");a.error=err
        with self.assertRaises(ValueError) as caught:term.apply_actions()
        self.assertIs(caught.exception,err);self.assertIs(term._processed_actions,old);self.assertEqual(t.context,[])
    def test_capture_failure_does_not_hide_original(self):
        e,q,a=make_env();t=install_actuation_tap(e)
        with patch.object(tapmod,"queue_snapshot",side_effect=RuntimeError("observer fail")):
            self.assertIs(q.submit("legs",[[.2]*4]*2,0),q.token)
        self.assertGreater(t.status()["observer_errors"],0);self.assertEqual(q.counts["submit"],1)
    def test_capture_failure_keeps_original_exception(self):
        e,q,a=make_env();t=install_actuation_tap(e);err=ValueError("original");q.error=err
        with patch.object(tapmod,"queue_snapshot",side_effect=RuntimeError("observer fail")):
            with self.assertRaises(ValueError) as caught:q.apply("legs",0)
        self.assertIs(caught.exception,err)
    def test_owned_snapshots_do_not_drift(self):
        e,q,a=make_env();t=install_actuation_tap(e);run_control(e);ev=t.drain();saved=deepcopy(ev)
        q.groups["legs"]["pending"][0][0]=999;e._mild_dr.factor[0]=999
        self.assertEqual(ev,saved)
    def test_no_io_in_tick_callbacks(self):
        e,q,a=make_env();t=install_actuation_tap(e)
        with patch("builtins.open",side_effect=AssertionError("No tick IO")),patch("os.open",side_effect=AssertionError("No tick IO")),patch.object(Path,"read_bytes",side_effect=AssertionError("No tick IO")),patch.object(Path,"write_text",side_effect=AssertionError("No tick IO")):
            run_control(e)
        self.assertEqual(t.status()["observer_errors"],0)
    def test_static_existing_source_memory_and_no_physical_claim(self):
        e,q,a=make_env();s=snapshot_static(e);r=validate_static_snapshot(s)
        self.assertTrue(r["step_scale_exactly_one"]);self.assertEqual(s["components"]["_chassis_com"]["delta_m"][0],[.001,0,-.001])
        self.assertTrue(tapmod.is_unknown(s["physical_readback"]))
    def test_static_missing_motor_is_unknown(self):
        e,q,a=make_env();del e._explicit_pd.legs.step_scale
        with self.assertRaises(CaptureUnknown):validate_static_snapshot(snapshot_static(e))
    def test_step_scale_non_one_rejected(self):
        e,q,a=make_env();e._explicit_pd.wheels.step_scale[0][0]=1.001
        with self.assertRaises(CaptureViolation):validate_static_snapshot(snapshot_static(e))
    def test_descriptors_are_not_evaluated(self):
        class Lazy:
            @property
            def factor(self):raise AssertionError("lazy getter executed")
        e,q,a=make_env();e._mild_dr=Lazy();s=snapshot_static(e)
        self.assertTrue(tapmod.is_unknown(s["mild"]["factor"]))
    def test_partial_reset_edge_without_reset_patch(self):
        e,q,a=make_env(2,1);t=install_actuation_tap(e);reset=q.reset;envreset=e._reset_idx
        run_control(e);old={g:queue_snapshot(q,g) for g in tapmod.GROUPS}
        for g in tapmod.GROUPS:q.reset(g,[0],1)
        for g in tapmod.GROUPS:
            r=validate_reset_edge(old[g],queue_snapshot(q,g));self.assertEqual(r["selected_env_ids"],[0]);self.assertIn("UNKNOWN",r["reset_tick"])
        self.assertEqual(q.reset,reset);self.assertIs(e._reset_idx,envreset)
        run_control(e,8,.2);validate_apply_window(t.drain(),8,{g:[2,1] for g in tapmod.GROUPS})
    def test_reset_stale_or_unselected_mutation_rejected(self):
        e,q,a=make_env();before=queue_snapshot(q,"legs");q.reset("legs",[0],1);after=queue_snapshot(q,"legs")
        after["pending"][1][0]=99
        with self.assertRaises(CaptureViolation):validate_reset_edge(before,after)
        after=queue_snapshot(q,"legs");after["pending_valid"][0]=True
        with self.assertRaises(CaptureViolation):validate_reset_edge(before,after)
    def test_sensor_reset_term_owner_composes_both_orders(self):
        for before in (True,False):
            e,q,a=make_env();original=e._reset_idx;b=lambda ids:original(ids)
            if before:e._reset_idx=b
            t=install_actuation_tap(e)
            if not before:e._reset_idx=b
            termination=e.termination_hook;run_control(e);t.close()
            self.assertIs(e._reset_idx,b);self.assertIs(e.termination_hook,termination)
            self.assertFalse(t.status()["reset_hook"]);self.assertFalse(t.status()["sensor_hook"])
    def test_method_restore_exact_own_and_class_descriptor(self):
        e,q,a=make_env();term=e._physics_action_delay.terms["legs"]
        old=term.process_actions;term.process_actions=old
        t=install_actuation_tap(e);self.assertTrue(t.close()["restored"])
        self.assertIs(term.process_actions,old);self.assertNotIn("apply",vars(q));self.assertNotIn("apply_actions",vars(term))
        self.assertTrue(t.close()["restored"])
    def test_later_wrapper_not_clobbered_and_conflict_persists(self):
        e,q,a=make_env();t=install_actuation_tap(e);new=lambda *args:None;q.apply=new
        self.assertFalse(t.close()["restored"]);self.assertIs(q.apply,new)
        self.assertFalse(t.close()["restored"]);self.assertEqual(t.status()["coverage"],"UNKNOWN")
    def test_double_wrap_preflight_no_partial_changes(self):
        e,q,a=make_env();t=install_actuation_tap(e);old=q.apply
        with self.assertRaises(CaptureUnknown):install_actuation_tap(e)
        self.assertIs(q.apply,old);t.close()
    def test_buffer_loss_is_explicit_unknown_not_behaviour_change(self):
        e,q,a=make_env();t=install_actuation_tap(e,capacity=1);run_control(e)
        self.assertGreater(t.status()["dropped_events"],0);self.assertEqual(q.counts["apply"],16)
        with self.assertRaises(CaptureUnknown):validate_apply_window(t.drain(),0,{g:[1,1] for g in tapmod.GROUPS},t.status())
    def test_missing_original_target_method_is_unknown(self):
        e,q,a=make_env();e._physics_action_delay.terms["legs"]._asset=NS()
        t=install_actuation_tap(e);self.assertTrue(t.status()["missing_hooks"]);self.assertFalse(t.status()["exact"])
    def test_missing_tick_due_or_writer_mismatch(self):
        e,q,a=make_env(1,0);t=install_actuation_tap(e);run_control(e);ev=t.drain();ep={g:[1,1] for g in tapmod.GROUPS}
        bad=deepcopy(ev);bad=[x for x in bad if not(x["kind"]=="queue_apply" and x["group"]=="legs" and x["tick"]==3)]
        with self.assertRaises(CaptureUnknown):validate_apply_window(bad,0,ep)
        bad=deepcopy(ev);next(x for x in bad if x["kind"]=="queue_apply")["post"]["due_tick"][0]+=1
        with self.assertRaises(CaptureViolation):validate_apply_window(bad,0,ep)
        bad=deepcopy(ev);next(x for x in bad if x["kind"]=="target_write")["args"][0][0][0]+=1
        with self.assertRaises(CaptureViolation):validate_apply_window(bad,0,ep)
    def test_source_pins_and_prior_nine_members_unchanged(self):
        r=verify_source_pins();self.assertTrue(r["source_hashes_match"]);self.assertTrue(verify_old_seal()["all_unchanged"])
    def test_observer_imports_are_stdlib_no_io_or_native_entry(self):
        tree=ast.parse((HERE/"actuation_tap.py").read_text(encoding="utf-8"))
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertEqual(imports,["functools"])
        self.assertFalse(any(isinstance(n,ast.Import) for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Name) and n.id in ("open","eval","exec","__import__") for n in ast.walk(tree)))


def run_with_receipt():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ActuationTests)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    log=stream.getvalue();print(log,end="")
    if not result.wasSuccessful():return 1
    logpath=HERE/"FAKE_TEST_LOG.txt";receiptpath=HERE/"SOURCE_RECEIPT.json"
    if logpath.exists() or receiptpath.exists():raise ValueError("Frozen receipt already exists; use ordinary read-only test run")
    pins=verify_source_pins();old=verify_old_seal()
    receipt={"version":1,"status":"SOURCE_FAKE_PASSIVE_OBSERVER_CONTRACT_PASS","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "tests_run":result.testsRun,"errors":len(result.errors),"failures":len(result.failures),"subtests":"nine lag pairs;two environments;partial reset;both sensor-hook orders",
             "source_identity":pins,"old_seal":old,"actual_sdk_pass":False,"gate1_admitted":False,"exact":False,"paper_ready":False,
             "physical_readback":"UNKNOWN","runtime_source_binding":"UNKNOWN","source_only":True,"reset_hook":False,"per_tick_io":False,
             "scope":"NEW actuation observer only; no SSH/SDK/GPU/PT/rawJSONL/model/replay/canonical/Git/native/stager/trainer",
             "test_log_sha256":hashlib.sha256(log.encode()).hexdigest()}
    logpath.write_text(log,encoding="utf-8",newline="\n")
    receiptpath.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    return 0

if __name__=="__main__":
    if "--receipt" in sys.argv:raise SystemExit(run_with_receipt())
    main(verbosity=2)
