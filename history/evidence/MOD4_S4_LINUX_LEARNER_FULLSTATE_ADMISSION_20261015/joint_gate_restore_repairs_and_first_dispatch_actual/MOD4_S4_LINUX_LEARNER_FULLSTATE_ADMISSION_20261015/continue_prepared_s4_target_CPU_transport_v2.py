"""One root-owned CPU-only publication to a new namespace; no once replay."""
from pathlib import Path
import hashlib,json,sys,time,traceback,shlex
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
REMOTE='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_RSL5_CPU_COMPONENTS_V1_20261015'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    payload=D/"target_CPU_components_v1"
    manifest=json.loads((payload/"CPU_COMPONENT_SOURCE_MANIFEST.json").read_bytes())
    assert manifest["approved_GPU"] is False and manifest["approved_PPO"] is False
    for name,h in manifest["files"].items(): assert sha(payload/name)==h
    stamp=str(time.time_ns());client=None;sf=None
    def run(code,label):
        si,so,se=client.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60)
        si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=R/(label+'_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_automatic_retry=True),indent=2),encoding='utf8');assert rc==0,str(p)
        return json.loads(raw)
    try:
        client=t.connect()
        guard=run('''from pathlib import Path
import json,hashlib,fcntl,psutil,subprocess,time
root=Path('''+repr(REMOTE)+''');assert not root.exists()
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(b.read_bytes());assert v['active_segment'] is None
for p in [b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
assert psutil.virtual_memory().available>4*1024**3
root.mkdir()
print(json.dumps(dict(root_created_CPU_only=True,canonical_SHA=hashlib.sha256(b.read_bytes()).hexdigest(),two_locks_free=True,epoch=time.time())))
''','S4_TARGET_CPU_SOURCE_ROOT_CREATED_ACTUAL')
        sf=client.open_sftp();sf.get_channel().settimeout(60)
        for p in sorted(payload.iterdir()):sf.put(str(p),REMOTE+'/'+p.name)
        result=run('''from pathlib import Path
import runpy,sys,json,hashlib
root=Path('''+repr(REMOTE)+''');sys.path.insert(0,str(root))
manifest=json.loads((root/'CPU_COMPONENT_SOURCE_MANIFEST.json').read_bytes())
for name,h in manifest['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h
runpy.run_path(str(root/'target_s4_rsl5_components_CPU_admission_v1.py'),run_name='__main__')
''','S4_TARGET_CPU_COMPONENT_TRANSPORT_ACTUAL')
        out=D/'target_actual_CPU_outputs'/stamp;out.mkdir(parents=True)
        for name in ('TARGET_S4_RSL5_COMPONENT_CPU_ACTUAL.json','S4_TARGET_CPU_ALGORITHM_FIXTURE.pt'):
            sf.get(REMOTE+'/'+name,str(out/name),max_concurrent_prefetch_requests=16)
        assert sha(out/'S4_TARGET_CPU_ALGORITHM_FIXTURE.pt')==result['fixture']['sha256']
        report=dict(epoch=time.time(),target_actual=result,twohost_CPU_fixture_SHA_exact=True,
            source_manifest_SHA=sha(payload/'CPU_COMPONENT_SOURCE_MANIFEST.json'),local_outputs=str(out),root_admission=guard,
            target_CPU_only_not_GPU_or_learning_admission=True,original_environment_fullrestore_pending=True)
        p=R/('S4_ACTUAL_LINUX_RSL5_COMPONENT_TARGET_CPU_ADMITTED_'+stamp+'.json');p.write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(dict(passed=True,report=str(p),target_versions=result['actual_versions'],optimizer_updates=0,GPU=False)))
    except BaseException:
        (R/('S4_TARGET_CPU_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry=True)),encoding='utf8');raise
    finally:
        if sf:sf.close()
        t.close(client)

if __name__=='__main__':main()
