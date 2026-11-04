"""New V5 code/entry from immutable V4; AST/text derivation only, no project imports."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;R=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fresh(p,text):
 with p.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
def main():
 old=R/'STARTUP_STAND_V4/controller.py';entry=R/'run_startup_stand_case_v6.py'
 assert sha(old)=='9dec4f858524aad034fb287ac31f864299d86a00bd6aaad4f38f04e5063a2bd4'
 assert sha(entry)=='c43ab1e83f7b6ef861591f75401e96dd804ddd358586544ddd420f41bb915386'
 text=old.read_text(encoding='utf-8');tree=ast.parse(text);cl=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='StartupStand');fn=next(x for x in cl.body if isinstance(x,ast.FunctionDef)and x.name=='command')
 original='\n'.join(text.splitlines()[fn.lineno-1:fn.end_lineno])+'\n'
 before="if self.phase in ('CAPTURE_WORLD_SUPPORT', 'RETURN_NOMINAL', 'VERIFY'):";after="if self.phase in ('LIFT_WORLD_SUPPORT', 'CAPTURE_WORLD_SUPPORT', 'RETURN_NOMINAL', 'VERIFY'):"
 assert original.count(before)==1
 command=original.replace('def command(', 'def _command_lift_permission(',1).replace(before,after)
 inverse=command.replace('def _command_lift_permission(', 'def command(',1).replace(after,before)
 assert inverse==original
 header='''"""V5: only earlier permission for unchanged V4 pose-wheel branch; no new K/gain/contact inputs."""
import math
import numpy as np
from STARTUP_STAND_V4.controller import StartupStand as PreviousStartupStand, RECOVER
from STARTUP_STAND_V1.controller import scalar, vector, project_reference, legal_reference, quintic, LEG, WHEEL, EFFORT

class StartupStand(PreviousStartupStand):
    def __init__(self, gain_nominal, geometry, config=None, support_reference=None):
        c = {} if config is None else dict(config)
        flag = c.pop('lift_pose_enable', False)
        if type(flag) is not bool:
            raise ValueError('V5 lift_pose_enable requires exact bool')
        if flag and (c.get('support_geometry_enable', False) is not True
                     or c.get('recovery_tracking_enable', False) is not True
                     or c.get('alignment_wheel_enable', False) is not False):
            raise ValueError('V5 requires V4 support/tracking and legacy alignmentFalse')
        super().__init__(gain_nominal, geometry, c, support_reference=support_reference)
        self.lift_pose_enable = flag
        self.lift_pose_active = bool(flag and self.support_geometry_active)
        self.lift_pose_first_branch_s = None

    def command(self, e, packet, now, attitude_q):
        if not self.lift_pose_active:
            return super().command(e, packet, now, attitude_q)
        if self.phase not in ('OBSERVE', 'LIFT_WORLD_SUPPORT') or self.fault_reason is not None:
            return super().command(e, packet, now, attitude_q)
        try:
            # Numerical/type validation only. Existing finite domains, freshness, clock,
            # envelope, readiness and sensor constraints remain inside original V4.
            scalar(now, 'control time')
            scalar(forward_dummy if False else e.roll, 'roll')
            vector(e.state14, 14, 'state14')
            vector(e.omega_body, 3, 'omega')
            scalar(e.sensor_age_s, 'sensor age')
            scalar(e.estimated_time_s, 'estimate time')
            if getattr(packet, 'validity', None) is not True:
                raise ValueError('sensor packet validity not True')
            scalar(packet.time_s, 'source time'); scalar(packet.arrival_s, 'arrival')
            vector(packet.joint_pos4, 4, 'encoder q4')
            vector(packet.joint_vel4, 4, 'encoder qd4')
            vector(packet.accel_proper_body, 3, 'IMU proper')
            vector(packet.gyro_body, 3, 'raw gyro')
            vector(packet.wheel_vel2, 2, 'wheel rate')
            vector(attitude_q, 4, 'attitude quaternion')
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._notes(self._fault(ex))
        return self._command_lift_permission(e, packet, now, attitude_q)

    def _notes(self, tau):
        if not self.lift_pose_active:
            return super()._notes(tau)
        result = super()._notes(tau)
        current = self.fault_reason is None and 'time_s' in self.log
        on = bool(current and self.phase == 'LIFT_WORLD_SUPPORT' and self.capture_active)
        if on and self.lift_pose_first_branch_s is None:
            self.lift_pose_first_branch_s = self.log['time_s']
        self.log.update(lift_pose_enable=self.lift_pose_enable,
            lift_pose_timing_active=self.lift_pose_active,
            lift_pose_branch_on_this_command=on if current else None,
            lift_pose_same_gate_this_command=bool(self.capture_gate) if current else None,
            lift_pose_first_branch_s=self.lift_pose_first_branch_s,
            earlier_lift_latch_carryover_is_timing_change=bool(self.capture_latched and self.lift_pose_first_branch_s is not None),
            no_new_contact_or_hardware_permission=True)
        return result

'''
 header=header.replace("scalar(forward_dummy if False else e.roll, 'roll')","scalar(e.roll, 'roll')")
 code=header+command+'\nController = StartupStand\n';ast.parse(code)
 assert (D/'controller.py').read_bytes()==code.encode('utf-8') and sha(D/'controller.py')=='209c0385d1501021b05822f0222228ae78b012570f73fb526a435e8c02b2045a', 'Existing partial core must remain byte-exact'
 s=entry.read_text(encoding='utf-8');changes=[]
 def change(a,b):
  nonlocal s
  assert a in s,a;n=s.count(a);s=s.replace(a,b);changes.append(dict(old=a,new=b,occurrences=n))
 change('from STARTUP_STAND_V4.controller import StartupStand','from STARTUP_STAND_V5.controller import StartupStand')
 change("{'operator_enable','recovery_tracking_enable','alignment_wheel_enable','support_geometry_enable'}","{'operator_enable','recovery_tracking_enable','alignment_wheel_enable','support_geometry_enable','lift_pose_enable'}")
 change('startup_front065_world_support_v4_nominal1','startup_front065_lift_pose_v5_nominal1')
 change('Only the new V4 front nominal ID is admitted; no old case replay','Only the new V5 front nominal ID is admitted; no old case replay')
 change('NEW_LYING_STARTUP_WORLD_SUPPORT_CAPTURE_RETURN_V4_TRAIN','NEW_LYING_STARTUP_LIFT_POSE_TIMING_ONLY_V5_TRAIN')
 # Preserve all old provenance members and add the actual new wrapper/preflight/scope.
 marker="dump(out/'SOURCE_MANIFEST.json',provenance)";assert s.count(marker)==1
 extra="provenance['files'].extend([file_record(ROOT/'STARTUP_STAND_V5/controller.py'),file_record(ROOT/'STARTUP_STAND_V5/PARENT_METHOD_AND_PREP_SCOPE.json'),file_record(ROOT/'STARTUP_STAND_V5/preflight001/RESULT.json')]);provenance['lift_pose_enable_requested']=cfg['controller']['lift_pose_enable'];provenance['timing_only_same_V4_gate_not_support_certificate']=True;"
 s=s.replace(marker,extra+marker)
 marker2="result=dict(";assert s.count(marker2)==1
 s=s.replace(marker2,"result=dict(lift_pose_enable_requested=cfg['controller']['lift_pose_enable'],lift_pose_active=bool(controller.lift_pose_active),timing_only_not_physical_standup=True,")
 ast.parse(s)
 def parts(t):
  a=ast.parse(t);f=[x for x in ast.walk(a)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='k'];assert len(f)==1
  ass={k:[ast.dump(x,include_attributes=False)for x in ast.walk(a)if isinstance(x,ast.Assign)and any(isinstance(v,ast.Name)and v.id==k for v in x.targets)]for k in('target','healthy','good','complete','passed')};assert all(len(x)==1 for x in ass.values())
  return ast.dump(f[0],include_attributes=False),ass
 assert parts(s)==parts(entry.read_text(encoding='utf-8'))
 assert 'dr.queue_receipt()'in s and 'runtime_receipt'not in s and "load_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')"in s
 fresh(R/'run_startup_stand_case_v7.py',s)
 evidence=dict(status='V5_TIMING_ONLY_CORE_AND_UNEXECUTED_V7_AST_DERIVATION',old_core=dict(path=str(old),SHA=sha(old)),new_core=dict(path=str(D/'controller.py'),SHA=sha(D/'controller.py')),core_active_command_exact_inverse_to_V4_except_phase_permission=True,disabled_and_non_LIFT_literal_V4_delegate=True,finite_prevalidation_before_new_path_scheduler=True,old_entry=dict(path=str(entry),SHA=sha(entry)),new_entry=dict(path=str(R/'run_startup_stand_case_v7.py'),SHA=sha(R/'run_startup_stand_case_v7.py')),changes=changes,full_loop_target_healthy_good_complete_passed_AST_equal=True,queue_receipt_preserved=True,support_gain20_actual_loader_preserved_and_future_source_pin_required=True,new_entry_not_imported_or_executed=True,model_FK_PHY_solver_QA_native_Git_calls=0,PH11pending=True)
 fresh(D/'SOURCE_DERIVATION.json',json.dumps(evidence,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:v for k,v in evidence.items()if k in('status','new_core','new_entry','full_loop_target_healthy_good_complete_passed_AST_equal','new_entry_not_imported_or_executed')}))
if __name__=='__main__':main()
