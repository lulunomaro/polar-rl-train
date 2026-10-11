"""Unique actual complete135/new136 stage; preserve originals and verify remote objects."""
from archive_slope_scope_stage_once import *
from capture_slope136_archive_encoding_reviewed import capture
import io,contextlib,importlib.util
ID='e1-slope8-precontrol-rayinput-rejection-and-isolated137-repair'

def main():
 assert json.loads((R/'SLOPE136_FAILURE_137_REPAIR_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 assert not g('diff','--name-only') and not g('diff','--cached','--name-only')
 assert all(x.startswith('history/evidence/'+D.name+'/slope136_failure_137_repair/') for x in g('ls-files','--others','--exclude-standard').splitlines())
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 save('SLOPE136_FAILURE_137_REPAIR_ENCODING_REVIEWED_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_tag_replay=True))
 assert (R/'SLOPE136_FAILURE_137_REPAIR_STAGE_REPORT.md').exists()
 note=R/'SLOPE136_FAILURE_137_REPAIR_STAGE_REPORT.md'
 entries,files=capture(DEST/'slope136_failure_137_repair')
 spec=importlib.util.spec_from_file_location('complete135_stage_record',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Preserve slope8 precontrol rayinput rejection and deploy isolated actual-input scope','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Original136 precontrolground assertion and2hostresult-errorbyteSHA retained,noPPO budgetcost. CPU2800rays shows ideal-versus-float32 input expectation mismatch1.059626870e-6;actualinputtriangleerror3.33e-16,notGPUmeasurement. New137 onlyexpected-inputidentity/protocoldisclosure,1e-6 tolerance geometry andloopASTexact,287manifest packageSHA exact. Oldworkernaturalexit/actualCIM nochildren sharedOSlockfree demandtask0triggersReady proven before unique namespace admission;only exactfailed136 retired,baseguardbridgeJSONlock unchanged.137 publishedfrozenonly source404own13524b,newresultpending.MasterapprovaltracksRMcanonicalbytespreserved.Allsavedfailures/reader/source/metadata/workorders indexed,largeactualpathsizeSHA only.','--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('SLOPE136_FAILURE_137_REPAIR_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_only_continue_objects=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('SLOPE136_FAILURE_137_REPAIR_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_FAILURE_137_REPAIR_ENCODING_REVIEWED_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
