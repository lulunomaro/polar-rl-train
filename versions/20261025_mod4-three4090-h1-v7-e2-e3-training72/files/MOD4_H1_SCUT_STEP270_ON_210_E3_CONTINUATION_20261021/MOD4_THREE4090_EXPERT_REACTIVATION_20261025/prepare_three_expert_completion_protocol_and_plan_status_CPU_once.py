"""Three-source final collection/wholeCPU protocol and evidence-based overall-plan status."""
from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025';P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'
source=(P/'collect_selected_pair_finals_unused_once.py').read_text('utf8');source=source[:source.index('def main():')]
source=source.replace("{'h1','recovery'}","{'h1','e2','recovery'}")
source=source.replace("root=Path(q['roots']['recovery'])","root=Path(q['roots'][v['key']])").replace("q['specs']['recovery']['private_lock']","q['specs'][v['key']]['private_lock']").replace("relative='recovery/'+p.relative_to(root).as_posix()","relative=v['key']+'/'+p.relative_to(root).as_posix()").replace('all_E3_processes_actual_out','all_selected_target_processes_actual_out')
source=source.replace('current_pair_closed_text','current_three_closed_text').replace('current_pair_closed_models','current_three_closed_models')
source=source.replace('def capture(c,receipt,models,key):','def capture(c,receipt,models,key,py):')
needle="assert rel.as_posix()=='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log'";assert source.count(needle)==1
source=source.replace(needle,"assert rel.as_posix() in {k+'/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log' for k in ('h1','e2','recovery')}",1)
source=source.replace('fresh=d.code(c,d.t.PY,code,','fresh=d.code(c,py,code,',1).replace("'PAIR_H1_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json'","'THREE_'+key+'_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json'")
MAIN='''
def main():
    metadata=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert metadata['passed'] and metadata['actual_finite_returned']
    assert max(x['nominal_end_epoch'] for x in metadata['source210']['current']['go'].values())-time.time()<=900,'Original <=900 closing boundary retained'
    q=json.loads((R/'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    put('THREE_EXPERT_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_owner=q['owner_identity']))
    sys.path.insert(0,str(N.parent/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory);secret=memory.recover();c=None
    try:
        c=route.connect();a=d.code(c,route.PY,READ210,dict(q=q),timeout=900);put('THREE_EXPERT_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json',a)
        row=a['cohort']['rows']['h1'];final=row.get('final') or {};texts,models=capture(c,a,[final['final']] if final.get('passed') else [],'h1',route.PY);complete=dict(h1=models);c.close();c=None
        c=d.connect72(secret);secret=None;target={}
        for key in ('e2','recovery'):
            b=d.code(c,d.PY72,READ72,dict(q=q,key=key),timeout=210);target[key]=b;row=a['cohort']['rows'][key];final=row.get('final') or {};part,models=capture(c,b,[final['final']] if final.get('passed') else [],key,d.PY72);texts.extend(part);complete[key]=models
            put('THREE_EXPERT_CLOSED_TARGET72_'+key.upper()+'_ACTUAL.json',b)
        result=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,target72=target,complete_models=complete,all_texts=texts,original_canonical_cost_settled=True,not_skill_qualification=True)
        put('THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',result);print(json.dumps(dict(closed=True,complete_models={k:len(v) for k,v in complete.items()},original_cost_settled=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('THREE_EXPERT_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay_or_refund_or_midwindow_PT=True));raise
'''
source+=MAIN;ast.parse(source)
with (N/'collect_actual_three72_finals_original_cost_unused_once.py').open('x',encoding='utf8') as f:f.write(source)
review=(P/'review_selected_pair_models_unused_once.py').read_text('utf8').replace('TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL','THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL').replace('PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL','THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL').replace("{'h1','recovery'}","{'h1','e2','recovery'}").replace("for key in ('h1','recovery'):","for key in ('h1','e2','recovery'):")
review=review.replace("updates=s['owned_H1_completed_updates'] if key=='h1' else s['E3_production_updates']","updates=s['owned_H1_completed_updates'] if key=='h1' else (s['owned_phase_complete_updates'] if key=='e2' else s['E3_production_updates'])")
review=review.replace("else:assert counts==[173,96] and s['policy_clock']['policy_hz']==50 and final['Adam_step']==Adam","else:\n            assert counts==([175,98] if key=='e2' else [173,96]) and s['policy_clock']['policy_hz']==50 and final['Adam_step']==Adam\n            if key=='e2':assert s['owned_phase']=='production' and s['owned_new_expert_task']['kind']=='E2_WORLD_MOVING_SIGNED4' and s['owned_new_expert_task']['source_SHA']==q['specs'][key]['source_SHA']")
review=review.replace("assert final['actual17Adam_steps']==[Adam]","assert final['actual17Adam_steps']==[Adam]\n            assert s['owned_H1_learning_task']['reward_recipe_version']=='step270_near_edge_takeoff_gate_v7_reward_only'",1).replace('PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL','THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL')
ast.parse(review)
with (N/'review_three_expert_complete_models_original_cost_CPU_unused_once.py').open('x',encoding='utf8') as f:f.write(review)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v108.py').read_text('utf8');needle="        'collect_three_experts72_first_PPO_finite_once.py',";assert s.count(needle)==1;s=s.replace(needle,needle+"\n        'collect_actual_three72_finals_original_cost_unused_once.py',",1)
with (B/'same_authorized_session_compressed_transport_v109.py').open('x',encoding='utf8') as f:f.write(s)
plan=dict(epoch=time.time(),human_question='现在进行到总计划的哪里？还有什么专家我们没有训练？',current_phase='Independent expert training/repair and partial E0/W35 learned gate; full expert gate/transition validation and T2-z not completed',expert_status={'E0':'Trained/frozen within verified scope','E1_WAVE_W35':'Independent35mm wave trained/frozen within scope','E1_CURB':'Has independent training and direction-repair attempts; full curriculum/acceptance incomplete','E1_SLOPE':'5degree source has training; broader slope curriculum/acceptance incomplete','H1':'Actual jump/step270 training ongoing, no qualified270mm success yet','E2':'Actual world-moving/signed rotation-translation training exists, target acceptance incomplete; new3GPU continuation staged','E3':'Actual recovery training exists, target acceptance incomplete','E4_LOW_POSTURE_TUNNEL':'Not trained in current authorized executed plan','E1_STAIR':'No completed independent continuous-stair training/acceptance; distinct from H1 single-step jumping','E5_EXTENDED_JUMP_FLIGHT_LANDING':'H1 has actual takeoff/jump training, extended flyramp/gap/landing curriculum incomplete; do not call entire jumping untouched'},gate='gate148 trained E0/W35 selection; H1/E2/E3 current player public-mode routing, no learned full-expert gate',T2z='Preparation/environment/interfaces and oneQ8 backbone only, no world-model or online adaptation training',evidence=[str(W/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md'),str(W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/reports/MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json'),str(T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025/engineering_agent/MOE_POLICY_REGISTRY.json'),str(W/'MOD4_CURRENT_EXPERT_GRADUATION_JUMP_FROZEN_20261021/reports/CURRENT_THREE_EXPERT_GRADUATION_AND_H1_HEIGHT_COMPLETE_V87_ACTUAL.json')],older_registry_player_pool_not_latest_training_model_pool=True,old_budgets_and_process_snapshots_not_current=True,no_policy_GPU_or_remote_query_for_plan_answer=True)
with (R/'MASTER_PLAN_PROGRESS_AND_UNTRAINED_EXPERTS_HUMAN_REPLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(plan,f,ensure_ascii=False,indent=2)
with (R/'THREE_EXPERT_COMPLETION_PROTOCOL_SOURCE_AST_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST=True,collector_unused=True,reviewer_unused=True,three_actual_sources_keys=['h1','e2','recovery'],original_gate900_and_parent3900_save3600_exit300_retained=True,source210_wait850_then_each_target72_wait180_serial=True,all_complete_models_wholeCPU17Adam_actor9_STD_critic8_required=True,no_actual_final_completion_yet=True,nonfatal_local_AST_warnings='2x backslash-S during late binding; original source retained, not training errors'),f,indent=2)
print(json.dumps(dict(prepared=True,three_final_collector_unused=True,wholeCPU_reviewer_unused=True,plan_status_report_saved=True)))
