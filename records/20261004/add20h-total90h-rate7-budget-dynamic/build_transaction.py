"""Reuse audited process/save helpers, never execute the old extension main."""
import ast
from pathlib import Path
D=Path(__file__).resolve().parent
old=ast.parse((D.parent/'MOD4_BUDGET_ADD20H_20261003/apply_add20h_20261003.py').read_text(encoding='utf8'))
keep={'read','sha','atomic','identity','same','live','processes','checkpoint','complete_run','syscall','pause_sleep'}
helpers='\n\n'.join(ast.unparse(f) for f in old.body if isinstance(f,ast.FunctionDef) and f.name in keep)
header='''import ast,copy,fcntl,hashlib,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
CODE=ROOT/'isaac/mod4'
STAGING=Path('/home/egde/rl_candidates/MOD4_BUDGET_ADD20H_20261004_4TH')
CANONICAL=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
REPORTS=ROOT/'reports';R=C/'reports';ID='USER_ADD20H_20261004_4TH';OLD=252000;NEW=324000;ADD=72000
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
APPLIED=REPORTS/(ID+'_APPLIED.json');PROGRESS=STAGING/'PROGRESS.json'
sys.path.insert(0,str(C));import supervise_rate7_transition as t
from budget_authority import validate_budget

def progress(stage,**kw):
    data=dict(stage=stage,epoch=time.time(),**kw);atomic(PROGRESS,data);print(json.dumps(data),flush=True)
'''
body=(D/'transaction_body.py').read_text(encoding='utf8')
result=header+'\n'+helpers+'\n\n'+body
ast.parse(result);(D/'apply_fourth20h.py').write_text(result,encoding='utf8')
print('New one-shot transaction compiled; old main not included')

