"""Workspace-owned paths and output helpers. Donor modules remain read-only."""
from pathlib import Path
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
DONOR = LOCAL / 'MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122'
PYTHON = Path(r'D:\claude2\fangzhen\.venv\Scripts\python.exe')
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP', 'TMP', 'MPLCONFIGDIR', 'TORCH_HOME'):
    directory = HERE / 'cache' / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
if str(DONOR) not in sys.path:
    sys.path.insert(0, str(DONOR))

def put(path, obj):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f'Output outside dedicated workspace: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.partial')
    def convert(value):
        if hasattr(value, 'tolist'):return value.tolist()
        if isinstance(value,Path):return str(value)
        raise TypeError(type(value).__name__)
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False, default=convert) + '\n', encoding='utf-8')
    tmp.replace(path)

def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def donor_imports():
    from fsm_paths import donor_imports as setup
    setup()

