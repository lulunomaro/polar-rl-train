from pathlib import Path
import ast,time,json,os,subprocess,argparse,traceback,hashlib
import supervise_wave50_route_second_bounded_once as prior446
from wave50_route_startup_resource_guard import verify_failed_boundary,INIT_SHA,ORIGINAL35_SHA
prior=prior446.prior;D=prior.D;R=prior.R;CODE=prior.CODE;s=prior.s
ENTRY='train_wave50_route_startup_resource_reviewed_ppo.py'
read=prior446.read;identity=prior446.identity;fullsave=prior446.fullsave
source=prior446.source;runtime=prior446.runtime
_trainers=prior446.trainers
def trainers():
    rows=_trainers()
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv=[x.decode(errors='replace') for x in p.read_bytes().split(bytes([0]))]
            if any(Path(x).name==ENTRY for x in argv):rows.append(identity(int(p.parent.name)))
        except (OSError,ValueError):pass
    return rows
prior446.trainers=trainers
boundary443=prior446.boundary
tree=ast.parse((D/'supervise_wave50_route_second_bounded_once.py').read_text())
node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='verify')
text=ast.unparse(node).replace('== 446','== 449');exec(compile(text,str(__file__)+'#source449-proof','exec'),vars(prior446))
verify449=prior446.verify

def verify():
    verify449()
    f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/SOURCE_FREEZE.json'))['sha256']
    assert len(f)==449 and len(old)==446 and all(f[k]==v for k,v in old.items())
    assert read(R/'RESOURCE_TARGET_CPU_PASSED.json')['source_count']==449

def boundary():
    boundary443();verify_failed_boundary(prior446)

for name in ('train','guardian'):
    node=next(x for x in ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name==name)
    text=ast.unparse(node)
    for a,b in prior446.replacements.items():text=text.replace(a,ENTRY if a=='train_wave50_route_resume_ppo.py' else b)
    exec(compile(text,str(__file__)+'#same-scope-'+name,'exec'),vars(prior))
prior.verify=verify;prior.source=source;prior.runtime=runtime;prior.trainers=trainers

def main():
    assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();boundary();init=source()
    s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
    prior.write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_WAVE50',source=fullsave(init),original446_failed_startup_unique_settled_and_human_ended=True,no_new_budget_seconds=True))
    prior.write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),target_seconds=1800,no_GPU_preflight_replay=True,new_budget_seconds=0))
    with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    prior.write('E1_GUARDIAN_STARTED.json',identity(g.pid))
    saved,row=prior.train(init,20000,10000,min(1800,s.left()),'e1_WAVE50_route_startup_resource_reviewed_observation',False)
    assert s.q.base.sha(init)==INIT_SHA and saved.is_relative_to(D/'learning_logs')
    prior.write('E1_WAVE50_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),source684_preserved=True,other_experts_unchanged=True))
    prior.publish(saved);prior.write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,requires_actual_fourcase_review=True,automatic_more_PPO_disallowed=True))
    prior.phase('E1_WAVE50_route_startup_resource_reviewed_saved_review_ready',child=None)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    try:
        if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
        else:main()
    except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],no_blind_resume=True));raise
