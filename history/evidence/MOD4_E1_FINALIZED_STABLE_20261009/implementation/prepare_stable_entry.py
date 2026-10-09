"""Create a distinct bounded entry; original310 source and training worker unchanged."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;B=D.parent
s=(B/'MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009/supervise_e1_route_health_review.py').read_text(encoding='utf8')
tree=ast.parse(s)
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
replacements={}
replacements['verify']='''def verify():
    verify_original_records(s.q,D)
    a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    f=read(R/'SOURCE_FREEZE.json')['sha256'];previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009');old=read(previous/'reports/SOURCE_FREEZE.json')['sha256']
    assert len(old)==310 and len(f)==311
    for n,h in f.items():assert s.q.base.sha(D/n)==h,n
    for n,h in old.items():assert f[n]==h and s.q.base.sha(previous/n)==h,n
    assert read(CODE/'env.json')==read(previous/'isaac/mod4/env.json')
    assert read(R/'REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json')['weights_discarded']
    assert read(R/'E1_ROUTE_HEALTH_CPU_PASSED.json')['passed']
    assert read(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json')['snapshot57_exact']
'''
replacements['source']='''def source():
    review=read(R/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json')
    assert review['actual_five_cases_review_complete'] and review['task_model_data_scope_accepted'] and review['no_systemic_direction_or_major_retention_failure_observed']
    actual=read(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json');row=actual['row'];p=Path(row['checkpoint']['path'])
    assert review['source_sha256']==row['checkpoint']['sha256']=='655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f'
    assert fullsave(p)==row['checkpoint'] and learning_health_pass(row['health']) and len(row['unique_completed_segment'])==1
    return p
'''
replacements['wait_existing']='''def wait_existing():
    previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009');pr=previous/'reports';ps=read(pr/'E1_STATE.json')
    assert ps['phase']=='E1_shallow_saved_review_ready' and ps.get('child') is None
    row=read(pr/'e1_gentle_route_recovery_PASSED.json')
    locators=[ps['owner'],read(pr/'E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=69438489)]
    assert all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in locators)
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert len([v for v in read(s.q.ctl.CANONICAL)['completed_segments'] if v['pid']==row['own_PID_bound_receipt']['pid']])==1
'''
replacements['publish']='''def publish(init,label):
    packages=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json');sha=s.q.base.sha(init);dest=s.q.ER.parent/'artifacts'/('e1-stable-own-'+sha+'.pt')
    if not dest.exists():shutil.copy2(init,dest)
    assert s.q.base.sha(dest)==sha;checkpoint=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha);jobs=[]
    # Exact admitted frozen dispatchers; one actual terrain route and three old skills.
    for template in packages['jobs'][1:]:
        row=json.loads(json.dumps(template));kind=row['kind'];terrain=row['actual_behavior_scope'].startswith('gentle terrain')
        job='clk2500-closure-episode-d3-'+label+('-terrain' if terrain else '-retention')+'-'+kind
        row.update(job_id=job,published_epoch=time.time(),role='Independent E1 unchanged-gentle stable candidate; actual terrain and inherited old skill, no learning evaluation',scope_pending_actual_review=True)
        row['artifacts']['checkpoint']=checkpoint;p=s.q.ER.parent/'eval_queue'/(job+'.json');assert not p.exists()
        s.q.base.atomic_json(p,row);jobs.append(row)
    write('E1_'+label+'_ASYNC_PUBLISHED.json',dict(epoch=time.time(),source=checkpoint,jobs=jobs,no_GPU_or_canonical_write=True))
'''
replacements['main']='''def main():
    import torch;torch.set_num_threads(1)
    assert not (R/'E1_DISPATCH_STARTED.json').exists();verify()
    write('E1_BEHAVIOR_GATED_ENTRY_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),CPU_only_while_waiting=True,no_GPU_or_canonical_write_before_actual_scope=True))
    phase('waiting_actual_E1_route_and_old_skill_review',child=None)
    while not (R/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json').exists():
        if (R/'E1_BEHAVIOR_SCOPE_ATTENTION.json').exists():
            write('E1_REVIEW_READY.json',dict(epoch=time.time(),actual_behavior_attention_hold=True,all_courses_finished=False));return
        time.sleep(15)
    verify();wait_existing();init=source()
    s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    wait_existing();before=s.q.ctl.CANONICAL.read_bytes()
    write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),old_parent_guardian_children_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0))
    write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),maximum_stable_window_seconds=14400,blocks=2,unchanged_gentle_geometry=True,repeated45min_clock_trial=False,new_budget_seconds=0))
    assert before==s.q.ctl.CANONICAL.read_bytes()
    with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    write('E1_GUARDIAN_STARTED.json',identity(g.pid))
    write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(read(R/'REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'),reused_exact_scope_no_GPU_replay=True))
    for block in (1,2):
        if s.left()<=120:break
        init,row=train(init,20000,10000,min(7200,s.left()),'e1_gentle_stable_block'+str(block),False)
        publish(init,'116-e1-gentle-b'+str(block))
    write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),all_courses_finished=False,next='Actual stable terrain and inherited retention review before any gradual geometry increment; E0 remains frozen; RM annotations retained'))
    phase('E1_gentle_stable_saved_review_ready',child=None)
'''
lines=s.splitlines(keepends=True)
for n in sorted(replacements,key=lambda n:functions[n].lineno,reverse=True):
 node=functions[n];lines[node.lineno-1:node.end_lineno]=[replacements[n]+'\n']
out=''.join(lines);ast.parse(out)
out=out.replace('"""Approved S3 independent E1; new terrain preflight and bounded first task, no clock repetition."""','"""Independent E1 same-scope stable entry gated by actual planned route and old skills."""')
(D/'supervise_e1_behavior_stable_continuation.py').write_text(out,encoding='utf8')
print('New behavior-gated bounded controller prepared; all original training and health functions unchanged')
