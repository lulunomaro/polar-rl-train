"""Prepare a new unique stage archive, without reusing a consumed recorder."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;W=B.parent
original=W/'MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019/archive_thirteenth_closed_sources_local_drift_unique_once.py'
destination=B/'archive_fourteenth_closed_sources_local_recovery_unique_once.py';assert not destination.exists()
source=original.read_text('utf8')
def replace(old,new):
 global source
 assert source.count(old)==1,(old[:100],source.count(old));source=source.replace(old,new)
replace("G=W/'MOD4_SCUT_FUDAN_TWELFTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019'")
replace("BASE='3dd619752f8b3699a3d9ece593c2da23bc467ece';ID='scut-fudan-thirteenth-hour-closed-sources-local-recovery-drift-review'","BASE='67d4bd5295f307a0ea8b7668f1cc705e4df9f7d5';ID='scut-fudan-fourteenth-hour-closed-sources-local-yaw-recovery-review'")
replace("TITLE='Continue all three experts from twelfth-hour full finals and preserve local late-yaw and stopping regression'","TITLE='Continue three experts from thirteenth-hour full finals and retain measured local recovery and stopping observations'")
source=source.replace('340946','352710')
replace('AUTOMATION_ACTUAL_THIRTEENTH_LOCAL_YAW_DRIFT_V36_ARGS.json','AUTOMATION_ACTUAL_FOURTEENTH_LOCAL_YAW_HOLD_V37_ARGS.json')
replace('AUTOMATION_V36_THIRTEENTH_ACTUAL_READBACK_CPU.json','AUTOMATION_V37_FOURTEENTH_ACTUAL_READBACK_CPU.json')
replace('assert len(old)==1400','assert len(old)==1401')
replace("REPO/'history/evidence/MOD4_SCUT_FUDAN_TWELFTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json'","REPO/'history/evidence/MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json'")
replace("B/'reports/TWELFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'","B/'reports/THIRTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'")
start=source.index("'--validation',")+len("'--validation',");end=source.index(",'--push'",start)
validation='Actual thirteenth-hour complete H1/E2/E3 finals43/241/94, whole model/runtime finite CPU, all17Adam20 per update and actor9STD/critic8 parameter changes; original10916.624554395676s independent cost once settled, oldowner340946/all own children out/canonicalNone/two original fcntl/private/shared free. Fourteenth actualowner352710 three GO/positive PPO/matching UUID worker compute verified from each latest full source. Same H1 update43 sourcefilename is bound by new full SHAa7da and Adam672200, never confused with prior96db/671340. Human-authorized H1 sharing, exact resource bytes including CRLF override after controller copy and before manifest, installed SDKmath/RSL/assets and original33 negative cases retained; normal full-three future healthy-runtime/account bindings preserved. Four genuinely new a7da-source local MuJoCo trajectories only, jump strict1/1/1 and .0847834m both-wheel clearance peak, postrecovery no yaw .2rad breach observed through15s, smaller local normal speed/displacement/heading drift versus retained source12 raw. Actual local actuator/action tail comparison preserves both generations clipped channel0, does not claim unique causality. Different backend/no20kDR/two deterministic yaws, not PhysX qualification, statistical significance, complete normal nonregression or graduation. No prior case replay, extra GPU/native/Task, live patch/stop, peer interference, account duplication/refund/clearactive, reward/LR/STD/physics/CAD/threshold/budget/player change.'
source=source[:start]+repr(validation)+source[end:]
replace("assert len(git('tag','--list').splitlines())==1401","assert len(git('tag','--list').splitlines())==1402")
replace('total_tags=1401,all1400old_objects_peels_exact=True','total_tags=1402,all1401old_objects_peels_exact=True')
ast.parse(source)
with destination.open('x',encoding='utf8',newline='\n') as stream:stream.write(source)
with (B/'reports/FOURTEENTH_UNIQUE_ARCHIVE_PREPARATION_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),prepared=str(destination),source_helper_retained_not_reexecuted=str(original),AST_parsed=True,record_not_yet_executed=True,only_after_actual_three_learning_and_V37_monitor_exact_readback=True,previous1401_tag_objects_and_peels_must_remain_exact=True,no_training_transport_or_PT_raw_rehash=True),stream,indent=2)
print(json.dumps(dict(prepared=str(destination),AST_parsed=True)))
