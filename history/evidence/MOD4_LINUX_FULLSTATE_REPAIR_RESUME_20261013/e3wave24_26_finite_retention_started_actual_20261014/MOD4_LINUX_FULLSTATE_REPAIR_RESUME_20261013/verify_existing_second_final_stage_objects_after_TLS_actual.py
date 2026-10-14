"""Verify and receipt existing pushed objects only; never record/tag/commit again."""
from pathlib import Path
import json,time
import archive_left_second_final_e3_candidate_actual_stage_once as stage
D=stage.D;cap=stage.cap;REPO=stage.REPO
def main():
 head='9a77133f0dfc185fa4ea7a05b358c965c08995dc';tag='trial-20261014-wave50-left-second-fullfinal191-reviewed-new-frozen80-started';obj='ad42602966b4655c051d43dc597381900be62c83'
 assert cap.g('rev-parse','HEAD')==head and cap.g('rev-parse',tag)==obj and not cap.g('status','--porcelain')
 index=REPO/'history/evidence'/D.name/'left_second_final191_new_e3_candidate_stage/REPORT_CAPTURE_INDEX.json';rows=json.loads(index.read_bytes())['entries']
 old=cap.a.gitio.refs();old.pop('refs/tags/'+tag)
 cap.a.verify(rows,old,head,tag,obj)
 p=D/'reports/LEFT_SECOND_FINAL191_E3_CANDIDATE_STAGE_GIT_RECORDED.json';assert not p.exists()
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),original_TLS_push_failure_preserved=True,only_original_existing_objects_pushed=True,no_record_tag_commit_replay=True,later_receipt_ordinary_supplement_required=True)
 p.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
