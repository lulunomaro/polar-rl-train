"""Independent zero-control repair namespace. Preserve all failed V1 bytes."""
from pathlib import Path
import ast,json,hashlib,time
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,text):
    ast.parse(text);p=D/name;assert not p.exists();p.write_text(text,encoding='utf8');return dict(path=str(p),sha256=sha(p))
def one(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
    decision=json.loads((D/'reports/S4_NATIVE120_PARTIAL_SAVE_FAILURE_AND_ZERO_CONTROL_LOGGER_REPAIR_CPU_ACTUAL.json').read_bytes())
    assert decision['passed_independent_classification'] and decision['no_native120_replay']
    source=D/'s4_linux20k_missing_native_fullstate_worker_v1.py';worker=source.read_text()
    worker=one(worker,"('own_native120','own_fullrestore0')","('own_first_fullsave0_loggerfix','own_fullrestore0_loggerfix')")
    worker=one(worker,"own=manifest['phase']=='own_fullrestore0'","own=manifest['phase']=='own_fullrestore0_loggerfix'")
    worker=one(worker,"obs=runtime_state.cache.clone();controls=120 if not own else 0","obs=runtime_state.cache.clone();controls=0  # New missing save scope, never replay native120")
    needle="runner=OnPolicyRunner(vec,cfg,log_dir=str(folder),device='cuda:0')"
    worker=one(worker,needle,needle+"\n        # Explicitly disabled writer for 0PPO saves, not a learn() logger change.\n        runner.logger.writer=None")
    worker=one(worker,"env=ns['build_env']()","""env=ns['build_env']()
        imported={}
        for name in ('torch','isaaclab','isaacsim','rsl_rl'):
            module=sys.modules.get(name)
            imported[name]=dict(file=getattr(module,'__file__',None),version_attribute=str(getattr(module,'__version__',None)))
        (folder/'S4_ACTUAL_IMPORTED_MODULE_PATHS.json').write_text(json.dumps(dict(epoch=time.time(),modules=imported,distribution_metadata_is_not_loaded_Kit_build=True),indent=2))""")
    worker=one(worker,'Only two new missing 0PPO integration scopes. No learner admission here.','Only missing zero-control fullsave and own restore; native120 is never replayed.')
    rows=[save('s4_linux20k_missing_zero_fullsave_worker_v2.py',worker)]
    parent=(D/'s4_missing_native_fullstate_parent_v1.py').read_text()
    parent=parent.replace('own_native120','own_first_fullsave0_loggerfix').replace('own_fullrestore0','own_fullrestore0_loggerfix')
    parent=one(parent,"done['controls']==(120 if phase=='own_first_fullsave0_loggerfix' else 0)","done['controls']==0")
    parent=one(parent,'s4_linux20k_missing_native_fullstate_worker_v1.py','s4_linux20k_missing_zero_fullsave_worker_v2.py')
    parent=one(parent,'native_and_own_fullrestore_sourcebound_complete=True','zero_control_fullsave_and_own_fullrestore_sourcebound_complete=True')
    parent=one(parent,'Finite new native120 -> own restore0 pipeline, original locks, no budget write.','New zero-control fullsave -> own restore0; original native120 is not repeated.')
    assert 'own_native120' not in parent and "controls']==0" in parent
    rows.append(save('s4_missing_zero_fullsave_parent_v2.py',parent))
    material=(D/'materialize_s4_native_fullstate_target_CPU_v1.py').read_text()
    material=one(material,'from s4_missing_native_fullstate_parent_v1 import LOCKS,B,guard','from s4_missing_zero_fullsave_parent_v2 import LOCKS,B,guard')
    material=one(material,'import torch\n        first=',"import torch,inspect\n        from rsl_rl.utils.logger import Logger\n        assert sha(inspect.getfile(Logger))==ctx['actual_logger_source_SHA']\n        first=")
    rows.append(save('materialize_s4_zero_fullsave_target_CPU_v2.py',material))
    publish=(D/'publish_s4_native_fullstate_target_CPU_once_v1.py').read_text()
    publish=one(publish,"TARGET=BASE+'/MOD4_S4_E0_WAVE35_LINUX_NATIVE_FULLSTATE_V1_20261015'","TARGET=BASE+'/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_LOGGER_V2_20261015'")
    publish=one(publish,"STAGE=BASE+'/MOD4_S4_E0_WAVE35_LINUX_NATIVE_FULLSTATE_UPLOAD_V1_20261015'","STAGE=BASE+'/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_UPLOAD_V2_20261015'")
    publish=publish.replace('s4_linux20k_missing_native_fullstate_worker_v1.py','s4_linux20k_missing_zero_fullsave_worker_v2.py').replace('s4_missing_native_fullstate_parent_v1.py','s4_missing_zero_fullsave_parent_v2.py').replace('materialize_s4_native_fullstate_target_CPU_v1.py','materialize_s4_zero_fullsave_target_CPU_v2.py')
    publish=one(publish,"payload=D/'native_fullstate_payload_v1'","payload=D/'zero_fullsave_logger_payload_v2'")
    publish=one(publish,"original_W35_manifest_SHA=sha(D/'actual_original_W35_run_manifest.json'))","original_W35_manifest_SHA=sha(D/'actual_original_W35_run_manifest.json'),actual_logger_source_SHA='d9822d8317724507a7c817e85399db0db9e56a4eae959435138e75cf92e44b8d')")
    publish=one(publish,"out=D/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'","out=D/'S4_ZERO_FULLSAVE_LOGGER_V2_TARGET_CPU_ACTUAL.json'")
    publish=one(publish,"sf.get(TARGET+'/'+out.name,str(out),max_concurrent_prefetch_requests=16)","sf.get(TARGET+'/S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json',str(out),max_concurrent_prefetch_requests=16)")
    publish=publish.replace('S4_NATIVE_FULLSTATE_TARGET_CPU_MATERIALIZED_ACTUAL_','S4_ZERO_FULLSAVE_LOGGER_V2_TARGET_CPU_MATERIALIZED_ACTUAL_')
    rows.append(save('publish_s4_zero_fullsave_target_CPU_once_v2.py',publish))
    dispatch=(D/'dispatch_s4_missing_native_fullstate_fixed_two_once_v1.py').read_text()
    dispatch=one(dispatch,"receipt=D/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'","receipt=D/'S4_ZERO_FULLSAVE_LOGGER_V2_TARGET_CPU_ACTUAL.json'")
    dispatch=dispatch.replace("['own_native120','own_fullrestore0']","['own_first_fullsave0_loggerfix','own_fullrestore0_loggerfix']")
    dispatch=dispatch.replace('s4_missing_native_fullstate_parent_v1.py','s4_missing_zero_fullsave_parent_v2.py')
    dispatch=dispatch.replace('S4_FIXED_TWO_UNIQUE_DISPATCH_ACTUAL_','S4_ZERO_FULLSAVE_LOGGER_V2_UNIQUE_DISPATCH_ACTUAL_').replace('S4_FIXED_TWO_UNIQUE_DISPATCH_TRANSPORT_ACTUAL_','S4_ZERO_FULLSAVE_LOGGER_V2_UNIQUE_DISPATCH_TRANSPORT_ACTUAL_')
    rows.append(save('dispatch_s4_missing_zero_fullsave_fixed_two_once_v2.py',dispatch))
    report=dict(epoch=time.time(),prepared=True,source_V1_SHA=sha(source),new_sources=rows,
        original_failed_native120_immutable=True,new_requested_controls=[0,0],PPO_updates_authorized=0,
        logger_only_save_interface_repair=True,no_old_GPU_replay=True,compiled_only_not_future_GPU_pass=True)
    p=D/'reports/S4_ZERO_CONTROL_LOGGER_REPAIR_V2_SOURCE_PREPARED_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
