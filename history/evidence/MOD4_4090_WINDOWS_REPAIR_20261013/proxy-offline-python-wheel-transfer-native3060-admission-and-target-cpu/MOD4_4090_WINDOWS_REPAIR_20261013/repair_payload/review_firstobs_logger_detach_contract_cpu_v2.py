"""Actual RSL5.0.1 order and prepared worker/parent contracts, CPU only."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,inspect,json,py_compile,time,traceback
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from rsl_rl.runners import OnPolicyRunner
from rsl_rl.utils.logger import Logger
from importlib import metadata
import windows4090_training_runtime as runtime
from windows20k_fullstate_binding import H,DONOR_SHA,same
D=Path(__file__).parent;W=D.parents[1]
SOURCE=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
class FakeVec:
 def __init__(self):self.episode_length_buf=torch.zeros(20000,dtype=torch.long);self.max_episode_length=2000;self.calls=0
 def get_observations(self):
  self.calls+=1
  # Intentionally use global RNG for the test. Reordering cannot be hidden by
  # independent private streams; this is not an actual physical observation.
  return torch.rand(20000,3)
def experiment(training,prepared):
 with torch.random.fork_rng(devices=[]):
  torch.manual_seed(20260928);vec=FakeVec()
  if prepared:
   obs=runtime.capture_original_first_observation(vec,training);before=torch.get_rng_state().clone();runtime.install_first_observation_once(vec,obs);used=vec.get_observations();after=torch.get_rng_state().clone();assert torch.equal(before,after)
  else:
   if training:vec.episode_length_buf=torch.randint_like(vec.episode_length_buf,high=int(vec.max_episode_length))
   used=vec.get_observations()
  return vec.episode_length_buf.clone(),used.clone(),torch.get_rng_state().clone(),vec.calls
def main():
 torch.set_num_threads(1);rng=torch.get_rng_state().clone();results=[]
 for training in (True,False):
  old=experiment(training,False);new=experiment(training,True);assert all(torch.equal(a,b) for a,b in zip(old[:3],new[:3])) and old[3]==new[3]==1
  if not training:assert torch.equal(new[0],torch.zeros_like(new[0]))
  results.append(dict(mode='train' if training else 'fullrestore',age_buffer_exact=True,normal_first_observation_exact=True,global_CPU_RNG_after_observation_exact=True,observation_calls=1,normal_age_draw_executed=training,no_extra_draw_inside_firstobs_cache=True))
 assert metadata.version('rsl-rl-lib')=='5.0.1'
 learn=inspect.getsource(OnPolicyRunner.learn);logger=inspect.getsource(Logger.init_logging_writer)
 assert learn.index('torch.randint_like')<learn.index('self.env.get_observations()')<learn.index('self.logger.init_logging_writer()')
 code=(D/'windows4090_training_runtime.py').read_text();worker=(D/'windows4090_repair_worker.py').read_text();parent=(D/'run_windows4090_stage_once.py').read_text();probe=(D/'windows4090_probe_contract.py').read_text()
 assert 'runner.logger.init_logging_writer()' not in code and 'init_at_random_ep_len=False' in code and "if hasattr(runner.logger,'writer')" in code
 assert 'writer.flush();writer.close()' in code and 'log_dir' in logger and 'SummaryWriter(' in logger
 assert worker.index('import torch,tensordict')<worker.index('from isaaclab.app import AppLauncher')
 assert 'actual_new_Windows20k_cfg' in worker and 'Linux_old_SDK_capacity_numerical_equivalence_not_claimed=True' in worker
 assert 'setattr(cfg.sim.physx' not in worker and 'project_tree' not in code
 assert "obs,_,_,_=vec.step(policy(obs))" in worker and 'if args.mode==\'sdk\':obs=vec.get_observations()' in worker
 assert 'obs,_,_,_=vec.step(policy(obs))' in code
 assert "private_rng==private_rng_hashes(env)" in code
 assert 'initialization_not_miscounted_as_PPO=True' in code and 'updates%2==0' in code
 assert 'actual_ground_query_error_m=ground_error' in probe and 'height_error<=1e-6' in probe and 'all_static_D0D7_recipes_exact_to_complete_source=True' in probe
 assert 'not still(exitrow[\'parent\'])' in parent and 'time.sleep(15)' in parent and 'msvcrt.LK_NBLCK' in parent
 # Verify actual Adam parameter references and source IDs using the same MLP
 # classes on CPU. This creates no environment or GPU and changes no donor.
 assert H(SOURCE)==DONOR_SHA;source=torch.load(SOURCE,map_location='cpu',weights_only=False)
 with torch.random.fork_rng(devices=[]):
  obs=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38)),batch_size=[1])
  actor=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar'))
  critic=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'critic',1,[256,128,64],'elu')
  actor.load_state_dict(source['actor_state_dict'],strict=True);critic.load_state_dict(source['critic_state_dict'],strict=True)
  optimizer=torch.optim.Adam(list(actor.parameters())+list(critic.parameters()));optimizer.load_state_dict(source['optimizer_state_dict'])
  fake=SimpleNamespace(alg=SimpleNamespace(actor=actor,critic=critic,optimizer=optimizer));runtime.assert_optimizer_layout(fake,source)
  assert same(optimizer.state_dict(),source['optimizer_state_dict'])
  optimizer.param_groups[0]['params'][0],optimizer.param_groups[0]['params'][1]=optimizer.param_groups[0]['params'][1],optimizer.param_groups[0]['params'][0]
  try:runtime.assert_optimizer_layout(fake,source)
  except AssertionError:negative_order=True
  else:raise AssertionError('wrong actual optimizer parameter binding accepted')
 files=[]
 for p in sorted(D.glob('*.py')):
  py_compile.compile(str(p),doraise=True);files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)))
 for p in sorted(D.glob('*.ps1')):files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),PowerShell_parser_validation_separate=True))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized() and H(SOURCE)==DONOR_SHA
 report=dict(epoch=time.time(),passed_CPU_prepared=True,rsl_version='5.0.1',actual_learn_source_SHA=hashlib.sha256(learn.encode()).hexdigest(),actual_logger_source_SHA=hashlib.sha256(logger.encode()).hexdigest(),normal_firstobs_order_and_RNG_fixtures=results,logger_original_init_not_idempotent=True,new_runtime_uses_only_original_learn_writer_init_once=True,zeroPPO_fullrestore_does_not_initialize_or_stop_logger=True,actual_source_actor_and_critic_parameter_ID_order_CPU_exact=True,wrong_Adam_parameter_reference_fixture_rejected=negative_order,complete_original_d05c_source_unchanged=True,only_new_CPU_prepared_runtime_changed=True,new_backend_capacities_disclosed_not_Linux_equivalence=True,SDK_native_fullrestore_geometry_D0D7_query_reward_command_hardware_receipt_code_prepared_not_GPU_passed=True,actual12restore_offset_full20k_newGPU_physical_probe_and_formal_pending=True,demand_only_task_source_prepared_no_registration_or_launch=True,executable_sources=files,no_GPU_SSH_canonical_write_or_oldonce=True,all_later_reports_ordinary_Git_supplement_pending_root=True)
 p=D/'reports/FIRSTOBS_LOGGER_DETACH_CPU_V2_FINAL_READINESS_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),files=len(files),RNG_fixture=results,actual_Adam_layout=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'reports'/('FIRSTOBS_LOGGER_DETACH_V2_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
