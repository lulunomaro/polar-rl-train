"""Fresh285 after283 USD numeric-type failure; predecessor remains immutable."""
from pathlib import Path
import ast,hashlib,json,shutil,time
OLD=Path(__file__).resolve().parent;T=OLD.parent
N=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V285_20261101';N.mkdir(exist_ok=False)
R=N/'reports';R.mkdir()
for folder in ('source','control283'):
    dest=N/('control285' if folder=='control283' else folder);dest.mkdir()
    for p in (OLD/folder).rglob('*.py'):
        if '__pycache__'in p.parts:continue
        rel=p.relative_to(OLD/folder);rel=rel.with_name(rel.name.replace('283','285'))
        out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True)
        text=p.read_text('utf8').replace('283','285')
        if p.name=='terrain283.py':
            text=text.replace("mesh.CreatePointsAttr().Set(points);", "mesh.CreatePointsAttr().Set(np.asarray(points,dtype=np.float32).tolist());")
        ast.parse(text);out.write_text(text,encoding='utf8')
for name in ('teacher_task283.py','launch283_original_teacher_student_once.py','collect283_status_readonly.py'):
    text=(OLD/name).read_text('utf8').replace('283','285')
    text=text.replace("R/'CPU284_ACTUAL_CARRIER_MIGRATION_AND_H32_NO_STEP.json'", "T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V283_20261101/reports/CPU284_ACTUAL_CARRIER_MIGRATION_AND_H32_NO_STEP.json'")
    out=N/name.replace('283','285');ast.parse(text);out.write_text(text,encoding='utf8')
shutil.copyfile(OLD/'reference283.npz',N/'reference285.npz')
oldtask=json.loads((OLD/'TASK283_FROZEN.json').read_bytes());task=dict(oldtask)
run='LQR_MPC_DEPTH_STUDENT285_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
task.update(kind='LQR_MPC_REFERENCE_DEPTH_SUPERMIMIC_400N50_V285',run_id=run,job_root=root+'/student72',owner_root=root+'/owner72',
 worker_SHA=hashlib.sha256((N/'source/worker285.py').read_bytes()).hexdigest(),generation='FROZEN_BEFORE_GO_TEACHER285',
 source_cpu_reuse='CPU284 algorithm/actual carrier identity/H32 unchanged. Mesh scalar repair and new typed names only.',
 predecessor_actual='283 failed before model read and naturally closed; original raw fee kept, no refund')
task['reference']=dict(task['reference'],path='reference285.npz')
(N/'TASK285_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
report=dict(epoch=time.time(),trial_id='teacher285-mesh-scalar-repair',predecessor_run=oldtask['run_id'],
 predecessor_failure='USD points contains numpy.float64; mixed python/numpy list cannot coerce to GfVec3f',
 repair='np.asarray(points,dtype=np.float32).tolist() matches existing qualified terrain builder',
 physical_geometry_reward_learner_optimizers_unchanged=True,CPU284_actual_identity_and_H32_reused=True,
 fresh_Task_namespace_manifest_admission_required=True,old283_source_frozen_preserved=True)
(R/'SOURCE285_MESH_SCALAR_REPAIR.json').write_text(json.dumps(report,indent=2),encoding='utf8')
index=dict(epoch=time.time(),kind='FROZEN_TEACHER285_BEFORE_GO',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
 for p in sorted(N.rglob('*'))if p.is_file()and p.suffix in('.py','.json')])
ip=N/'INDEX285_SOURCE_TASK_CALLERS_FROZEN.json';ip.write_text(json.dumps(index,indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(N),run_id=run,index_SHA=hashlib.sha256(ip.read_bytes()).hexdigest())))
