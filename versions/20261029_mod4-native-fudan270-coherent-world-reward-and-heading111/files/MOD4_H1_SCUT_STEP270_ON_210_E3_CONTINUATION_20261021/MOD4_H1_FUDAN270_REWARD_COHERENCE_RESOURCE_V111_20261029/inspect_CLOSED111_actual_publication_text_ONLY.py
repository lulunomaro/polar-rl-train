from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
L = ROOT.parent / "MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027"
Q = L / "TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3"
p=json.loads((Q/"reports/TWO111_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json").read_text(encoding="utf-8-sig"))
out={"fee":p["original_fee_by_slot"],"total":p["original_fee_seconds"],"closing_snapshot":p["closing_remaining_snapshot"],"allout":p["all_two_original_owner_nodes_workers_out"],"CNone":p["canonical_None"],"roles":{}}
for role in ["h1","h1_seed28"]:
 f=p["formals"][role]["final"]
 out["roles"][role]={"model":{k:f[k] for k in ["path","bytes","SHA","updates","world_updates","policy_updates"]},
 "counters":f["native88_migration_window"]["counters"],"events":f["original_H1_events"]["original270_completed_control_events"],
 "last_control_reward":f["original_H1_events"]["fudan_real_reward_tracking"]}
out["original_text_records_count"]=len(p["all_original_texts_full_case_safe"])
out["text_record_sample"]=p["all_original_texts_full_case_safe"][:2]
print(json.dumps(out,ensure_ascii=False,indent=2))

