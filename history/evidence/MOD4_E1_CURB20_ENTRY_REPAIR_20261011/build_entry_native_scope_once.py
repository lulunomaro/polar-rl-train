"""One new CPU/reset and SDK-native scope, keeping old source bytes intact."""
from repair_io import *
import ast,numpy as np
def write(path,t):
 assert not path.exists(),path;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.encode())
 if path.suffix=='.py':compile(t,str(path),'exec')
def main():
 source=D/'inherited_source/isaac/mod4';code=D/'payload/isaac/mod4'
 t=(source/'e1_full_pose_reset.py').read_text()
 old='    xy = env.scene.env_origins[ids, :2].clone()'
 assert t.count(old)==1
 t=t.replace(old,'    from curb20_entry_runtime import reset_entry_xy\n    xy = reset_entry_xy(env,ids)')
 t=t.replace('    env._rough_probe_reset_receipt = dict(','    env._rough_probe_reset_receipt = dict(independent_CURB_entry=env._curb_entry_map_receipt,')
 write(code/'curb20_entry_full_pose_reset.py',t)
 sys.path.insert(0,str(code));from curb20_entry_math import entry_map
 s=json.loads((W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB_TRAINING_RESET_ACTUAL_1791672164574719500.json').read_bytes())
 xy=np.array(s['spawn_xy']);bank=np.load(source/'MOD4_RESET_COLLISION_BANK.npz');pick=int(np.argmin(abs(bank['root_height']-.25)));pts=bank['points_root'][pick]
 # CPU mapping uses the exact retained grid geometry; actual generated member
 # assignment identities are rechecked on the new host during SDK/native.
 rows=[]
 for r in range(40):
  for c in range(40):rows.append(dict(row=r,column=c,family='random_uniform_for_rm' if c>=34 else 'background',bounds=[[r*9-180,c*9-180,0],[(r+1)*9-180,(c+1)*9-180,.02]]))
 moved,proof=entry_map(xy,rows,pts);again,_=entry_map(xy,rows,pts);assert np.array_equal(moved,again)
 assert proof['changed_environments']==2820 and np.array_equal(moved[np.floor((xy[:,1]+180)/9)<34],xy[np.floor((xy[:,1]+180)/9)<34])
 # Reject duplicate grid origins before deployment; strict footprint failure.
 try:entry_map(np.concatenate((xy[:1],xy[:1])),rows,pts)
 except ValueError:pass
 else:raise AssertionError('Duplicate placement accepted')
 save('ENTRY_RESET_COMPONENT_CPU_PASSED.json',dict(epoch=time.time(),passed=True,proof=proof,source_spawn_count=20000,bank_SHA=H((source/'MOD4_RESET_COLLISION_BANK.npz').read_bytes()),CPU_only=True,actual_generated_assignment_SDK_pending=True,no_causal_or_physical_pass_claim=True))
 native=(W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/implementation/native_e1_curbscope_probe.py').read_text()
 native=native.replace('from curb20_retention_runtime import','from curb20_entry_runtime import')
 native=native.replace("report['E1_reset_receipt']=env._rough_probe_reset_receipt;","report['E1_reset_receipt']=env._rough_probe_reset_receipt;report['CURB_entry_map']=env._curb_entry_map_receipt;")
 write(D/'payload/native_curb20_entry_probe.py',native)
 guard=(D/'inherited_source/reviewed_source_guard.py').read_text()
 guard=guard.replace("assert q.base.budget_state()['authorized_training_seconds']==828000 and q.base.sha(q.SOURCE)==q.SHA","from budget_authority import validate_budget\n assert validate_budget(q.base.budget_state())==1188000 and q.base.sha(q.SOURCE)==q.SHA\n assert len(q.base.budget_state()['budget_extensions'])==7")
 write(D/'payload/reviewed_budget005_source_guard.py',guard)
 for p in (D/'payload').rglob('*.py'):ast.parse(p.read_text())
 save('ENTRY_NATIVE_SCOPE_PREPARED.json',dict(epoch=time.time(),payload={p.relative_to(D/'payload').as_posix():H(p.read_bytes()) for p in (D/'payload').rglob('*') if p.is_file()},source_SHA=SHA,new_scope='Only actual CURB reset-entry positions; same20mm geometry/commands/clock/reward/DR',SDK_native_pending=True,fullstate_PPO_formal_not_yet_admitted=True,no_oldonce_replay=True))
 print(json.dumps(dict(CPU_passed=True,changed_roots=proof['changed_environments'],minimum_complete_footprint_support_m=proof['minimum_front_support_m'],SDK_native_pending=True)))
if __name__=='__main__':main()
