"""Mirror this independent headless MuJoCo trial to the authorized host72 root."""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import sys
import tarfile
import time

T = Path(__file__).resolve().parent
R = T.parents[2]
REMOTE = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_MOVING_CROUCH_JUMP_20261113_R1'
p = argparse.ArgumentParser()
p.add_argument('mode', choices=['prepare', 'run', 'status', 'collect', 'sync'])
p.add_argument('--access-dir', required=True)
p.add_argument('--name', default='flat_pilot_teacher_r1')
p.add_argument('--model', default='teacher')
p.add_argument('--terrain', default='flat')
p.add_argument('--configs')
p.add_argument('--speeds', nargs='+', default=['.6'])
p.add_argument('--seeds', nargs='+', default=['0'])
p.add_argument('--seconds', default='8')
a = p.parse_args()
sys.path.insert(0, a.access_dir)
from ssh72 import connect, execute


def run(client, command, timeout=50):
    status, out, err = execute(client, command, timeout)
    print(out, end='')
    print(err, end='')
    if status:
        raise RuntimeError(f'Remote command failed with status {status}')


c = connect()
try:
    s = c.open_sftp()
    if a.mode == 'prepare':
        archive = Path(a.access_dir)/'moving_jump_inputs.tar.gz'
        delivery = R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
        teacher = T.parent/'MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113'
        inputs = []
        for path in sorted(T.rglob('*')):
            if path.is_file() and path.suffix == '.py' and '__pycache__' not in path.parts:
                inputs.append((path, path.relative_to(T).as_posix()))
        for source in [delivery/'runtime/core', delivery/'plant']:
            for path in sorted(source.rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                    inputs.append((path, 'delivery/'+path.relative_to(delivery).as_posix()))
        for rel in ['viewer/showcase.py', 'viewer/MAP_MANIFEST.json', 'viewer/tiles/r03_c00.npz']:
            inputs.append((delivery/rel, 'delivery/'+rel))
        for model, path in [('teacher', teacher/'weights/selected_stair_teacher.pt'),
                            ('parent', teacher/'frozen_parent/best_parent_full_ppo.pt')]:
            inputs.append((path, 'weights/frozen_'+model+'.pt'))
        with tarfile.open(archive, 'w:gz') as tar:
            for path, name in inputs:
                tar.add(path, arcname=name, recursive=False)
        manifest = dict(root=REMOTE, epoch=time.time(), files=[
            dict(path=name, source=str(path), bytes=path.stat().st_size,
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path, name in inputs])
        (T/'evidence/INPUTS.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf8')
        run(c, 'test ! -e '+shlex.quote(REMOTE)+' && mkdir '+shlex.quote(REMOTE))
        s.put(str(archive), REMOTE+'/inputs.tar.gz')
        run(c, 'cd '+shlex.quote(REMOTE)+' && tar -xzf inputs.tar.gz && sha256sum weights/*.pt delivery/plant/MOD4v3_HW300N60_R3/mjcf/scene.xml')
    elif a.mode == 'run':
        for path in [T/'moving_jump.py', T/'remote_io.py']:
            s.put(str(path), REMOTE+'/'+path.name)
        command = ['/home/lc01/Zonglin Li/zonglin2/run-python.sh', '-u', '-B',
                   REMOTE+'/moving_jump.py', '--out', REMOTE+'/evidence/'+a.name,
                   '--model', a.model, '--terrain', a.terrain, '--seconds', a.seconds,
                   '--speeds', *a.speeds, '--seeds', *a.seeds]
        if a.configs:
            path = Path(a.configs)
            s.put(str(path), REMOTE+'/'+path.name)
            command += ['--configs', REMOTE+'/'+path.name]
        log = REMOTE+'/'+a.name+'.log'
        script = 'cd '+shlex.quote(REMOTE)+'\nmkdir -p evidence\nnohup env MUJOCO_GL=egl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 '+shlex.join(command)+' >'+shlex.quote(log)+' 2>&1 < /dev/null &\necho JOB_PID=$!'
        run(c, 'test ! -e '+shlex.quote(REMOTE+'/evidence/'+a.name))
        run(c, script)
        print(json.dumps(dict(name=a.name, log=log, command=command)))
    elif a.mode == 'status':
        run(c, 'tail -n 10 '+shlex.quote(REMOTE+'/'+a.name+'.log')+'; test ! -f '+shlex.quote(REMOTE+'/evidence/'+a.name+'/COMPLETE.json')+' || echo COMPLETE')
    elif a.mode == 'collect':
        archive = REMOTE+'/collected_'+a.name+'.tar.gz'
        run(c, 'cd '+shlex.quote(REMOTE)+' && tar -czf '+shlex.quote(archive)+' evidence/'+shlex.quote(a.name)+' '+shlex.quote(a.name+'.log'), 60)
        local = Path(a.access_dir)/('moving_jump_'+a.name+'.tar.gz')
        s.get(archive, str(local))
        with tarfile.open(local, 'r:gz') as tar:
            tar.extractall(T, filter='data')
        print('COLLECTED '+str(local))
    else:
        for path in sorted(T.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix not in ('.py', '.md', '.json', '.png', '.gif', '.log'):
                continue
            rel = path.relative_to(T).as_posix()
            if 'scene_assets' in path.parts:
                continue
            remote = REMOTE+'/'+rel
            parent = str(Path(remote).parent).replace('\\', '/')
            try:
                s.stat(parent)
            except FileNotFoundError:
                run(c, 'mkdir -p '+shlex.quote(parent))
            s.put(str(path), remote)
    s.close()
finally:
    c.close()
