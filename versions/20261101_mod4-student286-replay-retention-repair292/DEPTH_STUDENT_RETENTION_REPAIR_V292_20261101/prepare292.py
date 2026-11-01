"""Independent repair; rollback policy only, inherit latest complete own WM."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V286_20261101';R=N/'reports';R.mkdir(exist_ok=True)
S=N/'source';shutil.copytree(O/'source',S,ignore=shutil.ignore_patterns('__pycache__'))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_bytes(s.encode('utf8'));ast.parse(s,filename=str(p))
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)

shutil.copyfile(N/'bounded_actor292.py',S/'bounded_actor292.py')
text=(S/'teacher_student286.py').read_text('utf8').replace('286','292')
text=replace(text,'from jump194_boundary import LiteralJump194','from jump194_boundary import LiteralJump194\nfrom bounded_actor292 import bounded_actor_step')
text=replace(text,'self.reference=reference;self.Pi_updates=self.critic_updates=0', '''self.retention_actor=model(35,True,str(wm.device))
        self.retention_actor.load_state_dict(carrier['teacher_full_PPO_state']['actor_state_dict'],strict=True)
        for parameter in self.retention_actor.parameters():parameter.requires_grad_(False)
        for group in self.optimizers['actor'].param_groups:group['lr']=1e-5
        self.proposals=0
        self.reference=reference;self.Pi_updates=self.critic_updates=0''')
text=replace(text,"        if not len(candidates):return None", """        ground_candidates=self.env._mixed209_flat[None].expand(len(slots),-1).nonzero()
        if not len(candidates) or not len(ground_candidates):return None
        selected_ground=ground_candidates[torch.randint(len(ground_candidates),(128,),device=wm.device,generator=wm.generator)]
        grow=slots[selected_ground[:,0]];genv=selected_ground[:,1]
        ground_policy=self.saved['policy'][grow,genv].detach()
        ground_depth=b.data['xi'][grow,genv,31:].detach()/b.data['xi'].new_tensor(DEPTH_SCALE)
        ground_obs=torch.cat((ground_policy,ground_depth),-1)
        with torch.no_grad():ground_targets=forward(self.retention_actor,ground_policy)
        ground_loss=(forward(self.actor,ground_obs)-ground_targets).square().mean()""")
text=replace(text,'                action=forward(self.actor,obs).clamp(-6,6)', '''                raw_action=forward(self.actor,obs)
                if i==0:
                    trust_obs=torch.cat((obs.detach(),ground_obs),0)
                    overflow_loss=.001*torch.relu(raw_action.abs()-6.).square().mean()
                action=raw_action.clamp(-6,6)''')
text=replace(text,'loss=reward_loss+terminal_loss+coefficient*teacher_loss','loss=reward_loss+terminal_loss+coefficient*teacher_loss+ground_loss+overflow_loss')
text=replace(text,'            if apply_step:opt.step();self.Pi_updates+=1', '''            step=bounded_actor_step(self.actor,opt,lambda x:forward(self.actor,x),trust_obs,ground_obs,ground_targets,apply_step=apply_step)
            if apply_step:
                self.proposals+=1
                self.put('LATEST_ACTOR292_CONSTRAINT.json',dict(proposal=self.proposals,**step))
                if step['applied']:self.Pi_updates+=1
                else:self.put('REJECTED_ACTOR292_PROPOSAL_'+str(self.proposals)+'.json',dict(proposal=self.proposals,**step))''')
text=replace(text,'        # SuperMimic terminal critic target uses only unchanged Fudan rewards;', "        if apply_step and not step['applied']:return None\n        # SuperMimic terminal critic target uses only unchanged Fudan rewards;")
text=replace(text,'original_Fudan_reward_unchanged=True,teacher_actions_cloned=False)', '''original_Fudan_reward_unchanged=True,teacher_actions_cloned=False,
            old_policy_ground_distillation=True,ground_retention_loss=float(ground_loss.detach()),
            separate_action_overflow_loss=float(overflow_loss.detach()),actor_step_constraint=step,
            actor_learning_rate=1e-5,critic_learning_rate=1e-4)''')
text=replace(text,"inherited_WM_updates=self.initial_WM_updates,teacher_coefficient=", "inherited_WM_updates=self.initial_WM_updates,retention_actor_source='frozen2135',actor_proposals=self.proposals,actor_constraint_radius=.05,ground_retention_radius=.5,teacher_coefficient=")
write(S/'teacher_student292.py',text)

text=(O/'source/worker286.py').read_text('utf8').replace('286','292')
text=replace(text,"ck['kind']=='OWN_DEPTH_WM_ONLY_WARM276_COMPLETE' and ck['actual_new_WM_updates']==4719", "ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE' and ck['total_WM_updates']==7087")
text=text.replace('wm.updates==4719','wm.updates==7087').replace("int(v['step'])==4719","int(v['step'])==7087").replace('inherited_WM_updates=4719','inherited_WM_updates=7087').replace('wm.updates>4719','wm.updates>7087')
text=replace(text,"real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)", "real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)\n assert int(torch.count_nonzero(tensor(robot.data.default_joint_pos)))==int(torch.count_nonzero(tensor(robot.data.default_joint_vel)))==0")
# New inherited world state is restored; failed final286 policy is preserved in source carrier only.
text=replace(text,"replay_saved=False,replay_resume_scope='fresh physical and64-control own replay on resume; full optimizer/norm/RNG/DR/reward state retained')", "replay_saved=False,policy_rollback_source='frozen2135 full17Adam; failed student286 preserved in source carrier',failed_student_source_SHA=TASK['model_SHA'],inherited_world_updates=7087,replay_resume_scope='fresh physical and64-control own replay on resume; full optimizer/norm/RNG/DR/reward state retained')")
write(S/'worker292.py',text)
text=(O/'source/terrain286.py').read_text('utf8').replace('286','292').replace('np.random.default_rng(292)','np.random.default_rng(286)');write(S/'terrain292.py',text)
write(S/'reference292.py',(O/'source/reference286.py').read_text('utf8').replace('286','292'))
shutil.copyfile(O/'reference286.npz',N/'reference292.npz')

protocol=(O/'teacher_task286.py').read_text('utf8').replace('286','292').replace('cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b','4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d').replace('31985705','32407215').replace('4719','7087')
write(N/'teacher_task292.py',protocol);write(S/'teacher_task292.py',protocol)
C=N/'control292';C.mkdir()
for p in (O/'control286').glob('*.py'):
    name=p.name.replace('286','292');write(C/name,protocol if p.name=='teacher_task286.py' else p.read_text('utf8').replace('286','292'))

task=json.loads((O/'TASK286_FROZEN.json').read_bytes())
run='DEPTH_STUDENT_RETENTION292_'+str(time.time_ns());base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
task.update(kind='LQR_MPC_REFERENCE_DEPTH_SUPERMIMIC_400N50_V292',source_SHA='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d',model_SHA='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d',source_bytes=32407215,model_bytes=32407215,
 source_WM_updates=7087,window_start_world_updates=7087,source_CPU_report_SHA=H(N/'bounded_actor292.py'),
 carrier_CPU_receipt_SHA=H(O/'reports/ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
 model_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_LQR_MPC_DEPTH_STUDENT286_1793528911807459700/student72/production/model_final_complete.pt',
 run_id=run,job_root=base+'/student72',owner_root=base+'/owner72',worker_SHA=H(S/'worker292.py'),
 WM_ONLY=False,Pi_updates_allowed=True,critic_updates_allowed=True,STD_updates_allowed=False,freeze_actor_critic_STD_full17Adam=False,freeze_original_teacher_full17Adam=True,
 complete_three_optimizer_conversion=True,convert_actor44_critic47=True,new_WM_architecture_fresh=False,new_WM_Adam=False,
 actual_Pi_Critic_teacher_updates='Pi and critic allowed; teacher frozen',actual_H1_step270_scope_admitted=True,actual_Pi_runtime_admitted='Required actual H32 before firststep',
 terrain_scheme='teacher270 single platform72 plus8ground; same layoutseed286',terrain_levels=None,no_270mm_extension=False,training_layout_seed=286,
 source_cpu_reuse='final286 whole600CPU and original284 exact frozen2135 migration reused; bounded actor CPU source test and actual current H32 required',
 policy_rollback='Original2135 actor/critic/full17Adam partition from final286 carrier; final286 student not overwritten',student_optimizer_LR=None,actor_LR=1e-5,critic_LR=1e-4,
 old_policy_ground_retention_coefficient=1.,separate_action_overflow_coefficient=.001,actor_observed_step_radius=.05,ground_reference_action_radius=.5,
 budget='existing sole canonical remaining funds, original3900/save3600/exit300, no grant/extension',human_authorization='2026-11-01 replay then evaluate and decide continuation; every round',
 generation='FROZEN_BEFORE_GO_RETENTION292',reference=dict(path='reference292.npz',bytes=128231,SHA='d5bb68fdbe098c3fd3fa2bcba9e0f5121fae44dc43c9e9c30a2080b73a811650'))
task['run_id']=task['run_id'].replace('DEPTH_STUDENT_RETENTION292_','LQR_MPC_DEPTH_STUDENT292_')
(N/'TASK292_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
text=(O/'launch286_original_teacher_student_once.py').read_text('utf8').replace('286','292')
text=replace(text,"cpu=read(T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V283_20261101/reports/CPU284_ACTUAL_CARRIER_MIGRATION_AND_H32_NO_STEP.json');assert cpu['passed'] and cpu['optimizer_steps']==0", "cpu=read(R/'CPU292_BOUNDED_UPDATE_SOURCE_TEST.json');assert cpu['passed'] and cpu['real_model_reads']==0\n    final=read(T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V286_20261101/reports/ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed'] and final['total_WM_updates']==7087")
text=text.replace("CPU_report_scope='actual carrier identity + synthetic H32, no actual world accuracy claim'", "CPU_report_scope='existing final286 full-tree +284 original migration reused; new bounded source test; live H32 before step'")
text=text.replace("pattern='launch292_|", "pattern='run291_eval|run290_eval|run289_eval|run288_eval|launch286_|collect286_|launch292_|")
write(N/'launch292_original_teacher_student_once.py',text)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
(R/'SOURCE292_REPAIR_DECISION.json').write_text(json.dumps(dict(epoch=time.time(),decision='rollback actor/critic to frozen2135 and retain latest7087WM, repair shared-policy ground retention and constrain measured-observation action drift',original286='0/72strict;0/8ground;80orientation,max.28s',counterfactual291='0/72strict,3/8ground completed8s, source better but not graduated',not_a_reward_change=True,old_sources_preserved=True,default_joint_claim_correction='Actual291 all default q and dq zero; earlier suggested ABI error not causal. No claimed functional default-angle fix.',new_source_bounded_step=.05,ground_retention=1.,actorLR=1e-5,criticLR=1e-4,physical='unchanged400N50Hz/fullDR/TGS32-4/closure10mm',new_budget_grant=False,failed_student_final_preserved=True),indent=2),encoding='utf8')
print(json.dumps(dict(passed_AST=True,run_id=task['run_id'],worker_SHA=task['worker_SHA'])))
