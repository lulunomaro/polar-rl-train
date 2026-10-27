"""Read only remaining installed data API sources, no SDK scene or model."""
from pathlib import Path
import sys, json, time, traceback, hashlib, importlib.util
N = Path(__file__).resolve().parent
T = N.parent
W = T.parent
R = N / 'reports'

def main():
    sys.path.insert(0, str(W / 'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    sp = importlib.util.spec_from_file_location('native87R4_existing_memory_remaining_data_API', W / 'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    secret = m.recover()
    c = None
    try:
        c = d.connect72(secret)
        value = d.code(c, d.PY72, "from pathlib import Path\nimport json,hashlib,importlib.util\nsdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))\nsource_root=sdk.parent.parent\nbase=sdk/'assets/articulation/base_articulation_data.py'\nphysx_candidates=list(source_root.glob('**/isaaclab_physx/assets/articulation/articulation_data.py'))\nassert len(physx_candidates)==1,dict(source_root=str(source_root),candidates=[str(p) for p in physx_candidates])\npaths=dict(base=base,physx=physx_candidates[0]);result={}\nfor key,p in paths.items():\n p=p.resolve();assert p.is_relative_to(source_root.resolve());raw=p.read_bytes();assert len(raw)<1000000\n result[key]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'))\nprint(json.dumps(dict(actual_installed_source_only=True,no_class_instantiation_or_GPU_or_model=True,sources=result)))", {}, timeout=45)
        for key, source in value['sources'].items():
            p = N / 'saved_actual_SDK_source' / ('actual_' + key + '_articulation_data_for_R5_tensor_view.py.txt')
            with p.open('x', encoding='utf8', newline='') as f:
                f.write(source.pop('text'))
            assert hashlib.sha256(p.read_bytes()).hexdigest() == source['SHA']
            source['local_path'] = str(p)
        value.update(epoch=time.time(), actual_finite_returned=True, new_purpose='R4 actual applied_torque type failure; factory source already captured, only missing backend/base sources now')
        with (R / 'ACTUAL_PHYSX_BASE_DATA_API_SOURCES_FOR_R5_V2_RETURNED_ACTUAL.json').open('x', encoding='utf8') as f:
            json.dump(value, f, indent=2)
        print(json.dumps(value))
    finally:
        secret = None
        if c:
            c.close()
if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('R5_V2_DATA_API_SOURCE_READER_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc()), f, indent=2)
        raise
