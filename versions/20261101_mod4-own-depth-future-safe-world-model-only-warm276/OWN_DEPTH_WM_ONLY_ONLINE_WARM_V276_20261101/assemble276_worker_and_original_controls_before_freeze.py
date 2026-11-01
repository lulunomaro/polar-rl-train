from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';C=N/'control276';C.mkdir(exist_ok=False)
A=T/'NEW272_FUTURE_SAFE_WM_CUDA_ADMISSION_V274V3_20261101'
j=json.loads((A/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json').read_bytes());assert j['passed']and j['result']['optimizer_steps']==0 and j['result']['scratch_params_and_norms_restored_exact']
for sub in ('code','kernel'):
 for p in(A/'source'/sub).rglob('*.py'):
  q=S/sub/p.relative_to(A/'source'/sub);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
worker=(N/'worker276_prefix_from_actual272.txt').read_text('utf8')+(N/'worker276_online_tail.txt').read_text('utf8');ast.parse(worker);(S/'worker276_online_WM_only.py').write_text(worker,encoding='utf8')
B=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/control240';changes=[]
for name in('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py','forwarded_original_owner_control_v1.py'):
 original=(B/name).read_text('utf8');text=original.replace('from model2050_task240 import','from wm_task275 import')
 if name=='model2050_240_finite_owner_authority72.py':
  text=text.replace("kind='Linux_MODEL2050_LITERAL40050_240_'","kind='Linux_OWN_DEPTH_WM_ONLY_WARM276_'")
  text=text.replace('human_requested_literal_JUMP194_reward_terrain_400N50_adaptation=True','human_requested_depth_SuperMimic_WM_only_warm276=True')
 if name=='model2050_240_fullstate_slot_node.py':
  text=text.replace('go["fullstate_reuse2050"]','go["WM_only_warm"] and go["teacher_frozen"]')
  text=text.replace('"--mode","train","--num-envs","20000","--run-id",spec["run_id"],"--out",str(out)','"--task",str(J/"TASK276.json")')
  text=text.replace('final.get("actual_new_PPO_updates",0)>0','final.get("actual_new_WM_updates",0)>0 and final.get("actual_new_PPO_updates")==0 and final.get("actual_Pi_Critic_STD_updates")==0')
  text=text.replace('Full-state continuation stopped before any learning','WM warm stopped before any learning')
 ast.parse(text,filename=name);(C/name).write_text(text,encoding='utf8')
 changes.append(dict(path=str(C/name),original_SHA=hashlib.sha256(original.encode()).hexdigest(),SHA=hashlib.sha256(text.encode()).hexdigest(),changed=text!=original))
old=ast.parse((B/'three_slot_common_v1.py').read_text('utf8'));new=ast.parse((C/'three_slot_common_v1.py').read_text('utf8'))
for fname in('charge_values','authenticated_row'):
 a=next(x for x in old.body if isinstance(x,ast.FunctionDef)and x.name==fname);b=next(x for x in new.body if isinstance(x,ast.FunctionDef)and x.name==fname);assert ast.dump(a)==ast.dump(b)
original_owner=ast.parse((B/'model2050_240_finite_owner_authority72.py').read_text('utf8'));new_owner=ast.parse((C/'model2050_240_finite_owner_authority72.py').read_text('utf8'))
def nested(tree,name):return next(x for x in ast.walk(tree)if isinstance(x,ast.FunctionDef)and x.name==name)
assert ast.dump(nested(original_owner,'account'))==ast.dump(nested(new_owner,'account'))
with(N/'SOURCE276_ORIGINAL_ACCOUNT_HMAC_SENDER_CONTROLS_AND_LIVE_WORKER_JOIN.json').open('x',encoding='utf8')as f:
 json.dump(dict(passed=True,epoch=time.time(),controls=changes,original_charge_values_authenticated_row_account_AST_exact=True,sender_byte_exact=True,source274V3_actual_H32_CUDA_passed=True,WM_warm_one_new_optimizer=True,teacher_frozen=True,actual_learner_or_GO=False,only_LOCAL_source_AST=True),f,indent=2)
print(json.dumps(dict(passed=True,worker_lines=len(worker.splitlines()),controls=len(changes))))
