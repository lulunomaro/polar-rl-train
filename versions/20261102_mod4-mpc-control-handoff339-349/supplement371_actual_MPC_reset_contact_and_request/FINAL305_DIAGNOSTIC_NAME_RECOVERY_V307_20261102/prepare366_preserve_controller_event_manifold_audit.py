"""Keep365unused: separate read-only manifold acceptance from controller event.

Static review found365 reused new acceptance ontop for controller.observe_top,
which would alter recovery timing.366 preserves363's exact event expression.
"""
from pathlib import Path
import ast,hashlib,json,re,shutil,time,traceback
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
S=T/'MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V365_20261102';D=T/'MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V366_20261102'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
try:
    assert not(S/'reports/ROOT365_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
    put(R/'STATIC365_UNUSED_CONTROLLER_EVENT_SCOPE_ERROR.json',dict(epoch=time.time(),passed=False,network=0,SDK=0,NN=0,physics=0,consumed=False,original_frozen_package_preserved=True,error='365 measureontop reused by controller.observe_top would alter recoverevent; advertised samecontroller audit scope was incorrect',repair='366 independent keeps original363 geometry event separately; only evaluation uses actualtopmanifold andlatchedfirstclearance'))
    D.mkdir(exist_ok=False);(D/'reports').mkdir();rename=lambda s:re.sub(r'(?<=[A-Za-z_])365(?!\d)','366',s)
    for p in sorted(S.rglob('*')):
        rel=p.relative_to(S)
        if not p.is_file()or'__pycache__'in rel.parts or any(q in rel.parts for q in('reports','replay'))or p.name.startswith('INDEX365'):continue
        dest=D/rename(str(rel));dest.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix in('.py','.json'):dest.write_text(rename(p.read_text('utf8')),encoding='utf8')
        else:shutil.copyfile(p,dest)
    p=D/'source/evaluate366.py';w=p.read_text('utf8')
    old='top_force,ground_force,contact_counts,selected_manifold=read_manifold()';assert w.count(old)==1
    w=w.replace(old,'controller_ontop=inside.all(-1)&(low[:,:,2]>=.269).all(-1)&(low[:,:,2]<=.28).all(-1)&(wf[:,:,2]>1).all(-1)&(nw<=1)&active\n  '+old)
    assert w.count('bool(ontop[env_id])')==1;w=w.replace('bool(ontop[env_id])','bool(controller_ontop[env_id])')
    p.write_text(w,encoding='utf8');task=read(D/'TASK366_FROZEN.json');task.update(kind='MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT366',worker_SHA=H(p),source_recovery_event_same_as363=True,evaluation_contact_manifold_not_controller_input=True,unused365_static_scope_failure_retained=True)
    (D/'TASK366_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    p=D/'contract366.py';c=p.read_text('utf8').replace('MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT366','MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT366');p.write_text(c,encoding='utf8')
    for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    ns={};exec(compile(c,str(D/'contract366.py'),'exec'),ns);assert ns['validate_task'](task)
    put(D/'reports/STATIC366_SOURCE_EVENT_AND_LATCH.json',dict(epoch=time.time(),passed=True,original363_controller_ontop_expression_retained=True,actualmanifold_only_acceptance=True,firstflight_wholeclearance_stayslatched_aftertoprebound=True,groundreturn_edgeback_speed003_halfsecond_unchanged=True,physics=0,SDK=0,NN=0))
    files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
    put(D/'INDEX366_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
    put(R/'STATIC366_MANIFOLD_AUDIT_READY.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX366_SOURCE_TASK_CALLERS_FROZEN.json'),actual_runtime_started=False,unused365_preserved=True))
    print(json.dumps(dict(prepared=True,root=str(D),INDEX_SHA=H(D/'INDEX366_SOURCE_TASK_CALLERS_FROZEN.json'),SDK=0,GO=False)))
except BaseException:
    put(R/('LOCAL366_ORIGINAL_PREPARATION_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),NN=0,SDK=0,network=0,physics=0));raise
