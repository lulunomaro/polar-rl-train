"""Independent286; preserve CPU storage for CUDA generator RNG state."""
from pathlib import Path
import ast,hashlib,json,time,shutil
OLD=Path(__file__).resolve().parent;T=OLD.parent
N=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V286_20261101';N.mkdir(exist_ok=False);R=N/'reports';R.mkdir()
for folder in ('source','control285'):
    dest=N/('control286' if folder=='control285'else folder);dest.mkdir()
    for p in (OLD/folder).rglob('*.py'):
        if '__pycache__'in p.parts:continue
        rel=p.relative_to(OLD/folder);rel=rel.with_name(rel.name.replace('285','286'))
        q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True)
        text=p.read_text('utf8').replace('285','286')
        if p.name=='worker285.py':text=text.replace("wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'])", "wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())")
        ast.parse(text);q.write_text(text,encoding='utf8')
for name in ('teacher_task285.py','launch285_original_teacher_student_once.py','collect285_status_readonly.py'):
    text=(OLD/name).read_text('utf8').replace('285','286');ast.parse(text)
    (N/name.replace('285','286')).write_text(text,encoding='utf8')
shutil.copyfile(OLD/'reference285.npz',N/'reference286.npz')
task=json.loads((OLD/'TASK285_FROZEN.json').read_bytes())
oldrun=task['run_id'];run='LQR_MPC_DEPTH_STUDENT286_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
task.update(kind='LQR_MPC_REFERENCE_DEPTH_SUPERMIMIC_400N50_V286',run_id=run,job_root=root+'/student72',owner_root=root+'/owner72',
 worker_SHA=hashlib.sha256((N/'source/worker286.py').read_bytes()).hexdigest(),generation='FROZEN_BEFORE_GO_TEACHER286',
 predecessor_actual='285 carrier decoded once; failed restoring CUDA RNG tensor on CUDA. No new optimizer steps; original fee preserved.')
task['reference']=dict(task['reference'],path='reference286.npz')
(N/'TASK286_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
row=dict(epoch=time.time(),trial_id='teacher286-cuda-rng-cpu-storage-repair',predecessor_run=oldrun,
 error='torch.load map_location=cuda moved stored RNG bytes to CUDA; Generator.set_state requires CPU ByteTensor',
 repair='restore original16B CUDA Philox state through .cpu(), preserve exact saved bytes',
 independent_new_Task_and_manifest=True,old285_false_source_preserved=True,CPU284_identity_H32_reused=True,
 mesh_scalar_repair_reused=True,reference_NPZ_reused=True,actual_reference_teacher_model_rereads=0)
(R/'SOURCE286_CUDA_RNG_REPAIR.json').write_text(json.dumps(row,indent=2),encoding='utf8')
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(N.rglob('*'))if p.is_file()and p.suffix in('.py','.json')]
index=N/'INDEX286_SOURCE_TASK_CALLERS_FROZEN.json';index.write_text(json.dumps(dict(epoch=time.time(),kind='FROZEN_TEACHER286_BEFORE_GO',files=files),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(N),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest())))
