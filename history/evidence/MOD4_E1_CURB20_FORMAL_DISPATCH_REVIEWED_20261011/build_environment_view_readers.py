"""Create actual384 readers and a new annotation scope; unused380 helpers stay intact."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;R=D/'reports'
items={'read_reviewed_actual.py':'read_environment_view_actual.py','read_own_formal_cpu_actual.py':'read_environment_view_own_formal_cpu_actual.py','collect_curb133_actual.py':'collect_environment_view_curb133_actual.py','review_curb133_actual.py':'review_environment_view_curb133_actual.py','sync_fullstate_actual_scope_once.py':'sync_environment_view_actual_scope_once.py'}
for src,dst in items.items():
 text=(D/src).read_text().replace('from stage_reviewed_fullstate_once import','from stage_environment_view_log_receipt_once import')
 text=text.replace('supervise_curb20_fullstate_reviewed_once as own','supervise_curb20_environment_view_once as own')
 text=text.replace('REVIEWED_DISPATCH_ACTUAL_RECEIPT.json','ENVIRONMENT_VIEW_DISPATCH_ACTUAL_RECEIPT.json')
 text=text.replace('FULLSTATE_ACTUAL_','ENVIRONMENT_VIEW_ACTUAL_').replace('OWN_FORMAL_CPU_','ENVIRONMENT_VIEW_OWN_FORMAL_CPU_')
 text=text.replace('len(f)==380','len(f)==384')
 if src.startswith('sync_'):
  text=text.replace('FULLSTATE_METADATA_','ENVIRONMENT_VIEW_METADATA_')
  text=text.replace('FULLSTATE_REVIEWED','ENVIRONMENT_VIEW').replace('FULLSTATE_PREDEPLOY_VALIDATOR','ENVIRONMENT_VIEW_PRELEARNING_FAILURE')
  text=text.replace('curb20_fullstate_reviewed_scope','curb20_environment_view_scope')
  text=text.replace('REVIEWED_TARGET_CPU_PASSED.json','ENVIRONMENT_VIEW_TARGET_CPU_PASSED.json').replace('PREDEPLOY_VALIDATOR_SOURCE_REVIEW.json','ENVIRONMENT_VIEW_FAILURE_AND_REPAIR.json')
  text=text.replace("cpu['corrected_CURB_fullschema_CPU_fixture_passed']","cpu['strict_original_loader_and_private_owner_preserved']")
  text=text.replace('source_count=380','source_count=384').replace('CURB380','CURB384')
  text=text.replace('128x2/20kx4 new fullstate preflight each once charged by ownparent','128x2 exactreuse after its own PASSED; failed380big actual preload rejected and once settled; new384big CUDA fullrestore admission then formal each unique charged by ownparent')
  text=text.replace('old372/378 bytes retained','old372/378/380 bytes retained; sourceview num_envs/device uses actual installed manager properties')
 p=D/dst;assert not p.exists();compile(text,str(p),'exec');p.write_bytes(text.encode())
p=R/'ENVIRONMENT_VIEW_READER_SCOPE_PREPARED.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),new_root='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011',source_count=384,new_readers=items,readers_never_launch_or_signal=True,sync_is_new_annotation_only_not_old_once_replay=True,actual_FUTURE_files_pending_not_failure=True),indent=2))
