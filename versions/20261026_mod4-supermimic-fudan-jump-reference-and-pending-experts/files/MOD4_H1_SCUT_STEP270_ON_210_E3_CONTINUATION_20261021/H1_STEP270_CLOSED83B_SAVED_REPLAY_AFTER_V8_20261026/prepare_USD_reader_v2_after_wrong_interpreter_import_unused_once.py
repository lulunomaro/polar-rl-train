from pathlib import Path
import hashlib,json,time
U=Path(__file__).resolve().parent;old=U/'reconstruct_closed83B_saved_motion_USD_CPU_unused_once.py';assert not (U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz').exists()
with (U/'reports/LOCAL_USD_READER_ENV_ISAACLAB_MISSING_PXR_IMPORT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error='ModuleNotFoundError: No module named pxr',original_entry=str(old),original_source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),interpreter='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe',failed_at_module_import_before_main_or_NPZ_USD_read=True,correct_interpreter='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe',pxr_module_spec_actual_path='C:/Users/lulu/AppData/Local/Programs/Python/Python314/Lib/site-packages/pxr/__init__.py',not_training_failure=True),f,indent=2)
new=U/'reconstruct_closed83B_saved_motion_USD_CPU_v2_python314_unused_once.py'
with new.open('xb') as f:f.write(old.read_bytes())
print(json.dumps(dict(new_entry=str(new),same_source_only_correct_interpreter=True)))
