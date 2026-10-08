"""Record this new stage evidence once; binary/raw artifacts are SHA indexes."""
from pathlib import Path
import sys,json,time,hashlib,shutil,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008';REPO=D.parent/'polar-rl-train'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
receipt=R/'D4_COMPLETE_D5_SDK_GIT_RECORDED.json';assert not receipt.exists()
assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
nom=read(R/'D5_NOMINAL_ACTUAL_SDK_REVIEW.json');d4=read(W/'reports/D4_MODEL28633_COMPLETE_MATCHED_REVIEW.json')
assert nom['nominal_parameter_readback_scope_accepted'] and d4['decision']['complete_firstseed_white3_true_D4_behavior_scope_accepted']
folder=REPO/'history/evidence/MOD4_D4_COMPLETE_AND_D5_ACTUAL_SDK_20261008';assert not folder.exists();folder.mkdir(parents=True)
files=[]
def copy(source,name):
    p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,p);assert sha(p)==sha(source);files.append(p.relative_to(REPO).as_posix())
for n in ('read_installed_spring_sdk_source.py','read_nominal_frozen_source.py','spring_nominal_sdk_readback.py','publish_nominal_spring_sdk_once.py',
          'read_nominal_spring_sdk_actual.py','review_nominal_sdk.py','spring_pressure_component.py','test_spring_pressure_cpu.py','stage_spring_pressure_cpu_once.py',
          'spring_pressure_sdk_adapter.py','test_spring_pressure_adapter_cpu.py','stage_pressure_adapter_cpu_once.py','publish_pressure_sdk_once.py',
          'read_pressure_sdk_actual.py','spring_pressure_index_runtime.py','publish_pressure_index_review_once.py',
          'eval_worker_pressure_dependency_review.py','admit_pressure_dependency_worker_once.py','deploy_pressure_dependency_worker_once.py',
          'read_pressure_worker_actual.py','admit_pressure_worker_process_review.py','deploy_pressure_worker_process_review_once.py',
          'spring_pressure_audit_runtime.py','publish_pressure_audit_scope_once.py','eval_worker_spring_audit_review.py','admit_spring_audit_worker_once.py','deploy_spring_audit_worker_once.py',
          'record_actual_spring_and_d4_review_once.py','sync_actual_spring_and_d4_metadata_once.py'):
    copy(D/n,'D5/'+n)
for n in ('INSTALLED_SPRING_SDK_SOURCE.json','SPRING_NOMINAL_SDK_PUBLISHED.json','NOMINAL_SPRING_SDK_CURRENT_ACTUAL.json',
          'D5_NOMINAL_ACTUAL_SDK_REVIEW.json','D5_NOMINAL_ACTUAL_SDK_REPORT.md','SPRING_PRESSURE_CPU_PASSED.json',
          'SPRING_PRESSURE_ADAPTER_CPU_PASSED.json','SPRING_PRESSURE_SDK_PUBLISHED.json','PRESSURE_SDK_CURRENT_ACTUAL.json',
          'PRESSURE_SDK_FIRST_INDEX_ERROR.json','SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json','PRESSURE_DEPENDENCY_ADMISSION_FIRST_ERROR.json',
          'PRESSURE_DEPENDENCY_WORKER_ADMITTED.json','PRESSURE_WORKER_CURRENT_ACTUAL.json','PRESSURE_SDK_SECOND_FIXED_BASELINE_ERROR.json',
          'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json','SPRING_AUDIT_WORKER_ADMITTED.json'):
    copy(R/n,'reports/'+n)
for n in ('D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json','D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md','review_pressure_sdk.py'):
    source=R/n if n.endswith(('.json','.md')) else D/n
    if source.exists():copy(source,'pressure_actual/'+n)
copy(W/'review_completed_candidate_and_block2.py','D4/review_completed_candidate_and_block2.py')
for n in ('D4_MODEL28633_COMPLETE_MATCHED_REVIEW.json','D4_MODEL28633_COMPLETE_MATCHED_REPORT.md','COMPLETED_D4_SCOPE_FILES.json'):
    copy(W/'reports'/n,'reports/'+n)
copy(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json','reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
note=folder/'EXPERIMENT_NOTE.md'
text=(W/'reports/D4_MODEL28633_COMPLETE_MATCHED_REPORT.md').read_text(encoding='utf8')+'\n\n'+(R/'D5_NOMINAL_ACTUAL_SDK_REPORT.md').read_text(encoding='utf8')
if (R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md').exists():text+='\n\n'+(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md').read_text(encoding='utf8')
text+='\nThe first isolated stiffnessSDK constructor rejected direct CUDA-index .numpy conversion before its parameter setter/timed loop. Original failed66-off and unexecuted66-on packages/results remain. The corrected module changes only index-to-CPU conversion. Valid67-off was completed and reused.67-on then encountered the inherited D0 observer fixed3500-reference assertion for the intended D5 stiffness. A new68-on pressure-aware observer verifies actual drive/buffer/model against independent D5 state, keeps all other D0 checks and restores the original nominal baseline after reading; no error was masked or numeric tolerance loosened. Each new explicit worker authority was admitted after its predecessor/child actually exited and the shared lock was free; old demandtasks disabled, new demandtask has no trigger. Completed evidence was reused and reviewed invalid packages excluded, without marking unexecuted66-on as passed or completed. Original failed code, worker, attention and taskXML remain. The first admission reader mistook its own Windowsvenv parent for a GPU process and rejected before task mutations; the independent next reader verified the exact CPU parent/child chain.\n\nThis unique stage trial records no new PPO,4090training signal,budget mutation or nominal hardware certification. Production243 remains unchanged. No repeated clock45min or same-range preflight.\n'
note.write_text(text,encoding='utf8');files.append(note.relative_to(REPO).as_posix())
identity='d4-complete28633-block2-local-closure-and-d5-actual-spring-sdk-prepared'
args=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',identity,'--title','Review true D4 retention and local closure continuation; verify nominal spring SDK and prepare D5 pressure',
      '--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Matched full root/q/parameters/6000 action callbacks;CPU88 own243 source24snapshots;block2 507.84M steps and local closure reset;nominal1200 write/contact callbacks, SI approximate force primary-source audit;10+6 target CPU pressure contracts;actual67-off and68-on SDK1200 contact/apply callbacks each, CUDA reset/RNG disk roundtrip, exact PhysX/model stiffness and unchanged nominal preload/damping/limits','--push']
p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
    (R/'D4_D5_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=p.stdout,stderr=p.stderr,returncode=p.returncode,do_not_repeat_record=True),indent=2),encoding='utf8')
    raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();tagobject=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==tagobject and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),commit=head,tag=tag,tagobject=tagobject,remote_main_tag_peeled_verified=True,push_pending=False,
       master_plan_SHA_unchanged=MASTER,evidence_folder=str(folder),production243_changed=False,new_frozen_worker_dependency_authority=True,new_PPO_or_canonical_mutations=0,
       D4_candidate_complete_limited_scope=True,D5_nominal_SDK_complete=True,D5_pressure_actual_SDK_reviewed=(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json').exists(),D5_learning_executor_deployed=False)
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
