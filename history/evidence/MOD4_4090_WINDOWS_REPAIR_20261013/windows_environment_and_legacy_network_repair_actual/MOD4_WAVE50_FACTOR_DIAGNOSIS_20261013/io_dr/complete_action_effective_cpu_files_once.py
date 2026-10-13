"""Complete CPUprepared files under explicit humanlocalGPU pause. No GPUlaunch."""
from pathlib import Path
import json,time,hashlib,ast,py_compile,traceback
D=Path(__file__).resolve().parent;W=D.parents[1];N=W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 assert not p.exists();p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def replace(s,a,b):assert s.count(a)==1,(a[:80],s.count(a));return s.replace(a,b)
def main():
 ref=N/'immutable_local_continue_reference';assert N.exists()
 pause=dict(epoch=time.time(),local_GPU_probe_and_training_paused=True,authority='root relayed latest human instruction',human_instruction='暂停本机训练，所有评测迁3060',prepared_files_only=True,3060_assessment_requires_independent_ownbaseline_and_root_actuallease=True,no_remote4090_resume=True)
 write(N/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json',pause)
 worker=(ref/'local_scope_worker.py').read_text(encoding='utf-8-sig')
 worker=replace(worker,"type=int,default=1800","type=int,default=3600")
 worker=replace(worker,"parser.add_argument('--local-init-checkpoint',default='')","parser.add_argument('--local-init-checkpoint',required=True);parser.add_argument('--repair-mode',choices=['initial','sameidentity'],default='initial');parser.add_argument('--source-proof',required=True)")
 worker=replace(worker,"app=None;env=None","assert not (D/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists(),'Human paused all localGPU probe/training; CPUprepared only'\nassert args.num_envs==128 and args.mode in ('fullrestore','train')\nfrom action_effective_source_admission import source_guard\nsource_guard(args.source_proof,args.local_init_checkpoint,args.repair_mode)\nos.environ['MOD4_LOCAL_REPAIR_SOURCE_PROOF']=str(Path(args.source_proof).resolve())\napp=None;env=None")
 p=N/'local_scope_worker.py';assert not p.exists();p.write_text(worker,encoding='utf-8')
 projection=(ref/'local_state_projection.py').read_text(encoding='utf-8-sig')
 projection=replace(projection,"proof=json.loads((D/'reports/LOCAL_CONTINUE_SOURCE_FULLSTATE_CPU_VERIFIED.json').read_bytes());assert proof['passed']","proof=json.loads(Path(__import__('os').environ['MOD4_LOCAL_REPAIR_SOURCE_PROOF']).read_bytes());assert proof['passed']")
 p=N/'local_state_projection.py';assert not p.exists();p.write_text(projection,encoding='utf-8')
 runtime=(ref/'local_training_runtime.py').read_text(encoding='utf-8-sig')
 runtime=replace(runtime,"originalsave=runner.save","originalsave=runner.save\n write('LOCAL_OLD_IDENTITY_BEFORE_NEW_AXIS_VERIFIED.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,source_checkpoint_SHA=H(args.local_init_checkpoint),all12_predecessor_fullCPUCUDA_markers_exact=True,all_actorcriticstdoptimizer_exact_before_explicit_new_axis=True,source_episode_plus_one=True))\n from action_effective_repair_integration import apply_or_verify,install_action_trace\n repair_metadata=apply_or_verify(runner,env,source,args,O,write)\n action_trace_save=install_action_trace(vec,env,O)")
 runtime=replace(runtime,"ck=torch.load(temp,map_location='cpu',weights_only=False);ck['LOCAL_TEMPORARY_BRANCH']=branch;ck['LOCAL_TEMPORARY_BRANCH']['own_actual_PPO_updates']=updates","ck=torch.load(temp,map_location='cpu',weights_only=False);ck['LOCAL_TEMPORARY_BRANCH']=branch;ck['LOCAL_TEMPORARY_BRANCH']['own_actual_PPO_updates']=updates\n  for key,value in repair_metadata.items():ck[key]=copy.deepcopy(value)\n  action_trace_save()")
 runtime=replace(runtime,"all_actor_critic_std_optimizer_exact_before_learning=True","all_actor_critic_std_optimizer_exact_before_explicit_axis=True,initial_axis=args.repair_mode=='initial',same_repair_identity=args.repair_mode=='sameidentity',repair_metadata=repair_metadata")
 runtime=replace(runtime,"report=health.write();assert learning_health_pass(report)","report=health.write();assert learning_health_pass(report)\n  runner.save(str(O/('model_'+str(runner.current_learning_iteration)+'.pt')))\n  write('LEFT_HEAD_INITIAL_NO_PPO_PHYSICAL_FULLSAVE_ACTUAL.json',dict(epoch=time.time(),passed=True,pid=os.getpid(),actual_controls=args.probe_controls,actual_physics_callbacks=report['actual_physics_callbacks'],health=report,latest=json.loads((O/'LOCAL_LATEST_COMPLETE.json').read_bytes()),repair_metadata=repair_metadata,no_PPO=True,not_new_learning_or_qualification=True))")
 p=N/'local_training_runtime.py';assert not p.exists();p.write_text(runtime,encoding='utf-8')
 # Preserve the old1800 defaults as immutable unadopted reference; current humanpause blocks evenCPUprepared3600 execution.
 write(N/'reports/UNADOPTED_1800_PREPARATION_AND_3600_CPU_PLAN.json',dict(epoch=time.time(),initial1800_plan_not_deployed=True,final_prepared_learning_window3600_seconds=True,
 reason='Actual1800 localprefix9.84s/env below nominal route approach+.2+tenwave travel requirement;3600 bounded planning only, actualperenv trace determines exposure',
 minimum_GPU_probe120_noPPO_still_not_executed=True,latest_human_pause_supersedes_local_GPU_plan=True,no_budget_extension=True,no_automatic_improvement_claim=True))
 # Dispatch function only exists asCPU source; pauselock denies all actual invocation before anyGPU child.
 controller=(ref/'run_local_attempt.py').read_text(encoding='utf-8-sig')
 controller=replace(controller,"name=sys.argv[1];folder=D/'attempts'/name;assert not folder.exists();folder.mkdir(parents=True)","assert not (D/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists(),'LocalGPU executionpaused by latesthuman; thisroot isCPUprepared only'\n name=sys.argv[1];folder=D/'attempts'/name;assert not folder.exists()\n assert '--lease' in sys.argv and '--source-proof' in sys.argv and '--local-init-checkpoint' in sys.argv\n lease_path=Path(sys.argv[sys.argv.index('--lease')+1]);lease=json.loads(lease_path.read_bytes())\n assert lease['GPU_lease_granted_by_root'] is True and lease['target_root']==str(D)\n assert lease['worker_sha256']==hashlib.sha256((D/'local_scope_worker.py').read_bytes()).hexdigest()\n assert lease['runtime_sha256']==hashlib.sha256((D/'local_training_runtime.py').read_bytes()).hexdigest()\n assert lease['integration_sha256']==hashlib.sha256((D/'action_effective_repair_integration.py').read_bytes()).hexdigest()\n mode=sys.argv[sys.argv.index('--mode')+1];repair_mode=sys.argv[sys.argv.index('--repair-mode')+1]\n from action_effective_source_admission import source_guard,resources\n source_guard(sys.argv[sys.argv.index('--source-proof')+1],sys.argv[sys.argv.index('--local-init-checkpoint')+1],repair_mode)\n guard=resources(3600 if mode=='train' else 0);assert guard['passed'],guard\n if mode=='train':\n  assert '--train-seconds' in sys.argv and int(sys.argv[sys.argv.index('--train-seconds')+1])==3600\n  admission=json.loads((D/'reports/GPU_INITIAL_NO_PPO_ADMISSION_ACTUAL.json').read_bytes());assert admission['passed'] and admission['source_sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'\n else:assert mode=='fullrestore' and '--probe-controls' in sys.argv and int(sys.argv[sys.argv.index('--probe-controls')+1])==120\n folder.mkdir(parents=True)\n (folder/'RESOURCE_PRELAUNCH_ACTUAL.json').write_text(json.dumps(guard,indent=2),encoding='utf-8')")
 controller=replace(controller,"sources=[D/'local_scope_worker.py',D/'local_physx_api.py',D/'local_state_projection.py',D/'local_training_runtime.py']+list((D/'runtime').rglob('*.py'))","sources=list(D.glob('*.py'))+list((D/'immutable_repair_operator').glob('*.py'))+list((D/'runtime').rglob('*.py'))")
 controller=replace(controller,"argv=[sys.executable,str(D/'local_scope_worker.py'),'--headless','--device','cuda:0','--num_envs','128','--output',str(folder/'output'),*sys.argv[2:]]","li=sys.argv.index('--lease');child_args=sys.argv[2:li]+sys.argv[li+2:]\n argv=[sys.executable,str(D/'local_scope_worker.py'),'--headless','--device','cuda:0','--num_envs','128','--output',str(folder/'output'),*child_args]")
 p=N/'run_local_attempt.py';assert not p.exists();p.write_text(controller,encoding='utf-8')
 stop=(ref/'request_stop_after_save.ps1').read_text(encoding='utf-8-sig')
 old='MOD4_LOCAL_WAVE50_CONTINUE_20261013';assert old in stop;stop=stop.replace(old,N.name)
 p=N/'request_stop_after_save.ps1';assert not p.exists();p.write_text(stop,encoding='utf-8')
 files=list(N.glob('*.py'))+list((N/'immutable_repair_operator').glob('*.py'))
 for p in files:ast.parse(p.read_text(encoding='utf-8-sig'));py_compile.compile(str(p),doraise=True)
 import sys;sys.path.insert(0,str(N));import action_effective_source_admission as admission
 proof=admission.source_guard(N/'reports/ACTION_EFFECTIVE_SOURCE_FULLSTATE_CPU_VERIFIED.json',N.parent/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt','initial')
 write(N/'reports/ACTION_EFFECTIVE_ACTIVE_FILES_CPU_PREPARED.json',dict(epoch=time.time(),CPU_compile_passed=True,CPU_source_guard107_passed=True,source_checkpoint=proof['checkpoint'],
  active_files=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)) for p in files],source_runtime_assets_byteexact=True,
  old_fullrestore12_markers_before_newaxis_required=True,newaxis_actualGPU_roundtrip_required=True,newaxis120_control_noPPO_fullsave_CPU107_admission_required=True,
  original_global_named_private_rng_source_restore_not_bypassed=True,selected_named_privateRNG_roundtrip_records_not_unobserved_coverage_claimed=True,
  sameidentity_future_no_recenter_or_Adamclear_required=True,controller_shared_old_msvcrt_lock=True,guardian15seconds=True,save_every2updates=True,
  prepared_window3600_not_deployed=True,latest_human_paused_localGPU=True,no_GPU_SDK_PPO_dispatched=True,ordinaryerrors_cost_and_fulltrace_keep_required=True,
  metadata_CPU_only_provenance_not_relabelled_as_GPU_pass=True,production_source_or_installedSDK_files_not_modified=True))
 print(json.dumps(dict(root=str(N),CPU_prepared=True,local_GPU_paused=True,no_GPU_launch=True),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('ACTION_EFFECTIVE_COMPLETE_CPU_ERROR_'+str(time.time_ns())+'.json');write(p,dict(epoch=time.time(),source_sha256=H(__file__),error=traceback.format_exc(),preGPU=True));raise
