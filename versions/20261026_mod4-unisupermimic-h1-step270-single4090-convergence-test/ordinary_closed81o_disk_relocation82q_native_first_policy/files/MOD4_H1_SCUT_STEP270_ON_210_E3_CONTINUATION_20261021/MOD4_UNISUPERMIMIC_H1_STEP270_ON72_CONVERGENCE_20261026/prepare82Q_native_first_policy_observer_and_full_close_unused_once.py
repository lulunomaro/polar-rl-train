from pathlib import Path
import ast,json,time
H=Path(__file__).resolve().parent;T=H.parent;N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
old=N/'collect_actual82q_PPO_and_native_H1_policy_first_finite_unused_once.py';s=old.read_text('utf8');assert s.count('until=time.monotonic()+900')==1 and s.count('timeout=930')==1
s=s.replace('until=time.monotonic()+900','until=time.monotonic()+1200',1).replace('timeout=930','timeout=1230',1).replace('max_owner_wait=900','max_owner_wait=1200',1)
p=N/'collect_actual82q_native_policy_first_20min_finite_v2_unused_once.py';assert not p.exists();p.write_text(s,'utf8')
c=(P/'collect_actual_three80_finals_original_cost_unused_once.py').read_text('utf8').replace('THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','MIXED82Q_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
c=c.replace("q=v['q'];owner=Path(q['owner_root']);","q=v['q'];assert max(x['nominal_end_epoch'] for x in v['original_go'].values())-time.time()<=900;owner=Path(q['owner_root']);",1).replace('READ210,dict(q=q),timeout=900',"READ210,dict(q=q,original_go=metadata['source210']['current']['go']),timeout=900",1)
cp=N/'collect_actual82q_H1_PPO_native_method_E3_original_cost_unused_once.py';assert not cp.exists();cp.write_text(c,'utf8')
w=(B/'same_authorized_session_compressed_transport_v134.py').read_text('utf8');needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',";assert needle in w
wp=B/'same_authorized_session_compressed_transport_v135.py';assert not wp.exists();wp.write_text(w.replace(needle,needle+'\n        '+repr(p.name)+',\n        '+repr(cp.name)+',',1),'utf8')
for p in (p,cp):ast.parse(p.read_text('utf8'))
with (N/'reports/NATIVE_FIRST_POLICY_OBSERVER_ALLOWANCE_AND_ORIGINAL_CLOSURE_GATE_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),unrun_v1_first_reader_retained=True,new_unique_v2_first_policy_observer_max1200_seconds=True,reason='Real20k scene initialization plus48 warmup controls and10 native world-only iterations before policy update',no_training_timeout_or_owner_lifecycle_change=True,original3900_3600_300_and_closure900_local_remote_gates_retained=True,no_claim_of_first_policy_before_actual_receipt=True),f,indent=2)
print(json.dumps(dict(new_first_observer=p.name,original_closure900_retained=True)))
