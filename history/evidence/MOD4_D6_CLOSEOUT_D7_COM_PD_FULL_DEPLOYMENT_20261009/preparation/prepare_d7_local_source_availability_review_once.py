"""Local build may contain only fetched sources; remote inheritance remains all265."""
from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_D7_FULL_CONTRACT_20261009';OLD=P.parent/'MOD4_D6_FULL_CONTRACT_20261009'
assert D.exists() and not (D/'reports/LOCAL_D7_BUILD.json').exists()
freeze=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];available=[];not_local=[]
for n,h in freeze.items():
 if not (OLD/n).exists():not_local.append(n);continue
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h
 target=D/n;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==(OLD/n).read_bytes()
 else:shutil.copy2(OLD/n,target)
 available.append(n)
(D/'reports/LOCAL_SOURCE_AVAILABILITY_REVIEW.json').write_text(json.dumps(dict(available=available,not_local=not_local,remote_all265_exact_staging_required=True,first_build_error_preserved='Missing local probe_physx.py; no remote/GPU/budget transaction'),indent=2))
source=(P/'prepare_d7_combined_contract_once.py').read_text();tail='new=[]'+source.split('new=[]',1)[1]
scope=dict(PREP=P,OLD=OLD,D=D,R=D/'reports',read=lambda p:json.loads(p.read_text(encoding='utf8')))
exec('import ast,json,hashlib,shutil,time\n'+tail,scope)
