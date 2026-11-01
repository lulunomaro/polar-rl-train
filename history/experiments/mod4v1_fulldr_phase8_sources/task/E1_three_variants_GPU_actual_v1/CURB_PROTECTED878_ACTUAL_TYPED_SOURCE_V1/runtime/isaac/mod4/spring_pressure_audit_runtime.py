"""Pressure-aware expected-value auditor; retain every other D0 check.

The original MildDR observer assumed gas stiffness never varies. Here the
expected value is the independent D5 state and actual drive/buffer/model
must all match it. The original nominal baseline is restored after reading.
No error is masked or numeric tolerance loosened.
"""
import types,torch
from spring_pressure_index_runtime import SpringPressureSDK as OriginalPressureSDK,PressureSpringReadback
from spring_nominal_sdk_readback import tensor

class SpringPressureSDK(OriginalPressureSDK):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        mild=self.env._mild_dr;original=mild.audit;adapter=self
        def audit(this):
            expected=adapter.component.actual_stiffness(adapter.nominal)
            drive=tensor(adapter.robot.root_view.get_dof_stiffnesses())[:,adapter.ids].to(expected.device)
            buffered=tensor(adapter.robot.data.joint_stiffness)[:,adapter.ids]
            actual=tensor(adapter.actuator.stiffness)
            assert torch.equal(drive,expected) and torch.equal(buffered,expected) and torch.equal(actual,expected)
            nominal=this.gains['gas_springs']['stiffness']
            assert bool((nominal==2000).all()),'Original nominal observer reference was unexpectedly modified'
            this.gains['gas_springs']['stiffness']=expected.clone()
            try:row=original()
            finally:this.gains['gas_springs']['stiffness']=nominal
            assert this.gains['gas_springs']['stiffness'] is nominal
            row['D5_actual_stiffness_expected_value_audit']=dict(
                independent_D5_state_source=True,PhysX_buffer_implicit_model_exact=True,
                original_nominal_reference_restored=True,other_D0_checks_unchanged=True,
                actual_stiffness_range_N_m=[float(expected.min()),float(expected.max())],
                hardware_force_stroke_calibration=False)
            row['other_randomization']='D5 gas stiffness engineering episodefactor.9–1.1; gas preload/damping and other PD/COM/armature/friction unchanged; D1-D4 have their separate actual audits'
            return row
        mild.audit=types.MethodType(audit,mild)
