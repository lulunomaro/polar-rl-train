"""Admit only the reviewed send transport and own-channel close; preserve all node training AST."""
from pathlib import Path
import ast,hashlib,json
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(B,old,key):
 B=Path(B);old=Path(old);a=json.loads((B/'FORWARDED_NETWORK_CONTROL_AUTH_AND_CPU_ACTUAL.json').read_bytes())
 assert a['approved'] and a['human_authorization']=='开始训练；上台阶修复和提速一起' and key in ('h1','recovery')
 slot=a['slots'][key];node='three_slot_finite_node_v1.py';module='forwarded_original_owner_control_v1.py'
 assert H(old/node)==slot['old_node_SHA'] and H(B/node)==slot['new_node_SHA']
 assert H(B/module)==a['control_module_SHA']=='46372c53ad0987cf366ab906965e951fd4b87890750c913ed1ec3b4eb93833b7'
 guard='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 assert H(B/guard)==slot['new_guard_SHA']
 assert H(B/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json')==a['original_sampling_auth_SHA']
 text=(old/node).read_text('utf8');tree=ast.parse(text);f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='send');lines=text.splitlines(keepends=True)
 lines[f.lineno-1:f.end_lineno]=['def send(spec,row):\n',' from forwarded_original_owner_control_v1 import send as forwarded_send\n',' return forwarded_send(spec,row,b.PORT)\n'];expected=''.join(lines)
 needle='  if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()';assert expected.count(needle)==1
 expected=expected.replace(needle,'  from forwarded_original_owner_control_v1 import close as close_control\n  close_control()\n'+needle,1)
 assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse((B/node).read_text('utf8')),include_attributes=False)
 return dict(passed=True,key=key,only_original_HMAC_send_transport_and_own_channel_close_changed=True,worker_spawn_fullsave_childwait_terminal_retry_private_lock_AST_unchanged=True,control_module_SHA=a['control_module_SHA'],no_budget_writer_PPO_reward_physics_change=True)
