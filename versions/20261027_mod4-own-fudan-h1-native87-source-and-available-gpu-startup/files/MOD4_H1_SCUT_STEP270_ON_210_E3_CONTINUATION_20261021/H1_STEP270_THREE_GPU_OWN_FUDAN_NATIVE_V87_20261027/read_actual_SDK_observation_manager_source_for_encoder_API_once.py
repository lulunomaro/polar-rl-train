"""One actual installed SDK source read for the observed precontrol API failure."""
from pathlib import Path
import sys,json,time,hashlib,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def main():
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('native87R3_existing_memory_SDK_source_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
    try:
        c=d.connect72(secret)
        value=d.code(c,d.PY72,"""from pathlib import Path
import hashlib,json,importlib.util
sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
p=sdk/'managers/observation_manager.py';raw=p.read_bytes();assert len(raw)<150000
print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'),actual_installed_source=True,no_manager_instantiation_or_model_GPU_or_physics=True)))""",{},timeout=45)
        p=N/'saved_actual_SDK_source/observation_manager_6_1_14_actual.py.txt';p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('x',encoding='utf8',newline='') as f:f.write(value['text'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==value['SHA']
        value.pop('text');value.update(epoch=time.time(),local_actual_source=str(p),actual_finite_returned=True,new_purpose='Observed AttributeError in new encoder adapter; do not guess SDK API')
        with (R/'ACTUAL_SDK_OBSERVATION_MANAGER_SOURCE_FOR_ENCODER_API_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
        print(json.dumps(value))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('SDK_OBSERVATION_SOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
