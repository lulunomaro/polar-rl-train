from pathlib import Path
import hashlib,json,time,traceback
from prepare213 import HERE,T,OV,SRC,R,E2,BASE,P208,PINS,one,output
from prepare213 import source as original_source

def source(path):
    return original_source(path).replace('\r\n','\n')

def main():
    with (R/'PREPARATION213_V2_ONCE.json').open('x') as f:json.dump(dict(ID='NEW213_SOURCE_DERIVATION_V2_CRLF_REMAINDER_ONLY',epoch=time.time(),retains_original_CRLF_lookup_error=True,continues_only_unwritten_outputs=True),f)
    train=source(BASE/'train_E2_full_resume_v1.py')
    train=one(train,'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher',
        'from launcher213 import IsolatedAppLauncher213 as AppLauncher')
    train=train.replace('from e2_command_checkpoint_v1 import ','from e2_command_checkpoint_v1213 import ')
    train=one(train,'        runner.load(warm)',
        '        from source_cache213 import runner_source_load_scope\n        with runner_source_load_scope():\n            runner.load(warm)')
    train=one(train,'    def _sha256(path):\n        import hashlib',
        '    def _sha256(path):\n        from source_cache213 import cached_source_owns,cached_H\n        if cached_source_owns(path):return cached_H(path)\n        import hashlib')
    output('train_e2_213.py',train)
    panel=source(E2/'e2_profile_domain_telemetry_v1.py')
    panel=one(panel,'from pathlib import Path','from pathlib import Path\nfrom e2_cycles213 import E2Cycles213')
    panel=one(panel,'self.names=tuple(e.termination_manager.active_terms);self.book=E2Book(t,e.num_envs,e.device,self.names)',
        'self.names=tuple(e.termination_manager.active_terms);self.book=E2Book(t,e.num_envs,e.device,self.names)\n        self.full_world213=E2Cycles213(t,e.num_envs,e.device,self.out)')
    panel=one(panel,'self.start_tick=int(e._integrated_contact.tick);self.start_fb=int(e._feedback_100hz_tick);self.calls=0;self.frame=None',
        'self.start_tick=int(e._integrated_contact.tick);self.start_fb=int(e._feedback_100hz_tick);self.calls=0;self.frame=None\n        self.full_world213.begin(index,self.context,self.start_tick)')
    panel=one(panel,"self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names]);self.instances.observe(c,after)",
        "self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names]);self.instances.observe(c,after)\n        self.full_world213.observe(c,after,tm.terminated,tm.time_outs,{k:tm.get_term(k).bool() for k in self.names},int(e._integrated_contact.tick))")
    panel=one(panel,'    def finish(self):\n        self.uninstall();instances=',
        "    def finish(self):\n        complete213=self.full_world213.finish()\n        with (self.out/'E2_FULL_WORLD_CYCLES213_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(complete213,f,indent=2)\n        self.uninstall();instances=")
    output('e2_panel213.py',panel)
    for name in ['e2_early_original_resample_observer_v2_complete.py','e2_observed_command_instances_v1.py',
        'e2_original_profile_catalog_candidate_v1.py','original_flat_height_provider_v1.py','lossless_snapshot_pinned75d683.py']:
        output(name,source(E2/name))
    worker=source(E2/'evaluate_E2_adapted93_new86_frozen900_once_v1.py')
    worker=one(worker,"GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3';OUT=None","OUT=None;SELECTED_CACHE=None")
    worker=one(worker,"def H(p):\n with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()",
        "def H(p):\n if SELECTED_CACHE is not None and SELECTED_CACHE.owns(p):return SELECTED_CACHE.H(p)\n with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()")
    worker=worker.replace('MOD4_E2_ADAPTED93_NEW86_EARLY_RESAMPLE_COMMAND_INSTANCES_V5','MOD4_E2_MISSING_FULL_WORLD_FIELDS213')
    worker=worker.replace("task['controls']==900","task['controls']==1200")
    worker=worker.replace("task['actual_target86_SDK_admission_passed']","task['actual_target_SDK_new213_source_admission_passed']")
    worker=worker.replace(' global OUT\n',' global OUT,SELECTED_CACHE\n')
    worker=worker.replace("os.environ.get('CUDA_VISIBLE_DEVICES')==GPU","os.environ.get('CUDA_VISIBLE_DEVICES')==task['GPU_UUID']")
    worker=one(worker,' assert source.stat().st_size==14615089 and H(source)==MODEL_SHA',
        " import torch\n from source_cache213 import PinnedSource213,selected_source\n SELECTED_CACHE=PinnedSource213(torch,source,MODEL_SHA,14615089)\n os.environ['MOD4_EXPERT213_JOB_ROOT']=str(job)\n storage=job/'kit_isolation';storage.mkdir()\n for name in ('data','DerivedDataCache'):(storage/name).mkdir()\n (storage/'data/user.config.json').write_text('{}')\n os.environ['MOD4_EXPERT213_KIT_STORAGE_ROOT']=str(storage)")
    worker=worker.replace("entry=mod/'train_E2_full_resume_v1.py'","entry=mod/'train_e2_213.py'")
    worker=worker.replace('from e2_profile_domain_telemetry_v1 import E2Panel','from e2_panel213 import E2Panel')
    worker=worker.replace('import sensor_resume_contract,e2_command_checkpoint_v1',
        'import sensor_resume_contract213 as sensor_resume_contract,e2_command_checkpoint_v1213 as e2_command_checkpoint_v1')
    worker=worker.replace('for i in range(900):','for i in range(1200):').replace('requested_controls=900','requested_controls=1200').replace('completed<900','completed<1200')
    worker=worker.replace('FROZEN_E2_93_PROFILE_DOMAIN_NO_PPO','FROZEN_E2_FULL_WORLD_FIELDS213_NO_PPO')
    # Keep entire original invocation and restore checks within an exact selected
    # source cache scope, with no global Path/open redirect or source re-decode.
    start=worker.index(' original=read(job/');end=worker.index("\nif __name__=='__main__':")
    body=worker[start:end]
    worker=worker[:start]+" def run_selected_case():\n"+''.join(' '+line+'\n' for line in body.splitlines())+" with selected_source(SELECTED_CACHE):\n  try:return run_selected_case()\n  finally:put('SOURCE213_SELECTED_PT_READ_COUNTS.json',SELECTED_CACHE.receipt())\n"+worker[end:]
    output('evaluate_e2_world213.py',worker)
    with (R/'SOURCE213_DERIVATION_PINS.json').open('x',encoding='utf8') as f:json.dump(dict(
        ID='NEW213_SOURCE_DERIVATION_V2_CRLF_REMAINDER_ONLY',inputs=PINS,
        original_E2_V5_caller_and_all_old_once_consumed_not_rerun=True,
        new_E2_purpose='same original teacher/plant/commands;new same-cycle cross/signedyaw/terminal fields;1200controls24s request,1680s bound',
        new_E3_component='reuse unchangedV14 existing-instance metadata only;bootstrap still unselected',
        source_model_raw_NPZ_USD_SDK_GPU_remote_or_Git_access=0),f,indent=2)

if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('PREPARATION213_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
