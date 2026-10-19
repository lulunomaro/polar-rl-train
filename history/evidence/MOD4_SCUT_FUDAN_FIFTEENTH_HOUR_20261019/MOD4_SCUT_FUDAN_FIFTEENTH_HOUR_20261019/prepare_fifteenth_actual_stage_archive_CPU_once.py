"""Prepare a unique archive for the new actual stage, with every saved error retained."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;W=B.parent
original=W/'MOD4_SCUT_FUDAN_FOURTEENTH_HOUR_20261019/archive_fourteenth_closed_sources_local_recovery_unique_once.py'
destination=B/'archive_fifteenth_closed_sources_local_recovery_unique_once.py';assert not destination.exists()
source=original.read_text('utf8')
def replace(old,new):
 global source
 assert source.count(old)==1,(old[:100],source.count(old));source=source.replace(old,new)
replace("G=W/'MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_FOURTEENTH_HOUR_20261019'")
replace("BASE='67d4bd5295f307a0ea8b7668f1cc705e4df9f7d5';ID='scut-fudan-fourteenth-hour-closed-sources-local-yaw-recovery-review'","BASE='906eb654aedcb289939012725ed72990b77157ee';ID='scut-fudan-fifteenth-hour-closed-sources-local-recovery-review'")
replace("TITLE='Continue three experts from thirteenth-hour full finals and retain measured local recovery and stopping observations'","TITLE='Continue three experts from fourteenth-hour full finals and retain mixed local changes with delayed recovery'")
source=source.replace('352710','364556')
replace('AUTOMATION_ACTUAL_FOURTEENTH_LOCAL_YAW_HOLD_V37_ARGS.json','AUTOMATION_ACTUAL_FIFTEENTH_LOCAL_RECOVERY_V38_ARGS.json')
replace('AUTOMATION_V37_FOURTEENTH_ACTUAL_READBACK_CPU.json','AUTOMATION_V38_FIFTEENTH_ACTUAL_READBACK_CPU.json')
replace('assert len(old)==1401','assert len(old)==1402')
replace("REPO/'history/evidence/MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json'","REPO/'history/evidence/MOD4_SCUT_FUDAN_FOURTEENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json'")
replace("B/'reports/THIRTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'","B/'reports/FOURTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'")
start=source.index("'--validation',")+len("'--validation',");end=source.index(",'--push'",start)
validation='Actual fourteenth-hour complete H1/E2/E3 finals43/242/98, whole model/runtime finite CPU, all17Adam20 per update and actor9STD/critic8 parameter changes; original10940.84153175354s independent cost once settled, oldowner352710/all own children out/canonicalNone/two original fcntl/private/shared free. Fifteenth actualowner364556 three GO/positive PPO/matching UUID worker compute from each latest complete source. Same H1 update43 filename bound to full SHA51f4/Adam673060; human-authorized H1 sharing and exact CRLF helper after controller copy/before manifest retained, installed SDKmath/RSL/assets and original33 negative cases pass; normal three-final future runtime/account bindings retained. Four genuinely new51f4 local MuJoCo trajectories only: strict jump1/1/1 but recovery8.175s versus2.695, higher .0948115m both-wheel clearance and smaller planar drift, larger normal yaw drift. Existing raw condition timing: nonyaw last failure2.065s, yaw last failure7.675, original200-callback stable window7.6775 through8.175; temporal readout does not establish unique reward causation. Source-normalized generator first draft SyntaxError retained; V2 only fixes nested literal delimiter before any generator body or remote effect; clarified unused writer also retained. Different backend/no20kDR/two deterministic yaws, not PhysX qualification/statistical significance/full normal nonregression/graduation. No prior case replay, extra GPU/native/Task, live patch/stop, peer interference, accounting duplication/refund/clearactive, reward/LR/STD/physics/CAD/threshold/budget/player change.'
source=source[:start]+repr(validation)+source[end:]
replace("assert len(git('tag','--list').splitlines())==1402","assert len(git('tag','--list').splitlines())==1403")
replace('total_tags=1402,all1401old_objects_peels_exact=True','total_tags=1403,all1402old_objects_peels_exact=True')
ast.parse(source)
with destination.open('x',encoding='utf8',newline='\n') as stream:stream.write(source)
with (B/'reports/FIFTEENTH_UNIQUE_ARCHIVE_PREPARATION_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),prepared=str(destination),source_helper_retained_not_reexecuted=str(original),AST_parsed=True,record_not_yet_executed=True,only_after_actual_three_learning_and_V38_monitor_exact_readback=True,previous1402_tag_objects_and_peels_must_remain_exact=True,no_training_transport_or_PT_raw_rehash=True),stream,indent=2)
print(json.dumps(dict(prepared=str(destination),AST_parsed=True)))
