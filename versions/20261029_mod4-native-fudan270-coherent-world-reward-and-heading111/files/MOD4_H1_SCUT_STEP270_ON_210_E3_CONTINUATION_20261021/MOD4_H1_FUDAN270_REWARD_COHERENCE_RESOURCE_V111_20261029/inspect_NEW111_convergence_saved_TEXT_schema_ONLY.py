from pathlib import Path
import json
B=Path(__file__).resolve().parent
L=B.parent/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027"
Q=L/"TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3"
p=json.loads((Q/"reports/TWO111_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json").read_bytes())
rows=[x for x in p["all_original_texts_full_case_safe"] if "convergence" in x["relative"].lower() or "curve" in x["relative"].lower()]
print(json.dumps([{k:x[k] for k in ["relative","bytes","SHA","local_path"]} for x in rows],indent=2))
for x in rows:
 path=Path(x["local_path"])
 lines=path.read_text(encoding="utf8").splitlines()
 if not lines:continue
 try:
  a=json.loads(lines[0]); z=json.loads(lines[-1])
 except (json.JSONDecodeError,TypeError):continue
 print("ROW_SCHEMA",x["relative"],len(lines),json.dumps(a,ensure_ascii=False)[:16000],"\nLAST",json.dumps(z,ensure_ascii=False)[:1000])

