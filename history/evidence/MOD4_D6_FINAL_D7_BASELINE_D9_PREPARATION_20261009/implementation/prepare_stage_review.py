"""Summarize actual completed behavior and bounded D9 preparation; no training."""
from pathlib import Path
import json,time,hashlib,math,statistics
D=Path(__file__).resolve().parent;R=D/'reports';BASE=D.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=sha(BASE/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md');assert master=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
d6=read(BASE/'MOD4_D6_FULL_CONTRACT_20261009/reports/D6_ACTUAL_BASELINE_SCOPE_REVIEW.json')
d7=read(BASE/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_ACTUAL_BASELINE_SCOPE_REVIEW.json')
actual=read(BASE/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_CURRENT_ACTUAL.json');pub=read(R/'D9_PUBLICATION_CURRENT_ACTUAL.json')
assert actual['attention'] is None and pub['actual_publisher'] and pub['reports']['D9_NOMINAL_ACTUAL_SDK_REVIEW.json']['interface_scope_accepted']
columns={};p=read(BASE/'MOD4_D7_FULL_CONTRACT_20261009/reports/stage_scope/clk2500-closure-episode-d3-98-d7-com-pd-anchor-flat/probe.json')
cp=p['chassis_PD_initial_episode_assignments']
for i in range(3):columns['COM_'+str(i)]=[row[i] for row in cp['COM']['delta_m']]
for name,rows in cp['PD']['factors'].items():columns['PD_'+name]=[row[0] for row in rows]
for group,key in (('spring','spring_pressure_initial_episode_assignments'),('gas','gas_damping_initial_episode_assignments')):
 for i in range(2):columns[group+'_'+str(i)]=[row[i] for row in p[key]['factor']]
for name,row in p['physical_action_initial_episode_assignments'].items():columns['action_'+name]=row['delay_us']
assert all(len(x)==80 for x in columns.values())
def corr(x,y):
 a=statistics.mean(x);b=statistics.mean(y);den=math.sqrt(sum((v-a)**2 for v in x)*sum((v-b)**2 for v in y))
 return sum((v-a)*(w-b) for v,w in zip(x,y))/den if den else None
correlations=[dict(a=a,b=b,r=corr(columns[a],columns[b])) for i,a in enumerate(columns) for b in list(columns)[i+1:]]
audit=dict(epoch=time.time(),actual_fixed_eval_population=80,source_probe_SHA=sha(BASE/'MOD4_D7_FULL_CONTRACT_20261009/reports/stage_scope/clk2500-closure-episode-d3-98-d7-com-pd-anchor-flat/probe.json'),observed_columns={n:dict(min=min(x),max=max(x),mean=statistics.mean(x)) for n,x in columns.items()},finite_population_correlations=correlations,D0_nominal_count=p['mild_initial_parameters']['nominal_environment_count'],D0_nominal_fraction=p['mild_initial_parameters']['nominal_environment_count']/80,D0_nominal_does_not_disable_D1_D7=True,private_RNG_contracts_reused_from_actual_CUDA_startup=True,finite_correlations_not_proof_of_statistical_independence=True,all_approved_corners_not_measured=True,no_new_distribution_or_bounds_or_learning=True)
(R/'D9_ACTUAL_COMBINATION_ASSIGNMENT_AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
v=dict(epoch=time.time(),master_SHA_unchanged=master,D6_final_model32950_actual_paired_review=d6['summary']['86-d6-gas-b3'],D6_complete_scope=d6['scope'],D7_baseline_actual_scope=d7['summary']['98-d7-com-pd-anchor'],D7_candidate_scope_pending=True,D7_actual_formal=actual,D9_publication_actual=pub,D9_assignment_audit=audit,RM_terrain_annotation_ref='MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md/json',new_PPO_learning_or_canonical_transactions=0,no_new45min_clock_test=True,old_failed_reader_and_raw_retained=True,D9_not_graduated=True,S8_not_authorized=True,MoE_gate_not_trained=True)
(R/'D6_FINAL_D7_BASELINE_D9_PREPARATION_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
note='''# D6 final retained behavior, D7 baseline and D9 parallel preparation

D6 own final32950 has completed all three matched frozen15s cases in the same3060/firstseed20261002/white_v3/D0-D6 gas protocol. World64/64, worst absolute signed full-circle netcross0.034110931m/s, along0.471265702–0.542358618m/s. Pure left/right4pi each8/8; straight negative/positive errors0.014762998/0.037485845m/s. Complete root/30q/parameters/recipes/assignments and returned JSON byteSHA were checked. Raw and original flags are retained; this is not dualseed/allprofile or hardware certification. The already reviewed31416 source remains unchanged in activeD7.

D7 COM-PD baseline31416 now has actual D0-D7 frozen function scope: world64/64, netcross0.040780827m/s, along0.478745829–0.545008760m/s, pure4pi each8/8, straight negative/positive errors0.030663744/0.056608647m/s. Actual chassis-only COM and explicit PD readbacks, motor implicitdrive0, old groups and all data were verified. D7 learned candidate behavior is still pending. The active own31775 checkpoint is finiteCPU94/source277/44snapshots/PID-bound; live9000control/36000callbacks has7ordinary events (6orientation,1closure), peak2.086289926mm, integrity/unknown/nonfinite/STOP absent. This is an activity snapshot, not final health or skill maturity. Closure only reset its affected environment under authorized healthv3.

D9 development retention is prepared without changing existing distributions. A new immutable D7 nominal-D0 lifecycle package has exactly the same white MildDR class AST and D1-D7 source paths; nominal factor1/mu0.9 has no private D0 draws/setters. One actual10env300control nominal interface case completed with original D7 groups, each actiongroup1200callbacks, targeterror0, physics pass, nonfinitefalse. Its selected SDK reset[1,4,7] increments only those COM/PD episodes and preserves other rows. Original first CPU publisher erroneously required all assignments unchanged and exited; its source/attention are retained. A distinct CPU reset-aware reader reused the same completed case; no GPU repeat or4090 interruption. Current new reader is waiting for explicit actual fullpaired D7 source review.

The CPU-only publisher will accept SELECTED_D7_BEHAVIOR_SOURCE.json only after an actual stable PASSED/fullCPU94/source277/44snapshots/ownPID/unique completed segment and full three paired behavior cases are reviewed. It reuses the exact firstseed-white3 cases and publishes only15 new conditions for18 development cases (2seeds x D0nominal/white_v2/white_v3 x flat/spin/world), retaining D1-D7. They are not clean or heldout. It has no GPU/PPO/canonical/training-launch authority, holds on invalid evidence, and does not choose directory-max or preflight weights. No D9 learning executor or new distribution has been installed.

Observed assignment ranges/correlations and D0 nominal count are recorded as finite-population diagnostics, not proof of independence or allcorner coverage. Existing actual CUDA private-RNG/reset/save contracts and valid native/fullPPO scope are reused. No repeated45min clock or same-scope PPO. Future work must complete actual pairedD7 selection, review18 development cases and remaining approved corner evidence, then progress approved independentE1 rather than indefinitely stackingE0. S3/E1 and S7/E1-E2 must reference the new RM terrain spin exclusions and entrance lip annotation. Masterv1.5 SHA remains unchanged, canonical230h/six extensions/new0, S8 newdangerous reset still requires later specific approval, gate untrained, D8 load/absolute jointfriction/hardware force-stroke unmeasured.
'''
(R/'D6_FINAL_D7_BASELINE_D9_PREPARATION_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(dict(D6_final_reviewed=True,D7_baseline_accepted=True,D7_candidate_pending=True,D9_nominal_interface_accepted=True,publisher=pub['actual_publisher'],remaining_snapshot_seconds=actual['actual_tail_adjusted_remaining_seconds'],new_learning_transactions=0)))
