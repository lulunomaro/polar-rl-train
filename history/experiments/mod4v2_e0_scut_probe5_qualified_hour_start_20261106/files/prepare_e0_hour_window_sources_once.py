"""Prepare E0's human-requested original finite hour window; no training or resource action."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;build=json.loads((D/'CONTINUOUS_D6_BUILD_RECEIPT_V1.json').read_bytes());proof=json.loads((D/'E0_D6_NATIVE_DIAGNOSTIC_ADMISSION3_CLOSED_RESULT.json').read_bytes());pm=proof['metadata'];nf=pm['cases/E0/E0_MIMIC_DIAGNOSTIC_FINAL.json'];qs=pm['TERMINAL_ROWS.json'];assert proof['outer_actual_wait']['original_parent_reaped']is True and all(x['semantic_qualification']['qualified']is True for x in qs)and nf['PPO_updates']==nf['source_opens']==nf['source_decodes']==0
mx=nf['maxima_over_60_controls'];assert len(mx)==4 and all(0<=p['native_original_scalar_error_max_rad']<=.01 and p['native_relative_to_neutral_max_rad']<=.01 for p in mx.values())
outputs={};s=(D/'worker_mod4v2_expert_migration_v4.py').read_text(encoding='utf8')
def change(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change("        if self.updates >= self.task['max_additional_updates']:\n            return 'max_additional_updates'\n",'')
change('        self.stop_reason = None','        self.stop_reason = None\n        self.ppo_started_epoch = None\n        self.completed_save_wall_seconds = 0.0\n        self.ppo_update_call_wall_seconds = 0.0\n        self.rollout_step_call_wall_seconds = 0.0')
change('            path = Path(path).resolve()','            save_wall_started = time.time()\n            path = Path(path).resolve()')
change('            window.last_saved_update = window.updates','            window.last_saved_update = window.updates\n            window.completed_save_wall_seconds += time.time() - save_wall_started')
change("            candidate['mod4v2_historical_source_checkpoint'] = source","            candidate['mod4v2_migration'].update(window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR', requested_effective_update_quota=None, ppo_started_epoch=window.ppo_started_epoch, completed_save_wall_seconds=window.completed_save_wall_seconds)\n            candidate['mod4v2_historical_source_checkpoint'] = source")
change("            need(not window.in_update and window.updates < task['max_additional_updates'], 'Unbounded/recursive original update')","            need(not window.in_update, 'Recursive original update')")
change('            window.in_update = True\n            try:', '            update_wall_started = time.time()\n            window.in_update = True\n            try:')
change('                window.in_update = False\n            need(window.optimizer_steps', '                window.in_update = False\n                window.ppo_update_call_wall_seconds += time.time() - update_wall_started\n            need(window.optimizer_steps')
change('            result = old_step(*args, **kwargs)','            rollout_wall_started = time.time()\n            result = old_step(*args, **kwargs)\n            window.rollout_step_call_wall_seconds += time.time() - rollout_wall_started')
a="""            reason = window.boundary_reason()
            if reason:
                runner.save(str(out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)))
                raise SavedStop(reason)
"""
b="""            reason = window.boundary_reason()
            # Progress is metadata only, not an additional update, observation or checkpoint read.
            put(out / ('V2_TRAINING_PROGRESS_U%06d.json' % window.updates), dict(
                epoch=time.time(), actual_new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
                actual_rollout_controls=window.rollout_controls, optimized_transitions=20000*window.rollout_controls,
                ppo_started_epoch=window.ppo_started_epoch, rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,
                PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,
                own_complete_save_wall_seconds=window.completed_save_wall_seconds,
                observed_loop_wall_seconds_excluding_complete_save=time.time()-window.ppo_started_epoch-window.completed_save_wall_seconds,
                no_skill_claim=True, parent_save_deadline=task['save_deadline']))
            if reason:
                window.stop_reason = reason
            if reason or (window.updates % 20 == 0 and window.last_saved_update != window.updates):
                runner.save(str(out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)))
            if reason:
                raise SavedStop(reason)
"""
change(a,b)
change("        # Original RSL loop publishes source_iter .. source_iter+19 for 20 updates.","        window.ppo_started_epoch = time.time()\n        put(out / 'V2_PPO_LOOP_STARTED.json',dict(epoch=window.ppo_started_epoch,run_id=task['run_id'],role='E0',original_GO_epoch=task['save_deadline']-3600,native_and_load_startup_seconds=window.ppo_started_epoch-(task['save_deadline']-3600),requested_update_quota=None,original_save_deadline=task['save_deadline']))\n        # Original RSL iteration labels remain unmodified; wall-clock bounds govern this window.")
change("            completed_requested_update_window=window.updates == task['max_additional_updates'],","            completed_requested_update_window=window.updates>0 and window.stop_reason in ('STOP_SAVE','save_deadline'),\n            window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR', requested_update_quota=None,\n            requested_hour_wall_window_elapsed=time.time()>=task['save_deadline'],\n            training_timing=dict(ppo_started_epoch=window.ppo_started_epoch,ppo_ended_epoch=time.time(),native_and_load_startup_seconds=window.ppo_started_epoch-(task['save_deadline']-3600),observed_loop_wall_seconds_excluding_complete_save=time.time()-window.ppo_started_epoch-window.completed_save_wall_seconds,rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,own_complete_save_wall_seconds=window.completed_save_wall_seconds),")
change("need(type(task['max_additional_updates']) is int and 1 <= task['max_additional_updates'] <= 20,", "need(task['role']=='E0' and task.get('window_mode')=='ORIGINAL_FINITE_WALL_CLOCK_HOUR' and type(task['max_additional_updates']) is int and task['max_additional_updates']==1000000,")
change("'Original finite update bound must be 1..20'","'Human E0 original finite-hour window required; original deadline/STOP remains authoritative'")
a='    receipt = dict(schema=SCHEMA, epoch=time.time(), role=task[\'role\'], pid=os.getpid(),'
b="""    transmission = {}
    need(list(robot.root_view.shared_metatype.link_names)==body_names,'Actual native body order differs')
    for side in ('left','right'):
        for follower,reference in (('drive_hip','thigh'),('drive_input','input')):
            an,bn=side+'_'+follower,side+'_'+reference
            qa=poses[:,body_names.index(an),3:7];qb=poses[:,body_names.index(bn),3:7]
            na=torch.tensor(contract['bodies'][an]['neutral_quat_wxyz'],device=env.device,dtype=qa.dtype)
            nb=torch.tensor(contract['bodies'][bn]['neutral_quat_wxyz'],device=env.device,dtype=qa.dtype)
            neutral=2*torch.acos((na*nb).sum().abs().clamp(max=1.))
            error=(2*torch.acos((qa*qb).sum(-1).abs().clamp(max=1.))-neutral).abs()
            need(bool(torch.isfinite(error).all()) and float(error.max())<=.01,'Actual N20000 native continuous transmission health differs: '+an)
            transmission[an]=dict(native_original_scalar_error_max_rad=float(error.max()),all_N20000_verified=True,original_threshold_rad=.01)
    receipt = dict(schema=SCHEMA, epoch=time.time(), role=task['role'], pid=os.getpid(),"""
change(a,b);change('mechanical_limits=rows, gas=gas, closure_gaps=closure_gaps,','mechanical_limits=rows, gas=gas, closure_gaps=closure_gaps, continuous_transmission_native=transmission,')
outputs[D/'worker_mod4v2_expert_migration_hour_v5.py']=s
owner=(D/'source_owner_e0_single_v2/migration_nine_original_owner_v1.py').read_text(encoding='utf8').replace('47be6619a1ec78e7c1514aab673996f545feedb24fda05da3f359d69f4a4be7f',build['USD_sha256']).replace('5cf79932fb1f11edebcfa7e35ff63ed658bbfdf1dd56706ad201b3c4fd3141a1',build['contract_sha256'])
owner=owner.replace("e['max_additional_updates']==20","e['max_additional_updates']==1000000").replace("steps_per_env=e.get('steps_per_env',24)","window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR',steps_per_env=e.get('steps_per_env',24)")
owner=owner.replace("checks['finite20_actual']=f.get('completed_actual_updates')==20","checks['finite_hour_actual']=type(f.get('completed_actual_updates'))is int and f['completed_actual_updates']>0 and f.get('window_mode')=='ORIGINAL_FINITE_WALL_CLOCK_HOUR' and f.get('requested_update_quota')is None and f.get('stop_reason')in('STOP_SAVE','save_deadline') and f.get('actual_optimizer_steps')==20*f['completed_actual_updates'] and f.get('actual_rollout_controls')==24*f['completed_actual_updates']")
outputs[D/'source_owner_e0_hour_v1/migration_nine_original_owner_v1.py']=owner
stager=(D/'stage_e0_single_nonpt_runtime_v2.py').read_text(encoding='utf8').replace('stage_e0_single_nonpt_runtime_v2.py','stage_e0_hour_nonpt_runtime_v1.py').replace('worker_mod4v2_expert_migration_v4.py','worker_mod4v2_expert_migration_hour_v5.py');outputs[D/'stage_e0_hour_nonpt_runtime_v1.py']=stager
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
for p,s in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8',newline='\n')
print('Hour worker/owner/stager prepared; no20 hardstop, original3600/3900/300 and accounting retained; native20k transmission check on same poses; no runtime execution')
