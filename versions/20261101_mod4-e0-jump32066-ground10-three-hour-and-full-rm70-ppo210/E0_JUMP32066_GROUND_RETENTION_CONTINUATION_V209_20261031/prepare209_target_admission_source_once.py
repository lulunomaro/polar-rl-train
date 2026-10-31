"""New exact source caller from the already-proved198 mechanics; no execution."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
E=T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209/e0_72'

def write(name,s):
 with (N/name).open('x',encoding='utf8',newline='\n') as f:f.write(s)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()

source=(E/'remote198_CPU_and_native64_admission.txt').read_text('utf8')
for a,b in [('198','209'),('v209/e0_72','v209/e0_72'),('MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v209','MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209'),
 ('run209_E0_JUMP72_400N50_worker.py','run209_mixed_E0_JUMP_worker.py'),('jump195_boundary import LiteralJump195','jump194_boundary import LiteralJump194'),('LiteralJump195(','LiteralJump194('),
 ("source=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt')", "source=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72/production/model_final_complete.pt')"),
 ('14031973','17519967'),('641200','642840'),('31984','32066'),('a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'),
 ("'--num-envs','64'","'--num-envs','80'"),('admission64','admission80'),('GPU209_NATIVE64','GPU209_NATIVE80'),('admission_envs=64','admission_envs=80')]:source=source.replace(a,b)
ast.parse(source)
write('remote209_source_CPU_and_mixed_native80_admission.txt',source)
source=(E/'install198_E0_72_source_CPU_native64_admission_once.py').read_text('utf8')
source=source.replace('198','209').replace('ROOT197_EXCLUSIVE_ADMIT209_','ROOT209_EXCLUSIVE_ADMISSION_')
source=source.replace('MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v209','MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209')
source=source.replace('remote209_CPU_and_native64_admission.txt','remote209_source_CPU_and_mixed_native80_admission.txt')
source=source.replace("proof=json.loads((R/'SOURCE209_E0_FULLSTATE_LITERAL_JUMP_GO_CPU_ACTUAL.json').read_bytes())","proof=json.loads((R/'ROOT209_MIXED_SOURCE_AND_TaskGO_CPU_ACTUAL.json').read_bytes())")
source=source.replace("binding=json.loads((T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/KNOWN_ACTIVE194_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json').read_bytes())","binding=None")
start=source.index('  auth="""');end=source.index('"""\n  put(',start)+3
source=source[:start]+'''  auth="""from pathlib import Path
import hashlib,json,time
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),passed=True,canonical_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],no_canonical_write=True)))"""'''+source[end:]
source=source.replace("source_model_bytes=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt').stat().st_size","source_model_bytes=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72/production/model_final_complete.pt').stat().st_size")
source=source.replace('CPU_and_native64_admission_once','mixed_target80_admission_once')
source=source.replace('install209_E0_72_source_CPU_native64_admission_once','install209_mixed_target80_admission_once')
source=source.replace('TASK209.json','TASK209.json')
source=source.replace('Adam17=641200,RSL=31984','Adam17=642840,RSL=32066')
source=source.replace('actual_source_model_loads=0','actual_source_model_loads=0')
# Include every current control client used in this chat plus new209. The
# inventory is local and exact, no unknown remote PID or GPU process query.
source=source.replace("'install209_E0_72_source_CPU_native64_admission_once|", "'install209_mixed_target80_admission_once|")
source=source.replace("|install_capture193_'", "|install_capture193_|install209_|launch209_|collect209_|ROOT207_|evaluate207_|install208_|launch208_'" )
ast.parse(source)
write('install209_mixed_target80_admission_once.py',source)
with (R/'FROZEN209_TARGET_ADMISSION_CALLER_SOURCE_INDEX.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),source_only=True,remote_root=REMOTE,model_loads=0,raw_reads=0,
  files={name:H(N/name) for name in ('install209_mixed_target80_admission_once.py','remote209_source_CPU_and_mixed_native80_admission.txt')},
  purpose='one fresh canonicalNone, one complete source postcopy, sourceCPU, actual80env mixed native8/64physics/16feedback; no training or ledger write'),f,indent=2)
print(json.dumps(dict(passed=True,new_target_admission_source_only=True)))
