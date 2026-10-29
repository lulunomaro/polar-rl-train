from pathlib import Path
import json
B=Path(__file__).resolve().parent
L=B.parent/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027"
D=L/"E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4"
p=json.loads((D/"reports/E2_V4_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json").read_bytes())
exclude={"complete_original_own_stage_UTF8","restore","admission_readonly_evidence"}
out={k:v for k,v in p.items() if k not in exclude}
if "original_terminal" in out:
 t=out["original_terminal"]
 out["original_terminal_keys"]=list(t) if isinstance(t,dict) else type(t).__name__
 out.pop("original_terminal")
print(json.dumps(out,indent=2,ensure_ascii=False)[:20000])

