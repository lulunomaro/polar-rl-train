"""Import prepared local tools without invoking their execution entry points."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent
R=D/'reports'
sys.path.insert(0,str(D))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (R/'NOMINAL_ABC_FIXED30_ROOT_DISPATCH_INTENT.json').exists()
    rng=torch.get_rng_state().clone();rows=[]
    for name in ('dispatch_nominal_ABC_new_case_actual','collect_nominal_ABC_actual_boundary',
                 'review_nominal_original_physical_and_metrics_CPU','review_nominal_single_source_history_CPU',
                 'review_nominal_pair_routing_CPU','run_nominal_ABC_fixed30_case_batch_once','launch_nominal_ABC_fixed30_hidden_once'):
        p=D/(name+'.py');s=importlib.util.spec_from_file_location(name,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
        if hasattr(v,'t'):assert v.t.ROOT=='D:/MOD4_async_eval/'+D.name
        rows.append(dict(name=name,source_SHA=H(p),imported_without_main=True))
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    value=dict(epoch=time.time(),passed=True,imports=rows,
        static_prelaunch_transport_name_mismatch_preserved='Generated tools import transport_nominal_ABC_actual; uploader uses transport_nominal_isolated_ABC_actual. An explicit local re-export maps both to the same sole owner and identical ROOT. Found before any coordinator/native/Task launch.',
        explicit_alias_SHA=H(D/'transport_nominal_ABC_actual.py'),
        read_only_lookup_misses_preserved=['Optional target_CPU_sdk_scope_check_v1.py lookup returned no file; actual uploader contains the target CPU check.',
            'An exact guessed historical TLS-report basename was absent; wildcard actual error reports retained. Both were read-only, no GPU/runtime mutation.'],
        no_PPO_no_GPU_no_network_and_no_global_CPU_RNG_advance=True,
        target_CPU_upload_has_passed_but_native_physical_admission_still_pending=True)
    with (R/'NOMINAL_FIXED30_TOOL_IMPORTS_LOCAL_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(passed=True,local_tools=len(rows),no_new_GPU_or_transport=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NOMINAL_TOOL_IMPORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),no_main_entrypoint_GPU_network_PPO_budget=True),f,indent=2)
        raise
