"""Local-only prearchive receipt; do not rerun binder or query live training."""
from pathlib import Path
import hashlib
import json
import time
import tomllib

N = Path(__file__).resolve().parent
R = N / "reports"
source = R / "CURRENT_ACTUAL80_THREE4090_V8_LANDING_JOURNAL_MONITOR_SOURCE.txt"
automation = Path.home() / ".codex/automations/mod4-10/automation.toml"
a = tomllib.loads(automation.read_text("utf8"))
assert a["status"] == "ACTIVE"
assert a["target_thread_id"] == "01a07a2d-9036-7531-a012-692df9f56353"
assert a["rrule"] == "FREQ=HOURLY;INTERVAL=1"
assert a["prompt"] == source.read_text("utf8")
first = json.loads((R / "THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json").read_bytes())
assert first["passed"] and first["actual_finite_returned"]
journal = first["source210"]["landing_event_journal_first_snapshot"]
assert journal["present"] and journal["value"]["diagnostic_valid"]
value = journal["value"]
receipt = dict(
    epoch=time.time(),
    automation_id="mod4-10",
    status=a["status"],
    rrule=a["rrule"],
    target_thread_id=a["target_thread_id"],
    saved_prompt_exactly_matches=True,
    prompt_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),
    actual_first_PPO_finite_returned=True,
    binder_warning_classification=dict(
        observed_count=3,
        warning="nonfatal backslash-S invalid escape SyntaxWarning during source AST parsing",
        evidence="original successful binder tool output, retained in conversation",
        original_binder_succeeded=True,
        not_a_training_failure=True,
        binder_not_rerun_for_this_classification=True,
    ),
    first_journal_snapshot=dict(
        completed_control_rows=value["completed_control_rows_seen"],
        cases_started=value["cases_started"],
        cases=[dict(case_id=c["case_id"], env_id=c["env_id"],
                    closed_reason=c["closed_reason"], pre_rows=c["pre_rows"],
                    post_rows=c["post_rows"]) for c in value["cases"]],
        reset_censoring_is_not_proof_of_recovery_failure_cause=True,
        no_stable_recovery_or_frozen_skill_claim=True,
    ),
    no_remote_query_model_read_or_training_mutation=True,
    postGit_verification_will_remain_conversation_only=True,
)
with (R / "ACTUAL80_MONITOR_EXACT_SOURCE_AND_FIRST_JOURNAL_CENSORING_PREARCHIVE_ACTUAL.json").open("x", encoding="utf8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
print(json.dumps(dict(monitor_exact=True, first_journal_cases=value["cases_started"], prearchive_receipt_saved=True)))
