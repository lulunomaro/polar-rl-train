"""Generate NEW source-only owner/worker with narrowly enumerated metadata changes."""
from pathlib import Path
import ast,hashlib,json,difflib
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source'
PINS={
'supermimic_original_owner_shared_app_close_candidate_v5.py':(12478,'0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619'),
'worker_supermimic_bptt_app_close_candidate_v5.py':(17704,'7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7')}
def replace(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)
def original(name):
    raw=(SOURCE/name).read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==PINS[name]
    return raw.decode().replace('\r\n','\n')
def store(name,text):
    p=HERE/name
    if p.exists():p.read_bytes()
    p.write_text(text,encoding='utf-8',newline='\n')

def sources():
    owner=original('supermimic_original_owner_shared_app_close_candidate_v5.py')
    owner=replace(owner,'from resume_runtime_app_close_v5 import evaluate_waited_worker,bind_future_task_extensions',
        'from resume_runtime_app_close_v5 import evaluate_waited_worker as _original_evaluate_waited_worker,bind_future_task_extensions\nfrom quality_microtrain_contracts_v1 import (validate_microtrain_plan,validate_microtrain_entry,bind_microtrain_task,bind_microtrain_go,enforce_microtrain_waited_result)')
    owner=replace(owner,'def verify_sources(plan):',
        'def evaluate_waited_worker(job_root,returncode,entry,run_id):\n return enforce_microtrain_waited_result(_original_evaluate_waited_worker(job_root,returncode,entry,run_id),entry)\n\ndef verify_sources(plan):')
    owner=replace(owner,"1<=len(plan['entries'])<=8,'OriginalC only/eight nonH1'", "1<=len(plan['entries'])<=2,'OriginalC only/one-or-two requested nonH1'")
    owner=replace(owner,"e['target_bptt_steps']>=3000 and e['num_envs']in(512,1024,2048)","validate_microtrain_entry(e)['target_bptt_steps']==e['target_bptt_steps'] and e['num_envs']in(512,1024,2048)")
    owner=replace(owner,"plan=b.read(B/'OWNER_PLAN.json');verify_sources(plan)","plan=validate_microtrain_plan(b.read(B/'OWNER_PLAN.json'));verify_sources(plan)")
    owner=replace(owner,"task=bind_future_task_extensions(task,e);put(J/'TASK.json',task)","task=bind_future_task_extensions(task,e);task=bind_microtrain_task(task,e);g=bind_microtrain_go(g,e);put(J/'TASK.json',task)")
    owner=replace(owner,'target_per_expert=3000,final_skill_goal=.9',"target_per_expert=None,microtrain_requested_verified_increments={e['role']:e['microtrain']['target_verified_increment']for e in plan['entries']},final_skill_goal=.9")
    owner=owner.replace('errors=errors,H1_excluded=True,','errors=errors,H1_excluded=True,microtrain_requested_roles=plan[\'requested_roles\'],microtrain_deferred_roles=plan[\'deferred_roles\'],')
    owner='"""SOURCE ONLY: quality-driven 1/2-role A1 finite segment; not enabled/dispatched."""\n'+owner
    worker=original('worker_supermimic_bptt_app_close_candidate_v5.py')
    worker=replace(worker,"KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'", "from quality_microtrain_contracts_v1 import (validate_worker_microtrain_task,validate_microtrain_payload,start_microtrain_segment,finish_microtrain_segment)\nKIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'")
    worker=replace(worker,"task['num_envs']in(512,1024,2048)and task['target_bptt_steps']>=3000", "task['num_envs']in(512,1024,2048)and validate_worker_microtrain_task(task)")
    worker=replace(worker,'resume_source=None;resume_receipt=None;', 'resume_source=None;resume_receipt=None;segment=None;')
    worker=replace(worker,'value.update(bootstrap_teacher=', 'value.update(microtrain_segment=finish_microtrain_segment(segment,vars(self.counts),stopped=stop),bootstrap_teacher=')
    worker=replace(worker,"latest=dict(epoch=time.time(),path=str(dest)", "latest=dict(microtrain_segment=finish_microtrain_segment(segment,vars(self.counts),stopped=stop),epoch=time.time(),path=str(dest)")
    worker=replace(worker,"resume_receipt=load_decoded_full_checkpoint_once(learner,resume_source,task,bridge.observed_context_layout)","validate_microtrain_payload(resume_source.payload,task);resume_receipt=load_decoded_full_checkpoint_once(learner,resume_source,task,bridge.observed_context_layout)")
    worker=replace(worker,'  def before_action():',"  segment=start_microtrain_segment(task,vars(learner.counts),resume_receipt=resume_receipt);put(out/'MICROTRAIN_SEGMENT_BASELINE_V1.json',segment)\n  def before_action():")
    worker=replace(worker,"target_actual_BPTT_policy_steps=task['target_bptt_steps']", "microtrain_segment_baseline=segment,target_actual_BPTT_policy_steps=task['target_bptt_steps']")
    worker=replace(worker,"learner.train(target_bptt_steps=task['target_bptt_steps'])", "learner.train(target_bptt_steps=segment['target_cumulative_verified_counter'])")
    worker=replace(worker,"resume_receipt=resume_receipt,passed_execution=True", "resume_receipt=resume_receipt,microtrain_segment=finish_microtrain_segment(segment,vars(learner.counts),stopped=stop),passed_execution=True")
    worker='"""SOURCE ONLY: original A1 worker, loaded-counter finite increment metadata."""\n'+worker
    compile(owner,'owner_quality_microtrain_v1.py','exec');compile(worker,'worker_quality_microtrain_v1.py','exec')
    return owner,worker

def main():
    owner,worker=sources();store('owner_quality_microtrain_v1.py',owner);store('worker_quality_microtrain_v1.py',worker)
    patch=''
    for old,new,text in (('supermimic_original_owner_shared_app_close_candidate_v5.py','owner_quality_microtrain_v1.py',owner),('worker_supermimic_bptt_app_close_candidate_v5.py','worker_quality_microtrain_v1.py',worker)):
        patch+=''.join(difflib.unified_diff(original(old).splitlines(True),text.splitlines(True),fromfile=str(SOURCE/old),tofile=str(HERE/new)))
    store('QUALITY_MICROTRAIN_WHITELIST_DIFF_V1.patch',patch)
    for name in ('quality_microtrain_contracts_v1.py','owner_quality_microtrain_v1.py','worker_quality_microtrain_v1.py'):
        raw=(HERE/name).read_bytes();print(json.dumps(dict(path=str(HERE/name),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())))
if __name__=='__main__':main()
