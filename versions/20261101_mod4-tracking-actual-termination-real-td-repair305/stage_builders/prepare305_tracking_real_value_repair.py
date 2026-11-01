"""Independent305: restore final300, align termination, ground critic in actual returns."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shutil,time
T=Path(__file__).resolve().parent;O=T/'REFERENCE_TRACKING_BPTT_V300_20261101';N=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101';N.mkdir(exist_ok=False);R=N/'reports';R.mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode());ast.parse(s,filename=str(p))
def rename(s):
 keep=[]
 def h(m):keep.append(m.group());return '@HASH'+str(len(keep)-1)+'@'
 s=re.sub(r'\b[0-9a-f]{64}\b',h,s);s=re.sub(r'(?<=[A-Za-z_])300(?!\d)','305',s)
 for i,v in enumerate(keep):s=s.replace('@HASH'+str(i)+'@',v)
 return s
shutil.copytree(O/'source',N/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in('worker300.py','tracking_wm300.py','tracking_reference300.py','terrain300.py','tracking_task300.py','teacher_task300.py','complete_save300.py'):
 write(N/'source'/rename(name),rename((O/'source'/name).read_text('utf8')))
for p in (O/'control300').glob('*.py'):write(N/'control305'/rename(p.name),rename(p.read_text('utf8')))
shutil.copyfile(O/'reference300.npz',N/'reference305.npz')
for name in('launch300_reference_tracking_once.py','collect300_status_readonly.py','teacher_task300.py','tracking_task300.py'):
 write(N/rename(name),rename((O/name).read_text('utf8')))

# Keep the entire actor/critic/WM and all Adam moments from final300.
s=rename((O/'source/tracking_learner300.py').read_text('utf8'))
start=s.index('        nets,opts,identity=migrate(');end=s.index('        robot=env.scene',start)
s=s[:start]+'''        self.actor=model(ACTOR_DIM,True,str(wm.device));self.critic=model(CRITIC_DIM,False,str(wm.device))
        saved=carrier['student'];self.actor.load_state_dict(saved['actor_state_dict']);self.critic.load_state_dict(saved['critic_state_dict'])
        self.actor.distribution.std_param.requires_grad_(False)
        self.actor_optimizer=torch.optim.Adam(self.actor.parameters(),lr=1e-4)
        self.critic_optimizer=torch.optim.Adam(self.critic.parameters(),lr=1e-4)
        self.actor_optimizer.load_state_dict(saved['actor_optimizer']);self.critic_optimizer.load_state_dict(saved['critic_optimizer'])
        self.actor_offset=42940+carrier['actual_new_Pi_updates'];self.critic_offset=carrier['actual_new_critic_updates']
        assert self.actor_offset==45533 and self.critic_offset==2593
        for opt in(self.actor_optimizer,self.critic_optimizer):
            for group in opt.param_groups:group['lr']=1e-4
        self.optimizers={'actor':self.actor_optimizer,'critic':self.critic_optimizer};self.networks={'actor':self.actor,'critic':self.critic}
        from copy import deepcopy
        self.target_critic=deepcopy(self.critic).eval()
        for p in self.target_critic.parameters():p.requires_grad_(False)
        self.identity=dict(parent=saved['identity'],targets=dict(actor=binding_for({'actor':self.actor},self.actor_optimizer,'ACTUAL_RESTORED300_ACTOR_FULL_ADAM'),critic=binding_for({'critic':self.critic},self.critic_optimizer,'ACTUAL_RESTORED300_CRITIC_FULL_ADAM')),actor_Adam_offset=self.actor_offset,critic_Adam_offset=self.critic_offset)
        self.Pi_updates=self.critic_updates=self.proposals=0;self.initial_WM_updates=wm.updates;self.batch=256
''' +s[end:]
s=s.replace("put('ACTUAL305_TRACKING_THREE_OPTIMIZER_IDENTITIES.json',dict(passed=True,**self.identity,actor_dim=ACTOR_DIM,critic_dim=CRITIC_DIM,old_critic_preserved_in_source=True))", "put('ACTUAL305_TRACKING_THREE_OPTIMIZER_IDENTITIES.json',dict(passed=True,**self.identity,actor_dim=ACTOR_DIM,critic_dim=CRITIC_DIM,restored300_all_three_optimizers=True))")
s=s.replace("('policy',(35,),torch.float32),('critic',(38,),torch.float32),('phase',(),torch.int64)", "('policy',(35,),torch.float32),('critic',(38,),torch.float32),('phase',(),torch.int64),('next_critic',(38,),torch.float32),('next_depth',(9,),torch.float32)")
s=s.replace('def add_metadata(self,slot,policy,critic,phase):','def add_metadata(self,slot,policy,critic,phase,next_critic,next_depth):').replace("dict(policy=policy,critic=critic,phase=phase).items()", "dict(policy=policy,critic=critic,phase=phase,next_critic=next_critic,next_depth=next_depth).items()")
s=s.replace('        alive=state[0].new_ones', "        actual_start=tuple(x.detach().clone()for x in state)\n        alive=state[0].new_ones")
s=s.replace('for module in(wm.model,self.critic):','for module in(wm.model,self.critic,self.target_critic):',1)
s=s.replace("survival=torch.sigmoid((following[1][:,2,2]-.45)*20.)", "survival=matched_survival305(following)")
s=s.replace("forward(self.critic,cx).squeeze(-1)","forward(self.target_critic,cx).squeeze(-1).clamp(0.,100.)")
start=s.index('        with torch.no_grad():\n            target=forward(self.critic,cx.detach())');end=s.index('        assert all(torch.isfinite(p).all()',start)
s=s[:start]+'''        # One-step TD on actual own transitions, never imagined reward labels.
        with torch.no_grad():
            label_goal=self.reference.goals(actual_start,meta['phase'],envs,self.env.target305)
            actual_cx=torch.cat((meta['critic'],b.data['xi'][rows,envs,31:]/state[0].new_tensor(DEPTH_SCALE),label_goal),-1)
            next_state=wm.measured_layout.unpack(b.data['s1'][rows,envs])
            next_goal=self.reference.goals(next_state,meta['phase']+1,envs,self.env.target305)
            next_cx=torch.cat((meta['next_critic'],meta['next_depth']/state[0].new_tensor(DEPTH_SCALE),next_goal),-1)
            actual_reward=b.data['r'][rows,envs].reshape(-1)
            actual_done=b.data['done'][rows,envs].reshape(-1).bool()
            next_value=forward(self.target_critic,next_cx).squeeze(-1).clamp(0.,100.)
            td_target=actual_reward+.99*(~actual_done).float()*next_value
        prediction=forward(self.critic,actual_cx).squeeze(-1)
        value_loss=torch.nn.functional.smooth_l1_loss(prediction,td_target)
        self.critic_optimizer.zero_grad(set_to_none=True);value_loss.backward();cnorm=nn.utils.clip_grad_norm_(self.critic.parameters(),1.)
        assert torch.isfinite(cnorm)
        if apply_step:
            self.critic_optimizer.step();self.critic_updates+=1
            with torch.no_grad():
                for target_p,p in zip(self.target_critic.parameters(),self.critic.parameters()):target_p.lerp_(p,.01)
''' +s[end:]
s=s.replace("tracking_components=component_sums,", "tracking_components=component_sums,critic_target_source='actual own transition r/done/nextcritic/currentdepth, EMA.01target',actual_terminal_fraction=float(actual_done.float().mean()),actual_TD_reward_mean=float(actual_reward.mean()),actual_TD_target_mean=float(td_target.mean()),matched_orientation_angle=.75,bootstrap_value_clamp=[0,100],")
s=s.replace("inherited_WM_updates=self.initial_WM_updates,", "target_critic_state_dict=self.target_critic.state_dict(),critic_training='actual TD/Huber; sameexptrackingreward;EMA.01target',actor_Adam_offset=self.actor_offset,critic_Adam_offset=self.critic_offset,inherited_WM_updates=self.initial_WM_updates,")
s=s.replace('from tracking_reference305 import GOAL_DIM,tracking_cost305','from tracking_reference305 import GOAL_DIM,tracking_cost305\nfrom tracking_survival305 import matched_survival305')
write(N/'source/tracking_learner305.py',s)
helper='''"""Soft approximation of actual .75rad orientation termination, no plant change."""
import math,torch
def matched_survival305(state):
    return torch.sigmoid((state[1][...,2,2]-math.cos(.75))/.025)
'''
write(N/'source/tracking_survival305.py',helper)

# Worker resumes new source and original full state. Counts are window-local;
# optimizer step offsets retain history exactly.
p=N/'source/worker305.py';s=p.read_text('utf8')
s=s.replace("ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE' and ck['total_WM_updates']==7087", "ck['kind']=='REFERENCE_TRACKING_BPTT300_COMPLETE' and ck['total_WM_updates']==9712 and ck['actual_new_Pi_updates']==2593")
s=s.replace('assert wm.updates==7087 and all(int(v[\'step\'])==7087', "assert wm.updates==9712 and all(int(v['step'])==9712")
s=s.replace('inherited_WM_updates=7087','inherited_WM_updates=9712').replace('inherited_world_updates=7087','inherited_world_updates=9712')
s=s.replace("critic_meta=complete_adam_steps305(learner.optimizers['critic'],learner.critic_updates)","critic_meta=complete_adam_steps305(learner.optimizers['critic'],learner.critic_offset+learner.critic_updates)")
s=s.replace('42940+learner.Pi_updates','learner.actor_offset+learner.Pi_updates')
s=s.replace("learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_phase)", "learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_phase,obs['critic'],pending['depth']['features'])")
s=s.replace('assert wm.updates>7087','assert wm.updates>9712')
s=s.replace("policy_rollback_source='frozen2135 actor Adam plus59zero goal columns; NEW tracking critic Adam0; old all preserved'", "policy_rollback_source='restore exactfinal300 actor103critic106/allthreeAdam/STD/WM9712/norm/RNG; repair survival+actualTD only'")
# Native first32 real controls yield a same-start one-step WM error report.
needle="  if wm.ready_for_update():\n   diagnostic=wm.update()"
replacement='''  if wm.ready_for_update():
   if controls==64:
    with torch.no_grad():
     batch=wm.sample();before_rng=wm.generator.get_state().clone()
     loss,predicted,_=wm.rollout_loss(batch)
     actual=wm.measured_layout.unpack(batch['s1']);mask=batch['mask'].bool()
     poserr=torch.linalg.vector_norm(predicted[0]-actual[0],dim=-1)
     tilt_error=(predicted[1][...,2,2]-actual[1][...,2,2]).abs()
     put('ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json',dict(epoch=time.time(),passed=True,source='actual own contiguous transitions, fixed startobservedanchor; mask before episode reset',sample_count=int(mask.sum()),H32_position_RMSE_m=float(torch.sqrt(poserr[mask].square().mean())),H32_Rzz_MAE=float(tilt_error[mask].mean()),one_step_position_RMSE_m=float(torch.sqrt(poserr[:,0].square().mean())),one_step_Rzz_MAE=float(tilt_error[:,0].mean()),prediction_uses_no_future_real_depth=True,source_WM_updates=wm.updates,loss=float(loss)))
   diagnostic=wm.update()'''
assert needle in s;s=s.replace(needle,replacement)
write(p,s)

# Protocol source SHA and offsets bind this exact300final.
proof=json.loads((O/'reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());oldsha='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d'
for p in(N/'teacher_task305.py',N/'tracking_task305.py',N/'source/teacher_task305.py',N/'source/tracking_task305.py',N/'control305/teacher_task305.py'):
 s=p.read_text('utf8').replace(oldsha,proof['SHA']).replace('model_bytes=32407215','model_bytes=32593725').replace('source_WM_updates=7087','source_WM_updates=9712').replace('source_actor_Adam_step=42940','source_actor_Adam_step=45533').replace('new_tracking_critic_Adam_step=0','new_tracking_critic_Adam_step=2593').replace('==7087+','==9712+').replace('==42940+pi','==45533+pi').replace("s['critic_Adam_step_max']==pi", "s['critic_Adam_step_max']==2593+pi")
 write(p,s)

p=N/'launch305_reference_tracking_once.py';s=p.read_text('utf8')
start=s.index('    oldfinal=');end=s.index('    a=argparse.ArgumentParser()',start)
s=s[:start]+'''    closed=read(T/'REFERENCE_TRACKING_BPTT_V300_20261101/reports/ROOT300_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');assert closed['owner_closed']['canonical_None']and closed['owner_closed']['shared_locks_free']
    finalresult=read(T/'REFERENCE_TRACKING_BPTT_V300_20261101/reports/POSTROUND300_REPLAY_EVAL_DECISION.json');assert finalresult['status']=='COMPLETE_SAVE_REPLAY_EVAL_DECISION'
''' +s[end:]
start=s.index('    phasecheck=');end=s.index("    pattern=",start)
s=s[:start]+'''    check=read(R/'CPU305_MATCHED_SURVIVAL_REAL_TD_AND_RESUME_NO_STEP.json');assert check['passed']and check['model_reads']==1 and check['optimizer_steps']==0
    final=read(T/'REFERENCE_TRACKING_BPTT_V300_20261101/reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==9712
''' +s[end:]
s=s.replace("pattern='", "pattern='collect300_|launch300_|run303_eval|postround303_finalize|",1)
s=s.replace("'ACTUAL305_LIVE_H32_REWARD", "'ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json','ACTUAL305_LIVE_H32_REWARD")
write(p,s)
# Snapshot status caller must see all knowncontrollers, and ownlocaltimer is done.
p=N/'collect305_status_readonly.py';s=p.read_text('utf8').replace("patterns='", "patterns='collect300_|launch300_|run303_eval|postround303_finalize|",1);write(p,s)
task=json.loads((O/'TASK300_FROZEN.json').read_bytes())
for k in('kind','generation'):task[k]=rename(task[k])
nonce=str(time.time_ns());task.update(run_id='REFERENCE_TRACKING305_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING305_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING305_'+nonce+'/owner72',worker_SHA=H(N/'source/worker305.py'),source_SHA=proof['SHA'],model_SHA=proof['SHA'],source_bytes=proof['bytes'],model_bytes=proof['bytes'],model_path=json.loads((O/'reports/ROOT300_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())['roles']['jump_72']['formal']['path'],source_WM_updates=9712,window_start_world_updates=9712,source_actor_Adam_step=45533,new_tracking_critic_Adam_step=2593,carrier_CPU_receipt_SHA=H(O/'reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),source_CPU_report_SHA=H(O/'reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),new_tracking_critic=False,source_cpu_reuse='actual300finalfullCPU;305newresume/survival/realTDsyntheticH32no-step once;livepairedH32beforefirstPi',predecessor_actual='300complete/eval3030of80cross66orientation;304actualreplay+CPUdiagnosis; continue300state with explicit termination/criticfix',reward_definition='sameexp(-trackingcost/5); weightsreferenceunchanged; actual.75radterminationmatched forimagination; criticactualTDwithEMAtarget',critic_target_source='actualowntransitiontrackingreward/done/nextcritic/currentdepth; noimaginedrewardcriticlabels',human_authorization='2026-11-01 newtrackingstart and continueclose thenrepair',resume_scope='exactactorcriticSTDthreeoptimizers/norm/RNGfrom300;freshphysicalDRqueue/replay/episode',source_iteration=2135,source_Adam_step=45533)
task['reference']['path']='reference305.npz'
put(N/'TASK305_FROZEN.json',task)
put(R/'SOURCE305_PLANNED_REPAIR_AND_EVIDENCE.json',dict(epoch=time.time(),passed=True,source300_SHA=proof['SHA'],sourceWM=9712,sourcePi=2593,sourcecritic=2593,sourceactorAdam45533=True,sourcecriticAdam2593=True,softsurvivalactualangle=.75,oldsoftthreshold=.45,actualcosangle=0.7316888688738209,critic_realTD=True,EMA=.01,trackingcostreferenceweightsunchanged=True,physicalbudgetunchanged=True,original300preserved=True,new_model_training_GO=0))
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
spec=importlib.util.spec_from_file_location('p305',N/'teacher_task305.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
print(json.dumps(dict(passed=True,root=str(N),run_id=task['run_id'],source_SHA=proof['SHA'],sourceWM=9712,freeze_pending_CPU=True)))
