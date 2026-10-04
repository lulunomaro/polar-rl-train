"""Run actual CPU contracts, then launch exactly one guarded migration."""
import ast,hashlib,json,os,shlex,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
OLD=D.parent/'MOD4_SCUT_STYLE_RATE_CONTINUE_20261004'
STAGE='/home/egde/rl_candidates/MOD4_SCUT_STYLE_FLAT_GATE_FIX_20261004'
C='/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004'
P='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
assert not (D/'LAUNCHED.json').exists(),'Already launched; read journal, never rerun'
for file in D.glob('*.py'):ast.parse(file.read_text())
test=subprocess.run([sys.executable,'-X','utf8',str(D/'test_flat_gate_v2.py'),'--reports',str(OLD/'existing_assessments_0066_0069')],check=True,capture_output=True,text=True)
local=json.loads(test.stdout);assert local['pass_'];(D/'CPU_LOCAL.json').write_text(json.dumps(local,indent=2),encoding='utf8')
h=json.loads((OLD/'HEALTH_USER_FLAT_GATE_CORRECTION_20261004.json').read_text())
assert h['all_frozen_hashes_match'] and h['own_checkpoint']['finite_tensors']==68
expected=dict(parent=h['parent'],guardian=h['guardian'],trainer=h['processes']['training'])
assert all(expected.values())
files={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in
       ('scut_style_gate_v2.py','supervise_scut_style_continue_v2.py','migrate_flat_gate_v2.py','test_flat_gate_v2.py')}
prep=dict(acceptance_version=local['acceptance_version'],files=files,CPU_contracts=local,
          expected_processes=expected,last_paired_mature=h['SCUT_STYLE_STATE']['last_paired_mature'],
          existing_policy_review=dict(pass_=True,different_formal_policies=['19575','19732'],
              real19575_paired_reclassification=local['real19575_paired_reclassification'],
              reclassification_not_new_replays=True,old_reports_unchanged=True),
          complete_frozen_source_sha=h['rolling_source_freeze']['sha256'],budget_authorized=h['budget']['authorized_training_seconds'],
          scope='New evaluator/controller files only. Remove finite slip numeric veto from flat as well as spin; all old verdicts retained. No task/reward/physics/hardware/DR/PPO change.')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    with c.open_sftp() as s:
        try:s.stat(STAGE)
        except FileNotFoundError:s.mkdir(STAGE)
        else:raise AssertionError('Stage already exists; inspect before resuming')
        for name in (*files,'PLAN_AND_HANDOFF.md'):s.put(str(D/name),STAGE+'/'+name)
    command='PYTHONPATH='+shlex.quote(C+'/isaac/mod4')+' '+shlex.quote(PY)+' '+shlex.quote(STAGE+'/test_flat_gate_v2.py')+' --reports '+shlex.quote(P+'/reports')
    _,o,e=c.exec_command(command,timeout=45);raw=o.read().decode();err=e.read().decode()
    assert o.channel.recv_exit_status()==0,err+raw
    target=json.loads(raw);assert target==local,'Actual target CPU contracts differ'
    (D/'CPU_TARGET.json').write_text(json.dumps(target,indent=2),encoding='utf8')
    prep['target_CPU_verified']=True
    (D/'PREPARED.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
    with c.open_sftp() as s:s.put(str(D/'PREPARED.json'),STAGE+'/PREPARED.json')
    code=r'''import json,sys,subprocess
from pathlib import Path
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');D=Path('/home/egde/rl_candidates/MOD4_SCUT_STYLE_FLAT_GATE_FIX_20261004')
sys.path.insert(0,str(C));import supervise_scut_style_continue as old
old.repair.verify();prep=old.read(D/'PREPARED.json')
for identity in prep['expected_processes'].values():
    now=old.helpers.identity(identity['pid']);assert now and all(now[k]==identity[k] for k in ('pid','start_ticks','cwd','argv'))
assert not (C/'reports/SCUT_STYLE_V2_MIGRATION.json').exists()
for name,digest in prep['complete_frozen_source_sha'].items():assert old.base.sha(C/name)==digest
with (D/'migration.log').open('x') as log:
    p=subprocess.Popen([old.base.PY,str(D/'migrate_flat_gate_v2.py')],cwd=C,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
receipt=old.helpers.identity(p.pid);assert receipt
receipt.update(entry=str(D/'migrate_flat_gate_v2.py'),acceptance_version=prep['acceptance_version'])
old.base.atomic_json(D/'LAUNCHED.json',receipt);print(json.dumps(receipt))'''
    _,o,e=c.exec_command(PY+' -c '+shlex.quote(code),timeout=30)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
    launched=json.loads(raw);(D/'LAUNCHED.json').write_text(json.dumps(launched,indent=2),encoding='utf8')
    print(json.dumps(dict(contracts=target['contract_count'],target_pass=True,migration=launched)))
finally:c.close()
