"""Independent frozen worker after actual144 failure and old worker natural exit."""
from second_io import *
from curb_io import WIN

def main():
    assert not (R/'WAVE50_QUERY_WORKER_DEPLOY_STARTED.json').exists()
    failure=json.loads(sorted(R.glob('WAVE50_144_FAILED_ACTUAL_COLLECTION_[0-9]*.json'))[-1].read_bytes())
    assert failure['actual_processes']==[] and failure['result']['phase']=='retained_failed'
    folder=Path(next(x['local'] for x in failure['evidence'] if x['local'].endswith('result.json'))).parent
    source=(folder/'worker_source.py').read_bytes();assert H(source)==failure['worker_source_SHA']=='a4748760338c0a9132f6858ea26bf2b5a2148b8fcc06e5f3beb7fcd544a94b11'
    jid=failure['job_id'];text=source.decode().replace('E1_SLOPE8_QUERY_REVIEW','E1_WAVE50_QUERY_REVIEW')
    anchor='PAUSED_SHALLOW_JOBS=';assert text.count(anchor)==1;text=text.replace(anchor,"RETIRED=RETIRED+("+repr(jid)+",)\n"+anchor)
    compile(text,'eval_worker_e1_wave50_query_review.py','exec');worker=D/'eval_worker_e1_wave50_query_review.py';assert not worker.exists();worker.write_bytes(text.encode())
    old=(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011/admit_slope8_query_worker_once.py').read_text()
    old=old.replace('E1_G3_PACKAGE_REVIEW','OLD_NAMESPACE_TOKEN').replace('eval_worker_e1_g3_package_review.py','OLD_WORKER_TOKEN').replace('MOD4_AsyncFrozenEvaluation_v15_e1_g3_package_review','OLD_TASK_TOKEN')
    old=old.replace('E1_SLOPE8_QUERY_REVIEW','E1_WAVE50_QUERY_REVIEW').replace('SLOPE8_QUERY_WORKER_EXPECTED','WAVE50_QUERY_WORKER_EXPECTED').replace('eval_worker_e1_slope8_query_review.py','eval_worker_e1_wave50_query_review.py').replace('admit_slope8_query_worker_once.py','admit_wave50_query_worker_once.py').replace('MOD4_AsyncFrozenEvaluation_v15_e1_slope8_query_review','MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review')
    old=old.replace('OLD_NAMESPACE_TOKEN','E1_SLOPE8_QUERY_REVIEW').replace('OLD_WORKER_TOKEN','eval_worker_e1_slope8_query_review.py').replace('OLD_TASK_TOKEN','MOD4_AsyncFrozenEvaluation_v15_e1_slope8_query_review')
    old=old.replace('clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat',jid).replace('result136_SHA','result144_SHA').replace('error136_SHA','error144_SHA').replace('original_failed136_result','original_failed144_result').replace('exclusion136_before_control_not_physical_pass','exclusion144_before_control_not_physical_pass')
    old=old.replace('050ef42a3909b13292f0caf29c3a82a05c030d38a35a16312bdc6790c2a5b0c9',failure['result']['runtime_archive_sha256']).replace('24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411',failure['result']['checkpoint']['sha256'])
    old=old.replace("assert 'line 94, in main' in error and 'sampled-expected[None,:]' in error","assert 'line 98, in main' in error and 'assert actual_query_height_error<=1e-6' in error")
    old=old.replace('Retain136 precontrol nominal-versus-actual rayinput mismatch; exact new137 input-identity scope; original bridge/guard/lock; frozen only.','Retain144 precontrol ideal-versus-worldmesh query rejection; new independently validated float32 world triangles; original bridge/guard/lock; frozen only.')
    compile(old,'admit_wave50_query_worker_once.py','exec');admit=D/'admit_wave50_query_worker_once.py';assert not admit.exists();admit.write_bytes(old.encode())
    expected=dict(epoch=time.time(),old_worker_SHA=H(source),new_worker_SHA=H(worker.read_bytes()),result144_SHA=H((folder/'result.json').read_bytes()),error144_SHA=H((folder/'probe.json.error.txt').read_bytes()),namespace_only_and_exact_failed144_exclusion=True,no_base_bridge_lock_or_JSON_retry_change=True)
    ep=save('WAVE50_QUERY_WORKER_EXPECTED.json',expected);save('WAVE50_QUERY_WORKER_DEPLOY_STARTED.json',dict(epoch=time.time(),once=True))
    n,w=io.connect_both()
    try:
        with w.open_sftp() as f:
            assert H(f.open(WIN+'/eval_worker_closure2500.py').read())==failure['baseguard_SHA']=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
            for local in (worker,admit,ep):io.put(f,WIN+'/'+local.name,local.read_bytes())
        _,o,e=w.exec_command('D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe -X utf8 '+WIN+'/'+admit.name,timeout=60);out=o.read();err=e.read();rc=o.channel.recv_exit_status()
        (R/'WAVE50_QUERY_WORKER_DEPLOY_OUTPUT.txt').write_bytes(out+err);assert rc==0,(out+err).decode(errors='replace')
        with w.open_sftp() as f:
            for name in ('ADMISSION','STARTED','ADMITTED'):
                raw=f.open(WIN+'/E1_WAVE50_QUERY_REVIEW_WORKER_'+name+'.json').read();p=R/('E1_WAVE50_QUERY_REVIEW_WORKER_'+name+'.json');assert not p.exists();p.write_bytes(raw)
        print(out.decode())
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_QUERY_WORKER_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
