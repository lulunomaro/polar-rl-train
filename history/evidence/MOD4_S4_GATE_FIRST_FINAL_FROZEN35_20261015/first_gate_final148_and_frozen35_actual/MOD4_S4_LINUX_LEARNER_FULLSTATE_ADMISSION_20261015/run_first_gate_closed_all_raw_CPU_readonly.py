"""One sequential, source-bound CPU review of closed durable files; no poller."""
from pathlib import Path
import hashlib, json, shlex, sys, time
D = Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t

def main():
    assert json.loads((D/'reports/S4_FIRST_GATE_OWN_FINAL_WHOLE_LOCAL_CPU_VERIFIED.json').read_bytes())['passed'] is True
    source = D/'review_first_gate_closed_all_raw_remote_CPU.py'
    code = source.read_text(encoding='utf8');compile(code,str(source),'exec')
    c = None; stamp = str(time.time_ns())
    try:
        c = t.connect()
        si,so,se = c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=600)
        si.write(code);si.flush();si.channel.shutdown_write()
        lines = []
        for line in so:
            lines.append(line)
            if line.startswith('CPU_RAW_PROGRESS '): print(line.strip(),flush=True)
        err=se.read().decode('utf8','replace');rc=so.channel.recv_exit_status();raw=''.join(lines)
        transcript = D/'reports'/('S4_FIRST_GATE_FULL_RAW_CPU_TRANSPORT_'+stamp+'.json')
        transcript.write_text(json.dumps(dict(rc=rc,stdout=raw,stderr=err,
            reader_source_SHA=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2),encoding='utf8')
        assert rc == 0,str(transcript)
        result = json.loads(next(v[len('S4_FINAL_CPU_RESULT '):] for v in lines if v.startswith('S4_FINAL_CPU_RESULT ')))
        out = D/'reports'/'S4_FIRST_GATE_CLOSED_ALL_RAW_CPU_VERIFIED.json';assert not out.exists()
        out.write_text(json.dumps(result,indent=2),encoding='utf8')
        print(json.dumps({k:result[k] for k in ('passed','updates','controls','qualified_gradient_samples',
            'total_gate_rollout_bytes','total_prefix_bytes','ordinary_events','CPU_GPU_sample_joint_logp_max_abs_error')}),flush=True)
    finally:t.close(c)

if __name__=='__main__':main()
