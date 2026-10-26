"""Missing-only inactive method text and its original terminal fee; no model/raw reads."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback

H=Path(__file__).resolve().parent;T=H.parent;W=T.parent;R=H/'reports'
F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
TARGET=r'''
from pathlib import Path
import hashlib,json,os,psutil,time
B=Path(v['root']);e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());terminal=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and terminal['original_error'] and terminal['terminal_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
names=['NODE_IDENTITY.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','job0/GO_PRODUCTION.json','job0/production_STARTED_ACTUAL.json','job0/production_WAITED_EXIT_ACTUAL.json','job0/production_WORKER.log','job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/production/NATIVE_SUPERMIMIC_LEARN_ORIGINAL_ERROR.json','job0/production/FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json','job0/production/ACTUAL_H1_NEW_METHOD_STARTUP_CONTRACT.json','job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl','job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json','job0/production/native_supermimic/args.json','job0/production/native_supermimic/train_log.csv','job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json','job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json']
files=[];absent=[]
for rel in names:
 p=B/rel
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 else:absent.append(rel)
models=[]
for p in (B/'job0/production').glob('*.pt*'):
 if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,SHA=None,no_content_read=True,partial_original_retained=True))
print(json.dumps(dict(epoch=time.time(),node_exit=e,terminal=terminal,files=files,absent=absent,own_partial_model_stat_only=models,no_original_model_raw_GPU_policy_physics_or_account_action=True)))
'''
SOURCE=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['owner']['root']);p=psutil.Process(v['owner']['pid']);assert p.create_time()==v['owner']['creation'] and p.cmdline()==v['owner']['argv']
current=json.loads((B/'OWNER_CURRENT.json').read_bytes());C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==p.pid and set(a['experts'])=={'h1','e2','recovery'};row=current['rows']['e2'];assert row['original_error'] and row['terminal_all_own_children_waited'] and row['returncode']==0
cost=a['experts']['e2'];assert cost.get('ended_epoch') and cost['charged_seconds']>0
print(json.dumps(dict(epoch=time.time(),original_owner_identity=v['owner'],method_original_GO=current['go']['e2'],method_terminal_row=row,method_original_terminal_cost=cost,other_slots_still_owned_by_original_controller=True,original_active_not_cleared=True,whole_cohort_cost_pending=True,no_budget_or_controller_write=True)))
'''
try:
    q=json.loads((F/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    put('ACTUAL81O_METHOD_FAILURE_MISSING_ONLY_TEXT_READER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('own_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
    c=d.connect72(memory.recover())
    try:
        target=d.code(c,d.PY72,TARGET,dict(root=q['roots']['e2']),timeout=90);sf=c.open_sftp();files=[]
        try:
            for row in target['files']:
                p=H/'actual81O_failed_method_text'/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];files.append(dict(row,local_path=str(p)))
        finally:sf.close()
    finally:c.close()
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    c=route.connect()
    try:source=d.code(c,route.PY,SOURCE,dict(owner=q['owner_identity']),timeout=45)
    finally:c.close()
    put('ACTUAL81O_METHOD_FAILED_FULL_ERROR_TEXT_AND_ORIGINAL_TERMINAL_COST_RETURNED.json',dict(epoch=time.time(),actual_finite_returned=True,target=target,source_original_owner=source,files=files,original_error_not_rc0_success=True,no_same_root_retry_hotpatch_refund_or_second_writer=True))
    print(json.dumps(dict(returned_error_texts=len(files),method_original_fee=source['method_original_terminal_cost'],whole_cohort_pending=True)))
except BaseException:
    put('ACTUAL81O_MISSING_ERROR_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay=True));raise
