"""Own saved-document clarity amendment only; no old source/code execution."""
from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;R=O/'revisions/close_attempt_01';R.mkdir(parents=True,exist_ok=False)
for n in('REPORT.md','RECEIPT.json','CANDIDATE_BINDINGS.json','close_audit.py','close_01.log'):
 b=(O/n).read_bytes()
 with(R/n).open('xb')as f:f.write(b)
def rec(p):
 b=p.read_bytes();return dict(path='OLD_DEPLOYED_BOARD_AUDIT_V1/'+p.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def text(p,v):
 with p.open('w',encoding='utf-8',newline='\n')as f:f.write(v)
report=(O/'REPORT.md').read_text(encoding='utf-8')
a='DM 0x51..0x56（本机用51..54），LK141..144（用141/142）';b='DM 0x51..0x56（本机用0x51..0x54），LK 0x141..0x144（用0x141/0x142）'
assert report.count(a)==1;report=report.replace(a,b)
a='当前motor初始化mode0，normal MIT并不走float位置/速度mode。'
b='当前motor初始化mode0，normal MIT并不走float位置/速度mode；所有非OFF分支先检查fdb.state==DISABLE(0)便发DmEnable，再继续模式控制，未先以offline/fault/ACK确认使能。'
assert report.count(a)==1;report=report.replace(a,b)
assert len(report.splitlines())<=100;text(O/'REPORT.md',report)
B=json.loads((O/'CANDIDATE_BINDINGS.json').read_bytes());row=next(r for r in B['rows']if r['name']=='joint_DM8009_MIT_TX')
row['observed_old_source']['actual_auto_enable_condition']='every non-OFF cycle, fdb.state==DM_STATE_DISABLE(0) -> DmEnable, then mode control continues; no offline/fault/ACK admission'
text(O/'CANDIDATE_BINDINGS.json',json.dumps(B,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
V=json.loads((O/'RECEIPT.json').read_bytes());V['report']=rec(O/'REPORT.md');V['binding_table']=rec(O/'CANDIDATE_BINDINGS.json')
V['saved_only_clarity_amendment']='prior close succeeded; explicit hex prefixes and actual non-OFF state0->enable caller condition added, no new source/analysis/build/test/PHY; original metadata kept in revisions/close_attempt_01'
text(O/'RECEIPT.json',json.dumps(V,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(report=rec(O/'REPORT.md'),bindings=rec(O/'CANDIDATE_BINDINGS.json'),receipt=rec(O/'RECEIPT.json'),report_lines=len(report.splitlines())),indent=2))
