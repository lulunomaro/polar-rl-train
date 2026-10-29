from pathlib import Path
import json,time
N=Path(__file__).resolve().parent
p=N/"prepare_ARCHIVE111_complete_closed_roots_and_final_note_SOURCE_ONLY_once.py";s=p.read_text(encoding="utf8")
try:compile(s,str(p),"exec")
except SyntaxError as e:
 with (N/"reports/ARCHIVE111_SELECTION_PREPARER_ORIGINAL_SYNTAX_REFUSAL_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),type=type(e).__name__,message=str(e),before_any_Git_model_or_report_mutation=True,original_source_preserved=True),f,indent=2)
else:raise AssertionError("original syntax false expected")
s=s.replace("111_first_history_superseded_by_final=True,112_and_active_child_excluded_pending=True","first111_history_superseded_by_final=True,active112_and_child_excluded_pending=True")
compile(s,"source_v2","exec")
v=N/"prepare_ARCHIVE111_complete_closed_roots_and_final_note_SOURCE_ONLY_v2_once.py"
with v.open("x",encoding="utf8") as f:f.write(s)

