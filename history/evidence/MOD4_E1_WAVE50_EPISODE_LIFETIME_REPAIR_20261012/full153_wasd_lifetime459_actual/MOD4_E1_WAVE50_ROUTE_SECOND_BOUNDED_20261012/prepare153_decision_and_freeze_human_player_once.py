from pathlib import Path
import json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;P=W/'MOD4_LOCAL_WASD_WAVE50_70_20261012'
def put(p,v):assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def latest(pattern):return json.loads(max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
def main():
 review=latest('RESOURCE449_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');direct=latest('RESOURCE449_DIRECT152_PREFIX_ACTUAL_REVIEW_[0-9]*.json');assert review['review_complete'] and not review['pending'] and direct['passed']
 diagnosis=json.loads((R/'POST153_EPISODE_LIFETIME_CPU_ACTUAL.json').read_bytes());full=[x for x in diagnosis['ended_prefixes'] if x['observed_prefix']==2000];assert len(full)==173
 # The original preliminary observer marks first-prefix age ambiguous. Only actual full2000 observed rows are called full20s here.
 decision=dict(epoch=time.time(),passed=True,full_fourcase_actual_review=review,direct152=direct,forward_complete=13,reverse_complete=23,not_qualified50=True,two_same_route_blocks_complete=True,no_blind_third_same_route_duration_block=True,no_70_training_authorized=True,human_manual_feedback='Both manual50mm/70mm performance poor, continue training',next_axis='Only physical Wave-born episode time_out20to40seconds; other environments20seconds unchanged',new_lifetime_axis_authorized_by_human_continue_and004005_bounded_diagnosis=True,initial_source_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',lifetime_diagnosis=dict(full_observed20s_prefixes=len(full),root_not_beyond_wave_end=sum(not x['root_center_past_wave_end'] for x in full),command_integral_below3_4m=sum(x['absolute_command_integral_m']<3.4 for x in full),first_randomized_episode_age_not_claimed_zero=True,preliminary_fully_seen_flag_not_used_for_initial_prefixes=True,all_valid_prefixes_retained=True,no_rootproxy_contact_or_unique_causal_proof=True),unchanged=['50mm geometry','reset XY','fixed episode toward direction','route4m inward and2m others','absolute command draws andstanding.2','command12to16s','reward','LR','DR','clock','hardware','otherexperts','frozen15s protocol'],first_formal_seconds=300,max_blocks_before_fullaudit=2,max_block_seconds=7200,CPU_GPU_fullstate_and_resource_admission_still_required=True)
 put(R/'COMPLETE153_EPISODE_LIFETIME_AXIS_DECISION.json',decision)
 snapshots=[];stamp=str(time.time_ns())
 for name in ('INTERACTIVE_STARTED.json','INTERACTIVE_CURRENT.json'):
  p=P/name
  if p.exists():
   b=p.read_bytes();q=P/'reports'/('HUMAN_PLAYER_SNAPSHOT_'+stamp+'_'+name);assert not q.exists();q.write_bytes(b);snapshots.append(dict(original_path=str(p.resolve()),snapshot_path=str(q.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),captured_epoch=time.time()))
 put(P/'reports/HUMAN_MANUAL_FEEDBACK_ACTUAL.json',dict(epoch=time.time(),human_feedback='我试玩过了，表现的都很差劲，继续训吧',snapshots=snapshots,player_not_stopped_reset_restarted_or_keyed=True,manual_feedback_not_formal70_or_PhysX_equivalence=True,live_mutable_packets_excluded_from_stable_Git_capture_but_real_snapshots_archived=True))
 work=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012';work.mkdir(exist_ok=True);(work/'reports').mkdir(exist_ok=True)
 put(work/'reports/SCOPE_DECISION_ACTUAL.json',decision)
 print(json.dumps(dict(full153_complete=True,decision=str(R/'COMPLETE153_EPISODE_LIFETIME_AXIS_DECISION.json'),human_player_feedback_preserved=True,new_scope_prepare_pending=True)))
if __name__=='__main__':main()
