"""Explicit settled continuation from the preselected last paired mature source.

Reuses the completed fullscale frozen report; runs fresh short/PPO checks and
one bounded formal trial. Never repeats a handover or settles an old segment.
"""
import hashlib,json,os,signal,subprocess,sys,time,traceback,fcntl
from pathlib import Path
import supervise_autonomy as ctl
ROOT,CODE,REPORTS,CANONICAL=ctl.ROOT,ctl.CODE,ctl.REPORTS,ctl.CANONICAL
DIAG=Path('/home/egde/rl_candidates/MOD4_RATE5_FULLSCALE_DIAGNOSTIC_20261003/reports')
RECEIPT=REPORTS/'TARGETED_MATURE5_ENTRY_20261003.json'
SOURCE_SHA='63662952ea6be6ca6c259a0563fe2495cefc0ebadf9eb729c69ec1e92aba9075'
def validate_evidence(evidence,report,source):
    assert evidence['stage']=='completed' and evidence['preselected_last_paired_mature'] and evidence['no_checkpoint_search']
    assert evidence['source']['sha256']==source['sha256']==SOURCE_SHA and evidence['source']['path']==source['path']
    assert evidence['physical_smoke_pass'] and evidence['actual_material_parameters_pass'] and evidence['initial_root_q_with_newer_source_exact']
    assert evidence['PPO_performed'] is False and evidence['frozen_ledger_exact']
    assert report['checkpoint']==source['path'] and report['num_envs']==20000 and report['seconds']==1.2
    assert report['explicit_yaw_groups_rad_s'][-2:]==[-5.,5.]
    assert report['mild_initial_parameters']['profile']==report['mild_final_parameters']['profile']=='white_v2'
    assert report['mild_initial_parameters']['actual_parameters_pass'] and report['mild_final_parameters']['actual_parameters_pass']
    assert not report['nonfinite'] and report['terminations']==0 and report['max_tilt_deg']<15
def actual_children():
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        a=ctl.identity(int(p.name))
        if a and a['state']!='Z' and '-c' not in a['argv'] and any(x.endswith(('/train_mod4_ppo.py','/fullscale_worst_diagnostic.py','/supervise_autonomy.py','/supervise_targeted_mature5.py','/spin_rate_probe.py','/validate_speed.py')) for x in a['argv']):found.append(a)
    return found
if __name__=='__main__':
    assert not RECEIPT.exists(),'Completed/interrupted explicit entry: inspect actual state, never repeat'
    assert not actual_children(),actual_children()
    __import__('torch').set_num_threads(1)
    ctl.base.STATE.update(ctl.read(ROOT/'status.json'));ctl.S=ctl.read(ctl.STATE_PATH)
    ctl.idle();ctl.verify()
    assert ctl.read(ROOT/'status.json')['stage']=='targeted_repair_hold' and ctl.S['pending_intermediate5'] is None
    assert ctl.S['profile']=='white_v2' and ctl.rate.current_limit()==4. and set(ctl.S['rate_rejected'])=={5.,6.}
    assert ctl.base.budget_state()['authorized_training_seconds']==252000
    source=Path(ctl.S['mature']['checkpoint']);info=ctl.base.checkpoint(source)
    assert source.name=='model_16425.pt' and info['sha256']==SOURCE_SHA and info['finite_tensors']==68
    evidence=ctl.read(DIAG/'MATURE_SOURCE_DIAGNOSTIC.json');report_path=Path(evidence['report']);r=ctl.read(report_path)
    validate_evidence(evidence,r,info)
    paired=ctl.read(next(REPORTS.glob('auto_0023_*paired_decision.json')))
    assert paired['pass'] and paired['checkpoint']['sha256']==SOURCE_SHA and paired['fixed_cap']==4. and paired['profiles']==['nominal','white_v2']
    for seed in (20261002,20261003):
        for kind in ('flat','spin'):
            reports=[ctl.read(next(REPORTS.glob(f'auto_0023_*_{kind}_{profile}_{seed}.json'))) for profile in ('nominal','white_v2')]
            assert all(v['checkpoint']==str(source) and ctl.gate(v,kind) for v in reports)
            assert all(all(v[k]==reports[0][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics')) for v in reports)
    locks=[]
    for p in (ROOT/'autonomy_controller.lock',CANONICAL.parent/'native_floor_supervisor.lock'):
        stream=p.open('a+');fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(stream)
    record={'stage':'verified_settled_entry','source':info,'rejected_newer_source_retained':ctl.S['chosen_checkpoint'],
        'old_rejections_retained':ctl.S['rate_rejected'],'reused_cap4_multiseed':paired,'reused_fullscale_report':str(report_path),
        'reused_fullscale_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'frozen_material_and_root_q_evidence':evidence,
        'begin_epoch':time.time(),'no_old_segment_settlement':True,'supervisor_identity':ctl.identity(os.getpid())}
    ctl.base.atomic_json(RECEIPT,record)
    owner=ctl.identity(os.getpid());old=ctl.read(ctl.RECEIPT)['old_parent']
    with (ROOT/'autonomy_guardian.log').open('a') as f:
        guardian=subprocess.Popen([ctl.base.PY,str(CODE/'supervise_autonomy.py'),'--guardian',str(os.getpid()),owner['start_ticks'],str(old['pid']),str(old['start_ticks'])],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    record['guardian_pid']=guardian.pid
    ctl.S['chosen_checkpoint']=str(source);ctl.S['consecutive']=0;ctl.S['failed_blocks']=0
    ctl.S['targeted_mature5']={'id':'TARGETED_MATURE5_ROLLBACK_20261003','phase':'preflight','source':info,'entry_receipt':str(RECEIPT)};ctl.persist()
    original=ctl.fullscale
    def reuse_fullscale(ck,label):
        assert str(ck)==str(source) and ctl.rate.current_limit()==5. and ctl.S['profile']=='white_v2'
        current=ctl.read(report_path);validate_evidence(evidence,current,ctl.base.checkpoint(ck))
        passed,acceptance=ctl.base.accept_physics_smoke(current);assert passed
        ctl.base.atomic_json(REPORTS/(label+'_20k_REUSED.json'),dict(current,reused_frozen_report=True,source_report=str(report_path),source_report_sha256=record['reused_fullscale_sha256']))
        ctl.base.atomic_json(REPORTS/(label+'_20k_acceptance_REUSED.json'),dict(acceptance,reused_frozen_report=True,source_report=str(report_path)))
        return current
    try:
        ctl.fullscale=reuse_fullscale
        ctl.rate_preflight(source,5.)
        ctl.fullscale=original
        if ctl.rate.current_limit()!=5.:
            ctl.S['targeted_mature5']['phase']='preflight_rejected';ctl.persist()
            ctl.targeted_hold(source,5.,'Explicit mature-source short/PPO preflight rejected; no blind repeat')
            record['stage']='preflight_rejected';ctl.base.atomic_json(RECEIPT,record);sys.exit(0)
        ctl.S['rollback']={'checkpoint':str(source),'profile':'white_v2','cap':4.}
        ctl.S['targeted_mature5']['phase']='trial45';ctl.persist()
        record.update(stage='formal45_starting',cap=5.,profile='white_v2',preflight_weights_discarded=True)
        ctl.base.atomic_json(RECEIPT,record)
        trial=ctl.training(source,'intermediate5_trial45',duration=2700)
        ctl.S['targeted_mature5']['phase']='saved_pending_assessment';ctl.persist()
        record.update(stage='formal45_saved_pending_assessment',trial=ctl.base.checkpoint(trial));ctl.base.atomic_json(RECEIPT,record)
        for stream in locks:stream.close()
        locks=[]
        ctl.controller()
    except BaseException:
        ctl.fullscale=original
        if not ctl.base.trainers() and not ctl.base.budget_state().get('active_segment'):
            ctl.rate.set_limit(4.,'Explicit entry exception; preserve source and reports')
            ctl.S['chosen_checkpoint']=str(source);ctl.S['targeted_mature5']['phase']='error_preserved';ctl.persist()
        record.update(stage='attention_required',error=traceback.format_exc());ctl.base.atomic_json(RECEIPT,record)
        ctl.base.status(stage='attention_required',supervisor_pid=os.getpid(),error=record['error'],instructions='Preserve full weights and budget. Inspect live children and explicit phase; do not repeat this one-shot or blindly resume.')
        raise
    finally:
        for stream in locks:stream.close()
