from pathlib import Path
import ast,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();norm=lambda s:ast.dump(ast.parse(s),include_attributes=False)
grant=read(R/'NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json');before=read(R/'ORIGINAL_BUDGET_NINTH_BEFORE_ACTUAL.json')['source210'];assert grant['passed'] and grant['budget']['authorized_after']==2268000 and grant['budget']['extension_records']==9 and grant['budget']['charged_seconds']==before['charged'] and grant['budget']['completed_digest']==before['completed_digest']
assert not any((N/x).exists() for x in ('payloads','controllers','reports/PAIR_DEPLOY_STARTED_ACTUAL.json','reports/PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json'))
saved=B/'unused64_sources_before_binding';saved.mkdir();rows=[]
def binding(s):return s.replace('1548000','2268000').replace("len(c['budget_extensions'])==8","len(c['budget_extensions'])==9")
for folder in (N,N/'paired_controllers',N/'h1_only_controllers'):
 for p in folder.glob('*.py'):
  if p.name.startswith('UNUSED_'):continue
  old=p.read_text('utf8');new=binding(old)
  if new==old:continue
  assert norm(new.replace('2268000','1548000').replace("len(c['budget_extensions'])==9","len(c['budget_extensions'])==8"))==norm(old)
  dst=saved/p.relative_to(N);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(old,'utf8');p.write_text(new,'utf8');rows.append(dict(path=str(p),old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(p),only_total_and_count_AST=True))
# Shared imported deployer remains unchanged; bind only this unused caller's OWNER expression.
for filename in ('deploy_selected_pair_unused_once.py','deploy_selected_H1_only_unused_once.py'):
 p=N/filename;s=p.read_text('utf8');needle='import deploy_two50_reconciled_original_writer_once as d';assert s.count(needle)==1;s=s.replace(needle,needle+'\n'+"d.OWNER=d.OWNER.replace('1548000','2268000').replace(\"len(c['budget_extensions'])==8\",\"len(c['budget_extensions'])==9\")");ast.parse(s);p.write_text(s,'utf8')
p=N/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py';s=p.read_text('utf8');old=s;(saved/p.name).write_text(old,'utf8')
needle=" assert proof['remaining_actual_snapshot']>82512.86069250107";assert s.count(needle)==1
insert=""" extension=read(T/'MOD4_BUDGET_ADD200H_NINTH_20261024/reports/NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json');assert extension['passed'] and extension['budget']['authorized_after']==2268000 and extension['budget']['extension_records']==9
 if P.name=='H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024':
  assert abs(proof['remaining_actual_snapshot']+720000-extension['budget']['remaining_seconds'])<1e-7
  proof=dict(proof,remaining_actual_snapshot=extension['budget']['remaining_seconds'])
"""
s=s.replace(needle,insert+needle)
needle=" put('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)";s=s.replace(needle," rec.update(authorized_total=2268000,extension_records=9,explicit_ninth_extension_receipt=extension)\n"+needle);ast.parse(s);p.write_text(s,'utf8')
# Exact budget-only TLS source binding; reuse passed transport tests, not rerun them.
old=T/'forensic_tls_peer_transfer_V96_V4.py';s=old.read_text('utf8');needle="budget['authorized_training_seconds']==1548000 and len(budget['budget_extensions'])==8";assert s.count(needle)==1;new=s.replace(needle,"budget['authorized_training_seconds']==2268000 and len(budget['budget_extensions'])==9");assert norm(new.replace("budget['authorized_training_seconds']==2268000 and len(budget['budget_extensions'])==9",needle))==norm(s)
proto=T/'forensic_tls_peer_transfer_V96_V5_NINTH.py';assert not proto.exists();proto.write_text(new,'utf8');sha=H(proto)
with (T/'reports/V96_V5_NINTH_PROTOCOL_BUDGET_BINDING_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,source_SHA=sha,old_source_SHA=H(old),only_authorized_total_and_extension_count_AST=True,passed_TLS_HMAC_CPU_reference='V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json',no_protocol_reexecution=True),f,indent=2)
for filename in ('relocate_selected_pair_closed_forensics_unused_once.py','relocate_selected_H1_closed_forensics_unused_once.py'):
 p=N/filename;s=p.read_text('utf8');s=s.replace('forensic_tls_peer_transfer_V96_V4.py',proto.name).replace('V96_V4_TARGET_PROTOCOL_INSTALLED_SOURCE_AST_ACTUAL.json','V96_V5_NINTH_PROTOCOL_BUDGET_BINDING_AST_ACTUAL.json');ast.parse(s);p.write_text(s,'utf8')
# New, unused closed63 storage support takes the extension receipt's pre-next-GO balance.
src=P/'relocate_selected_pair_closed_forensics_unused_once.py';s=binding(src.read_text('utf8')).replace('forensic_tls_peer_transfer_V96_V4.py',proto.name).replace('V96_V4_TARGET_PROTOCOL_INSTALLED_SOURCE_AST_ACTUAL.json','V96_V5_NINTH_PROTOCOL_BUDGET_BINDING_AST_ACTUAL.json')
needle="    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']";assert s.count(needle)==1
s=s.replace(needle,needle+"\n    extension=read(T/'MOD4_BUDGET_ADD200H_NINTH_20261024/reports/NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json');assert extension['passed'];assert abs(proof['remaining_actual_snapshot']+720000-extension['budget']['remaining_seconds'])<1e-7;proof=dict(proof,remaining_actual_snapshot=extension['budget']['remaining_seconds'])")
dest=P/'relocate_closed63_after_ninth_extension_unused_once.py';assert not dest.exists();ast.parse(s);dest.write_text(s,'utf8')
oldw=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v38.py';s=oldw.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";s=s.replace(needle,needle+"\n        'relocate_closed63_after_ninth_extension_unused_once.py',");wrapper=oldw.with_name('same_authorized_session_compressed_transport_v39.py');assert not wrapper.exists();ast.parse(s);wrapper.write_text(s,'utf8')
tests=[]
for mode in ('paired_controllers','h1_only_controllers'):
 tree=ast.parse((N/mode/'three_slot_finite_owner_v1.py').read_text('utf8'));guard=next(x.test for x in ast.walk(tree) if isinstance(x,ast.Assert) and 'authorized_training_seconds' in ast.unparse(x.test));fn=compile(ast.Expression(guard),'<actual_owner_guard>','eval')
 class Stub:CAPS={'h1':3900,'recovery':3900}
 for label,total,count,remaining,active,expected in [('extended',2268000,9,grant['budget']['remaining_seconds'],None,True),('oldtotal',1548000,9,802000,None,False),('oldcount',2268000,8,802000,None,False),('equal',2268000,9,82512.86069250107,None,False),('above',2268000,9,82512.86069250108,None,True),('active',2268000,9,802000,{'id':1},False)]:
  c=dict(active_segment=active,authorized_training_seconds=total,budget_extensions=[{}]*count,remaining_training_seconds=remaining);got=eval(fn,dict(c=c,b=Stub,specs={'h1':{},'recovery':{}}));assert got==expected;tests.append(dict(mode=mode,name=label,passed=True,admitted=got))
 tree=ast.parse((N/mode/'three_slot_common_v1.py').read_text('utf8'));ns={};exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('terminal','charge_values')],type_ignores=[]),'<charge_only>','exec'),ns)
 c=dict(charged_training_seconds=1465916.3691596985,remaining_training_seconds=802083.6308403015);a=dict(experts={},charged_expert_seconds=0.);go={k:dict(learning_started_epoch=t,max_parent_seconds=3900) for k,t in [('h1',100.),('recovery',110.)]};ns['charge_values'](c,a,go,{},120.);rows2={'h1':dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=125.)};ns['charge_values'](c,a,go,rows2,130.);rows2['recovery']=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=132.);ns['charge_values'](c,a,go,rows2,140.);assert a['charged_expert_seconds']==47.;tests.append(dict(mode=mode,name='independent_terminal_sumonce47',passed=True))
with (R/'NINTH_UNUSED64_AND_PROTOCOL_BINDING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,changes=rows,CPU_cases=tests,protocol_source=str(proto),protocol_SHA=sha,storage_helper=str(dest),wrapper=str(wrapper),no_active_source_or_physics_reward_change=True,original_82512_guard_and_7800_reserve_preserved=True,old_sources_retained=str(saved),no_GO_or_hostquery=True),f,indent=2)
print(json.dumps(dict(passed=True,CPU_cases=len(tests),protocol_SHA=sha,storage_helper=str(dest),wrapper=str(wrapper))))
