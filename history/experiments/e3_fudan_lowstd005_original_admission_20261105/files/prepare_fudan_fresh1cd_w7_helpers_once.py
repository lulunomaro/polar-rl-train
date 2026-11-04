"""Prepare one fresh1cd N20000/25 pilot namespace; do not stage or dispatch here."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent
names={'prepare_stage_fudan_timeout8_w6_once.py':'prepare_stage_fudan_fresh1cd_w7_once.py','dispatch_fudan_timeout8_w6_original_owner_once.py':'dispatch_fudan_fresh1cd_w7_original_owner_once.py','collect_fudan_timeout8_w6_window_once.py':'collect_fudan_fresh1cd_w7_window_once.py'}
assert not any((D/name).exists()for name in names.values())
payload={}
for old,new in names.items():
 s=(D/old).read_text(encoding='utf8').replace('FDN_N20000_W6_TIMEOUT8_','FDN_N20000_W7_FRESH1CD_')
 if old.startswith('prepare_'):
  s=s.replace('full learner continuation, fresh environment','fresh Fudan learner with only1cd MLP warm start')
  s=s.replace('native_payload_v6_n20000_timeout8','native_payload_v7_n20000_fresh1cd_25').replace('source_fudan_native_worker_v4_20k_timeout8','source_fudan_native_worker_v5_fresh1cd_timeout8').replace('source_original_owner_v4_20k_timeout8','source_original_owner_v5_fresh1cd_timeout8').replace('stage_fudan_nonpt_v4_20k_timeout8.py','stage_fudan_nonpt_v5_fresh1cd_timeout8.py').replace('MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_','MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W7_')
  lines=s.splitlines(keepends=True);assert lines[4].startswith('prior=')and lines[13].startswith('overlay=')
  front="""prior=json.loads((D/'reports/FDN_N20000_W6_TIMEOUT8_20261104_231152/CLOSED_RESULT.json').read_bytes());assert prior['closed']is True
m=prior['metadata'];x=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];f=m['FDN_FINAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];qualification=m['FDN_PARENT_WAIT_QUALIFICATION.json']
assert x['errors']==[]and all(x[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert outer['actual_wait_returncode']==0 and outer['original_owner_reaped']is True and outer['original_owner_pid']==1621824 and outer['controller_pid']==1621817
assert qualification['qualified']is True and all(v is True for v in qualification['checks'].values())
assert latest==f['latest_complete_save']and latest['sha256']=='3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e'and latest['bytes']==1204253399
assert f['counters']==dict(updates=205,policy_optimizer_steps=4100,encoder_optimizer_steps=4100,transitions_seen=147942912)and f['window_counters']['updates']==72 and f['native_counters']['actual_native_policy_steps']==3504
assessment=json.loads((D/'FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json').read_bytes());assert assessment['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION'and assessment['original_N80']['execution_qualified']is True and assessment['original_N80']['actual_original_parent_qualified']is True
source=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt',sha256='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8',bytes=14715029,mode='ACTOR_CRITIC_MLP_ONLY_FRESH_FDN_LEARNER',new_window_updates=25,all_new_learner_counters_start_zero=True,bad_candidate_not_continued=True)
"""
  s=''.join(lines[:4])+front+''.join(lines[13:])
  s=s.replace('learner_source=source','warm_source=source')
  pin="assert N.is_dir() and not P.exists()"
  assert s.count(pin)==1;s=s.replace(pin,"assert H((N/'worker_fudan_sequence_ppo_native_v1.py').read_bytes())=='e4d5df2827a2d07d7c880f72bd09e483d4987072c005253c7f93e6b2cccfdeb5'\n"+pin)
 if old.startswith('collect_'):
  assert s.count('FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json')==2
  s=s.replace('FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json','FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json')
 ast.parse(s);compile(s,new,'exec');payload[new]=s
for name,s in payload.items():(D/name).write_text(s,encoding='utf8',newline='\n')
print('Prepared three new W7 helpers; one sourceAST pass; original resource parent and observer loops unchanged; no SSH/SDK/PT/GPU/C/stage/dispatch')
