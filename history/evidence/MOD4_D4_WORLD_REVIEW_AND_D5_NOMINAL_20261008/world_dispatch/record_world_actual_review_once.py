"""Record the actual isolated evaluator repair and completed block review once."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time

D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
receipt=R/'D4_WORLD_REPAIR_GIT_RECORDED.json'
assert not receipt.exists(), 'Already recorded; never repeat'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
v=read(R/'D4_BLOCK1_WORLD_DISPATCH_REVIEW.json')
assert v['decision']['limited_true_D4_baseline_functional_scope_accepted']
assert v['actual_block2']['startup']['action_queue_targets_timestamps_both_RNG_restored_exact']
folder=REPO/'history/evidence/MOD4_D4_WORLD_REVIEW_AND_D5_NOMINAL_20261008'
assert not folder.exists(), 'Archive preparation already happened; inspect existing objects instead of re-recording'
folder.mkdir(parents=True)
files=[]
def copy(source, name):
    dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest);assert sha(dest)==sha(source)
    files.append(dest.relative_to(REPO).as_posix())
for name in ('build_world_package.py','supervise_world_evidence_publication.py','deploy_world_dispatch_publication_once.py',
             'read_world_publication_actual.py','collect_completed_d4_scope.py','review_existing_baseline.py',
             'review_true_d4_scope.py','prepare_actual_review.py','record_world_actual_review_once.py','sync_world_actual_metadata_once.py'):
    copy(D/name,'world_dispatch/'+name)
copy(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/read_verified_d4_blocks.py','read_verified_d4_blocks.py')
for name in ('WORLD_DISPATCH_PACKAGE.json','WORLD_PUBLICATION_DEPLOYED.json','PUBLISHER_STARTED.json',
             '45-d4world-anchor_PUBLISHED.json','55-d4world-b1_PUBLISHED.json','PUBLICATION_STATE.json',
             'D4_EXISTING_BASELINE_SCOPE_REVIEW.json','COMPLETED_D4_SCOPE_FILES.json','D4_TRUE_WORLD_SCOPE_REVIEW.json',
             'D4_BLOCK1_WORLD_DISPATCH_REVIEW.json','D4_BLOCK1_WORLD_DISPATCH_REPORT.md','FIRST_TRUE_SCOPE_READER_ERROR.json'):
    copy(R/name,'reports/'+name)
S=D.parent/'MOD4_D5_SPRING_LAW_PREPARE_20261008'
for name in ('read_spring_nominal_source.py','review_nominal_curve.py'):
    copy(S/name,'D5_nominal/'+name)
copy(S/'reports/D5_NOMINAL_MODEL_CURVE_REPORT.md','D5_nominal/D5_NOMINAL_MODEL_CURVE_REPORT.md')
copy(S/'reports/FIRST_SOURCE_READER_ERROR.json','D5_nominal/FIRST_SOURCE_READER_ERROR.json')
spring=read(S/'reports/D5_NOMINAL_MODEL_CURVE_REVIEW.json')
compact={k:v for k,v in spring.items() if k not in ('curves','rows','samples')}
compact['joints']=[{k:v for k,v in j.items() if k!='curve'} for j in spring['joints']]
# The exact full curve stays local as an indexed offline artifact, not raw training data.
compact['full_offline_curve_JSON']=dict(path=str(S/'reports/D5_NOMINAL_MODEL_CURVE_REVIEW.json'),sha256=sha(S/'reports/D5_NOMINAL_MODEL_CURVE_REVIEW.json'))
dest=folder/'D5_nominal/D5_NOMINAL_MODEL_CURVE_REVIEW.json'
dest.write_text(json.dumps(compact,indent=2),encoding='utf8');files.append(dest.relative_to(REPO).as_posix())
source_index=dict(epoch=time.time(),actualUSD_sha256='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87',
    actual_import_contract_sha256='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f',
    source_files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in (S/'reviewed_sources').iterdir() if p.is_file()],
    source_readback_JSON_sha256=sha(S/'reports/ACTUAL_FROZEN_SPRING_SOURCE.json'),
    actual_SDK_force_or_hardware_calibration_completed=False,D5_component_or_executor_deployed=False,nominal_model_changed=False)
dest=folder/'D5_nominal/FROZEN_SOURCE_INDEX.json';dest.write_text(json.dumps(source_index,indent=2),encoding='utf8');files.append(dest.relative_to(REPO).as_posix())
note=folder/'EXPERIMENT_NOTE.md'
note.write_text((R/'D4_BLOCK1_WORLD_DISPATCH_REPORT.md').read_text(encoding='utf8')+'\n\nThis unique trial records a real frozen-dispatch repair, actual D4 first-block and next-block full queue resume, corrected frozen scope and offline nominal source audit. No new PPO/preflight, training signal, production source mutation, new clock trial, budget write or graduation claim occurred. Existing historical results remain.\n',encoding='utf8')
files.append(note.relative_to(REPO).as_posix())
identity='d4-world-dispatch-repaired-block1-resume-and-d5-nominal-audited'
command=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',identity,
         '--title','Repair true D4 world replay while preserving continuous training and audit nominal spring law',
         '--kind','repair','--note-file',str(note),'--files',*files,
         '--validation','Own CPU88/243-source/24 snapshots;1059 updates/508.32M steps;actual block2 queue RNG resume;true6000 world action callbacks;bridge JSON byte SHA;offline SI curve only','--push']
run=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace')
if run.returncode:
    (R/'WORLD_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=run.stdout,stderr=run.stderr,returncode=run.returncode,do_not_repeat_record=True),indent=2),encoding='utf8')
    raise RuntimeError(run.stdout+'\n'+run.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=run.stdout.strip().splitlines()[-1].split()
tagobj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==tagobj and remote['refs/tags/'+tag+'^{}']==head
value=dict(epoch=time.time(),tag=tag,commit=head,tagobject=tagobj,
    remote_main_tag_peeled_verified=True,push_pending=False,master_plan_SHA_unchanged=MASTER,
    evidence_folder=str(folder),production243_changed=False,new_PPO_or_budget_operations=0,
    CPU_only_publisher_actual=v['CPU_only_publisher'],scope_decision=v['decision'])
receipt.write_text(json.dumps(value,indent=2),encoding='utf8')
print(json.dumps(value))
