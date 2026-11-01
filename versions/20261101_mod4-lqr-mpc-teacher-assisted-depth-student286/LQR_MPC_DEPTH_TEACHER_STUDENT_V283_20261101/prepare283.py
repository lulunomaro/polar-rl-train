"""Continue interrupted282 in a distinct source tree; preserve every predecessor."""
from pathlib import Path
import ast, hashlib, json, shutil, time

N=Path(__file__).resolve().parent; T=N.parent; W=T.parent
OLD=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V282_20261101'
R=N/'reports'; R.mkdir(exist_ok=True)
S=N/'source'; S.mkdir(exist_ok=False)
shutil.copytree(OLD/'source_v2',S,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

reference=(OLD/'reference282.py').read_text('utf8').replace('Reference282','Reference283')
(S/'reference283.py').write_text(reference,encoding='utf8')
ref=json.loads((OLD/'REFERENCE282_PRODUCER.json').read_bytes())
assert H(OLD/'reference282.npz')==ref['SHA']
shutil.copyfile(OLD/'reference282.npz',N/'reference283.npz')

text=(OLD/'teacher_student282.py').read_text('utf8')
text=text.replace('TeacherStudent282','TeacherStudent283')
text=text.replace("assert 'chain(self.actor.parameters(), self.critic.parameters())' in text",
                  "assert 'chain(self.actor.parameters(), self.critic.parameters())' in text")
text=text.replace("self.initial_WM_quality=None", "self.initial_WM_quality=None\n        self.batch=256")
text=text.replace("    def update(self):\n        wm=self.wm;b=wm.buffer;k=32;B=256",
                  "    def update(self, *, apply_step=True):\n        wm=self.wm;b=wm.buffer;k=32;B=self.batch")
text=text.replace("opt.step();self.Pi_updates+=1", "if apply_step:opt.step();self.Pi_updates+=1")
text=text.replace("cnorm=nn.utils.clip_grad_norm_(self.critic.parameters(),1.);assert torch.isfinite(cnorm);opt.step();self.critic_updates+=1",
                  "cnorm=nn.utils.clip_grad_norm_(self.critic.parameters(),1.);assert torch.isfinite(cnorm)\n        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in self.critic.parameters())\n        if apply_step:opt.step();self.critic_updates+=1")
text=text.replace("return dict(Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,H32=k,batch=B,",
                  "return dict(Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,H32=k,batch=B,optimizer_steps_applied=bool(apply_step),")
text=text.replace("assert diagnostic['combined']>0 and diagnostic['teacher_only']>0",
                  "assert diagnostic['combined']>0 and diagnostic['teacher_only']>0 and diagnostic['reward_only']>0 and diagnostic['terminal_only']>0")
text=text.replace("'ACTUAL282_THREE_OPTIMIZER_IDENTITY_MIGRATION.json'","'ACTUAL283_THREE_OPTIMIZER_IDENTITY_MIGRATION.json'")
# No producer claims from a synthetic admission caller are turned into actual
# simulation evidence. Production records are qualified separately after GO.
(S/'teacher_student283.py').write_text(text,encoding='utf8')

terrain=(OLD/'terrain282.py').read_text('utf8').replace('282','283')
terrain=terrain.replace("def configure(cfg):\n    mixed.configure(cfg);cfg.scene.ground.spawn.func=spawn",
'''class Teacher283Command(mixed.Mixed209Command):
    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        jump=ids[~self._env._mixed209_flat[ids]]
        self.vel_command_b[jump]=torch.tensor([1.4,0.,0.],device=self.device)
        task.height_cmd(self._env)[jump,0]=.135

def configure(cfg):
    mixed.configure(cfg);cfg.commands.twist.class_type=Teacher283Command;cfg.scene.ground.spawn.func=spawn''')
(S/'terrain283.py').write_text(terrain,encoding='utf8')
shutil.copyfile(N/'teacher_task283.py',S/'teacher_task283.py')

package=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package'
runtime=package/'payload/job0/runtime/isaac/mod4'
for name in ('owned_h1_public4_mean_overflow_ppo_v2.py','h1_public4_mean_overflow_loss_v2.py'):
    shutil.copyfile(runtime/name,S/name)
for name in ('jump194_boundary.py','literal_original_methods.py','literal_original_config.py'):
    shutil.copyfile(package/name,S/name)

worker=(OLD/'source_v2/worker282.py').read_text('utf8')
worker=worker.replace('teacher_task282','teacher_task283').replace('teacher_student282','teacher_student283')
worker=worker.replace('Reference282','Reference283').replace('reference282','reference283')
worker=worker.replace('TeacherStudent282','TeacherStudent283').replace('terrain282','terrain283').replace('Teacher282Env','Teacher283Env')
worker=worker.replace('control282','control283').replace('STUDENT282','STUDENT283').replace('STUDENT_UPDATE','STUDENT283_UPDATE')
worker=worker.replace('LQR_MPC_DEPTH_TEACHER_STUDENT282_COMPLETE','LQR_MPC_DEPTH_TEACHER_STUDENT283_COMPLETE')
worker=worker.replace("generation='OWN_LIVE_WM_WARM276_FRESH_EPISODES'","generation='OWN_TEACHER_DEPTH_STUDENT283_FRESH_EPISODES'")
worker=worker.replace('"""Live ownMOD4 WM-only warm: frozen2135 teacher, one fresh WM Adam, original finite owner."""',
    '"""Teacher-assisted depth SuperMimic; restored WM, migrated actor/critic, original finite owner."""')
worker=worker.replace("wm.updates=carrier['world_model']['world_updates'];wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'])",
    "wm.updates=carrier['world_model']['world_updates'];wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'])\n initial_WM_updates=wm.updates")
worker=worker.replace("controls=0;last_saved=0.;first=None;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None",
    "controls=0;last_saved=0.;first=None;student=None;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None")

start=worker.index(' def save(label):'); end=worker.index(' original=real.literal.measured_step',start)
save=''' def save(label):
  global last_saved
  state=dict(kind='LQR_MPC_DEPTH_TEACHER_STUDENT283_COMPLETE',source_carrier_SHA=TASK['model_SHA'],
   teacher_full_PPO_state=ck,teacher_source_SHA=TASK['teacher_SHA'],teacher_saved_iteration=2135,teacher_Adam17_step=42940,
   typed_TEACHER283_task=TASK,original_finite_owner_GO=go,student=learner.checkpoint(),world_model=wm.checkpoint(),
   actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,
   actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,
   actual_new_PPO_updates=0,actual_new_STD_updates=0,learning_scope='teacher_assisted_depth_SuperMimic',
   target_DR_state=full_DR(),mixed_ground_JUMP_state=command_memory(),original_jump_reward_memory=reward_memory(),
   current_measured_state224=copied(state_now()),current_static31=copied(xi),current_episodes=copied(episodes),
   current_episode_steps=copied(epstep),previous_clipped_action=copied(previous_action),reference=TASK['reference'],
   teacher_target_layout=copied(real.target283),controls=controls,own_transitions=controls*80,
   physics_callbacks=controls*8,feedback_samples=controls*2,full_physics_resume_claimed=False,
   complete_three_optimizer_conversion=True,actual_Pi_runtime_qualified=learner.Pi_updates>0,
   replay_saved=False,replay_resume_scope='fresh physical and64-control own replay on resume; full optimizer/norm/RNG/DR/reward state retained')
  finite(state);dest=OUT/(label+'.pt');temp=dest.with_suffix('.pt.partial');torch.save(state,temp);os.replace(temp,dest)
  with dest.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  wmsteps=[int(v['step'])for v in wm.optimizer.state.values()];assert min(wmsteps)==max(wmsteps)==wm.updates
  pi_steps=[int(v['step'])for p,v in learner.optimizers['actor'].state.items() if p.requires_grad]
  critic_steps=[int(v['step'])for v in learner.optimizers['critic'].state.values()]
  assert min(pi_steps)==max(pi_steps)==42940+learner.Pi_updates
  assert min(critic_steps)==max(critic_steps)==42940+learner.critic_updates
  epoch=time.time()
  row=dict(epoch=epoch,save_epoch=epoch,path=str(dest),bytes=dest.stat().st_size,SHA=sha,
   Pi_updates=learner.Pi_updates,critic_updates=learner.critic_updates,actual_new_WM_updates=wm.updates-initial_WM_updates,
   total_WM_updates=wm.updates,WM_Adam_step_min=min(wmsteps),WM_Adam_step_max=max(wmsteps),
   actor_Adam_step_min=min(pi_steps),actor_Adam_step_max=max(pi_steps),critic_Adam_step_min=min(critic_steps),critic_Adam_step_max=max(critic_steps),
   controls=controls,own_transitions=controls*80,teacher_source_SHA=TASK['teacher_SHA'],teacher_iteration=2135,
   teacher_Adam_step=42940,full_student_WM_tree_finite=True,complete_student_WM_three_optimizers=True,
   frozen_teacher_fullstate_preserved=True,full_Adam_norm_RNG_DR_reward_memory_saved=True,replay_saved=False)
  put('latest_complete.json',row);last_saved=time.time();return row
'''
worker=worker[:start]+save+worker[end:]
worker=worker.replace("'NATIVE24_WM_WARM276_ACTUAL.json'","'NATIVE24_TEACHER283_ACTUAL.json'")
worker=worker.replace('WM_updates=0,teacher_updates=0,original_literal_calls=24',
    'new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,Pi_updates=learner.Pi_updates,critic_updates=learner.critic_updates,original_literal_calls=24')
worker=worker.replace("native_proof['WM_updates']==0 and native_proof['teacher_updates']==0",
    "native_proof['new_WM_updates']==0 and native_proof['Pi_updates']==0 and native_proof['critic_updates']==0")
worker=worker.replace("put('LATEST_STUDENT283.json'","put('LATEST_STUDENT283.json'")
start=worker.index('    receipt=dict(epoch=time.time(),kind=FIRST_KIND'); end=worker.index('   elif time.time()-last_saved',start)
first='''    native=json.loads((OUT/'NATIVE24_TEACHER283_ACTUAL.json').read_bytes())
    receipt=dict(epoch=time.time(),kind=FIRST_KIND,passed=True,source_SHA=TASK['model_SHA'],run_id=TASK['run_id'],
     actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,
     actual_new_PPO_updates=0,actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,
     actual_new_STD_updates=0,actual_frozen_teacher_updates=0,num_envs=80,controls=controls,
     new_completed_controls=controls,new_environment_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,
     student=student,first_complete=first,diagnostic=diagnostic,original_JUMP_reward_unchanged=True,
     complete_three_optimizer_conversion=True,teacher_frozen=True,student_skill_not_yet_evaluated=True,
     actual_resource_admission_SHA=TASK['actual_resource_admission_SHA'],
     native24_before_first_WM_step_passed=bool(native['passed'] and native['controls']==24 and native['physics_callbacks']==192
      and native['feedback_samples']==48 and native['new_WM_updates']==native['Pi_updates']==native['critic_updates']==0))
    validate_first(receipt,TASK,go);put('FIRST_ACTUAL_TEACHER_DEPTH_STUDENT283_UPDATE.json',receipt)
'''
worker=worker[:start]+first+worker[end:]
worker=worker.replace("actual_new_WM_updates=wm.updates,actual_new_PPO_updates=0,controls=controls,own_transitions",
 "actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,actual_new_PPO_updates=0,controls=controls,own_transitions")
worker=worker.replace('from teacher_task283 import FINAL_KIND','from teacher_task283 import FINAL_KIND,validate_final')
worker=worker.replace('kind=FINAL_KIND,actual_new_WM_updates=wm.updates,controls=',
    'kind=FINAL_KIND,actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,controls=')
worker=worker.replace("actual_Pi_Critic_STD_updates=learner.Pi_updates,student=student);put('FINAL.json',receipt)",
    "student=student);validate_final(receipt,TASK,go);put('FINAL.json',receipt)")
worker=worker.replace('except BaseException:\n put(\'ORIGINAL_ERROR.json\'',
'''except BaseException:
 if 'learner' in globals() and 'save' in globals():
  try:save('model_error_complete')
  except BaseException:put('ERROR_SAVE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 put('ORIGINAL_ERROR.json' ''')
# Existing snapshot labels remain evidence of their276 origin; correct the
# substantive fields that must describe the new restored/migrated learner.
worker=worker.replace('teacher_optimizer_constructed=False,new_optimizer_count=3',
    'source_optimizer_identity_restored_for_migration=True,new_optimizer_count=3')
worker=worker.replace('fresh_physics_DR_queues_and_WM_not_exact_PhysX_resume=True',
    'inherited_WM_updates=4719,fresh_physics_DR_queues_replay_not_exact_PhysX_resume=True')
(S/'worker283.py').write_text(worker,encoding='utf8')
for p in S.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))

control=N/'control283';control.mkdir(exist_ok=False)
parent=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101/control276'
for p in parent.glob('*.py'):
    if p.name=='wm_task275.py':continue
    text=p.read_text('utf8').replace('wm_task275','teacher_task283')
    text=text.replace('Linux_OWN_DEPTH_WM_ONLY_WARM276_','Linux_LQR_MPC_DEPTH_STUDENT283_')
    text=text.replace('human_requested_depth_SuperMimic_WM_only_warm276=True','human_requested_LQR_MPC_depth_SuperMimic_student283=True')
    text=text.replace('go["WM_ONLY"] and go["FROZEN_TEACHER"]','go["teacher_student283"] and go["FROZEN_TEACHER"]')
    text=text.replace('"TASK276.json"','"TASK283.json"')
    text=text.replace('final.get("actual_Pi_Critic_STD_updates")==0',
        'final.get("actual_new_Pi_updates",0)>0 and final.get("actual_new_critic_updates",0)>0')
    ast.parse(text);(control/p.name).write_text(text,encoding='utf8')
shutil.copyfile(N/'teacher_task283.py',control/'teacher_task283.py')
row=dict(epoch=time.time(),trial_id='teacher283-independent-source-repair',passed_AST=True,
 predecessor_source=str(OLD),predecessor_false_preserved=True,predecessor_unexecuted_v2_preserved=True,
 new_source=str(S),files=len(list(S.rglob('*.py'))),reference=dict(ref,path=str(N/'reference283.npz')),
 repairs=['use corrected282 root state loss rather than its stale assembly copy',
 'preserve full inherited WM and explicit actual source/target optimizer identity',
 'correct inherited WM-only counter/save/Task/node receipts for real student learning',
 'new first/final protocol binds full three optimizers and original3600save/3900exit',
 'resample declared forward commands consistently at every teacher episode',
 'no-step CPU admission uses the production H32 objective; no fake source success'],
 original_reward_and_276_source_untouched=True,new_training=False)
(R/'SOURCE283_ASSEMBLY.json').write_text(json.dumps(row,indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,source_files=row['files'],reference_SHA=ref['SHA'])))
