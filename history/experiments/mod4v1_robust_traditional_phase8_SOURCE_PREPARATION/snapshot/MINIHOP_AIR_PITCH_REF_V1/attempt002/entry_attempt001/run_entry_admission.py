"""Invoke actual new main twice, controlled pre-loop stop, zero real physics.

Plant/DR/bounds and upstream large-asset manifest are explicitly fake backends.
New controller, observer/geometry, loaders, source extension and StreamedRows are
real. This is not fullmodel, dynamic or actual driver admission.
"""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,shutil,sys,traceback
from unittest.mock import patch
from contextlib import ExitStack
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=json.loads((D/'SOURCE_LOCK.json').read_bytes());method=json.loads((D/'METHOD.json').read_bytes());u=json.loads((D/'UNIT_RESULT.json').read_bytes())
assert u['math_gate_pass']and u['reference_limits_gate_pass']and u['default_ticks']==u['enabled_ticks']==600
assert sha(D/'controller.py')==u['core_SHA']and sha(D/'METHOD.json')==lock['method_SHA']
for x in lock['sources']:assert sha(Path(x['path']))==x['SHA']
A=D/'entry_attempt001';A.mkdir(exist_ok=False)
for n in ['controller.py','run_manual_air_pitch_ref_v1.py','run_entry_admission.py','ENTRY_AST.json','METHOD.json','SOURCE_LOCK.json','UNIT_RESULT.json']:shutil.copy2(D/n,A/n)
with(A/'PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(dict(files=[dict(path=p.name,SHA=sha(p))for p in A.iterdir()if p.is_file()and p.name!='PREEXEC.json']),f,indent=2)
counts=dict(actual_model_boot_attempts=0,forward_attempts=0,integrator_attempts=0,other_dynamics_attempts=0,fake_plant_constructions=0,fake_DR_constructions=0,
            fake_initial_grades=0,actuator_call_attempts=0,packet_call_attempts=0,control_loop_body_entries=0)
rows=[]
class ControlledPreloopStop(Exception):pass

def denied(k):
    def call(*a,**kw):counts[k]+=1;raise AssertionError('Forbidden actual physics API during controlled entry: '+k)
    return call

def main_test():
    import mujoco
    with ExitStack()as stack:
        # Block before importing any project bridge, including model constructors.
        class BlockedModel:
            from_xml_string=staticmethod(denied('actual_model_boot_attempts'))
            from_xml_path=staticmethod(denied('actual_model_boot_attempts'))
            from_binary_path=staticmethod(denied('actual_model_boot_attempts'))
        stack.enter_context(patch.object(mujoco,'MjModel',BlockedModel))
        stack.enter_context(patch.object(mujoco,'mj_forward',denied('forward_attempts')))
        for n in ['mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit']:
            stack.enter_context(patch.object(mujoco,n,denied('integrator_attempts')))
        for n in ['mj_inverse','mj_rnePostConstraint','mj_fwdAcceleration']:
            stack.enter_context(patch.object(mujoco,n,denied('other_dynamics_attempts')))
        ep=D/'run_manual_air_pitch_ref_v1.py'
        spec=importlib.util.spec_from_file_location('airref_actual_entry_admission',ep);entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
        import run_minihop_landing_v4 as landing
        import MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2 as bridge
        from streamed_trace_rows_v1 import StreamedRows
        from MINIHOP_AIR_PITCH_REF_V1.attempt002.controller import MiniHop
        from sensor_core_jump_v1 import StateEstimator
        from sensor_core import LinkageGeometry
        class FakeDR:
            def __init__(self,seed,nominal):counts['fake_DR_constructions']+=1;self.seed=seed;self.nominal=nominal
        class FakePlant:
            def __init__(self,step):
                assert step is False;counts['fake_plant_constructions']+=1
                self.tick_phys=0;self.imu_offset=np.array([.03,0.,.04]);self.instrumentation_error=None;self.d=SimpleNamespace(time=0.)
            def attach_dr(self,dr):self.dr=dr;return dict(kind='CONTROLLED_FAKE_NO_DR_SAMPLES')
            def reset(self,symmetric,start_x):self.reset_args=(list(symmetric),start_x)
            def grade(self):counts['fake_initial_grades']+=1;return dict(kind='CONTROLLED_FAKE_INITIAL_GRADE_NOT_PHYSICS',xyz=[0.,0.,0.])
            def sensor_packet(self):counts['packet_call_attempts']+=1;raise AssertionError('No packet/update permitted before entry preloop stop')
            def apply_torque_request(self,*a,**kw):counts['actuator_call_attempts']+=1;raise AssertionError('No actuator call permitted')
        class FakeBounds(StreamedRows):
            def bind(self,plant):self.plant=plant;self.first_bar=None;self.next_bar=None
        def small_manifest(scene,cfg):
            assert scene=='flat'
            for x in lock['sources']:assert sha(Path(x['path']))==x['SHA']
            return dict(kind='CONTROLLED_UPSTREAM_MANIFEST_BACKEND_NOT_FULL_ASSET_VERIFY',files=[dict(path=x['path'],bytes=Path(x['path']).stat().st_size,SHA=x['SHA'])for x in lock['sources']],
                        model_assets=[],model_asset_verification='UNKNOWN_NOT_PERFORMED_IN_FAKE_ENTRY',model_SHA='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324',
                        public_sensor_projection_changed=False,contact_confidence_promoted=False,operator_enable_default=False)
        stack.enter_context(patch.object(bridge,'MiniHopAuditPlant',FakePlant))
        stack.enter_context(patch.object(entry,'FullDR',FakeDR))
        stack.enter_context(patch.object(entry,'BoundsRows',FakeBounds))
        stack.enter_context(patch.object(landing,'base_manifest',small_manifest))
        tree=ast.parse(ep.read_text(encoding='utf-8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');loop=next(n for n in ast.walk(fn)if isinstance(n,ast.For))
        for enabled in [False,True]:
            cfg=dict(scene='flat',forward_m_s=.7,brake_at_s=4.,duration_s=6.,seed=0,nominal=True,start_x_m=0.,
                     end_gain_file='TALL_ROUGH_BANK_V1/gain_delta20.json',landing_gain=dict(file='TALL_ROUGH_BANK_V1/gain_delta0.json'),hop=method['synthetic_config'].copy())
            del cfg['hop']['operator_enable'];cfg['hop']['air_pitch_ref_enable']=enabled
            cp=A/('config_on.json'if enabled else'config_off.json');out=A/('actual_main_on'if enabled else'actual_main_off')
            with cp.open('x',encoding='utf-8')as f:json.dump(cfg,f,indent=2)
            record=dict(enable=enabled,expected_stop=False)
            def trace(frame,event,arg):
                if event=='line'and frame.f_code.co_filename==str(ep)and frame.f_code.co_name=='main':
                    if frame.f_lineno==loop.body[0].lineno:counts['control_loop_body_entries']+=1
                    if frame.f_lineno==loop.lineno:
                        loc=frame.f_locals;hop=loc['hop'];est=loc['est'];geom=loc['geom']
                        assert type(hop)is MiniHop and type(est)is StateEstimator and isinstance(geom,LinkageGeometry)
                        assert hop.air_pitch_ref_enable is enabled and hop.enabled is False and hop.launched is False and hop.air_h_rad==0. and hop.capture_anchor_rad is None
                        assert len(loc['controls'])==len(loc['physical'])==0 and loc['plant'].tick_phys==0 and loc['N']==600
                        record.update(expected_stop=True,real_controller_class=type(hop).__module__+'.'+type(hop).__name__,
                            real_estimator_class=type(est).__module__+'.'+type(est).__name__,real_geometry_class=type(geom).__module__+'.'+type(geom).__name__,
                            operator_enable_default=False,position_active=False,scheduled_ticks=loc['N'],controls=0,physics_rows=0,actual_physics_steps=0,
                            source_closure_executed=True,controlled_asset_backend=True,real_fullmodel_admission='UNKNOWN_NOT_ATTEMPTED')
                        raise ControlledPreloopStop('EXPECTED controlled pre-loop admission stop, not a physics run/failure grade')
                return trace
            oldtrace=sys.gettrace();caught=False
            try:
                with patch.object(sys,'argv',[str(ep),'--config',str(cp),'--out',str(out)]):
                    sys.settrace(trace)
                    try:entry.main()
                    except ControlledPreloopStop:caught=True
            finally:sys.settrace(oldtrace)
            assert caught and record['expected_stop']
            err=json.loads((out/'ERROR.json').read_bytes());manifest=json.loads((out/'SOURCE_MANIFEST.json').read_bytes())
            assert 'EXPECTED controlled pre-loop admission stop'in err['error']and err['controls']==err['physics_steps']==0
            for key in ['trace_prefix','physics_prefix']:
                assert err[key]['actual_prefix_matches_producer']and err[key]['bytes']==0 and err[key]['producer']['successful_rows']==0
            assert manifest['air_reference_and_continuous_capture_anchor_enabled']is enabled
            assert manifest['relative_V3_push_flight_capture_equations_unchanged']is(not enabled)
            newpaths={x['path']for x in manifest['files']}
            for p in [ep,D/'controller.py',D/'METHOD.json',D/'SOURCE_LOCK.json']:assert str(p)in newpaths
            assert not(out/'result.json').exists()
            record.update(output=str(out.relative_to(D)),expected_stop_ERROR_SHA=sha(out/'ERROR.json'),source_manifest_SHA=sha(out/'SOURCE_MANIFEST.json'),empty_prefix_SHA=sha(out/'trace.jsonl'))
            rows.append(record)
        assert counts['fake_plant_constructions']==counts['fake_DR_constructions']==counts['fake_initial_grades']==2
        assert all(v==0 for k,v in counts.items()if not k.startswith('fake_'))
try:
    main_test()
    result=dict(status='PASS_TWO_CONTROLLED_REAL_ENTRY_PRELOOP_INVOCATIONS_NOT_FULLMODEL_ADMISSION',rows=rows,counts=counts,
        method_SHA=sha(D/'METHOD.json'),source_lock_SHA=sha(D/'SOURCE_LOCK.json'),core_SHA=sha(D/'controller.py'),entry_SHA=sha(D/'run_manual_air_pitch_ref_v1.py'),
        old_sources_unchanged=26,fullmodel_boot_and_asset_verification='UNKNOWN_NOT_PERFORMED',gain_or_plan_fitted=False,PH7_pending=True)
except BaseException:
    result=dict(status='FAILED_OR_UNKNOWN_PRESERVED_NO_RETRY',rows=rows,counts=counts,error=traceback.format_exc(),PH7_pending=True)
    with(D/'ENTRY_RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2));raise
with(D/'ENTRY_RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(result,indent=2,allow_nan=False))
