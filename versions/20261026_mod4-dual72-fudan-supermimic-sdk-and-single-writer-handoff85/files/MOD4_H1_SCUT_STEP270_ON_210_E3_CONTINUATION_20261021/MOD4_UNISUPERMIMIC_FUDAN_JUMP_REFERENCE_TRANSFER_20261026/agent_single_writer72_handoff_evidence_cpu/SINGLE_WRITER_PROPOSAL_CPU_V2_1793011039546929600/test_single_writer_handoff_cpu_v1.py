"""Read-only proposal and rejection fixtures. No actual authority or account IO."""
from pathlib import Path
from copy import deepcopy
from decimal import Decimal
import hashlib,json,time,unittest
import single_writer_handoff_contract_cpu_v1 as C

HERE=Path(__file__).resolve().parent


class Contracts(unittest.TestCase):
    def test01_valid_review_is_not_authorized_or_executed(self):
        p=C.proposal();r=C.validate_review(p)
        self.assertFalse(p["human_authorized"]);self.assertFalse(r["activation_permitted"])
        self.assertFalse(p["canonical_created_or_copied"])
        with self.assertRaisesRegex(C.HandoffRejected,"human.*confirmation"):C.validate_activation_request(p)

    def test02_exact_original_total_charged_and_remaining(self):
        p=C.proposal();c=p["carry_forward"]
        self.assertEqual(Decimal(c["original_charged_seconds"])+Decimal(c["original_remaining_seconds"]),Decimal("2268000"))
        self.assertEqual(c["original_remaining_seconds"],"595256.8240613937")
        self.assertEqual(c["original_extension_count"],9)

    def test03_any_balance_rounding_refund_or_grant_rejected(self):
        for key,value in (("original_remaining_seconds","595256.824061394"),("original_authorized_total_seconds","2300000"),("original_extension_count",10)):
            p=C.proposal();p["carry_forward"][key]=value
            with self.assertRaises(C.HandoffRejected):C.validate_review(p)
        for key in ("refund","new_extension","budget_increase","unreconciled_pending_turned_into_charge"):
            p=C.proposal();p["accounting"][key]=True
            with self.assertRaises(C.HandoffRejected):C.validate_review(p)

    def test04_old_authority_cannot_be_revived_or_coexist(self):
        p=C.proposal();p["old_authority"]["allow_any_future_old_owner_writes"]=True
        with self.assertRaisesRegex(C.HandoffRejected,"permanently retired"):C.validate_review(p)
        p=C.proposal();p["old_authority"]["restored_old_disk_or_route_does_not_reauthorize_old_owner"]=False
        with self.assertRaisesRegex(C.HandoffRejected,"revive"):C.validate_review(p)
        p=C.proposal();p["new_authority"]["exactly_one_account_writer"]=False
        with self.assertRaisesRegex(C.HandoffRejected,"second writer"):C.validate_review(p)

    def test05_human_yes_alone_does_not_retire_old_writer_or_prove_locks(self):
        p=C.proposal();p["human_authorized"]=True;p["activation_requirements"]["explicit_human_confirmation"]=True
        with self.assertRaisesRegex(C.HandoffRejected,"retirement declaration"):C.validate_activation_request(p)
        p["old_authority"]["retirement_effective"]=True;p["activation_requirements"]["old_authority_retirement_declaration"]=True
        with self.assertRaisesRegex(C.HandoffRejected,"proof incomplete"):C.validate_activation_request(p)

    def test06_unknown_active_or_nonunique_last_run_rejected(self):
        p=C.proposal();p["carry_forward"]["last_observed_active"]={"owner":"unknown"}
        with self.assertRaisesRegex(C.HandoffRejected,"unknown active"):C.validate_review(p)
        p=C.proposal();p["carry_forward"]["last_settled_run_id"]="different_old_owner"
        with self.assertRaises(C.HandoffRejected):C.validate_review(p)

    def test07_history_gap_cannot_be_labeled_full_byte_migration(self):
        p=C.proposal();p["migration_kind"]="byte_for_byte_migration"
        with self.assertRaisesRegex(C.HandoffRejected,"full original ledger"):C.validate_review(p)
        for key in ("old_run_history_reconstructed","full_original_canonical_bytes_available"):
            p=C.proposal();p["carry_forward"][key]=True
            with self.assertRaisesRegex(C.HandoffRejected,"fabricated"):C.validate_review(p)
        p=C.proposal();p["carry_forward"]["old_Git_history_rewritten"]=True
        with self.assertRaisesRegex(C.HandoffRejected,"Git evidence"):C.validate_review(p)

    def test08_two_new_owner_locks_must_be_distinct_and_same72_root(self):
        p=C.proposal();p["new_authority"]["owner_locks"][1]=p["new_authority"]["owner_locks"][0]
        with self.assertRaises(C.HandoffRejected):C.validate_review(p)
        p=C.proposal();p["new_authority"]["owner_locks"][1]="/old210/writer.lock"
        with self.assertRaises(C.HandoffRejected):C.validate_review(p)

    def test09_pending_safety_and_original_caps_are_preserved(self):
        p=C.proposal();C.validate_review(p)
        self.assertEqual(p["holds"]["strict_required_runway_seconds"],"86412.86069250107")
        self.assertEqual(p["holds"]["Windows_pending_unsettled_seconds"],"9400.860692501068")
        for key in ("Windows_pending_unsettled_seconds","unknown_pending_reserve_seconds","safety_headroom_seconds","existing_scope_parent_caps_total_seconds"):
            q=deepcopy(p);q["holds"][key]="0"
            with self.assertRaises(C.HandoffRejected):C.validate_review(q)

    def test10_go_terminal_sum_once_and_old83B_not_recharged(self):
        def row(key,start,end):return dict(interval_id=key,actual_GO=True,actual_terminal_received=True,GO_epoch=start,terminal_epoch=end,
            charged_seconds=end-start,authority_generation="PROPOSED_MOD4_SINGLE_WRITER72_20261026",post_cutover_new_interval=True)
        a=row("CPU_FIXTURE_A",100,200);b=row("CPU_FIXTURE_B",110,260)
        self.assertEqual(C.charge_sum_once_candidate([a,b]),Decimal(250))
        with self.assertRaisesRegex(C.HandoffRejected,"duplicate"):C.charge_sum_once_candidate([a,a])
        old=row(C.LAST_SETTLED_RUN,0,10)
        with self.assertRaisesRegex(C.HandoffRejected,"settled"):C.charge_sum_once_candidate([old])
        a["post_cutover_new_interval"]=False
        with self.assertRaisesRegex(C.HandoffRejected,"back-charged"):C.charge_sum_once_candidate([a])

    def test11_no_GO_no_terminal_wrong_duration_or_overcap_cannot_charge(self):
        base=dict(interval_id="CPU_FIXTURE",actual_GO=True,actual_terminal_received=True,GO_epoch=0,terminal_epoch=100,charged_seconds=100,
            authority_generation="PROPOSED_MOD4_SINGLE_WRITER72_20261026",post_cutover_new_interval=True)
        for changed in ({"actual_GO":False},{"actual_terminal_received":False},{"charged_seconds":50},{"terminal_epoch":4000,"charged_seconds":4000}):
            with self.assertRaises(C.HandoffRejected):C.charge_sum_once_candidate([{**base,**changed}])


class RecordingResult(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.records=[]
    def addSuccess(self,t):super().addSuccess(t);self.records.append(dict(test=t.id(),status="PASS"))
    def addFailure(self,t,e):super().addFailure(t,e);self.records.append(dict(test=t.id(),status="FAIL",error=self._exc_info_to_string(e,t)))
    def addError(self,t,e):super().addError(t,e);self.records.append(dict(test=t.id(),status="ERROR",error=self._exc_info_to_string(e,t)))


if __name__=="__main__":
    trial="SINGLE_WRITER_PROPOSAL_CPU_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False);sources=[]
    for p in (HERE/"single_writer_handoff_contract_cpu_v1.py",Path(__file__)):
        data=p.read_bytes();(out/p.name).write_bytes(data);sources.append(dict(path=str(out/p.name),SHA256=hashlib.sha256(data).hexdigest()))
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    report=dict(trial_id=trial,status="PASS" if result.wasSuccessful() else "FAIL",tests=result.records,source=sources,
        tests_run=result.testsRun,actual_authority_activation_or_canonical_IO=False,
        human_confirmation=False,simulated_approval_flags_only_in_memory_not_authorization=True,git_archive_state="pending_root_archive")
    p=out/"CPU_PROPOSAL_REJECTION_TEST_RESULT.json"
    with p.open("x",encoding="utf8") as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(path=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),status=report["status"],tests=result.testsRun)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
