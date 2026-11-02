"""New finite373 package; never edit or rerun frozen368."""
from pathlib import Path
import ast,hashlib,json,shutil,time
P=Path(__file__).resolve().parent;T=P.parent
OLD=T/'MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102';N=T/'MPC_MATCHED_DR_AIR_REQUEST_V373_20261102'
assert not N.exists();N.mkdir();(N/'reports').mkdir()
shutil.copytree(OLD/'source',N/'source',ignore=shutil.ignore_patterns('__pycache__'))
def copytext(old,new):
 p=N/new;p.write_text((OLD/old).read_text('utf8').replace('368','373'),encoding='utf8');return p
for old,new in [('contract368.py','contract373.py'),('target368_parent.py','target373_parent.py'),('run368_probe_once.py','run373_probe_once.py'),('view368_actual_MPC_target_replay.py','view373_actual_MPC_target_replay.py'),('render368_recorded_frames.py','render373_recorded_frames.py'),('cpu368_control_request_no_step.py','cpu373_control_request_no_step.py')]:copytext(old,new)
for name in ['source/planned_hold368.py','source/evaluate368.py']:
 p=copytext(name,name.replace('368','373'));(N/name).unlink()
for name in ['planned_mpc_motor368.json','source353_gains.json','reference324.npz']:
 shutil.copyfile(OLD/name,N/name.replace('368','373'))
worker=N/'source/evaluate373.py';s=worker.read_text('utf8')
s=s.replace('"""Teacher-assisted depth SuperMimic; restored WM, migrated actor/critic, original finite owner."""','"""40 matched D0-D7 pairs: source vs bounded air-wheel request; zero NN."""')
s=s.replace(" real.reset();put('ACTUAL373_INITIAL_PHYSX_STATE.json'", " real.reset()\n from matched_DR373 import install_matched_pairs373\n pair_audit=install_matched_pairs373(real,TASK['seed'],max_feedback_ticks=1100)\n put('ACTUAL373_MATCHED_D0_D7_AND_NOISE_ADMISSION.json',pair_audit)\n put('ACTUAL373_INITIAL_PHYSX_STATE.json'")
s=s.replace("DR_same_distribution_not_matched=True", "DR_paired=True").replace("DR_same_distribution_not_exactpaired=True", "DR_paired=True").replace("DR_same_distribution_not_paired=True", "DR_paired=True")
s=s.replace(" selected=[0,1,40,41];old_scene_update", " selected=[0,1,40,41];recorded=list(range(80));old_scene_update")
s=s.replace("assert TASK['model_byte_reads']==TASK['model_decodes']==0", "assert TASK['model_byte_reads']==TASK['model_decodes']==0\n put('ACTUAL373_MATCHED_SENSOR_NOISE_FINAL.json',real._matched373_receipt())")
s=s.replace("frames.append(dict(pos=captured['pos'][selected]", "frames.append(dict(pos=captured['pos'][recorded]")
start=s.index("  frames.append(dict(pos=");end=s.index("  active&=~done.bool()",start)
s=s[:start]+s[start:end].replace('[selected]','[recorded]')+s[end:]
s=s.replace(" replay=[]\n for j,env_id in enumerate(selected):", " replay=[]\n discordant=[i for i in range(40)if results[i]['strict270_stable']!=results[i+40]['strict270_stable']]\n successful=[i for i in range(40)if results[i]['strict270_stable']or results[i+40]['strict270_stable']]\n chosen=[]\n for i in discordant+successful+list(range(40)):\n  if i not in chosen:chosen.append(i)\n  if len(chosen)==2:break\n replay_selected=[chosen[0],chosen[0]+40,chosen[1],chosen[1]+40]\n for env_id in replay_selected:\n  j=env_id")
s=s.replace('DR_paired=False,results=results', 'DR_paired=True,matched_pairs=40,matched_DR_admission=pair_audit,results=results')
worker.write_text(s,encoding='utf8')
# Correct visible replay scope in this independent version; recorded poses only.
p=N/'view373_actual_MPC_target_replay.py';s=p.read_text('utf8');s=s.replace("if r['result']['kind']in('state_target','processed_MPC_target')else[0,0,-10]",'')
s=s.replace('actual PhysX373 first episodes','actual PhysX373 traditional MPC first episodes').replace('PhysX373 final324 first episodes','PhysX373 traditional MPC first episodes')
s=s.replace('FINAL324 / NO NN / source target trace','TRADITIONAL MPC / NO NN / MATCHED DR').replace('actor terminal0 / WM H32','source vs bounded wheel request').replace('REFERENCE TRACKER: planned goals; use saved independent evaluation facts','MPC50Hz / full D0-D7 matched pairs / actual solver contact acceptance')
p.write_text(s,encoding='utf8')
task=json.loads((OLD/'TASK368_FROZEN.json').read_bytes());task=json.loads(json.dumps(task).replace('368','373'))
task['kind']='MPC_AIR_WHEEL_REQUEST_ENVELOPE_COMPARISON373'
task['human_request']='Matched40pair D0-D7 and common per-feedback-tick D1 noise, source vs bounded push/flight wheel request; original50/100/400Hz physical path and366manifold evaluation preserved. ZeroNN/account.'
task['distinct_evaluation_purpose']='Independent matchedDR finite comparison after unpaired368; no replay of consumed368.'
task['matched_pair_count']=40;task['D0_D7_matched_pairs']=True;task['common_sensor_noise_by_absolute_feedback_tick']=True
task['independent_new_measurement_purpose']='Actual373 matched D0-D7 comparison, actual firstflight wholefootprint/topmanifold/strict halfsecond retained.'
task['only_group40_79_airwheel_requested_torque_prebounded']=True
task['control_resampling']='Currentstate/eventMPC re-solved at50Hz with20ms predictiondt/H8; source100Hz not claimed.'
task['worker_SHA']='PENDING_HELPER_CPU_VALIDATION'
with(N/'TASK373_PREPARE_NOT_FROZEN.json').open('x',encoding='utf8')as f:json.dump(task,f,indent=2)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
print(json.dumps(dict(root=str(N),prepared=True,frozen=False,network=0,SDK=0,physics=0)))
