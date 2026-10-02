"""Apply the verified floor candidate ONLY to a separately copied, inactive task.

Does not launch training, alter checkpoints, change rewards or overwrite the source task.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil

SOURCE=Path('/home/egde/rl_candidates/MOD4_contact_integrated_repair_20260930')
EXPECTED_TASK_SHA='af03769591164a48b478ad5635c864069541c04789ff359786215f1e1b6c914f'
p=argparse.ArgumentParser();p.add_argument('--task-root',required=True);args=p.parse_args()
r=Path(args.task_root).resolve()
if r==SOURCE.resolve() or r in SOURCE.resolve().parents or SOURCE.resolve() in r.parents:
    raise SystemExit('Refusing to patch original task or its parent/subdirectories; use a separate copied task.')
code=r/'isaac/mod4';task=code/'mod4_task.py';envpath=code/'env.json'
if not task.is_file() or not envpath.is_file():raise SystemExit('Expected a copied MOD4 task with isaac/mod4 source and env.json.')
for status in [r/'status.json']:
    if status.exists():
        s=json.loads(status.read_text())
        for key in ['training_pid','supervisor_pid','evaluation_pid']:
            pid=s.get(key)
            if pid and Path(f'/proc/{pid}/cmdline').exists():
                raise SystemExit('Target status refers to a live process. Prepare a clean inactive copy first.')
raw=task.read_bytes();sha=hashlib.sha256(raw).hexdigest()
if sha!=EXPECTED_TASK_SHA:raise SystemExit(f'Source differs from audited task: {sha}. Review diff first; no patch applied.')
cfg=json.loads(envpath.read_text())
if cfg.get('RM_MOD4_TERRAIN','flat')!='flat':raise SystemExit('This candidate is for flat only. Do not deploy it to Rough/RMUC unchanged.')
anchor='        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)))'
s=raw.decode('utf-8').replace('\r\n','\n');assert s.count(anchor)==1
block='''
    # Verified isolated flat-floor fix, 2026-09-30. No robot/actuator/reward changes.
    if os.environ.get("RM_FLAT_NATIVE_PLANE", "0") == "1":
        if os.environ.get("RM_MOD4_TERRAIN", "flat") != "flat":
            raise RuntimeError("Native flat-floor candidate requires flat terrain")
        from ground_plane_candidate import spawn_local_native_plane
        ground.spawn.func = spawn_local_native_plane
        ground.init_state.pos = (0.0, 0.0, 0.0)
'''
s=s.replace(anchor,anchor+block,1);ast.parse(s)
backup=code/'floor_fix_source_before';backup.mkdir(exist_ok=False)
shutil.copy2(task,backup/task.name);shutil.copy2(envpath,backup/envpath.name)
shutil.copy2(Path(__file__).with_name('ground_plane_candidate.py'),code/'ground_plane_candidate.py')
task.write_text(s,encoding='utf-8',newline='\n');ast.parse(task.read_text(encoding='utf-8'));cfg['RM_FLAT_NATIVE_PLANE']='1'
envpath.write_text(json.dumps(cfg,indent=2),encoding='utf-8',newline='\n')
manifest={'source_task':str(SOURCE),'patched_task':str(r),'before_mod4_task_sha256':sha,
    'after_mod4_task_sha256':hashlib.sha256(task.read_bytes()).hexdigest(),
    'scope':'Flat ground only: replace huge thin Cube with native Z-plane at z=0; same friction/offset settings.',
    'training_started':False,'warm_start_checkpoint':'model_8648.pt',
    'warm_start_sha256':'343c56615e7ee6708a6a6a8057cb30877f5ea83d9a2249e079a991db522196d2'}
(r/'NATIVE_FLOOR_PATCH_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
