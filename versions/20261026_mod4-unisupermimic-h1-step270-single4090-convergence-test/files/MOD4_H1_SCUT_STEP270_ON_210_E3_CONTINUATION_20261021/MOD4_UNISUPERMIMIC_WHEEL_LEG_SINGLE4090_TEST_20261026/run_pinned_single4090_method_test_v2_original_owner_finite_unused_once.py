"""One finite, serial transport: stage/admit/GO/test/normal original-writer closure."""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import json
import os
import secrets
import sys
import time
import traceback

J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports'
def put(name,value):
    with (R/('V2_'+name)).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

PREFLIGHT72=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2');s=v['spec'];old=Path(s['previous_runtime_root'])
assert str(B)==str(owned/'research/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026_V2/e2') and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['returncode']==0 and not r['original_error'] and r['final']['passed'] and r['final']['final']['SHA']==v['closed80_E2_SHA']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
failed=owned/'research/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/e2';fe=json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((failed/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['original_error'] and fr['returncode']==1 and not (failed/'job0/production_STARTED_ACTUAL.json').exists()
assert not any(p.pid!=os.getpid() and any(a.startswith(str(failed)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (Path(s['private_lock']),owned/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),root=str(B),selected_GPU_line=line,source80_E2_closed=True,actual_original_private_shared_fcntl_free=True,available_RAM=psutil.virtual_memory().available,disk_free=shutil.disk_usage(owned).free,no_unknown_peer_identity_query=True,no_GO=True)))
'''
PREFLIGHT210=r'''
from pathlib import Path
import fcntl,json,psutil,shutil,time
B=Path(v['root']);owned=Path('/mnt/mod4_linux_durable_20261013');assert str(B)==str(owned/'UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026_V2/owner') and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']>86412.86069250107
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),root=str(B),remaining_actual_snapshot=c['remaining_training_seconds'],canonicalNone=True,two_original_fcntl_free=True,no_canonical_write_or_new_budget=True)))
'''
READOWNER=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
B=Path(v['root']);until=time.monotonic()+600
def own():
 return [p.info for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or [])]
while not (B/'COHORT_FINAL.json').exists() or not (B/'OWNER_EXIT_ACTUAL.json').exists() or own():
 assert time.monotonic()<until,'Original method owner not actually closed';time.sleep(3)
co=json.loads((B/'COHORT_FINAL.json').read_bytes());exit=json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes());assert co['original_cost_settled'] and exit['original_cost_settled']
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
segments=[s for s in c['completed_segments'] if s.get('owner_parent_pid')==v['identity']['pid'] and s['started_epoch']>=v['identity']['creation']];assert len(segments)==1 and set(segments[0]['experts'])=={'e2'}
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
texts=[]
for p in B.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.txt','.log'):
  raw=p.read_bytes();texts.append(dict(path=str(p),relative='owner/'+p.relative_to(B).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),cohort=co,owner_exit=exit,segment=segments[0],original_remaining_closed_snapshot=c['remaining_training_seconds'],original_canonicalNone=True,original_two_fcntl_free=locks,texts=texts)))
'''
READTARGET=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
B=Path(v['root']);until=time.monotonic()+180
while not (B/'NODE_EXIT_ACTUAL.json').exists() or any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline'])):
 assert time.monotonic()<until;time.sleep(3)
e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited']
locks=[]
for p in (Path(v['spec']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
texts=[]
for p in B.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.txt','.log'):
  raw=p.read_bytes();texts.append(dict(path=str(p),relative='e2/'+p.relative_to(B).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),node_exit=e,terminal=r,original_private_shared_free=locks,texts=texts,no_GPU_or_model_reread=True)))
'''

def upload(c,local,remote):
    sf=c.open_sftp()
    try:
        made={remote}
        for p in sorted(local.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            rel=p.relative_to(local);target=PurePosixPath(remote).joinpath(*rel.parts)
            for parent in reversed(target.parents):
                path=str(parent)
                if path==remote or path.startswith(remote+'/'):
                    if path not in made:sf.mkdir(path);made.add(path)
            sf.put(str(p),str(target))
    finally:sf.close()

def capture(c,rows):
    sf=c.open_sftp();out=[]
    try:
        for row in rows:
            rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
            p=J/'actual_returned_text_v2'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p))
            assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];out.append(dict(row,local_path=str(p)))
    finally:sf.close()
    return out

def main():
    assert json.loads((R/'EXACT_NEW_METHOD_READY_NEGATIVES_AND_ORIGINAL_ACCOUNTING_CPU_ACTUAL.json').read_bytes())['passed']
    q=json.loads((R/'REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_V2_ACTUAL.json').read_bytes());spec=q['spec']
    proof=json.loads((T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026/reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed']
    put('ONE_CARD_METHOD_TEST_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,root=q['root'],owner_root=q['owner_root'],GPU_UUID=spec['GPU_UUID'],original_accounting_required=True))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    sp=importlib.util.spec_from_file_location('own_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
    secret=memory.recover();c=None;cfg=None;child=None;password=None
    try:
        c=d.connect72(secret)
        pre=d.code(c,d.PY72,PREFLIGHT72,dict(root=q['root'],spec=spec,closed80_E2_SHA=proof['models']['e2']['final']['SHA']),timeout=90);put('ONE_CARD_TARGET72_FRESH_OWN_RESOURCE_PREFLIGHT_ACTUAL.json',pre)
        upload(c,J/'payload_v2',q['root'])
        after=d.code(c,d.PY72,"from pathlib import Path;import json,shutil;B=Path(v['root']);assert shutil.disk_usage(B).free>25*1024**3;print(json.dumps(dict(actual_payload_after_copy_free=shutil.disk_usage(B).free,passed25GiB=True)))",dict(root=q['root']),timeout=30);put('ONE_CARD_ACTUAL_PAYLOAD_AFTER_COPY_DISK25_ACTUAL.json',after)
        c.close();c=None;c=route.connect()
        pre=d.code(c,route.PY,PREFLIGHT210,dict(root=q['owner_root']),timeout=90);put('ONE_CARD_ORIGINAL_OWNER_FRESH_CANONICAL_AND_LOCKS_ACTUAL.json',pre)
        upload(c,J/'owner_source',q['owner_root'])
        cfg=dict(role='owner',experts=dict(e2=spec),scheduling_authority='human_one_dual4090_wheelleg_method_test',deferred_experts=[],run_id='UNISUPERMIMIC_MOD4_METHOD_TEST_'+str(time.time_ns()),token=secrets.token_hex(32))
        owner=d.launch(c,route.PY,q['owner_root'],'three_slot_finite_owner_v1.py',cfg)
        ready=d.code(c,route.PY,"from pathlib import Path;import json,psutil,socket,time;B=Path(v['root']);until=time.monotonic()+25\nwhile not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)\np=psutil.Process(v['pid']);assert str(B/'three_slot_finite_owner_v1.py') in p.cmdline()\nwhile True:\n try:\n  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass\n  break\n except ConnectionRefusedError:\n  assert time.monotonic()<until;time.sleep(.1)\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))",dict(root=q['owner_root'],pid=owner['detached_pid']),timeout=35)
        c.close();c=None;c=d.connect72(secret);secret=None
        sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover;password,_=recover('RM_SSH_PASSWORD');assert password
        child=dict(spec,role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=password)
        node=d.launch(c,d.PY72,q['root'],'three_slot_finite_node_v1.py',child);child.clear();password=None
        put('ONE_CARD_METHOD_TEST_ORIGINAL_OWNER_AND_NODE_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,owner_identity=ready['owner'],node=node,run_id=cfg['run_id'],root=q['root'],owner_root=q['owner_root'],spec=spec,not_a_GPU_success_until_actual_result=True))
        cfg.clear();c.close();c=None;c=route.connect()
        a=d.code(c,route.PY,READOWNER,dict(root=q['owner_root'],identity=ready['owner']),timeout=650);put('ONE_CARD_ORIGINAL_OWNER_CLOSED_COST_ACTUAL.json',a);texts=capture(c,a['texts'])
        c.close();c=None;c=d.connect72(memory.recover())
        b=d.code(c,d.PY72,READTARGET,dict(root=q['root'],spec=spec),timeout=210);put('ONE_CARD_TARGET72_NODE_CHILDREN_OUT_ACTUAL.json',b);texts+=capture(c,b['texts'])
        terminal=b['terminal'];cost=a['segment']['experts']['e2'];result=terminal.get('final') or {}
        put('ONE_CARD_METHOD_TEST_FULL_TEXT_ORIGINAL_COST_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,source210=a,target72=b,texts=texts,original_fee=cost,original_closed_remaining_snapshot=a['original_remaining_closed_snapshot'],original_canonicalNone=True,not_a_production_expert_source=True))
        print(json.dumps(dict(actual_finite_returned=True,method_result_passed=result.get('passed'),original_worker_error=terminal.get('original_error'),original_fee=cost,closed_remaining=a['original_remaining_closed_snapshot'])))
    finally:
        secret=None;password=None
        if cfg:cfg.clear()
        if child:child.clear()
        if c:c.close()

if __name__=='__main__':
    try:main()
    except BaseException:
        put('ONE_CARD_METHOD_TEST_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_root_retry_or_second_writer_or_refund=True));raise
