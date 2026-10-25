"""Unused until complete74b wholeCPU/exit/cost. New74b last-two saved-prefix CPU read, no policy or physics."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,re,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';R.mkdir(exist_ok=True)
N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    proof=json.loads((N/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    indexpath=N/'current_three_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json';index=json.loads(indexpath.read_bytes())
    rows=[]
    for row in index['index']:
        name=Path(row['path']).name;match=re.fullmatch(r'control_prefix_(\d+)\.npz',name)
        if match:rows.append((int(match[1]),row))
    rows.sort(key=lambda x:x[0]);assert len(rows)>=3
    selected=rows[-2:];assert selected[1][0]==selected[0][0]+1
    files=[dict(row,target_path=row['path']) for _,row in selected]
    assert all(row['target_path'].startswith('/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2610v74b/h1/job0/production/control_prefix_raw/') for row in files)
    old=T/'H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025/extract_latest67_retained_motion_CPU_unused_once.py'
    tree=ast.parse(old.read_text('utf8'));code=next(x.value.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='CODE' for k in x.targets))
    previous='Latest closed67 stochastic PPO saved pre-selected-reset control records, adjacent prefixes116/117 only.48 frames/0.48s across20k. Selected motion includes explicit reset masks. Not frozen FINAL policy evaluation, full-window totals, or callback dynamic replay.'
    assert code.count(previous)==1
    scope='Closed74b actual saved pre-selected-reset records, last two adjacent retained prefixes '+str([i for i,_ in selected])+'.48controls/.48s across20k. Explicit reset masks. Not frozen FINAL evaluation, whole-window events, callback replay, or matched-cohort learning-gain comparison.'
    code=code.replace(previous,scope,1)
    put('CLOSED74B_LAST_TWO_SAVED_PREFIX_EXTRACTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,files=files,prefix_ids=[i for i,_ in selected],source_FINAL=proof['models']['h1']['final'],source_old_helper_AST_only_not_reexecuted=str(old)))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    c=route.connect()
    try:
        result=d.code(c,route.PY,code,dict(files=files,reward_terms=index['reward_terms'],control_first=selected[0][0]*24+1,out='/mnt/mod4_linux_durable_20261013/replay_diagnostics/H1_STEP270_CLOSED74B_SAVED_ONLY_20261026'),timeout=240)
        put('CLOSED74B_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json',result)
        p=S/'SELECTED_RECORDED_MOTION.npz';assert not p.exists();sf=c.open_sftp()
        try:sf.get(result['selected_artifact']['path'],str(p))
        finally:sf.close()
        assert p.stat().st_size==result['selected_artifact']['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==result['selected_artifact']['SHA']
        put('CLOSED74B_SELECTED_MOTION_TWOHOST_SHA_ACTUAL.json',dict(epoch=time.time(),path=str(p),bytes=p.stat().st_size,SHA=result['selected_artifact']['SHA'],twohost_complete_SHA=True,no_original_raw_download=True))
    finally:c.close()
    print(json.dumps({k:result[k] for k in ('frames','selected_count','recorded_event_counter_positive_increments','recorded_both_wheels_crossed_envframes','recorded_success_envframes','selected_artifact')}))
except BaseException:
    put('CLOSED74B_SAVED_PREFIX_EXTRACTION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_rerun=True));raise
