"""Bundle approved bytes and new task distribution for the isolated host72 job."""
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
p = argparse.ArgumentParser()
p.add_argument('--access-dir', required=True)
p.add_argument('--archive', required=True)
a = p.parse_args()
sys.path.insert(0, a.access_dir)
from ssh72 import connect, execute

remote = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_LOW_SPEED_RETRACTION_20261113_R1'
origin = T.parent / 'MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113'
plan = json.loads((origin / 'PLAN.json').read_text())
plan.update(root=remote, runtime=remote+'/dependencies/launcher', shared_package=remote+'/dependencies/package',
            package=remote+'/native_package', support=remote+'/support', source_paths=remote+'/dependencies/SOURCE_PATHS.72.json',
            reset_bank=remote+'/dependencies/reset_bank.json', cumulative_training_seconds_before=0,
            budget_total_training_seconds=1200, phase='straight_low_speed_distribution_only',
            python='/home/lc01/Zonglin Li/zonglin2/run-python.sh')
plan['training_round']['seconds'] = 600
plan['training_round']['num_envs'] = 2048
plan['continuous_stair'].update(command_vx_m_s=[.2,.6],mid_start_fraction_of_ascent=0.)
plan['specialist'].update(straight_fraction=1.,oblique_fraction=0.,whole_start_fraction=1.,mid_start_fraction=0.,train_seconds=600)
plan['task_change'] = 'Only training task distribution: straight whole-course low-speed approaches. Original rewards, DR, PPO, controller and guards unchanged. Only independently confirmed post-block recovery counts for the requested skill.'
plan['teacher_retention'].update(keep_teacher=remote+'/teacher_data/healthy_flat_rough_teacher.pt',dataset=remote+'/teacher_data/native_stair_success_demos.pt')

# Read the original seed data through the existing authorized connection; no writes on210.
sys.path.insert(0, str(R.parent/'tmp'))
from step7_remote_access import connect as connect210
data_dir = T/'teacher_data'
data_dir.mkdir(exist_ok=True)
c210 = connect210()
try:
    s = c210.open_sftp()
    for filename in ('healthy_flat_rough_teacher.pt','native_stair_success_demos.pt'):
        target = data_dir/filename
        if not target.exists():
            s.get(json.loads((origin/'PLAN.json').read_text())['root']+'/'+filename, str(target))
    s.close()
finally:
    c210.close()
assert hashlib.sha256((data_dir/'healthy_flat_rough_teacher.pt').read_bytes()).hexdigest()==plan['teacher_retention']['keep_teacher_sha256']
assert hashlib.sha256((data_dir/'native_stair_success_demos.pt').read_bytes()).hexdigest()==plan['teacher_retention']['dataset_sha256']

for model in ('parent','teacher'):
    part = json.loads(json.dumps(plan))
    filename = 'frozen_'+model+'.pt'
    part['parent'] = remote+'/weights/'+filename
    part['parent_sha256'] = hashlib.sha256((T/'weights'/filename).read_bytes()).hexdigest()
    part['parent_iteration'] = 25331 if model=='parent' else 25432
    (T/('PLAN_'+model+'.json')).write_text(json.dumps(part,indent=2)+'\n')
paths = json.loads((T/'dependencies/SOURCE_PATHS.relative.json').read_text())
(T/'dependencies/SOURCE_PATHS.72.json').write_text(json.dumps({k:remote+'/dependencies/'+v for k,v in paths.items()},indent=2)+'\n')
(T/'MODELS.72.json').write_text(json.dumps({k:remote+'/weights/frozen_'+k+'.pt' for k in ('parent','teacher')},indent=2)+'\n')
manifest = []
include = ['support','dependencies','native_package','weights','teacher_data','native_low_speed_pair.py','PLAN_parent.json','PLAN_teacher.json','MODELS.72.json']
with tarfile.open(a.archive,'w:gz') as tar:
    for name in include:
        source = T/name
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':
                continue
            rel = path.relative_to(T).as_posix()
            tar.add(path,arcname=rel,recursive=False)
            manifest.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(T/'evidence/REMOTE_INPUTS.json').write_text(json.dumps(dict(epoch=time.time(),root=remote,files=manifest),indent=2)+'\n')
client = connect()
try:
    s=client.open_sftp()
    remote_archive=remote+'/inputs.tar.gz'
    s.put(a.archive,remote_archive)
    s.close()
    status,out,err=execute(client,'cd '+shlex.quote(remote)+' && tar -xzf inputs.tar.gz && sha256sum weights/frozen_parent.pt weights/frozen_teacher.pt native_package/assets/robot.usd native_package/mjcf/scene.xml',60)
    print(out,err)
    if status:raise RuntimeError('Host72 input extraction failed')
finally:
    client.close()
print(json.dumps(dict(uploaded_files=len(manifest),archive_bytes=Path(a.archive).stat().st_size,root=remote)),flush=True)
