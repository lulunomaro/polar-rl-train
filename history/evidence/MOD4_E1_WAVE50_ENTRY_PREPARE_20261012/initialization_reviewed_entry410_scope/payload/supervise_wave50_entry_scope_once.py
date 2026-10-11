"""One new isolated WAVE50 scope, once SDK/native/PPO, fresh fullresume,300s."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,shutil,time,traceback,sys
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';sys.path.insert(0,str(CODE))
import supervise_e1_command_retention_episode_reviewed_once as inherited
from clock_training_health import learning_health_pass
from wave50_entry_source_guard import verify_original_records
s=inherited.s;read=inherited.read;write=inherited.write;identity=inherited.identity;freeze_run=inherited.freeze_run
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012')
BASE=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012')
SOURCE_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
def verify():
 verify_original_records(s.q,D)
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages']
 rev=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(BASE/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==384 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert s.q.base.sha(D/n)==h,n
 cpu=read(R/'WAVE50_TARGET_CPU_PASSED.json');assert cpu['passed'] and cpu['source_count']==len(f)
 decision=read(R/'COMPLETE147_ENTRY_AXIS_DECISION.json');assert decision['new_entry_axis_approved'] and decision['default_source_SHA']==SOURCE_SHA
 for row in read(R/'REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']:assert s.q.base.sha(Path(row['path']))==row['sha256']
 jobs=read(R/'WAVE50_FOUR_CASE_TEMPLATES.json')['jobs'];assert len(jobs)==4
 for t in jobs:assert s.q.base.sha(Path(t['artifacts']['runtime']['path']))==t['artifacts']['runtime']['sha256']
def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE50_second_bounded_saved_review_ready' and st['child'] is None
 p=read(OLD/'reports/e1_WAVE50_second_bounded_observation_PASSED.json');assert len(p['unique_completed_segment'])==1 and p['checkpoint']['sha256']=='a67b955f680dd101cc4480f19c2e95dd86c34423148302fad1d8e925e206d4df'
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=89922117)):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
def runtime():
 e=inherited.runtime()
 for name in tuple(e):
  if name.endswith('INITIAL_ADMISSION'):e.pop(name)
 e['RM_WAVE50_INITIAL_ADMISSION']='verified_G3_to_independent_WAVE50_entry';return e
def phase(name,**kw):
 write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_WAVE50',owner=identity(os.getpid()),**kw))
 s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='Approved004 independentWAVE50, new physical/state scope; first300s then fullfourcase review',active_expert='E1_WAVE50',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
inherited.s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)
def fullsave(path,count=20000):
 import torch
 from wave50_entry_fullsave_cpu import fullsave as validate_full
 info=validate_full(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']==SOURCE_SHA
 return info
def source():
 row=read(R/'SOURCE_SELECTED.json');p=Path(row['path']);assert s.q.base.sha(p)==SOURCE_SHA and inherited.fullsave(p)['finite_tensors']==102;return p
def trainers():
 result=inherited.trainers();own={'train_wave50_entry_fresh_preflight_ppo.py','train_wave50_entry_resume_ppo.py','native_e1_wave50_entry_scope_probe.py','probe_wave50_entry_fresh_process_full_resume.py'}
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   argv=[v.decode(errors='replace') for v in p.read_bytes().split(b'\0')]
   if any(Path(v).name in own for v in argv):result.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return result
def train(init,count,updates,duration,label,discard):
    verify();assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert s.left()>120;deadline=time.time()+min(duration,s.left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
    e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline);entry='train_wave50_entry_fresh_preflight_ppo.py' if count==128 else 'train_wave50_entry_resume_ppo.py'
    args=[s.q.base.PY,str(CODE/entry),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
    with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    s.LIVE=p;s.q.base.start_segment(p,'S3_E1_'+name,log);s.q.ctl.S=read(s.q.ctl.STATE_PATH)
    s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,feedback_delay_profile='control_0_10ms_v1',discarded_preflight=discard);s.q.ctl.persist()
    phase('E1_complete_PPO_preflight' if discard else 'bounded_E1_WAVE50_independent_learning',child=identity(p.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
    while p.poll() is None:
        s.q.base.account_segment();roots=list(logs.glob('*_'+name))
        if len(roots)==1:
            run=roots[0]
            if (run/'latest_complete.json').exists():
                rec=read(run/'latest_complete.json');assert rec['pid']==p.pid;freeze_run(run);write('E1_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=rec,discarded_preflight=discard))
            if (run/'CLOCK_TRAINING_HEALTH.json').exists():write('E1_ACTIVE_HEALTH.json',read(run/'CLOCK_TRAINING_HEALTH.json'))
        time.sleep(1 if discard else 5)
    s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
    assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
    run=s.q.w.rate.trainer_run(logs,p.pid);freeze_run(run);rec=read(run/'latest_complete.json');ck=fullsave(Path(rec['checkpoint']),count=count);m=read(run/'run_manifest.json');h=read(run/'CLOCK_TRAINING_HEALTH.json')
    assert rec['pid']==p.pid and m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
    assert m['feedback_delay_recipe']['profile']=='control_0_10ms_v1' and m['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1' and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
    for n,v in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==v,n
    if count==20000:
        terrain=read(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');assert terrain['source_sha256']==s.q.base.sha(init) and terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and terrain['complete_D1_D7_optimizer_global_named_streams_verified'] and terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']
        assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']
        entryproof=read(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');assert entryproof['passed'] and entryproof['explicit_new_entry_scope'] and not entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']
        cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');assert cp['source_sha256']==s.q.base.sha(init) and cp['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and cp['COM_PD_episode_incremented_once'] and cp['complete_D1_D6_optimizer_global_named_streams_verified'] and not cp['PhysX_exact_resume_claimed']
        gas=read(run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json');assert gas['source_sha256']==s.q.base.sha(init) and gas['actual_CUDA_gas_state_disk_roundtrip_exact'] and gas['gas_episode_incremented_once'] and gas['complete_D1_D5_optimizer_global_named_streams_verified'] and not gas['PhysX_exact_resume_claimed']
        spring=read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json');assert spring['source_sha256']==s.q.base.sha(init) and spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once'] and spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']
        startup=read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['action_episode_incremented_once'] and startup['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
    a=read(run/'RETENTION_COMMAND_ACTUAL.json');assert a['actual_controls']==h['control_steps']
    if count==20000:
        v=read(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert v['saved_source_episode_plus_one_verified'] and v['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and v['old_full_D1_D7_optimizer_global_named_streams_verified'] and v['E1_episode_incremented_once']
    assert m['gas_damping_recipe']['profile']=='gas_damping_independent_episode_090_110_v1'
    seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(seg)==1
    assert Path(rec['checkpoint']).is_relative_to(D/('discard_logs' if discard else 'learning_logs'))
    row=dict(epoch=time.time(),expert='E1_WAVE50',source_sha256=s.q.base.sha(init),source_count=len(read(R/'SOURCE_FREEZE.json')['sha256']),checkpoint=ck,run=str(run),own_PID_bound_receipt=rec,health=h,actual_updates=h['control_steps']//24,actual_environment_steps=h['control_steps']*count,unique_completed_segment=seg,discarded_preflight=discard,small128_uses_fresh_sensor_feedback_action_pressure_gas_streams=count==128,ordinary_events_preserved=True,new_physical_episode=True)
    write(label+'_SAVED_EXIT.json',row);assert learning_health_pass(h),('Integrity failure, own source retained',h)
    if discard:assert h['control_steps']==24*updates
    write(label+'_PASSED.json',row);return Path(ck['path']),row
def native_contract(cp):
    budget=s.q.ctl.CANONICAL.read_bytes()
    results={};env=runtime()
    for name in tuple(env):
        if name.endswith('INITIAL_ADMISSION'):env.pop(name)
    for count,steps,label in ((10,300,'WAVE50_SDK10'),(20000,120,'WAVE50_NATIVE20K')):
        verify();outpath=D/(label+'.json');log=D/(label+'.log');assert not outpath.exists() and not log.exists()
        args=[s.q.base.PY,str(D/'native_e1_wave50_entry_scope_probe.py'),'--headless','--dt','.0025','--checkpoint',str(cp),'--output',str(outpath),
            '--num_envs',str(count),'--warmup','0' if count==10 else '24','--steps',str(steps),'--profile_steps','0']
        with log.open('x') as out:child=subprocess.Popen(args,cwd=s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        loc=identity(child.pid)
        write(label+'_PID_RECEIPT.json',dict(epoch=time.time(),child=loc,argv=args,no_PPO=True,source_SHA=SOURCE_SHA))
        phase('WAVE50_new_SDK_native_no_PPO',child=loc,active_log=str(log),scope=label)
        while child.poll() is None:time.sleep(5)
        assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),label
        v=json.loads(outpath.read_bytes())
        assert v['actual_all_reset_origins_equal_new_entry_map'] and v['actual_entry_map_receipt']['actual_origin_bound']
        assert v['PPO_update_count']==0 and not v['nonfinite'] and v['actual_task_failed_environments']==0
        assert v['physical_callback_count']==steps*4 and v['health']['actual_physics_callbacks']==(steps+(24 if count==20000 else 0))*4
        assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6
        t=v['E1_terrain_identity'];assert t['profile']=='mod4_G4_CAD_derived_50mm_entry_v1' and t['G4_height_peak_to_trough_m']==.05
        assert v['actual_solver_readback']['all_position32_velocity4'] and v['physical_action_delay_audit']['application_formula_max_error']==0
        hist=v['command_retention']['sample_histogram'];assert v['command_retention']['projection_error']<=1e-6
        assert all(sum(row[2:6])==0 for row in hist[:1]+hist[2:]) and not v['command_retention']['pure_high_spin']
        if count==10:
            assert v['sensor_sdk_audit']['selected_reset']['selected_entry_reset_exact'] and v['SDK_WAVE50_actual_assignment_placement']['actual_origin_bound_entry_cache_verified']
            assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact'] and v['SDK_WAVE50_actual_assignment_placement']['reset_root_before_physics_exact'] and v['SDK_WAVE50_actual_assignment_placement']['actual_G4_cell_count']==10 and v['SDK_WAVE50_actual_assignment_placement']['complete_footprint_all_flat_hits']
            assert v['command_retention']['eligible']==0 and sum(hist[1][2:6])==0
        else:
            assert all(hist[1][i]>0 for i in (2,3,4,5))
            assert v['actual_entry_map_receipt']['map_sha256']=='f42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d'
            assert v['actual_entry_map_receipt']['Wave_environments']==2820 and v['actual_entry_map_receipt']['other_environments_unchanged']==17180
            audit_native_trace(outpath,v)
        assert s.q.ctl.CANONICAL.read_bytes()==budget and s.q.base.sha(cp)==SOURCE_SHA
        results[label]=dict(path=str(outpath),sha256=s.q.base.sha(outpath),own_child_PID_receipt=loc,callbacks=steps*4,
            closure_m=v['max_closure_error_m'],ground_error_m=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],
            passed=True,no_PPO=True,canonical_bytes_preserved=True)
        write(label+'_PASSED.json',results[label])
    write('WAVE50_NATIVE_SCOPE_PASSED.json',dict(epoch=time.time(),results=results,no_PPO_or_optimizer_update=True,canonical_bytes_preserved=True,full_WAVE50_CPUCUDA_resume_and_PPO_pending=True))
    phase('WAVE50_new_native_contract_complete_review_ready',child=None,results=results,no_PPO=True)
def audit_native_trace(outpath,v):
 import numpy as np
 paths=list(outpath.parent.glob(outpath.stem+'_trace/retention_prefix_*.npz'));assert len(paths)==1
 with np.load(paths[0]) as z:
  rows=z['rows'];root=rows[:,:,:3];cmd=rows[:,:,7:10];fam=rows[:,:,10]
  assert len(cmd)==144 and cmd.shape[1:]==(20000,3) and np.isfinite(root).all() and np.isfinite(cmd).all()
  origins=np.array(v['reset_root_before_physics'])[:,:2];counts=[]
  rows=v['actual_generated_family_assignments']
  for side in (-1,1):
   mask=np.zeros(20000,dtype=bool)
   for a in rows:
    if a['family']!='random_uniform_for_rm':continue
    b=np.array(a['bounds']);center=(b[0,0]+b[1,0])*.5
    mask|=((origins>=b[0,:2])&(origins<b[1,:2])).all(1)&((origins[:,0]<center) if side<0 else (origins[:,0]>center))
   take=(fam==4)&mask[None,:];vx=cmd[:,:,0][take];vyaw=cmd[:,:,1:][take]
   c=dict(side=side,negative=int((vx<0).sum()),positive=int((vx>0).sum()),standing=int((vx==0).sum()),maxabs=float(abs(vx).max()))
   assert all(c[k]>0 for k in ('negative','positive','standing')) and c['maxabs']<=.300001 and np.max(abs(vyaw))==0
   counts.append(c)
 write('ENTRY_NATIVE_FULL_TRACE_REVIEW.json',dict(passed=True,path=str(paths[0]),bytes=paths[0].stat().st_size,sha256=s.q.base.sha(paths[0]),two_sides_signed_standing=counts,not_fullroute_contact_or_causal_certificate=True))

def fresh_resume(big):
 budget=s.q.ctl.CANONICAL.read_bytes();write('WAVE50_BIG_CORE_VERIFIED.json',big)
 e=runtime();e['RM_WAVE50_FRESH_RESUME_ONLY']='1'
 args=[s.q.base.PY,str(CODE/'probe_wave50_entry_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--max_iterations','0','--steps_per_env','24','--seed','20260928','--learning_rate','.0001','--init_checkpoint',big['checkpoint']['path'],'--log_root',str(D/'fresh_process_resume'),'--run_name','wave50_fresh_full_resume_no_learning']
 log=D/'fresh_process_resume.log'
 with log.open('x') as out:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;phase('WAVE50_fresh_same_scope_full_resume_no_PPO',child=identity(p.pid),active_log=str(log),no_PPO=True)
 write('WAVE50_FRESH_RESUME_PID_RECEIPT.json',dict(child=identity(p.pid),argv=args,no_PPO=True))
 while p.poll() is None:time.sleep(2)
 s.LIVE=None;assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text()
 proof=read(D/'fresh_process_resume/FRESH_PROCESS_SAME_WAVE50_FULL_RESUME_PASSED.json');assert proof['passed'] and proof['pid']==p.pid and proof['actual_control_steps']==proof['actual_additional_PPO_updates']==0
 assert proof['actual_same_WAVE50_terrain_command_private_CPUCUDA_disk_roundtrip_exact'] and proof['saved_source_episode_plus_one_verified']
 assert s.q.ctl.CANONICAL.read_bytes()==budget
 write('WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json',proof);return proof
def publish(init):
 sha=s.q.base.sha(init);dest=s.q.ER.parent/'artifacts'/('e1-wave50-entry-own-'+sha+'.pt');assert not dest.exists();shutil.copy2(init,dest);assert s.q.base.sha(dest)==sha
 checkpoint=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha);templates=read(R/'WAVE50_FOUR_CASE_TEMPLATES.json')['jobs'];number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number']
 for folder in ('eval_queue','eval_results'):
  assert not any('episode-d3-'+str(number)+'-' in p.name for p in (s.q.ER.parent/folder).iterdir())
 rows=[]
 for i,t in enumerate(templates):
  row=json.loads(json.dumps(t));kind=row['kind'];job='clk2500-closure-episode-d3-'+str(number)+'-e1-wave50-entry-repair'+('-terrain' if i==0 else '-retention')+'-'+kind
  p=s.q.ER.parent/'eval_queue'/(job+'.json');assert not p.exists()
  row.update(job_id=job,published_epoch=time.time(),role='Own independent50mm fullsaved candidate; terrain acceptance and inherited diagnostic, no learned gate',scope_pending_actual_review=True,learning_executor_not_deployed=False,source_saved_terraincommand_remains35mm=False)
  row['artifacts']['checkpoint']=checkpoint;s.q.base.atomic_json(p,row);rows.append(row)
 write('E1_WAVE50_ASYNC_PUBLISHED.json',dict(epoch=time.time(),source=checkpoint,jobs=rows,no_GPU_or_canonical_write=True))
def guardian(owner,ticks):
 while True:
  a=identity(owner);lost=not a or a['state']=='Z' or a['start_ticks']!=ticks
  segment=s.q.base.budget_state()['active_segment'];state=read(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else {}
  loc=state.get('child');child=identity(loc['pid']) if loc else None
  own=bool(child and loc['start_ticks']==child['start_ticks'] and state['owner']['pid']==owner and any(str(CODE/n) in child['argv'] for n in ('train_wave50_entry_fresh_preflight_ppo.py','train_wave50_entry_resume_ppo.py')))
  if segment and own and segment['pid']==child['pid'] and (lost or s.left()<=0):
   for root in (D/'discard_logs',D/'learning_logs'):
    try:run=s.q.w.rate.trainer_run(root,child['pid']);break
    except (AssertionError,FileNotFoundError):run=None
   if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own WAVE50 complete save: guardian budget/parent protection\n')
  if not own and (lost or (R/'E1_REVIEW_READY.json').exists() or (R/'E1_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_WAVE50',source=inherited.fullsave(init),old386_own_PASSED_actual_exits_two_OS_locks_held_active_empty=True,new_budget_seconds=0))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_WAVE50',genuinely_new_scope=True,first_formal_seconds=300,no_oldonce_replayed=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid));native_contract(init)
 _,small=train(init,128,2,900,'wave50_discard128',True)
 _,big=train(init,20000,4,900,'wave50_discard20k',True)
 fresh=fresh_resume(big)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=small,big=big,fresh_same_scope=fresh,weights_discarded=True,no_fresh_only_restore_on_stepped_environment=True,SDK_native_new_scope_passed=True,old_clock_DR_exact_reused_no_replay=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_WAVE50_entry_observation',False)
 assert s.q.base.sha(init)==SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_WAVE50_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),source_SHA_preserved=True,E0_CURB_SLOPE_frozen_WAVE35_not_optimizer_or_save_targets=True))
 publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_WAVE50',all_courses_finished=False,requires_actual_fourcase_review=True,candidate_number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number'],automatic_more_PPO_disallowed=True))
 phase('E1_WAVE50_entry_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
