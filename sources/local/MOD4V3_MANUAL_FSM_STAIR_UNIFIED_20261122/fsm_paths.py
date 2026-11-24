"""Read-only donor locations; all generated files belong to this experiment."""
from pathlib import Path
import os
import sys

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[2]
ROOT = REPO.parent
E0_DIR = LOCAL / 'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120'
R61_DIR = LOCAL / 'MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120'
SOFT_DIR = LOCAL / 'MOD4V3_UNIFIED_SILKY_LOCO_GPU_RL_20261121'
JUMP_DIR = LOCAL / 'MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121'
E0_PATH = E0_DIR / 'weights/e0_c874_004m.pt'
E0_SHA = 'b271cafbb8f3c926b05637ede96fe505ec9e7e1be7300d9230212832220faddb'
E0_BASE_PATH = REPO / 'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
E0_BASE_SHA = 'c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
JUMP_PATH = JUMP_DIR / 'evidence/jump380_r10/ppo/model_009m.pt'
JUMP_SHA_PREFIX = '4c35c0e1'
STAIR_DONOR = SOFT_DIR / 'evidence/softmoe_r9/train/model_final.pt'
LOW_STAIR = LOCAL / 'MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118/weights/model_rl_stair_best.pt'
PYTHON = ROOT / '.venv/Scripts/python.exe'

def donor_imports():
    sys.dont_write_bytecode = True
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    os.environ.setdefault('MKL_NUM_THREADS', '1')
    for folder in (R61_DIR, E0_DIR, SOFT_DIR, JUMP_DIR):
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))

