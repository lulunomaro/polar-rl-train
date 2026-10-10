"""Create independent read-only365/130 readers. Never call historical executors."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
def put(name,source):
 p=D/name;assert not p.exists();ast.parse(source);p.write_bytes(source.encode());return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 rows=[]
 source=(D/'read_episode_reviewed_actual.py').read_text(encoding='utf8')
 source=source.replace('MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010','MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010').replace('EPISODE_REPAIR_ACTUAL_','COMMAND_MATCHED_ACTUAL_').replace('EPISODE_REPAIR_READER_ERROR_','COMMAND_MATCHED_READER_ERROR_')
 source=source.replace("x['kind'].startswith('S3_E1_e1_G3_command_retention_observation_')","x['kind'].startswith('S3_E1_e1_G3_command_retention_matched_')")
 source=source.replace("remaining_accounted_snapshot=left,active=a,", "remaining_accounted_snapshot=left,remaining_after_actual_unaccounted_tail=left-max(0,time.time()-a['accounted_through_epoch']) if a else left,active=a,")
 rows.append(put('read_matched_command_actual.py',source))
 source=(D/'collect_episode_reviewed129_actual.py').read_text(encoding='utf8').replace('EPISODE_REPAIR_ACTUAL_','COMMAND_MATCHED_ACTUAL_').replace('129-e1-g3-command-retention','130-e1-g3-command-retention-matched').replace('e1_G3_command_retention_observation_PASSED','e1_G3_command_retention_matched_PASSED').replace('CANDIDATE_129_','CANDIDATE_130_').replace('129','130')
 rows.append(put('collect_matched_command130_actual.py',source))
 source=(D/'review_command129_actual.py').read_text(encoding='utf8').replace('CANDIDATE_129_','CANDIDATE_130_').replace('129','130')
 rows.append(put('review_matched_command130_actual.py',source))
 p=R/'COMMAND_MATCHED_READERS_PREPARED.json';assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),new_readonly_actual_stage_readers=rows,no_readers_or_GPU_or_PPO_executed=True,new_budget_seconds=0),indent=2).encode())
 print(json.dumps(dict(readonly_readers_prepared=rows)))
if __name__=='__main__':main()
