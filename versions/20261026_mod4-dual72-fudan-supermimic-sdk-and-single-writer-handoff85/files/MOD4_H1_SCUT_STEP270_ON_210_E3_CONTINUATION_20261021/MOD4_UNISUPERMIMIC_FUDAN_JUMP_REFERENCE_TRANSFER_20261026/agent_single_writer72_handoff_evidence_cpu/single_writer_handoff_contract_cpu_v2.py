"""V2: actual over-cap GO-terminal cost is fully charged once, never forgiven.
V1 source/test pass remains preserved but its over-cap rejection was semantically
wrong. Admission cap stays3900; a violation only makes duration_bound_passed=false.
No authority/account/controller IO exists in either review contract.
"""
from decimal import Decimal
import single_writer_handoff_contract_cpu_v1 as V1
from single_writer_handoff_contract_cpu_v1 import HandoffRejected,require


def proposal():
    p=V1.proposal();p["schema"]="mod4.single_writer72.handoff_proposal.v2"
    p["accounting"].update(over_cap_actual_GO_terminal_cost_charged_fully_once=True,
        over_cap_marks_duration_bound_passed_false_not_normal_source_qualification=True,
        never_cap_clamp_refund_or_drop_actual_over_cap_cost=True)
    p["source_protocol_review_correction"]="V1_overcap_refusal_rejected;V2_actual_full_charge_and_separate_admission_status"
    return p


def validate_review(p):
    result=V1.validate_review(p)
    require(all(p["accounting"].get(k) is True for k in (
        "over_cap_actual_GO_terminal_cost_charged_fully_once",
        "over_cap_marks_duration_bound_passed_false_not_normal_source_qualification",
        "never_cap_clamp_refund_or_drop_actual_over_cap_cost")),"actual over-cap cost must remain fully charged, flagged separately")
    result["schema"]="mod4.single_writer72.handoff_review.v2"
    return result


def validate_activation_request(p):
    validate_review(p)
    return V1.validate_activation_request(p)


def charge_sum_once_candidate(records,already_settled_ids=()):
    seen=set(already_settled_ids);seen.add(V1.LAST_SETTLED_RUN);total=Decimal(0);intervals=[]
    for row in records:
        key=row["interval_id"]
        require(key not in seen,"duplicate or already-settled interval")
        require(row.get("authority_generation")=="PROPOSED_MOD4_SINGLE_WRITER72_20261026" and row.get("post_cutover_new_interval") is True,
                "legacy or pre-cutover intervals may not be back-charged through this handoff")
        require(row.get("actual_GO") is True and row.get("actual_terminal_received") is True,"actual GO and terminal receipts required")
        start=Decimal(str(row["GO_epoch"]));end=Decimal(str(row["terminal_epoch"]))
        require(end>=start,"terminal precedes actual GO")
        cost=end-start
        require(Decimal(str(row["charged_seconds"]))==cost,"charge must equal the whole observed interval exactly once")
        # A cap violation is NOT a waiver/refund. Preserve all actual cost while
        # refusing normal duration-qualified source admission independently.
        intervals.append(dict(interval_id=key,charged_seconds=cost,duration_bound_passed=cost<=Decimal(3900)))
        total+=cost;seen.add(key)
    return dict(charged_seconds=total,duration_bound_passed=all(r["duration_bound_passed"] for r in intervals),
                intervals=intervals,no_clamp_or_refund=True)
