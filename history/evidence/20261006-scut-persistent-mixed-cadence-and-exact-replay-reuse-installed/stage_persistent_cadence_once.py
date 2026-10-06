"""Preserve201 preparation; add explicit202 persistent authority, no GPU."""
import sys,shlex,json,shutil,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent;OLD=W/'MOD4_SCUT_CONTINUOUS_CADENCE_20261006'
(D/'reports').mkdir(exist_ok=True);assert not (D/'reports/SOURCE_FREEZE.json').exists()
freeze=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());assert len(freeze['sha256'])==201
for n,h in freeze['sha256'].items():
    p=OLD/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
    dst=D/n;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copy2(p,dst)
shutil.copy2(OLD/'reports/DISPLAY_SOURCE_REVIEW.json',D/'reports/DISPLAY_SOURCE_REVIEW.json')
name='supervise_scut_persistent_mix.py';new=dict(freeze['sha256']);new[name]=hashlib.sha256((D/name).read_bytes()).hexdigest()
(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=new,scope='201 exact previous files; add persistent cadence authority only'),indent=2)+'\n')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();remote='/home/egde/rl_candidates/'+D.name
try:
    with c.open_sftp() as s:
        try:s.stat(remote);raise AssertionError('Already staged; never restage')
        except FileNotFoundError:pass
        s.mkdir(remote);s.mkdir(remote+'/reports');s.put(str(D/name),remote+'/'+name)
    code='''import sys,shutil,json,hashlib,ast,subprocess,time
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_SCUT_PERSISTENT_MIX_20261006');OLD=Path('/home/egde/rl_candidates/MOD4_SCUT_CONTINUOUS_CADENCE_20261006')
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==201
for n,h in f['sha256'].items():
 p=OLD/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 dst=D/n;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copy2(p,dst)
shutil.copy2(OLD/'reports/DISPLAY_SOURCE_REVIEW.json',D/'reports/DISPLAY_SOURCE_REVIEW.json')
name='supervise_scut_persistent_mix.py';new=dict(f['sha256']);new[name]=hashlib.sha256((D/name).read_bytes()).hexdigest()
(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=new,scope='201 exact files; persistent cadence only'),indent=2)+'\\n')
sys.path.insert(0,str(D));import supervise_scut_persistent_mix as p;q=p.q;c=p.c;c.verify()
before=c.ctl.CANONICAL.read_bytes();r=subprocess.run([sys.executable,str(D/'test_cadence_contract.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
tree=ast.parse((D/name).read_text());ctrl=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='controller')
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('old_paired','preflight','kill') for n in ast.walk(ctrl))
loops=[n for n in ast.walk(ctrl) if isinstance(n,ast.While)];assert len(loops)==1
assert (D/'isaac/mod4/train_mod4_ppo.py').read_bytes()==(q.PREVIOUS/'isaac/mod4/train_mod4_ppo.py').read_bytes()
assert c.ctl.CANONICAL.read_bytes()==before and not c.ctl.S
old=json.loads((OLD/'reports/CADENCE_INSTALL_BOUNDARY.json').read_text());assert q.live(old['old_trainer'])
out=dict(old,epoch=time.time(),source_count=202,runtime_freeze_sha256=c.base.sha(c.w.F),
 persistent_controller_contract_pass=True,healthy_review_auto_continues=True,controller_not_executed=True,
 all201_previous_sources_exact=True,original198_runtime_exact=True,full_review_window_s=21600,
 guardian_max_block_s=7200,quick_checks_per_block=2,budget_operations=0,actual_tests_pass=True)
c.base.atomic_json(c.R/'CADENCE_CPU_SOURCE_CONTRACT.json',out);c.base.atomic_json(c.R/'CADENCE_INSTALL_BOUNDARY.json',out)
print(json.dumps(dict(pass_=True,source_count=202,old_trainer_unchanged=old['old_trainer']['pid'],budget_bytes_exact=True)))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
    result=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;print(result)
    with c.open_sftp() as s:
        for n in ('SOURCE_FREEZE.json','CADENCE_CPU_SOURCE_CONTRACT.json','CADENCE_INSTALL_BOUNDARY.json'):
            s.get(remote+'/reports/'+n,str(D/'reports'/n))
finally:c.close()
