"""Read sole canonical segment identities; no budget mutation or copied ledger."""
from scut_wave_io import *

def main():
    n,w=transport.io.connect_both()
    try:
        code=r'''from pathlib import Path
import json,hashlib,time
p=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=p.read_bytes();b=json.loads(raw)
segments=b['completed_segments']
rows=[x for x in segments if 'wave' in str(x.get('kind','')).lower()]
print(json.dumps(dict(epoch=time.time(),canonical_path=str(p),canonical_bytes=len(raw),canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_keys=list(b),all_wave_named_completed_segments=rows,completed_segments=len(segments),active=b.get('active_segment'),Sactive=b.get('S_active'),no_ledger_write_or_copy=True)))
'''
        _,o,e=n.exec_command(transport.io.PY+' -c '+transport.shlex.quote(code),timeout=60)
        raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')
        v=json.loads(raw);save('WAVE_CANONICAL_NAMED_SEGMENTS_ACTUAL.json',v)
        print(json.dumps(dict(keys=v['canonical_keys'],segments=v['all_wave_named_completed_segments'])))
    finally:transport.io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE_DURATION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_budget_write=True));raise
