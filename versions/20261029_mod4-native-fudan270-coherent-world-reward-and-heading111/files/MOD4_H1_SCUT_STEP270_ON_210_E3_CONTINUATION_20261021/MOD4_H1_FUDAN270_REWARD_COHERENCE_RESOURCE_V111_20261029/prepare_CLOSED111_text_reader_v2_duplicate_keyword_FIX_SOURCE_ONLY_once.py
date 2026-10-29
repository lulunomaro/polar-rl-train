from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent
old=B/"review_CLOSED111_new_publication_full_curves_TEXT_ONLY_once.py"
s=old.read_text(encoding="utf8")
try:compile(s,str(old),"exec")
except SyntaxError as e:
 with (B/"reports/CLOSED111_LOCAL_TEXT_READER_V1_SYNTAX_ERROR_PRESERVED_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),type=type(e).__name__,message=str(e),before_any_report_or_model_read=True,original_source_preserved=True),f,indent=2)
else:raise AssertionError("Expected original duplicate-key syntax refusal")
a="initialCPU=str(cpu)";assert s.count(a)==1;s=s.replace(a,"initialCPU_report=str(cpu)")
compile(s,"NEW_V2","exec")
v=B/"review_CLOSED111_new_publication_full_curves_TEXT_ONLY_v2_once.py"
with v.open("x",encoding="utf8") as f:f.write(s)

