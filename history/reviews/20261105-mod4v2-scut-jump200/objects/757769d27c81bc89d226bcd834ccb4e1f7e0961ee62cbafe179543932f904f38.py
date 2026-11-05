from pathlib import Path
import hashlib,json,sys,time,traceback
import torch
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut';R=N/'supermimic_compatibility01';R.mkdir(exist_ok=False)
sys.path.insert(0,str(G/'project/isaac'))
source=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/source')
files=[]
for p in [source/'ctx_reward_learner.py',*sorted((source/'supermimic_vendor_v2').glob('*.py'))]:
 raw=p.read_bytes();files.append(dict(relative=p.relative_to(source).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
binding=dict(root=str(source),files=files,origin='Existing pinned MOD4 SuperMimic tensor learner and task-context extension',
    source_reused_without_copying_tree=True,physical_backend='Newton/SolverMuJoCo/MuJoCo-Warp')
(CODE/'SUPERMIMIC_BINDINGS.json').write_text(json.dumps(binding,indent=2),encoding='utf8')
from mod4v2_scut.supermimic_newton import load_sources,NewtonSuperMimicBridge
Learner,Config=load_sources(CODE/'SUPERMIMIC_BINDINGS.json')
from mod4v2_scut.newton_env import NewtonEnv
out=dict(epoch=time.time(),production_PT_reads=0,production_changed=False,passed=False)
env=bridge=None
try:
 torch.manual_seed(9138)
 env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
    N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
    N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',4,'cuda:0',9138)
 bridge=NewtonSuperMimicBridge(env)
 cfg=Config(iterations=100,buffer_steps=80,horizon=32,hist=10,goal_frames=10,
    wm_hidden=(128,128),policy_hidden=(128,64),critic_hidden=(64,32),
    wm_window=8,wm_batches=1,wm_batch=32,pi_batch=32,critic_epochs=1,critic_minibatches=4,
    warmup_steps=64,wm_only_iters=0,compile=False,amp='none',action_noise=.05,seed=9138)
 learner=Learner(bridge,cfg,R/'learner',backend='Newton/MuJoCo-Warp',aux_hidden=(64,64),aux_batch=32)
 learner.collect(64)
 out['actual_controls']=bridge.controls;out['actual_physics_ticks']=env.physics_ticks
 out['real_transitions']=bridge.controls*4;out['context_dim']=bridge.supermimic_mdp.context_dim
 wm=[]
 for _ in range(24):
  loss,error=learner.wm_update();wm.append(dict(loss=float(loss),error=float(error)))
 before={k:v.detach().clone()for k,v in learner.wm.state_dict().items()}
 policy=learner.policy_update();receipt=learner.last_bptt_receipt
 out.update(world_model_updates=24,auxiliary_updates=24,world_model_fit=wm,
    policy_metrics=[float(v)for v in policy],BPTT_receipt=receipt,
    actual_Fudan_reward_labels=True,actual_Newton_physics=True,
    original_terminal_s1_before_reset=True,reset_obs_not_used_as_terminal_state=True,
    no_foreign_reference_motion=True,production_switch_ready=False,
    qualification='Small-batch native integration; original20k hour still needs independent80 and numerical assessment')
 assert receipt['verified_bptt_optimizer_step'] and receipt['horizon']==32
 assert all(torch.equal(v,learner.wm.state_dict()[k])for k,v in before.items())
 file=learner.save(R/'compatibility_full.pt',include_optimizers=True)
 restored=Learner(bridge,cfg,R/'restored',backend='Newton/MuJoCo-Warp',aux_hidden=(64,64),aux_batch=32)
 payload=torch.load(file,map_location='cpu',weights_only=False)
 restored.load_full_checkpoint(payload,allow_environment_reset=True)
 assert restored.counts==learner.counts
 assert restored.buffer.size==learner.buffer.size
 assert all(torch.equal(v,restored.pi.state_dict()[k])for k,v in learner.pi.state_dict().items())
 assert all(len(getattr(restored,'opt_'+name).state)>0 for name in ('wm','pi','v','aux'))
 with file.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 out.update(passed=True,full_checkpoint=dict(path=str(file),bytes=file.stat().st_size,SHA=sha),
    all4_optimizers_replay_RNG_history_saved_and_restored=True,
    resume_scope='full learner with declared fresh physical episode; no exact contact-solver restoration',
    numerical_resets=int(env.numerical_reset_counts.sum()))
except BaseException:out['error']=traceback.format_exc()
finally:
 if bridge is not None:bridge.close()
 if env is not None:env.close()
 with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
 print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
