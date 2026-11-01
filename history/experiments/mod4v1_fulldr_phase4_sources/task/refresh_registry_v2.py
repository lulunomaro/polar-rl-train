"""Publish a new factual snapshot; prior registry/archive remains intact."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parent;src=R/'EXPERT_NORMALIZATION_REGISTRY_v1.json';out=R/'EXPERT_NORMALIZATION_REGISTRY_v2.json';assert not out.exists()
r=json.loads(src.read_text(encoding='utf-8'));r['schema']='mod4v1.expert_normalization.registry.v2';r['captured_local']=datetime.datetime.now().astimezone().isoformat();r['previous_registry']=str(src)
for e in r['selected_formals']:
 if e['expert']=='E0':
  e.update(source_remote='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',source_saved_CPU_SHA='1364e84c2e732b347457aa7e7f6366d28203e40e93b42a4c798fb23f5b6ebd0e',derived_source='staged_sources/E0_MOD4V1_SOURCE_FINAL',status='SOURCE_STATIC_PASS_TARGET_FRESH80_WAIT_RESOURCE',target_noPT_attempt1='reports/E0_fresh80_collect_20261102_014231/COLLECTION.json',target_noPT_attempt2_waiter='reports/E0_attempt2_waiter_dispatch_20261102_015129_1793555489733223300.json',source_PT_opens_this_phase=0)
 if e['expert']=='W35':
  e.update(status='ACTUAL_MOD4V1_20K_FULLSTATE_D0D7_AND_NATIVE24_PASS_32S_SKILL_PENDING',derived_source='staged_sources/W35_MOD4V1_SOURCE_V2_FINAL',actual_restore_report='reports/W35_eval_snapshot_20261102_013744.json',source_physical_byte_opens_this_purpose=1,source_decodes_this_purpose=1,optimizer_updates_this_purpose=0,one_original_fresh_reset=True,new_constructor_nominals_preserved=True,full_expert_skill='UNKNOWN',current_eval_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800')
 if e['expert']=='E2':e['status']='SOURCE_PRODUCER_AND_ENTRY_JOINED_PARTIAL_BUILDER_PAUSED_NO_TARGET';e['source_LR']=.00022500000000000002
 if e['expert']=='E3':e['status']='SOURCE_METADATA_BOUND_NEW_DERIVATION_NOT_STARTED'
r['DR_contract']['mod4v1_full_DR_component_runtime_passed']=True;r['DR_contract']['mod4v1_full_DR_passed']=False
r['actual_full_DR_runtime_scope']={'fresh80_report':'reports/fullDR80_snapshot_20261102_005626.json','native24_controls':24,'physics_callbacks':192,'feedback_samples':48,'W35_saved20k_fullrestore_passed':True,'all_frozen_experts_fullDR_adaptation_completed':False,'hardware_full_uncertainty_coverage':False}
r['current_stage']='W35 actual newplant20k restore+native24 passed,32s no-optimizer evaluation in progress. E0 full nonPT runtime staged, attempt1resourceWAIT/exit clean; attempt2metadata waiter waits original finiteEX natural release, SDK notyet qualified. E2partial/E3notstarted. No expert normalized freeze or skill graduation declared.'
r['git_evidence']={'phase1_commit':'0b0073f1f383bfe3bc48badf0b24041f6105def3','phase2_commit':'2bdd2ee975efa97892275e9332138a783ef796c3','branch':'mod4v1-experts-fulldr-rm70','phase2_tag':'trial-20261102-mod4v1-fulldr-w35-e0-phase2','remote_branch_tag_peeled_verified':True,'main_modified':False,'phase3_pending':['postphase2 W35metadata/terminal/decision','E0actualstage/resourcewait/attempt2','E2partialadditional-source','registryv2 and acceptance ledger']}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(out)
