"""New explicitly requested latest116 physical motion/blue imagination purpose.
Derive a fresh118 namespace from completed112 source, never execute an old entry.
"""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
OLD=T/'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029'
S=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029';assert not S.exists();(S/'code').mkdir(parents=True);(S/'reports').mkdir()
Q=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1';qual=json.loads((Q/'reports/NATIVE116_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json').read_bytes());assert qual['passed']
model=qual['model'];pub=model['original_producer'];assert model['SHA']=='78f5840ec3db38a3fe2c8c16852b81a5bc7f02b445acd4a7901dafc7078d9976'
replacements=[('fudan112','fudan118'),('native112','native118'),('FROZEN112','FROZEN118'),('NEW112','NEW118'),('SOURCE112','SOURCE118'),('SOURCE108','SOURCE118'),('not_actual108','not_actual118'),('qualified111','qualified116'),('source_qualified111','source_qualified116'),('NATIVE111','NATIVE116'),('native111','native116'),('original111','original116'),('admitted111','admitted116'),('for qualified111','for qualified116'),('MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029','MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029'),('TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3','TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'),('TWO111','TWO116'),('MOD4_H1_FUDAN270_REWARD_COHERENCE_2610v111','MOD4_H1_DIRECT_COMMAND_2610v116'),('MOD4_H1_NATIVE111_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029v112','MOD4_H1_NATIVE116_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029v118'),('MOD4_H1_NATIVE111_FUDAN270_FROZEN_MOTION_WM_DIAG_','MOD4_H1_NATIVE116_FUDAN270_FROZEN_MOTION_WM_DIAG_'),('FROZEN_NATIVE111','FROZEN_NATIVE116'),('payloads_v2/seed27','payloads/seed27'),('H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029','H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029'),('24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12',model['SHA']),('256235849',str(model['bytes'])),("native['iteration']==18597","native['iteration']=="+str(pub['updates'])),("publication['world_updates']==185970","publication['world_updates']=="+str(pub['world_updates'])),("publication['policy_updates']==17893","publication['policy_updates']=="+str(pub['policy_updates']))]
sources=list((OLD/'code').glob('*.py'))+[OLD/'run_NEW112_qualified111_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py',OLD/'verify_SOURCE112_actual_phase_and_contiguous_window_CPU_synthetic_UNUSED_once.py']
rows=[]
for path in sources:
    original=path.read_bytes();s=original.decode('utf8');name=path.name
    for a,b in replacements:s=s.replace(a,b);name=name.replace(a,b)
    ast.parse(s);dest=S/('code/'+name if path.parent.name=='code' else name);dest.write_text(s,encoding='utf8',newline='\n')
    rows.append(dict(original=str(path),original_SHA=hashlib.sha256(original).hexdigest(),selected=str(dest),selected_SHA=hashlib.sha256(dest.read_bytes()).hexdigest()))
entry=S/'run_NEW118_qualified116_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py';assert entry.is_file()
assert (N/'payloads/seed27/THREE_SLOT_COMPLETE_MANIFEST_V1.json').is_file()
helper=(S/'code/run_native118_frozen_flat_WM_N1_once.py').read_text(encoding='utf8');assert helper.count('torch.load(')==1
assert "native['iteration']=="+str(pub['updates']) in helper and model['SHA'] in helper
with (S/'SOURCE118_EXACT_QUALIFIED116_AND_USER_VISUAL_PURPOSE.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),user_request='latest116 in MuJoCo with actual gray and blue imagined motion',new_purpose=True,one_new_physical_case20s=True,old112_entry_not_executed=True,source_model=model,rows=rows,actual_entry=str(entry),no_model_raw_SDK_GPU_SSH_or_account_action_yet=True),f,indent=2)
print(json.dumps(dict(prepared=True,folder=str(S),entry=str(entry),native_iteration=pub['updates'],WM=pub['world_updates'],Pi=pub['policy_updates'])))
