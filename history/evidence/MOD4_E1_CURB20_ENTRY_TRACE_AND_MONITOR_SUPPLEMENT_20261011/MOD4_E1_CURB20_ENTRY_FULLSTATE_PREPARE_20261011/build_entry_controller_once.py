from pathlib import Path
import ast,json,hashlib,time
D=Path(__file__).resolve().parent;OLD=D.parent/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011';P=D/'payload';R=D/'reports'

def main():
    p=P/'supervise_curb20_entry_fullstate_once.py';assert not p.exists()
    t=(OLD/'inherited_source/supervise_curb20_fullstate_once.py').read_text(encoding='utf8')
    start=t.index('def fullsave(');end=t.index('def source():',start)
    t=t[:start]+'''def fullsave(path,count=20000):
 from curb20_entry_fullsave_cpu import fullsave as core
 info=core(path,count=count)
 import torch
 from curb20_entry_current_state import PROFILE
 ck=torch.load(path,map_location='cpu',weights_only=False);assert ck['E1_terrain_state']['profile']==PROFILE
 assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==SOURCE_SHA
 return info
'''+t[end:]
    start=t.index('def verify():');end=t.index('def trainers():',start)
    t=t[:start]+'''def verify():
 from reviewed_budget005_source_guard import verify_original_records
 from budget_authority import validate_budget
 verify_original_records(s.q,D);assert validate_budget(s.q.base.budget_state())==1188000
 c=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json');assert c['terrain_subexpert_revision004']['approved'] and c['budget_retrain_revision005']['approved']
 assert read(R/'ENTRY_TARGET_FULLSTATE_CPU_PASSED.json')['passed']
 assert read(R/'ENTRY_NATIVE_ACTUAL_REVIEW.json')['native20k_scope_passed']
 reuse=read(R/'ENTRY_REUSED_NATIVE20K.json');assert reuse['passed'] and reuse['no_PPO'] and s.q.base.sha(Path(reuse['path']))==reuse['sha256']
 own=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==398 and all(own[n]==h for n,h in old.items())
 for n,h in own.items():assert s.q.base.sha(D/n)==h,n
'''+t[end:]
    start=t.index('def wait_existing():');end=t.index('def runtime():',start)
    t=t[:start]+'''def wait_existing():
 st=read(OLD/'reports/ENTRY_NATIVE_STATE.json');assert st['phase']=='CURB20_entry_native_complete_review_ready' and st['child'] is None
 passed=read(OLD/'reports/ENTRY_NATIVE_SCOPE_PASSED.json');assert passed['passed']
 for v in [st['owner']]+[x['own_child_PID'] for x in passed['results'].values()]:
  a=identity(v['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=v['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
'''+t[end:]
    t=t.replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011')","OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_REPAIR_20261011')")
    t=t.replace('train_curb20_fresh_preflight_ppo.py','train_curb20_entry_fresh_preflight_ppo.py').replace('train_curb20_full_resume_ppo.py','train_curb20_entry_resume_ppo.py')
    t=t.replace("inherited.s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:inherited.verify_original_records(s.q,D)","from reviewed_budget005_source_guard import verify_original_records\ninherited.s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)")
    t=t.replace("'RM_CURB_PREFLIGHT_SELF_RESUME']='1' if count==20000 and discard else '0'","'RM_CURB_PREFLIGHT_SELF_RESUME']='0'")
    t=t.replace("if discard:assert read(run/'OWN_SAME_CURB_FULL_RESUME_PASSED.json')['passed']","assert terrain['explicit_new_entry_reset_scope'] and not terrain['entry_reset_state_restored_exact']")
    t=t.replace("verify();assert not trainers()", "verify();assert read(R/'ENTRY_ORIGIN_BOUND_SDK10_PASSED.json')['passed'];assert not trainers()")
    t=t.replace('bounded_E1_G3_command_retention_learning','bounded_E1_CURB20_entry_repair_learning')
    t=t.replace("curb_discard128", "entry_discard128").replace("curb_discard20k", "entry_discard20k")
    t=t.replace("e1_CURB20_independent_observation", "e1_CURB20_entry_repair_observation")
    t=t.replace('clk2500-closure-episode-d3-133-e1-curb20-independent','clk2500-closure-episode-d3-139-e1-curb20-entry-repair')
    t=t.replace('E1_CURB133_ASYNC_PUBLISHED.json','E1_CURB139_ASYNC_PUBLISHED.json').replace('requires_actual133_fourcase_review','requires_actual139_fourcase_review')
    t=t.replace("'CURB_REUSED_NATIVE.json'","'ENTRY_REUSED_NATIVE20K.json'")
    t=t.replace('E1_CURB20_independent_saved_review_ready','E1_CURB20_entry_repair_saved_review_ready')
    native='''def origin_bound_SDK10():
 import numpy as np
 assert not (R/'ENTRY_ORIGIN_BOUND_SDK10_PID_RECEIPT.json').exists()
 output=D/'ENTRY_ORIGIN_BOUND_SDK10.json';log=D/'ENTRY_ORIGIN_BOUND_SDK10.log';before=s.q.ctl.CANONICAL.read_bytes()
 args=[s.q.base.PY,str(D/'native_curb20_entry_origin_bound_sdk_probe.py'),'--headless','--dt','.0025','--checkpoint',str(source()),'--output',str(output),'--num_envs','10','--warmup','0','--steps','300','--profile_steps','0']
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 loc=identity(p.pid);write('ENTRY_ORIGIN_BOUND_SDK10_PID_RECEIPT.json',dict(epoch=time.time(),child=loc,argv=args,no_PPO=True,new_origin_bound_missing_scope_only=True))
 phase('ENTRY_origin_bound_SDK10_no_PPO',child=loc,active_log=str(log))
 while p.poll() is None:time.sleep(2)
 assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 assert s.q.ctl.CANONICAL.read_bytes()==before
 v=read(output);h=v['health'];assert v['PPO_update_count']==0 and not v['nonfinite'] and v['actual_task_failed_environments']==0
 assert v['physical_callback_count']==1200 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==1200
 assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and h['stop_reason'] is None
 assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6 and v['actual_solver_readback']['all_position32_velocity4']
 assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact'] and v['CURB_entry_map']['changed_environments']==10
 root=np.array(v['reset_root_before_physics'],dtype='<f4');assert root.shape==(10,13) and hashlib.sha256(root[:,:2].tobytes()).hexdigest()==v['CURB_entry_map']['map_sha256']
 for i,cell in enumerate(v['SDK_CURB_actual_assignment_placement']['chosen_actual_assignments']):
  b=np.array(cell['bounds']);assert ((root[i,:2]>=b[0,:2])&(root[i,:2]<b[1,:2])).all()
 trace=output.with_name(output.stem+'_trace');audit=read(trace/'RETENTION_COMMAND_ACTUAL.json');x=np.concatenate([np.load(trace/n)['rows'] for n in audit['trace_files']]);assert x.shape==(300,10,16) and (x[:,:,10]==4).all() and (x[:,:,11]==0).all() and abs(x[:,:,8:10]).max()==0
 row=dict(epoch=time.time(),passed=True,path=str(output),bytes=output.stat().st_size,sha256=s.q.base.sha(output),no_PPO=True,actual_CURB_start_environments=10,old_SDK_scope_defect_retained_not_relabelled=True,health=h,entry_map=v['CURB_entry_map'],actual_child=loc)
 write('ENTRY_ORIGIN_BOUND_SDK10_PASSED.json',row)

def fresh_same_scope(big):
 source_ck=big['checkpoint'];fullsave(Path(source_ck['path']))
 write('FRESH_PROCESS_BIG_CORE_VERIFIED.json',dict(epoch=time.time(),checkpoint=source_ck,CPU_fullsave_passed=True))
 log=D/'ENTRY_FRESH_SAME_SCOPE.log';directory=D/'fresh_same_scope';assert not log.exists() and not directory.exists()
 args=[s.q.base.PY,str(CODE/'probe_curb20_entry_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--max_iterations','0','--log_root',str(directory),'--init_checkpoint',source_ck['path']]
 e=runtime();e['RM_CURB_FRESH_RESUME_ONLY']='1'
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('ENTRY_FRESH_SAME_SCOPE_PID_RECEIPT.json',dict(epoch=time.time(),child=identity(p.pid),argv=args,no_PPO=True));phase('ENTRY_fresh_same_scope_no_PPO',child=identity(p.pid),active_log=str(log));before=s.q.ctl.CANONICAL.read_bytes()
 while p.poll() is None:time.sleep(2)
 assert s.q.ctl.CANONICAL.read_bytes()==before and p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 v=read(directory/'FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json');assert v['passed'] and v['actual_control_steps']==v['actual_additional_PPO_updates']==0 and v['terrain']['entry_reset_state_restored_exact'] and not v['terrain']['explicit_new_entry_reset_scope']
 write('ENTRY_FRESH_SAME_SCOPE_PASSED.json',v)

'''
    at=t.index('def main():');t=t[:at]+native+t[at:]
    t=t.replace(" _,small=train(init,128,2,900,'entry_discard128',True)"," origin_bound_SDK10()\n _,small=train(init,128,2,900,'entry_discard128',True)")
    t=t.replace(" _,big=train(init,20000,4,900,'entry_discard20k',True)"," _,big=train(init,20000,4,900,'entry_discard20k',True)\n fresh_same_scope(big)")
    t=t.replace('actual_same_CURB_fullresume_verified_inside_big=True','actual_same_CURB_entry_fullresume_verified_in_fresh_process=True,fresh=read(R/\'ENTRY_FRESH_SAME_SCOPE_PASSED.json\')')
    t=t.replace('original372 physicalscope exactreuse; new explicitsourcecommand/geometry fullrestore;2discardpreflights then300s and4case review','entry398 native20k exactreuse; origin-bound SDK repair; new entry identity fullrestore;2discardpreflights/fresh then300s/4case review')
    ast.parse(t);p.write_text(t,encoding='utf8')
    files={x.relative_to(P).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in P.rglob('*') if x.is_file()}
    (R/'CONTROLLER_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),new_files=files,controller=str(p),sequence=['repair missing origin-bound SDK10','newfullstate128x2','newfullstate20kx4','fresh20k0control0PPO exactsameentryrestore','formal300s','ownfullsave/PASSED/unique settle','publish139fourcase','exit reviewready'],no_deployment_yet=True),indent=2),encoding='utf8')
    print(json.dumps(dict(controller_prepared=True,new_files=len(files))))

if __name__=='__main__':main()
