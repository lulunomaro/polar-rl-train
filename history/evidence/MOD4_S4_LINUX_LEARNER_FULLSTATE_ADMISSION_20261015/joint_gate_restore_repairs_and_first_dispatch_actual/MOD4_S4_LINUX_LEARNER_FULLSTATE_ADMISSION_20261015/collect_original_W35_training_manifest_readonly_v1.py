"""Read actual original W35 exposure/clock; no GPU/import/old launcher."""
from pathlib import Path
import sys,json,time,hashlib,traceback,shlex
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
PATH='/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_SECOND_BOUNDED_20261011/learning_logs/2026-10-11_23-27-01_e1_WAVE35_second_bounded_observation_1791732224672851875/run_manifest.json'
def main():
    c=None; stamp=str(time.time_ns())
    try:
        c=t.connect();code='from pathlib import Path\nimport json,hashlib\np=Path('+repr(PATH)+');raw=p.read_bytes();print(json.dumps(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),manifest=json.loads(raw))))'
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
        (D/'reports'/('W35_ORIGINAL_MANIFEST_TRANSPORT_'+stamp+'.json')).write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),readonly=True)),encoding='utf8');assert rc==0
        v=json.loads(raw);p=D/'actual_original_W35_run_manifest.json';assert not p.exists()
        sf=c.open_sftp()
        try:sf.get(PATH,str(p),max_concurrent_prefetch_requests=16)
        finally:sf.close()
        assert p.stat().st_size==v['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
        print(json.dumps(dict(source=v['path'],sha256=v['sha256'],env=v['manifest']['env'],num_envs=v['manifest']['num_envs'],source_map_count=len(v['manifest'].get('source_map',{})))))
    except Exception:
        (D/'reports'/('W35_ORIGINAL_MANIFEST_READER_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True)),encoding='utf8');raise
    finally:t.close(c)
if __name__=='__main__':main()
