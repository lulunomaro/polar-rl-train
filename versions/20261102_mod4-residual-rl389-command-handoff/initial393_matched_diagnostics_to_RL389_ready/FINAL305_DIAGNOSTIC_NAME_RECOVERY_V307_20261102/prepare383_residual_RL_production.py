"""Human redirected objective: learned residual RL, no online MPC solver at inference."""
from pathlib import Path
import ast,hashlib,json,re,shutil,time
P=Path(__file__).resolve().parent;T=P.parent;S=T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102';N=T/'MPC_COMMAND_RESIDUAL_RL_V383_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not N.exists();N.mkdir();(N/'reports').mkdir()
def rename(s):
 s=s.replace(str(S),str(N)).replace(S.as_posix(),N.as_posix());saved=[]
 def hide(m):saved.append(m.group());return '@HASH'+str(len(saved)-1)+'@'
 s=re.sub(r'\b[0-9a-f]{64}\b',hide,s);s=re.sub(r'(?<=[A-Za-z_])345(?!\d)','383',s)
 for i,v in enumerate(saved):s=s.replace('@HASH'+str(i)+'@',v)
 return s
for folder in('source','control345','normal345'):
 for p in sorted((S/folder).rglob('*.py')):
  out=N/rename(folder)/rename(str(p.relative_to(S/folder)));out.parent.mkdir(parents=True,exist_ok=True);out.write_text(rename(p.read_text('utf8')),encoding='utf8')
for name in('launch345_reference_tracking_once.py','collect345_status_readonly.py','review345_NEW_final_whole_CPU_UNUSED_once.py','teacher_task345.py','tracking_task345.py'):
 (N/rename(name)).write_text(rename((S/name).read_text('utf8')),encoding='utf8')
shutil.copyfile(S/'reference345.npz',N/'reference383.npz')
trace=T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102/reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json'
saved=json.loads(trace.read_bytes());commands=saved['commands'];assert len(commands)==500
ff=dict(kind='FIXED347_COMMAND_FEEDFORWARD_FOR_RESIDUAL_RL383',source=dict(path=str(trace),bytes=trace.stat().st_size,SHA=H(trace)),source_control_hz=100,actual_policy_hz=50,source100Hz_not_faithfully_reproduced=True,commands=[commands[2*i]['processed_target']for i in range(250)],initial=commands[0],joint_names=saved['joint_names'],normal_action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],legscale=.5,wheelscale=10.,residual_normalized_radius=1.,no_online_MPC=True,no_torque_labels_in_actor_loss=True,learned_residual_zero_at_source_actor=True)
put(N/'feedforward383.json',ff)
# No online source controller imported. Fixed measured motor targets remain only a baseline.
p=N/'source/tracking_learner383.py';s=p.read_text('utf8')
s=s.replace('from tracking_survival383 import matched_survival383','from tracking_survival383 import matched_survival383\nfrom residual_policy383 import ResidualPolicy383')
needle="        self.actor.distribution.std_param.requires_grad_(False)"
s=s.replace(needle,needle+"\n        from copy import deepcopy\n        self.residual_origin_actor=deepcopy(self.actor).eval()\n        for parameter in self.residual_origin_actor.parameters():parameter.requires_grad_(False)\n        self.residual_policy=ResidualPolicy383(reference.path.parent/'feedforward383.json',wm.device)",1)
s=s.replace('return forward(self.actor,x).clamp(-6,6)','return self.residual_policy.action(forward(self.actor,x),self.residual_origin_actor(x).detach(),phase)')
# RSL model __call__ may require distribution update; use established forward for both.
s=s.replace('self.residual_origin_actor(x).detach()','forward(self.residual_origin_actor,x).detach()')
s=s.replace('raw=forward(self.actor,x);action=raw.clamp(-6,6)','raw=self.residual_policy.raw(forward(self.actor,x),forward(self.residual_origin_actor,x).detach(),meta[\'phase\']+i);action=raw.clamp(-6,6)')
s=s.replace("tracker_scope='planned reference goals + measured current pose; not autonomous depth-only student'", "tracker_scope='RL residual on fixed processed motor command feedforward; online actor only/no MPC solver; plannedreference conditioned',residual_RL=True,residual_radius=1.,fixed_feedforward_source='347',online_MPC=False")
s=s.replace("return dict(actor_state_dict=self.actor.state_dict(),critic_state_dict=", "return dict(residual_origin_actor_state_dict=self.residual_origin_actor.state_dict(),residual_policy_protocol=self.residual_policy.protocol,RL_residual=True,online_MPC=False,actor_state_dict=self.actor.state_dict(),critic_state_dict=")
p.write_text(s,encoding='utf8')
# Reference object has no need for checkpoint reads; make path binding explicit.
p=N/'source/tracking_reference383.py';s=p.read_text('utf8');idx=s.index('    def __init__');end=s.index('\n',s.index('):',idx))+1
s=s[:end]+"        self.path=__import__('pathlib').Path(path)\n"+s[end:] if 'def __init__(self,path,'in s else s
p.write_text(s,encoding='utf8')
# Source347 planned initial physical state and held targets at each episode, including SDK derived-cache fix.
p=N/'source/worker383.py';s=p.read_text('utf8');needle="real=sdk.Teacher383Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)"
assert needle in s;s=s.replace(needle,needle+"\n from residual_reset383 import install_planned_reset383\n reset383=install_planned_reset383(real,P/'feedforward383.json')\n real.reset()\n put('ACTUAL383_RL_PLANNED_RESET_AND_IMU_CACHE_REPAIR.json',reset383.receipt())")
s=s.replace("assert int(torch.count_nonzero(tensor(robot.data.default_joint_pos)))==int(torch.count_nonzero(tensor(robot.data.default_joint_vel)))==0", "assert torch.isfinite(tensor(robot.data.joint_pos)).all()and torch.isfinite(tensor(robot.data.joint_vel)).all()")
s=s.replace("reference=Reference383(P/'reference383.npz',TASK['reference'],joint_names,real.device,real.hip_anchors194)","reference=Reference383(P/'reference383.npz',TASK['reference'],joint_names,real.device,real.hip_anchors194)\n reference.path=P/'reference383.npz'")
s=s.replace("reference=TASK['reference'],", "reference=TASK['reference'],residual_RL=True,feedforward_protocol=learner.residual_policy.protocol,planned_reset_protocol=reset383.receipt(),")
p.write_text(s,encoding='utf8')
# File transfer and CPU receipt are for383, not reused behavioral admission344.
p=N/'launch383_reference_tracking_once.py';s=p.read_text('utf8')
start=s.index('    check=');end=s.index('    pattern=',start)
s=s[:start]+"    check=read(R/'CPU383_RESIDUAL_RL_NO_STEP.json');assert check['passed']and check['optimizer_steps']==0 and check['learner_SHA']==H(N/'source/tracking_learner383.py')\n"+s[end:]
s=s.replace("pattern='", "pattern='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|prepare_archive|single_gpu|collect_nine|deploy_nine|E1_actual_qualification|collect_e1_own_case|",1)
s=s.replace("for name in ('TASK383_FROZEN.json','reference383.npz'):","for name in ('TASK383_FROZEN.json','reference383.npz','feedforward383.json'):")
s=s.replace("'TASK383.json' if name.endswith('.json')else name", "'TASK383.json' if name=='TASK383_FROZEN.json'else name")
p.write_text(s,encoding='utf8')
# Collector does not repeat startup/hardware/model validation.
p=N/'collect383_status_readonly.py';s=p.read_text('utf8').replace("patterns='","patterns='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|prepare_archive|single_gpu|collect_nine|",1);p.write_text(s,encoding='utf8')
task=json.loads(json.dumps(json.loads((S/'TASK345_FROZEN.json').read_bytes())).replace('345','383'));nonce=str(time.time_ns())
task.update(run_id='REFERENCE_TRACKING383_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_RESIDUAL_RL383_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_RESIDUAL_RL383_'+nonce+'/owner72',human_authorization='2026-11-02human:I_need_RL_upstairs;newlearnedresidualRL/noonlineMPC,existinggoalbudget',actor_objective='H8directsameweightedtrackingcost, actor learns residual about fixed347processedcommandtable; no torque cloning/no online MPC',residual_RL=True,residual_radius=1.,fixed_command_feedforward=dict(path='feedforward383.json',bytes=(N/'feedforward383.json').stat().st_size,SHA=H(N/'feedforward383.json')),initial_state='source347plannedinitial/fullq/dq/root+actualqheldqueue+derivedIMUcachefresh;independentDRresets',source_cpu_reuse=False,CPU383_new_required=True,worker_SHA='NOT_FROZEN_YET')
task['reference']['path']='reference383.npz';put(N/'TASK383_PREPARE.json',task)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
put(P/'reports/ACTUAL383_HUMAN_RL_REDIRECTION_AND_RESIDUAL_PROTOCOL.json',dict(epoch=time.time(),human='我需要的是rl上台阶',objective='RLpolicyjump270andstable;traditionalMPCsamplesnotdelivery',prior381_timingnext_superseded=True,traditional_diag_stop=True,newroot=str(N),RL=True,online_MPC=False,fixedfeedforward='source347processedmotorcommands50Hz; not directtorque',residual='actor103online + savedfrozenoriginactor produces1*tanh(outputdifference); initialresidual0/fullweightsallAdamretained',training='ownPhysXWMH32/RLactorH8directcost/criticownTD;source324fullstate;noresetAdam',acceptance='RLactual80freshfirstepisodes400controls/firstflightwholefootprint/actualtopmanifold/strict.5s;feedforwardalonecannotclaimlearnedskill',physical_unchanged=True,original_budget=True,network=0,SDK=0,model_reads=0,GO=False))
print(json.dumps(dict(root=str(N),prepared=True,RL=True,onlineMPC=False,GO=False)))
