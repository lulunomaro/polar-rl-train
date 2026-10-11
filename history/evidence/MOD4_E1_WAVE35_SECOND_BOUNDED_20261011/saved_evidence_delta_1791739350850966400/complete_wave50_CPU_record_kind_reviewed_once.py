"""Continue only unexecuted record after argparse rejected unsupported kind."""
from second_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name/'complete145_learning_CPU377';ID='wave50-full145-incomplete-isolated377-fullstate-cpu-admitted'
assert not gitio.g('tag','--list','*'+ID) and not gitio.g('diff','--cached','--name-only')
started=json.loads((R/'LEARNING_CPU_STAGE_ARCHIVE_STARTED.json').read_bytes());assert gitio.g('rev-parse','HEAD')==started['prior_main']
previous=gitio.refs();rows=json.loads((DEST/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries']
files=[p.relative_to(REPO).as_posix() for p in DEST.rglob('*') if p.is_file()]
save('LEARNING_CPU_RECORD_KIND_PREWRITE_REJECTION.json',dict(epoch=time.time(),original_source=str(D/'archive_wave50_learning_CPU_stage_once.py'),original_SHA=H((D/'archive_wave50_learning_CPU_stage_once.py').read_bytes()),argparse_kind_preparation_rejected=True,HEAD_unchanged=True,no_original_trial_objects=True,captured_original_evidence_not_recreated=True,only_unexecuted_record_kind_diagnostic_continued=True))
sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
def short_git(*args):
    if args[:2]==('add','--'):
        p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
    return original(*args)
rec.git=short_git
sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review incomplete50mm145 and independently admit source377 fullstate CPU preparation','--kind','diagnostic','--note-file',str(R/'LEARNING_CPU_STAGE_REPORT.md'),'--files',*files,'--validation','Complete145 fullraw and queryNPZ audited:50mm forward11 reverse23/27 ordinary0 route7; nonqualified/no70. Independent actual4090 source377=369exact+8new statecomponents; CPU102/sourceb026/D0D7/source35 identity/storage/strictwrongassignment/privatecommand CPUfixture/noCUDA pass. No50SDKnative/PPO/fresh/formal deployed. CentralCAS/canonical/master protected/samehourlymonitorverified. Unsupportedkind argparse rejected beforeoriginalobjects; onlyunexecutedrecordcontinued, originalcaptures/source/errors preserved.','--push']
try:rec.main()
except BaseException:save('LEARNING_CPU_KIND_REVIEWED_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_only=True));raise
tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
tracked=set(gitio.g('ls-files').splitlines())
for row in rows:
    if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
save('LEARNING_CPU_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,old_tags_preserved=len(previous),saved_sources=len(rows),actual_targetCPU_only_not_GPU_admission=True,all_captured_sources_tracked_exact=True))
print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
