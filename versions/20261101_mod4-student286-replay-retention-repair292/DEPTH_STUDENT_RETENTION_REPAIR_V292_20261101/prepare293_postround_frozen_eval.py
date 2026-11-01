"""Freeze next evaluation implementation before292 closes; Task binds new final later."""
from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'TEACHER286_REPLAY_EVAL_V288_20261101';D=N/'postround292';D.mkdir(exist_ok=False)
S=D/'eval293_source';S.mkdir()
worker=(O/'source/evaluate288.py').read_text('utf8').replace('288','293')
worker=worker.replace("ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE' and ck['actual_new_Pi_updates']==2336", "ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT292_COMPLETE' and ck['actual_new_Pi_updates']==TASK['expected_Pi_updates']")
worker=worker.replace('seconds=(int(counts[i])+1)*.02','seconds=int(counts[i])*.02')
worker=worker.replace('previous_air=torch.zeros_like(active);physics_counts=', 'previous_air=torch.zeros_like(active);support_seen=torch.zeros_like(active);physics_counts=')
worker=worker.replace('previous,previous_air,phys_calls','previous,previous_air,support_seen,phys_calls')
worker=worker.replace('  first_air+=(airborne&~previous_air&active).long();first=first_air==1', '  support_seen|=(torch.linalg.vector_norm(wf,dim=-1)>1).all(-1)&active\n  first_air+=(airborne&~previous_air&active&support_seen).long();first=(first_air==1)&support_seen')
for name,text in (('evaluate293.py',worker),('terrain293.py',(O/'source/terrain288.py').read_text('utf8'))):
    p=S/name;p.write_bytes(text.encode());ast.parse(text)
contract='''def validate_task(t):
    assert t['kind']=='FROZEN292_RETENTION_FINAL_HELDOUT270_GROUND_EVAL293'
    assert len(t['model_SHA'])==64 and t['model_bytes']>0 and t['expected_Pi_updates']>0
    assert t['num_envs']==80 and t['seed']==9137 and t['max_controls']==400
    assert t['physics_dt']==.0025 and t['policy_hz']==50 and t['feedback_hz']==100 and t['TGS']==[32,4]
    assert t['closure_m']==.01 and t['mimic_rad']==.01
    assert t['optimizer_steps']==t['account_writes']==0 and t['model_byte_reads']==t['model_decodes']==1
    return True

def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
    assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
    assert c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
    return True
'''
(S/'contract293.py').write_bytes(contract.encode());ast.parse(contract)
runner=(O/'run288_eval_once.py').read_text('utf8').replace('288','293')
runner=runner.replace("patterns='run293_eval|", "patterns='postround292|collect292_|launch292_|run293_eval|")
(D/'run293_eval_once_template.py').write_bytes(runner.encode());ast.parse(runner)
viewer=(O/'view288_actual_final286_replay.py').read_text('utf8').replace('288','293').replace('286','292')
viewer=viewer.replace("'Final292 / actual PhysX293 replay / evaluation failed'", "'Final292 / actual PhysX293 recorded replay'")
(D/'view293_actual_final292_replay_template.py').write_bytes(viewer.encode());ast.parse(viewer)
print(json.dumps(dict(passed=True,directory=str(D),worker_SHA=hashlib.sha256((S/'evaluate293.py').read_bytes()).hexdigest())))
