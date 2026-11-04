"""Collect only the original owned early full-save/exit/evaluation results."""
from pathlib import Path
import importlib.util
import json
import os
import time
import traceback
N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104';R=A/'reports'
def put(name,value):
    with(R/name).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)
assert(R/'CAPACITY_ERROR_STOP_AFTER_SAVE_ACTUAL.json').exists()
assert not(R/'POSTROUND_ONCE.json').exists()
put('POSTROUND_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),sameprocess_finite_receiver=True,
    early_complete_save_requested_for_actual_capacity_error=True,no_second_train_or_eval=True))
s=importlib.util.spec_from_file_location('scut_stair_original_early_return',N/'postround.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.A=A;m.R=R;m.m.R=R;m.put=put
try:m.receive(json.loads((A/'PLAN.json').read_bytes())['remote_root'],'SCUT_STAIRS_CAPACITY_EARLY_RETURN')
except BaseException:
    put('POSTROUND_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
    raise
