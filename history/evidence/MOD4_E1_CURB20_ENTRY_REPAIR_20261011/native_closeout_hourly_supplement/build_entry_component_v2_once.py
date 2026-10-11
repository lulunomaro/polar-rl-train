from repair_io import *
import numpy as np,ast
def write(path,t):
 assert not path.exists(),path;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.encode())
 if path.suffix=='.py':compile(t,str(path),'exec')
def main():
 C=D/'payload/isaac/mod4';S=D/'inherited_source/isaac/mod4'
 save('ENTRY_COMPONENT_V1_CPU_REJECTED.json',dict(epoch=time.time(),trial_id='CURB20-ENTRY-CPU-01',actual_error='ValueError: Complete footprint outside actual cell',failed_before_GPU=True,reason='Original Y grid may be within 0.292m collision extent of a cell edge; explicit full-cell containment rejected.',original_math_SHA=H((C/'curb20_entry_math.py').read_bytes()),original_builder_SHA=H((D/'build_entry_native_scope_once.py').read_bytes()),original_false_preserved=True,physical_failure=False))
 t=(C/'curb20_entry_math.py').read_text().replace("PROFILE='CURB20_actual_cell_entry_reset_v1'","PROFILE='CURB20_actual_cell_entry_reset_v2'")
 t=t.replace('  u=old[ids,0]-center[0]','  xy[ids,1]=np.clip(xy[ids,1],b[0,1]+extent[1]+.004,b[1,1]-extent[1]-.004)\n  u=old[ids,0]-center[0]')
 write(C/'curb20_entry_v2_math.py',t)
 t=(C/'curb20_entry_runtime.py').read_text().replace('curb20_entry_math','curb20_entry_v2_math').replace('curb20_entry_full_pose_reset','curb20_entry_v2_full_pose_reset')
 write(C/'curb20_entry_v2_runtime.py',t)
 t=(C/'curb20_entry_full_pose_reset.py').read_text().replace('curb20_entry_runtime','curb20_entry_v2_runtime')
 write(C/'curb20_entry_v2_full_pose_reset.py',t)
 sys.path.insert(0,str(C));from curb20_entry_v2_math import entry_map
 s=json.loads((W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB_TRAINING_RESET_ACTUAL_1791672164574719500.json').read_bytes());xy=np.asarray(s['spawn_xy'])
 bank=np.load(S/'MOD4_RESET_COLLISION_BANK.npz');pick=int(np.argmin(abs(bank['root_height']-.25)));pts=bank['points_root'][pick]
 rows=[dict(row=r,column=c,family='random_uniform_for_rm' if c>=34 else 'background',bounds=[[r*9-180,c*9-180,0],[(r+1)*9-180,(c+1)*9-180,.02]]) for r in range(40) for c in range(40)]
 moved,proof=entry_map(xy,rows,pts);again,_=entry_map(xy,rows,pts);assert np.array_equal(moved,again) and proof['changed_environments']==2820
 mask=np.floor((xy[:,1]+180)/9)<34;assert np.array_equal(moved[mask],xy[mask])
 try:entry_map(np.concatenate((xy[:1],xy[:1])),rows,pts)
 except ValueError:pass
 else:raise AssertionError('Duplicate placement accepted')
 save('ENTRY_V2_COMPONENT_CPU_PASSED.json',dict(epoch=time.time(),trial_id='CURB20-ENTRY-CPU-02',passed=True,proof=proof,CPU_only=True,actual_generated_assignment_SDK_pending=True,no_command_rng_change=True,no_physical_or_causal_pass_claim=True))
 native=(W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/implementation/native_e1_curbscope_probe.py').read_text().replace('from curb20_retention_runtime import','from curb20_entry_v2_runtime import')
 native=native.replace("report['E1_reset_receipt']=env._rough_probe_reset_receipt;","report['E1_reset_receipt']=env._rough_probe_reset_receipt;report['CURB_entry_map']=env._curb_entry_map_receipt;")
 write(D/'payload/native_curb20_entry_v2_probe.py',native)
 guard=(D/'inherited_source/reviewed_source_guard.py').read_text().replace("assert q.base.budget_state()['authorized_training_seconds']==828000 and q.base.sha(q.SOURCE)==q.SHA","from budget_authority import validate_budget\n assert validate_budget(q.base.budget_state())==1188000 and q.base.sha(q.SOURCE)==q.SHA\n assert len(q.base.budget_state()['budget_extensions'])==7")
 write(D/'payload/reviewed_budget005_source_guard.py',guard)
 save('ENTRY_NATIVE_V2_SCOPE_PREPARED.json',dict(epoch=time.time(),source_SHA=SHA,payload={p.relative_to(D/'payload').as_posix():H(p.read_bytes()) for p in (D/'payload').rglob('*') if p.is_file() and '__pycache__' not in p.parts},CPU_passed=True,new_SDK_native_pending=True,fullstate_PPO_formal_not_yet_admitted=True,new_budget_seconds=0))
 print(json.dumps(dict(CPU_passed=True,changed_roots=2820,minimum_complete_footprint_support_m=proof['minimum_front_support_m'],SDK_native_pending=True)))
if __name__=='__main__':main()
