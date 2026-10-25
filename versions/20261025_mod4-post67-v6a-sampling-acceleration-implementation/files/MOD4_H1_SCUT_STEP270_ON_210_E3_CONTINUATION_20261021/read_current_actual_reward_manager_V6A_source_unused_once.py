from pathlib import Path
import hashlib,json,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'H1_STEP270_POST67_TIMING_REPAIR_PREPARATION_20261025/reports';R.mkdir(parents=True,exist_ok=True)
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    code="from pathlib import Path;import importlib.util,hashlib,json;root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));p=root/'managers/reward_manager.py';raw=p.read_bytes();print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),source=raw.decode('utf8'),actual_installed_source_only_no_GPU=True)))"
    c=d.t.connect()
    try:v=d.code(c,d.t.PY,code,{},timeout=45)
    finally:c.close()
    raw=v.pop('source').encode();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['SHA']
    p=R/'ACTUAL_CURRENT_INSTALLED_REWARD_MANAGER_SOURCE.py'
    with p.open('xb') as f:f.write(raw)
    put('ACTUAL_CURRENT_INSTALLED_REWARD_MANAGER_METADATA_V6A_REVIEW_ACTUAL.json',dict(epoch=time.time(),**v,local_path=str(p),no_old_SDK_relabel=True));print(json.dumps(v))
except BaseException:
    put('ACTUAL_V6A_SDK_SOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_new_reward_or_GO=True));raise
