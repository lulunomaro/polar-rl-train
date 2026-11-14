"""Collect and archive the finite job after its own evaluation supervisor exits."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
import traceback

T = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--access-dir', required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.access_dir)
    from ssh72 import connect, execute
    lease = T / 'evidence/FINALIZER_OWNER.json'
    with lease.open('x', encoding='utf8') as stream:
        json.dump(dict(pid=os.getpid(), epoch=time.time(), restarts_training=False), stream, indent=2)
    plan = json.loads((T / 'PLAN.json').read_bytes())
    while True:
        client = None
        try:
            client = connect()
            script = '''
import json
from pathlib import Path
p=PLAN
r=Path(p['task_root'])
t=r/p['training_job']
h=r/('SUPERVISION_'+p['training_job']+'.jsonl')
done=False
if h.exists():
 rows=[json.loads(line) for line in h.read_text().splitlines() if line.strip()]
 done=bool(rows) and rows[-1]['event'] in ('complete','training_failed')
print(json.dumps(dict(ready=done and (t/'SAFE_CLOSED.json').exists())))
'''.replace('PLAN', repr(plan))
            code, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 30)
            assert code == 0, out + err
            if json.loads(out)['ready']:
                break
        except Exception:
            print(traceback.format_exc(), flush=True)
        finally:
            if client is not None:
                client.close()
        time.sleep(60.)
    subprocess.run([sys.executable, '-X', 'utf8', '-B', str(T / 'control72.py'), '--access-dir',
                    args.access_dir, '--mode', 'collect'], check=True)
    subprocess.run([sys.executable, '-X', 'utf8', '-B', str(T / 'report.py'), '--phase', 'final'], check=True)
    subprocess.run([sys.executable, '-X', 'utf8', '-B', str(T / 'archive_results.py'), '--phase', 'final'], check=True)


if __name__ == '__main__':
    main()
