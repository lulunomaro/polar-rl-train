from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent
p=R/'prepare_closed55_pair56_future57_handoff_once.py';s=p.read_text('utf8')
fixes={
 'CLOSED55_OLD52_53_PEER_PAIR55':'CLOSED55_OLD52_53_PEER_PAIR56',
 'OLD52_53_PEER_PAIR55_BOTH_PPO':'OLD52_53_PEER_PAIR56_BOTH_PPO',
 'closed54_pair_complete_CPU':'closed55_pair_complete_CPU',
 'latestactual覆盖54active/55reserved':'latestactual覆盖55active/56reserved',
 '当前56/future56 collector':'当前56/future57 collector',
 '55runid=':'56runid=',
 '未选H1only55helper':'未选H1only56helper',
 '未两完整不跑56bothFINAL':'未两完整不跑57bothFINAL',
 '不要求paired55不存在H1onlyreceipt':'不要求paired56不存在H1onlyreceipt',
 '只actual56GO/PPO后后继reserved':'只actual57GO/PPO后后继reserved',
}
counts={}
for a,b in fixes.items():
 assert a in s,a
 counts[a]=s.count(a);s=s.replace(a,b)
ast.parse(s)
q=R/'prepare_closed55_pair56_future57_handoff_checked_V2_once.py';assert not q.exists();q.write_text(s,'utf8')
with (R/'CLOSED55_UNUSED_HANDOFF_LABEL_REVIEW_V2_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_unused_source=str(p),original_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_not_executed=True,checked_source=str(q),checked_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),passed_AST_only=True,exact_label_replacements=fixes,counts=counts,scope='Pre-execution handoff labels only. No runtime source, host query, training failure, fee, or budget mutation.',all_original_drafts_preserved=True),f,ensure_ascii=False,indent=2)
print(q)
