"""D5 comparison reader: anchor follows its own immutable source, not active block."""
from pathlib import Path
p=Path(__file__).with_name('review_d5_scope.py')
t=p.read_text(encoding='utf8')
old="actual=read(R/'D5_CURRENT_ACTUAL.json');source=actual['state']['source']['sha256'];out={}"
new="source=read(R/'SELECTED_D4_BEHAVIOR_SOURCE.json')['checkpoint']['sha256'];out={}"
assert t.count(old)==1
t=t.replace(old,new).replace("R/'D5_ACTUAL_BASELINE_SCOPE_REVIEW.json'","R/'D5_MODEL30649_MATCHED_REVIEW.json'")
exec(compile(t,str(p),'exec'),globals())
