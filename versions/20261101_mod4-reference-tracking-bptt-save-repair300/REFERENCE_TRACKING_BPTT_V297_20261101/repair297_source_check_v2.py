from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;old=N/'finalize297_source_checks.py';text=old.read_text('utf8')
text=text.replace("assert 'imagined_step('not in learner and 'LiteralJump194'in learner is False", "assert 'imagined_step('not in learner and 'LiteralJump194' not in learner")
text=text.replace("p.write_bytes(text.encode());ast.parse(text)", "ast.parse(text)\nif p.read_bytes()!=text.encode():p.write_bytes(text.encode())")
p=N/'finalize297v2_source_checks.py';p.write_bytes(text.encode());ast.parse(text)
with(N/'reports/LOCAL297_SOURCE_CHECK_CHAINED_COMPARISON_FALSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original='Assertion used chained in learner is False, tested learneridentityFalse rather than exclusion. No Fudan call in learner.',repair='v2 explicit notin; production unchanged.0GPU/model/GO.',old_source_preserved=True),f,indent=2)
