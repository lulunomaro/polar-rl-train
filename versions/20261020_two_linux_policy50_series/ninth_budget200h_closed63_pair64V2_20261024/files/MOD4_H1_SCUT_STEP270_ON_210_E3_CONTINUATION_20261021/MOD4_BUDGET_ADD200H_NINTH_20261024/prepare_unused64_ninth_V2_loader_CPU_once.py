from pathlib import Path
import ast,hashlib,json,shutil,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_NINTH_V2_20261024';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (P/'reports/PAIR_DEPLOY_STARTED_ACTUAL.json').is_file() and not (P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').exists();assert not N.exists();N.mkdir();(N/'reports').mkdir()
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(P/folder,N/folder)
for p in P.glob('*.py'):
 if p.name.startswith('UNUSED_'):continue
 s=p.read_text('utf8').replace('H1step270_reward_tuckclear4_2410v64/','H1step270_reward_tuckclear4_2410v64n9v2/');ast.parse(s);(N/p.name).write_text(s,'utf8')
p=N/'repair_sources/closed_production_continuation_CPU_v2.py';old=p.read_text('utf8');needle="        if rel.endswith('.py') and rel in prior and rel not in (trace,";assert old.count(needle)==1
extra="""        if rel=='three_slot_common_v1.py' and row['SHA']!=prior[rel]['SHA']:
            rec=read(B/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');ext=rec['explicit_ninth_extension_receipt'];assert ext['passed'] and ext['budget']['extension_id']=='USER_ADD200H_20261024_9TH' and ext['budget']['authorized_after']==2268000 and ext['budget']['extension_records']==9 and ext['budget']['charged_unchanged'] and ext['budget']['old_eight_extensions_unchanged']
            assert H(old/rel)==prior[rel]['SHA'] and H(B/rel)==row['SHA']
            expected=(old/rel).read_text('utf8').replace('1548000','2268000')
            assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse((B/rel).read_text('utf8')),include_attributes=False)
            continue
"""
s=old.replace(needle,extra+needle);ast.parse(s);assert s.replace(extra,'')==old;p.write_text(s,'utf8')
tree=ast.parse(s);assert any(isinstance(x,ast.If) and "rel == 'three_slot_common_v1.py'" in ast.unparse(x.test) for x in ast.walk(tree))
for name in ('h1_step270_sdk_runtime_candidate.py','h1_step270_path_reward_v1.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py'):assert H(N/'repair_sources'/name)==H(P/'repair_sources'/name)
src=B/'probe_original_budget_ninth_boundary_V2_once.py';prefix="from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom ninth_budget_ops import *\nimport traceback\n"
remote="""from pathlib import Path
import fcntl,json,os,psutil,time
roots=[Path(x) for x in v['roots']]
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for root in roots:
 assert not (root/'NODE_IDENTITY.json').exists() and not (root/'OWNER_IDENTITY.json').exists()
 if root.exists():assert not list(root.rglob('GO_PRODUCTION.json'))
for path in v['locks']:
 with Path(path).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),all_failed64_processes_out=True,no_GO_no_owner_no_fee=True,roots=[dict(path=str(p),exists=p.exists()) for p in roots],original_locks_free=True,no_raw_PT_or_GPU_read=True)))
"""
probe=prefix+'REMOTE='+repr(remote)+'''
try:
 put('FAILED64_PREOWNER_NO_GO_PROBE_STARTED.json',dict(epoch=time.time()));q=closed();pw=secret();c=d.connect72(pw);pw=None
 try:r72=d.code(c,d.PY72,REMOTE,dict(roots=['/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_reward_tuckclear4_2410v64/recovery'],locks=[q['specs']['recovery']['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock']),timeout=60)
 finally:c.close()
 c=d.t.connect()
 try:r210=d.code(c,d.t.PY,REMOTE,dict(roots=['/mnt/mod4_linux_durable_20261013/H1step270_reward_tuckclear4_2410v64/owner','/mnt/mod4_linux_durable_20261013/H1step270_reward_tuckclear4_2410v64/h1'],locks=[q['specs']['h1']['private_lock'],'/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock']),timeout=60)
 finally:c.close()
 put('FAILED64_INSTALLED_PREOWNER_NO_GO_TWOHOST_ALL_OUT_ACTUAL.json',dict(passed=True,source72=r72,source210=r210,no_budget_refund_or_recharge=True));print(json.dumps(dict(passed=True,no64_GO_no_fee=True,both_hosts_actual_out=True)))
except BaseException:
 put('FAILED64_OUT_PROBE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
''';q=B/'read_failed64_preowner_no_GO_allout_once.py';assert not q.exists();ast.parse(probe);q.write_text(probe,'utf8')
w=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v41.py';v=w.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";v=v.replace(needle,needle+"\n        'read_failed64_preowner_no_GO_allout_once.py',");wrapper=w.with_name('same_authorized_session_compressed_transport_v42.py');assert not wrapper.exists();ast.parse(v);wrapper.write_text(v,'utf8')
with (R/'UNUSED64_NINTH_V2_LOADER_BUDGET_ONLY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_deployed_yet=True,failed_original_namespace=P.name,new_namespace=N.name,old_loader_SHA=H(P/'repair_sources/closed_production_continuation_CPU_v2.py'),new_loader_SHA=H(p),only_explicit_ninth_receipt_and_exact_common_AST_budget_binding_allowed=True,all_remaining_loader_checks_AST_exact=True,runtime_reward_target_byteexact=True,original_failed64_source_and_error_preserved=True,new_probe=str(q),wrapper=str(wrapper)),f,indent=2)
print(json.dumps(dict(new_namespace=str(N),probe=str(q),wrapper=str(wrapper),AST=True)))
