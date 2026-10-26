from pathlib import Path
import ast,json,time
H=Path(__file__).resolve().parent;T=H.parent;O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=(O/'collect_actual_mixed81o_PPO_and_H1_native_policy_first_finite_unused_once.py').read_text(encoding='utf8');tree=ast.parse(old)
get=lambda k:next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==k for t in n.targets))
r210=get('READ210');start=r210.index(';until=time.monotonic()+900');end=r210.index("C=Path('/home/egde")
r210=r210[:start]+"\ncurrent=json.loads((B/'OWNER_CURRENT.json').read_bytes());rows=current['rows'];go=current['go'];assert set(go)=={'h1','e2','recovery'}\nassert all((rows[k].get('latest_save') or {}).get('updates',0)>0 and not rows[k].get('original_error') for k in ('h1','recovery'))\nassert rows['e2']['original_error'] and rows['e2']['terminal_all_own_children_waited']\n"+r210[end:]
r72=get('READ72')
main='''from pathlib import Path
import importlib.util,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
'''+f'READ210={r210!r}\nREAD72={r72!r}\n'+'''try:
 q=json.loads((R/'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('MISSING_HEALTHY_PAIR_AND_ALL_GO_CLOCK_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,one_missing_identity_clock_read_not_watcher=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:a=d.code(c,route.PY,READ210,dict(owner=q['owner_identity'],root=q['roots']['h1'],source_SHA=q['sources']['h1']['SHA'],GPU_UUID=q['specs']['h1']['GPU_UUID'],run_id=q['run_id']),timeout=90)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);c=d.connect72(m.recover())
 try:b=d.code(c,d.PY72,READ72,dict(root=q['roots']['recovery'],row=a['current']['rows']['recovery'],run_id=q['run_id'],source_SHA=q['sources']['recovery']['SHA'],GPU_UUID=q['specs']['recovery']['GPU_UUID'],key='recovery'),timeout=60)
 finally:c.close()
 result=dict(epoch=time.time(),passed=True,actual_finite_returned=True,run_id=q['run_id'],source210=a,target72=dict(recovery=b),only_H1_E3_actual_PPO_UUID_identity_verified=True,failed_method_not_PPO_or_convergence=True,all_three_original_GO_clocks_recovered=True,earliest_close_epoch=max(x['nominal_end_epoch'] for x in a['current']['go'].values())-900)
 put('HEALTHY_PAIR_PPO_UUID_IDENTITY_AND_ALL_ORIGINAL_GO_CLOCKS_ACTUAL.json',result);print(json.dumps(dict(passed=True,healthy_updates={k:a['current']['rows'][k]['latest_save']['updates'] for k in ('h1','recovery')},earliest_close_epoch=result['earliest_close_epoch'],failed_method_not_success=True)))
except BaseException:
 put('MISSING_HEALTHY_PAIR_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
'''
name='read_missing81o_healthy_PPO_identities_and_all_original_GO_clocks_unused_once.py';p=O/name;assert not p.exists();p.write_text(main,encoding='utf8')
# Original closure/read/capture logic retained. A failed slot is preserved as an empty model list.
c=(T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026/collect_actual_three80_finals_original_cost_unused_once.py').read_text(encoding='utf8')
c=c.replace('THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','HEALTHY_PAIR_PPO_UUID_IDENTITY_AND_ALL_ORIGINAL_GO_CLOCKS_ACTUAL.json')
c=c.replace("assert metadata['passed'] and metadata['actual_finite_returned']","assert metadata['passed'] and metadata['actual_finite_returned'] and metadata['failed_method_not_PPO_or_convergence']")
# Add remote <=900 gate using the exact actual GO clocks recovered above.
c=c.replace("q=v['q'];owner=Path(q['owner_root']);", "q=v['q'];assert max(x['nominal_end_epoch'] for x in v['original_go'].values())-time.time()<=900;owner=Path(q['owner_root']);")
c=c.replace('READ210,dict(q=q),timeout=900','READ210,dict(q=q,original_go=metadata[\'source210\'][\'current\'][\'go\']),timeout=900')
c=c.replace("not_skill_qualification=True)","not_skill_qualification=True,failed_method_preserved_not_PPO_or_convergence=True)")
cp=O/'collect_closed81o_healthy_FINALs_failed_method_original_all_cost_unused_once.py';assert not cp.exists();cp.write_text(c,encoding='utf8')
for p in (p,cp):ast.parse(p.read_text(encoding='utf8'))
w=(B/'same_authorized_session_compressed_transport_v129.py').read_text(encoding='utf8');needle='target.name in {'
# allowlist uses an assert followed by the literal set; insert before existing exact name.
needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',"
assert needle in w
w=w.replace(needle,needle+f"\n        '{name}',\n        '{cp.name}',",1)
wp=B/'same_authorized_session_compressed_transport_v130.py';assert not wp.exists();wp.write_text(w,encoding='utf8')
(H/'reports/MISSING_CLOCK_READER_AND_PARTIAL_COHORT_CLOSURE_PROTOCOL_SOURCE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),reader=str(p),collector=str(cp),transport=str(wp),healthy_model_keys=['h1','recovery'],failed_method_model_expected_absent=True,original_all_three_cost_and_locks_unchanged=True,no_controller_or_budget_change=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,reader=name,collector=cp.name)))
