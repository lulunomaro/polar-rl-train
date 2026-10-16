"""The stage commit exists; Windows206 prevented even spawning tag -m. Never rerecord."""
from pathlib import Path
import sys,time,json,importlib.util,traceback
V=Path(__file__).resolve().parent;W=V.parent;R=V/'reports';REPO=W/'polar-rl-train';TAG='trial-20261017-three-expert-recovered-finals-same-scope-continuation';TITLE='Continue three independent experts from recovered complete finals under one original budget writer'
sp=importlib.util.spec_from_file_location('existing_stage_functions_only',V/'archive_recovered_three_expert_same_scope_stage_once.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);git=a.git;H=a.H
def main():
 head=git('rev-parse','HEAD');assert head=='7908d77104809925fb7e837057f05ff2e7989134' and git('log','-1','--format=%s')==TITLE and not git('status','--porcelain') and not git('tag','--list',TAG);errs=list(R.glob('RECOVERED_STAGE_GIT_ORIGINAL_ERROR_*.json'));assert len(errs)==1 and 'WinError 206' in errs[0].read_text('utf8');old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1361;message=V/'EXISTING_STAGE_ANNOTATED_TAG_EXACT_TITLE_AND_NOTE_UTF8.txt';assert not message.exists();note=(V/'ACTUAL_HUMAN_RECOVERED_THREE_FINALS_CONTINUATION_STAGE_NOTE.txt').read_text('utf8');message.write_text(TITLE+'\n\n'+note,encoding='utf8');git('tag','-a',TAG,'-F',str(message),head);obj=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head;git('push','--atomic','origin',head+':refs/heads/main','refs/tags/'+TAG);idx=REPO/'history/evidence'/V.name/'actual_recovered_finals_same_scope_new_native_finite_stage_v1/REPORT_CAPTURE_INDEX.json';rows=json.loads(idx.read_bytes())['entries'];a.a.g.n.m.cap.a.gitio.g=git;a.a.g.n.m.cap.a.verify(rows,old,head,TAG,obj);v=dict(epoch=time.time(),existing_unique_stage_commit=head,annotated_tag=TAG,object=obj,actual_remote_main_tag_peeled_all1361_oldtags_tracked_SHA_verified=True,source_entries=len(rows),original_Windows206_before_tag_process_creation_preserved=True,no_new_commit_record_or_tag_recreation=True,exact_original_tag_message_file_argument_avoids_Windows_argv_limit=True,tag_message_path=str(message),tag_message_SHA=H(message),postcapture_errors_receipt_message_monitor_need_ordinarysupplement=True);p=R/'RECOVERED_STAGE_EXISTING_COMMIT_TAG_FILE_REMOTE_VERIFIED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('EXISTING_STAGE_TAG_FILE_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_tag_exists_continue_existingobjects_never_retag_or_commit=True),f,indent=2)
  raise
