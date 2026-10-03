"""One authorized extension, complete-save boundary and budget-only controller migration."""
import argparse, ast, copy, fcntl, hashlib, json, os, shutil, signal, subprocess, sys, time, traceback
from pathlib import Path

ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE=ROOT/'isaac/mod4'
STAGING=Path('/home/egde/rl_candidates/MOD4_BUDGET_ADD20H_20261003')
CANONICAL=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
REPORTS=ROOT/'reports'
ID='USER_ADD20H_20261003_3RD'
OLD=180000;NEW=252000;ADD=72000
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
APPLIED=REPORTS/(ID+'_APPLIED.json')
PROGRESS=STAGING/'PROGRESS.json'
sys.path.insert(0,str(CODE))
from budget_authority import validate_budget

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
    q=p.with_name(p.name+'.'+ID+'.partial')
    q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(q,p)
def progress(stage,**kw):
    data={'stage':stage,'epoch':time.time(),**kw};atomic(PROGRESS,data)
    print(json.dumps(data,ensure_ascii=False),flush=True)
def identity(pid):
    if not pid:return None
    p=Path('/proc')/str(pid)
    try:
        st=(p/'stat').read_text().rsplit(')',1)[1].split()
        try:cwd=os.readlink(p/'cwd')
        except OSError:cwd=None
        return {'pid':pid,'state':st[0],'start_ticks':int(st[19]),'ppid':int(st[1]),'session':int(st[3]),
            'cwd':cwd,'argv':(p/'cmdline').read_bytes().decode().split('\0')[:-1],
            'exit_code_encoded':int(st[49]) if len(st)>49 else None}
    except (OSError,ValueError):return None
def same(p):
    now=identity(p['pid']);return now and now['start_ticks']==p['start_ticks']
def live(p):
    now=identity(p['pid']);return now and now['start_ticks']==p['start_ticks'] and now['state']!='Z'
def processes():
    result=[]
    for d in Path('/proc').glob('[0-9]*'):
        p=identity(int(d.name))
        if p and p['state']!='Z' and '-c' not in p['argv'] and p['cwd']==str(ROOT):result.append(p)
    return result
def checkpoint(path):
    import torch
    torch.set_num_threads(1)
    d=torch.load(path,map_location='cpu',weights_only=True)
    def floats(x):
        if torch.is_tensor(x) and x.is_floating_point():yield x
        elif isinstance(x,dict):
            for v in x.values():yield from floats(v)
        elif isinstance(x,(list,tuple)):
            for v in x:yield from floats(v)
    fs=list(floats(d))
    assert len(fs)==68 and all(bool(torch.isfinite(t).all()) for t in fs)
    assert all(k in d for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict','iter'))
    assert any('std' in k.lower() for k in d['actor_state_dict'])
    return {'path':str(path),'iteration_stored':d['iter'],'sha256':sha(path),'finite_tensors':len(fs),
            'actor_critic_optimizer_std_iter_preserved':True}
def complete_run(pid):
    matches=[p.parent for p in (ROOT/'logs').glob('*/latest_complete.json') if int(read(p)['pid'])==pid]
    assert len(matches)==1,'No unique complete receipt bound to this actual trainer'
    return matches[0]
def check_source():
    prepared=read(STAGING/'PREPARED.json')
    assert sha(CODE/'supervise_autonomy.py')==prepared['original_controller_sha256']
    assert sha(STAGING/'supervise_autonomy.py')==prepared['new_controller_sha256']
    old=ast.parse((CODE/'supervise_autonomy.py').read_text());new=ast.parse((STAGING/'supervise_autonomy.py').read_text())
    assert len(old.body)==len(new.body)
    changed=[]
    for x,y in zip(old.body,new.body):
        if ast.dump(x,include_attributes=False)!=ast.dump(y,include_attributes=False):
            assert isinstance(x,ast.FunctionDef) and x.name in ('status','verify','training');changed.append(x.name)
    assert changed==['status','verify','training']
    compile((STAGING/'supervise_autonomy.py').read_text(),'prepared_controller','exec')
    frozen=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
    for name,digest in frozen['sha256'].items():
        p=Path(name);p=p if p.is_absolute() else ROOT/p
        assert sha(p)==digest,'Source drift: '+name
    return prepared,frozen
def inspected_state():
    b=read(CANONICAL);assert validate_budget(b)==OLD
    assert b['owner_root']==str(ROOT) and not any(e['extension_id']==ID for e in b.get('budget_extensions',[]))
    s=read(ROOT/'status.json');a=read(REPORTS/'AUTONOMY_STATE.json')
    parent=identity(s['supervisor_pid']);trainer=identity(s['training_pid'])
    assert parent and trainer and parent['cwd']==trainer['cwd']==str(ROOT)
    assert parent['state'] not in ('T','t','Z') and trainer['state']!='Z'
    assert any(x.endswith('/supervise_autonomy.py') for x in parent['argv']) and '--resume' in parent['argv']
    assert any(x.endswith('/train_mod4_ppo.py') for x in trainer['argv'])
    assert trainer['ppid']==parent['pid']
    assert s['stage']=='training' and s['profile']=='white_v2' and float(s['yaw_limit_rad_s'])==4
    assert s['canonical_budget']==str(CANONICAL)
    assert b['active_segment']['pid']==trainer['pid'] and a['active_training']['pid']==trainer['pid']
    ps=processes()
    assert [p['pid'] for p in ps if any(x.endswith('/train_mod4_ppo.py') for x in p['argv'])]==[trainer['pid']]
    assert not any(any(x.endswith(('/validate_speed.py','/spin_rate_probe.py','/spin_rate_fullscale_probe.py','/autonomy_turn_probe.py')) for x in p['argv']) for p in ps)
    guardians=[p for p in ps if '--guardian' in p['argv'] and str(parent['pid']) in p['argv']]
    assert len(guardians)==1
    run=complete_run(trainer['pid'])
    return b,s,a,parent,trainer,guardians[0],run
def syscall(pid,secret):
    p=Path('/proc')/str(pid)/'syscall'
    try:return p.read_text().strip()
    except PermissionError:
        assert secret,'Read-only process inspection credential unavailable'
        r=subprocess.run(['sudo','-S','-p','','cat',str(p)],input=secret+'\n',text=True,capture_output=True,timeout=5)
        assert r.returncode==0,'Verified process syscall inspection failed'
        return r.stdout.strip()
def pause_sleep(parent,secret):
    for _ in range(150):
        assert same(parent) and live(parent)
        before=syscall(parent['pid'],secret)
        if not before or before.split()[0]!='230':time.sleep(.05);continue
        os.kill(parent['pid'],signal.SIGSTOP)
        stopped=identity(parent['pid'])
        for _ in range(80):
            if stopped and stopped['state'] in ('T','t'):break
            time.sleep(.005);stopped=identity(parent['pid'])
        after=syscall(parent['pid'],secret)
        if stopped and stopped['state'] in ('T','t') and after and after.split()[0]=='230':
            return {'before':before,'stopped':after,'state':stopped['state'],'outside_ledger_write':True}
        if same(parent):os.kill(parent['pid'],signal.SIGCONT)
    raise AssertionError('No safe supervisor accounting pause; do not modify budget')

def main(check_only=False):
    lock=(STAGING/'extension_transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    b=read(CANONICAL);validate_budget(b)
    matches=[e for e in b.get('budget_extensions',[]) if e['extension_id']==ID]
    if matches:
        assert len(matches)==1 and matches[0]['additional_training_seconds']==ADD and b['authorized_training_seconds']==NEW
        progress('already_applied_do_not_repeat',receipt=str(APPLIED),receipt_exists=APPLIED.exists());return
    assert not APPLIED.exists(),'Receipt and ledger disagree; manual reconciliation required'
    prepared,frozen=check_source();b,s,a,parent,trainer,guardian,run=inspected_state()
    info=checkpoint(Path(read(run/'latest_complete.json')['checkpoint']))
    if check_only:
        test=copy.deepcopy(b);test['budget_extensions'].append({'extension_id':ID,'additional_training_seconds':ADD,'state':'applied','authorization_basis':'explicit_user_request'})
        test['authorized_training_seconds']=NEW;assert validate_budget(test)==NEW
        progress('prepared_verified_no_budget_applied',parent=parent,trainer=trainer,guardian=guardian,
                 bound_checkpoint=info,original_budget=OLD,new_budget=NEW,source=prepared);return
    secret=sys.stdin.readline().rstrip('\n')
    request={'extension_id':ID,'additional_training_seconds':ADD,'authorization_basis':'explicit_user_request',
        'authorization':'User explicitly requested in this chat: 预算再加20小时',
        'requested_epoch':time.time(),'authorized_seconds_before':OLD,'authorized_seconds_after':NEW}
    assert not (REPORTS/(ID+'_REQUEST.json')).exists(),'Request already registered; inspect worker before retry'
    atomic(REPORTS/(ID+'_REQUEST.json'),request)
    backup=STAGING/'before';backup.mkdir(exist_ok=False)
    for path,name in [(CANONICAL,'canonical.json'),(ROOT/'status.json','status.json'),(REPORTS/'AUTONOMY_STATE.json','autonomy_state.json'),(REPORTS/'SPIN_SOURCE_FREEZE.json','source_freeze.json'),(CODE/'supervise_autonomy.py','supervise_autonomy.py')]:
        shutil.copy2(path,backup/name)
    paused=False;retired=False;stop=run/'STOP_AFTER_SAVE'
    try:
        sleep=pause_sleep(parent,secret);secret=None;paused=True
        assert same(trainer) and live(trainer) and not stop.exists()
        b=read(CANONICAL);assert validate_budget(b)==OLD and b['active_segment']['pid']==trainer['pid']
        stop.write_text('Explicit additional 20h: full actor/critic/optimizer/std save, budget-only supervisor compatibility migration.\n')
        began=time.time();progress('waiting_complete_save',parent=parent,trainer=trainer,run=str(run),safe_pause=sleep)
        while live(trainer):
            assert same(parent) and identity(parent['pid'])['state'] in ('T','t')
            assert time.time()-began<1200,'Complete-save timeout: preserve original budget and controller'
            time.sleep(.25)
        ended=time.time();exited=identity(trainer['pid'])
        if exited:
            assert exited['start_ticks']==trainer['start_ticks'] and exited['state']=='Z' and exited['exit_code_encoded']==0
        saved=read(run/'latest_complete.json');assert int(saved['pid'])==trainer['pid'] and saved['saved_at']>=began-.5
        path=Path(saved['checkpoint']);assert path.parent==run
        text=Path(s['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in text and 'Traceback (most recent call last)' not in text
        info=checkpoint(path);manifest=read(run/'run_manifest.json')
        assert manifest['env']['RM_KEEP_STD']=='1' and manifest['env']['RM_MILD_DR_PROFILE']=='white_v2' and float(manifest['env']['RM_SPIN_MAX_RAD_S'])==4
        assert same(parent) and same(guardian)
        # Only this controller and its verified guardian retire; other AI tasks are untouched.
        os.kill(guardian['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGKILL);retired=True;paused=False
        for _ in range(100):
            if not live(parent) and not live(guardian):break
            time.sleep(.05)
        assert not live(parent) and not live(guardian) and not live(trainer)
        b=read(CANONICAL);assert validate_budget(b)==OLD
        segment=b['active_segment'];assert segment['pid']==trainer['pid']
        charged_before=float(b['charged_training_seconds']);tail=max(0.,ended-segment['accounted_through_epoch'])
        b['charged_training_seconds']=charged_before+tail
        segment.update(accounted_through_epoch=ended,ended_epoch=ended,end_reason='normal full save for explicit20h budget runtime migration',
            observation_uncertainty_upper_s=.25,end_evidence={'receipt':saved,'zombie_exit_code_encoded':exited.get('exit_code_encoded') if exited else None})
        b.setdefault('completed_segments',[]).append(segment);b['active_segment']=None
        extension={'extension_id':ID,'additional_training_seconds':ADD,'authorization_basis':'explicit_user_request',
            'authorization':request['authorization'],'requested_epoch':request['requested_epoch'],'applied_epoch':time.time(),'state':'applied'}
        b['budget_extensions'].append(extension);b['authorized_training_seconds']=NEW
        b['remaining_training_seconds']=max(0.,NEW-b['charged_training_seconds'])
        b['deadline_epoch']=time.time()+b['remaining_training_seconds']
        b['latest_explicit_extension_receipt']=str(APPLIED)
        b['budget_scope']='Original10h plus three explicitly authorized20h additions, effective PPO process time; no automatic extension'
        assert validate_budget(b)==NEW and len([e for e in b['budget_extensions'] if e['extension_id']==ID])==1
        atomic(CANONICAL,b)
        result={'extension_id':ID,'added_seconds':ADD,'authorized_training_seconds':NEW,'charged_before_tail':charged_before,
            'tail_charged_s':tail,'charged_training_seconds':b['charged_training_seconds'],'remaining_training_seconds':b['remaining_training_seconds'],
            'canonical_budget':str(CANONICAL),'checkpoint':info,'old_parent':parent,'old_guardian':guardian,'old_trainer':trainer,
            'bound_complete_receipt':saved,'exit_evidence':exited,'save_exit_detection_uncertainty_upper_s':.25,
            'safe_pause':sleep,'new_controller_sha256':prepared['new_controller_sha256'],
            'physics_reward_ppo_dr_policy_unchanged':True,'weights_optimizer_std_iteration_not_reset':True,'applied_epoch':time.time()}
        atomic(APPLIED,result);progress('budget_applied_once',receipt=str(APPLIED),total=NEW,remaining=b['remaining_training_seconds'],checkpoint=info)
        a=read(REPORTS/'AUTONOMY_STATE.json');assert a['active_training']['pid']==trainer['pid']
        a['chosen_checkpoint']=str(path);a['active_training']=None
        a['latest_budget_runtime_handover']={'extension_id':ID,'source':info,'receipt':str(APPLIED)}
        atomic(REPORTS/'AUTONOMY_STATE.json',a)
        # Prepared patch changes only status, budget verification and budget labels; all policy gates remain byte-equivalent AST.
        check_source();os.replace(STAGING/'supervise_autonomy.py',CODE/'supervise_autonomy.py')
        frozen['sha256']['isaac/mod4/supervise_autonomy.py']=sha(CODE/'supervise_autonomy.py')
        atomic(REPORTS/'SPIN_SOURCE_FREEZE.json',frozen)
        for name,digest in frozen['sha256'].items():
            p=Path(name);p=p if p.is_absolute() else ROOT/p;assert sha(p)==digest
        s=read(ROOT/'status.json');s.update(stage='budget_extended_resuming',training_pid=None,evaluation_pid=None,validation_pid=None,
            supervisor_pid=None,budget_seconds=NEW,authorized_training_seconds=NEW,
            charged_training_seconds=b['charged_training_seconds'],remaining_training_seconds=b['remaining_training_seconds'],
            deadline_epoch=b['deadline_epoch'],latest_checkpoint=str(path),iteration=info['iteration_stored'],
            budget_extension_receipt=str(APPLIED),autonomy_version='sleep_v3_budget_dynamic',updated_at=time.time())
        atomic(ROOT/'status.json',s)
        log=ROOT/'supervisor_autonomy_budget70h_20261003.log';assert not log.exists()
        with log.open('x') as out:
            proc=subprocess.Popen([PY,'-u',str(CODE/'supervise_autonomy.py'),'--resume'],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        result.update(new_supervisor_pid=proc.pid,new_supervisor_log=str(log),runtime_installed=True)
        atomic(APPLIED,result);progress('new_controller_launched',supervisor_pid=proc.pid,log=str(log),receipt=str(APPLIED))
    finally:
        if paused and not retired and same(parent):
            # Before mutation, restore the original controller. Remove only our request if its trainer remains live.
            if live(trainer) and stop.exists():stop.unlink()
            os.kill(parent['pid'],signal.SIGCONT)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-check',action='store_true');args=parser.parse_args()
    try:main(args.prepare_check)
    except BaseException:
        progress('attention_required',error=traceback.format_exc(),receipt_exists=APPLIED.exists(),
            instruction='Inspect actual children, receipt and canonical ledger; do not repeat an applied extension, clear charged or start a second trainer.')
        raise
