"""Reuse the saved-pose renderer, binding the actual v2 collision contract."""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'mod4v1_scut_step270_2h_20261103/render80.py'
if __name__=='__main__':
    source=SOURCE.read_text(encoding='utf8')
    old="F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json"
    contract=ROOT/'attempt02/hardware/assets/import_contract.json'
    assert hashlib.sha256(contract.read_bytes()).hexdigest()=='00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e'
    assert source.count(old)==1
    source=source.replace(old,str(contract).replace('\\','/')).replace('Actual MOD4v1','Actual MOD4v2')
    exec(compile(source,str(SOURCE),'exec'),dict(__name__='__main__',__file__=str(SOURCE)))
