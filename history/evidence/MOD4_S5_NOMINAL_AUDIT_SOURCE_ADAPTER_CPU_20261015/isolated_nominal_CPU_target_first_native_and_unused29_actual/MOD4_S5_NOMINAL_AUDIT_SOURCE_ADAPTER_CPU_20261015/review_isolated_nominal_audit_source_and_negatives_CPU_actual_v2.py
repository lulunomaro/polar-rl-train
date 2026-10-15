"""Reader-only correction: provide os to extracted legacy audit globals.

V1 NameError and source are retained. Candidate/runtime bytes are unchanged.
"""
from pathlib import Path
import importlib.util
import json
import os
import time
import traceback

D=Path(__file__).resolve().parent
p=D/'review_isolated_nominal_audit_source_and_negatives_CPU_actual.py'
s=importlib.util.spec_from_file_location('nominal_cpu_v1_retained',p)
v1=importlib.util.module_from_spec(s)
s.loader.exec_module(v1)
original_methods=v1.methods


def methods(path,names):
    namespace=original_methods(path,names)
    namespace['os']=os
    return namespace


if __name__=='__main__':
    try:
        v1.methods=methods
        v1.run()
    except BaseException:
        with (v1.R/('NOMINAL_CPU_REVIEW_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),reader_only_os_globals_fix=True,no_GPU_network_PPO_budget=True),f,indent=2)
        raise
