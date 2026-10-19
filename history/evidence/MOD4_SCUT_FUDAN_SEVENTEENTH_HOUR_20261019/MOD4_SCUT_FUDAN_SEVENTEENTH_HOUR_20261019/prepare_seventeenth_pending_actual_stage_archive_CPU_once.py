"""Prepare one unique archive for actual closure and resource pending, without a GO claim."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019';R=B/'reports'
s=(P/'archive_sixteenth_closed_sources_local_recovery_unique_once.py').read_text('utf8')
s=s.replace('69bc89eb3fa71d0d5c09e86b69d72aacb14c5227','7b5943c06ef0e26a965c4a932c13f3977a6a1971')
s=s.replace('scut-fudan-sixteenth-hour-closed-sources-local-recovery-review','scut-fudan-seventeenth-hour-closed-sources-resource-capacity-pending')
s=s.replace('FIFTEENTH_','SIXTEENTH_')
s=s.replace('AUTOMATION_ACTUAL_SIXTEENTH_LOCAL_RECOVERY_V39_ARGS','AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_PENDING_V40_ARGS').replace('AUTOMATION_V39_SIXTEENTH','AUTOMATION_V40_SEVENTEENTH_CAPACITY_PENDING')
s=s.replace('1404','NEW_TAG_COUNT').replace('1403','1404').replace('NEW_TAG_COUNT','1405')
lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('TITLE='):lines[i]="TITLE='Close sixteenth-hour full models and prepare seventeenth continuation pending original disk guard; retain local recovery regression'"
 if line.startswith(" d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json')"):
  lines[i]=" d=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/SEVENTEENTH_PREPARED_ORIGINAL_DISK_GUARD_CAPACITY_PENDING_CPU_ACTUAL.json').read_bytes());f=json.loads((G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert d['passed'] and f['passed_all_three_whole_final_models_CPU'] and f['one_original_writer_actual_segment']['owner_parent_pid']==376288 and learning['seventeenth_actual_owner'] is None and learning['capacity']['actual_free_GiB']<25 and not (B/'reports/THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()"
s='\n'.join(lines)+'\n'
assert "d['owner']['detached_pid']==376288" not in s
s=s.replace('actual_three_learning_and376288_binding=True','actual_closed376288_prepared_seventeenth_no_new_owner_or_GO=True')
s=s.replace('current_full_three_closing_and_next_generic_healthy_runtime_H1_sharing_preserved=True','prepared_full_three_healthy_source_H1_sharing_and_unused_capacity_reader_preserved=True')
s=s.replace('Actual new dispatch and learning metadata:','Prepared next sources and actual capacity pending facts:')
validation='Actual sixteenth-hour complete H1/E2/E3 finals42/242/98, two-host full SHA, whole model/runtime finite CPU, all17Adam20 per update and actor9STD/critic8 changes; original10879.442652702332s independent cost once settled, originalowner376288/all own children out/canonicalNone/two original fcntl/private/shared free. Prepared seventeenth sourcescb11/c51a/d17a and33 negative cases pass; no seventeenth deploy/owner/worker/GO/PPO/admission Task or charge. Actual72 disk snapshot25709084672bytes23.943450927734375GiB is below original strict25GiB start guard; source21033903357952bytes, H1 explicit sharing remains authorized, no peer identity query/interference or GPUempty rollback. Unused single finite capacity reader and original full-three deployer prepared, no new partial writer or budget contract. Four newcb11 local MuJoCo trajectories only, normal and jump alive15s; each jump strict1takeoff1landing0recovery compared with preceding1/1/1, peak.0932178m, finalyaw+.469549 and no stable recovery callbacks. Normal speed.0100764/displacement.157370/yaw-.0650358 improved relative to previous.016753/.254691/-.377346; preserve mixed change and lost local recovery, not PhysX/statistical qualification or unique cause. Strict report complete before stdout pipe Select-ObjectFirst5 wrapper failure; original exact toolcall/result/source and complete report readback retained, Python exact returncode unknown; no strict once or raw trajectory replay, only missing events/residual CPU reports completed. All original reports/errors/unused helpers retained; no delete/move/oldcleanup replay/guard reduction, original budget/account/physics/reward/LR/STD/threshold/player untouched. Same hourly monitor preserved and current pending capacity/human action updated.'
start=s.index("'--validation',");end=s.index(",'--push'",start);s=s[:start]+"'--validation',"+repr(validation)+s[end:]
ast.parse(s);q=B/'archive_seventeenth_closed_sources_capacity_pending_unique_once.py'
with q.open('x',encoding='utf8',newline='\n') as f:f.write(s)
with (R/'SEVENTEENTH_PENDING_UNIQUE_ARCHIVE_PREPARED_CPU.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),new_archive_writer=dict(path=str(q),bytes=q.stat().st_size,SHA=hashlib.sha256(q.read_bytes()).hexdigest()),base='7b5943c06ef0e26a965c4a932c13f3977a6a1971',old1404_new1405=True,stage='scut-fudan-seventeenth-hour-closed-sources-resource-capacity-pending',not_a_seventeenth_launch_or_learning_claim=True,no_record_or_tag_yet=True),f,indent=2)
print(json.dumps(dict(prepared_pending_archive=True,writer=str(q))))
