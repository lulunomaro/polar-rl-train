"""Same11 bounded fixtures; correct only over-cap fee/admission semantics."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,time,unittest
import test_single_writer_handoff_cpu_v1 as previous
import single_writer_handoff_contract_cpu_v2 as C
import single_writer_handoff_contract_cpu_v1 as constants

previous.C=C


class CorrectedContracts(previous.Contracts):
    def test10_go_terminal_sum_once_and_old83B_not_recharged(self):
        def row(key,start,end):return dict(interval_id=key,actual_GO=True,actual_terminal_received=True,GO_epoch=start,terminal_epoch=end,
            charged_seconds=end-start,authority_generation="PROPOSED_MOD4_SINGLE_WRITER72_20261026",post_cutover_new_interval=True)
        a=row("CPU_FIXTURE_A",100,200);b=row("CPU_FIXTURE_B",110,260)
        self.assertEqual(C.charge_sum_once_candidate([a,b])["charged_seconds"],Decimal(250))
        with self.assertRaisesRegex(C.HandoffRejected,"duplicate"):C.charge_sum_once_candidate([a,a])
        with self.assertRaisesRegex(C.HandoffRejected,"settled"):C.charge_sum_once_candidate([row(constants.LAST_SETTLED_RUN,0,10)])
        a["post_cutover_new_interval"]=False
        with self.assertRaisesRegex(C.HandoffRejected,"back-charged"):C.charge_sum_once_candidate([a])

    def test11_no_GO_no_terminal_wrong_duration_or_overcap_cannot_charge(self):
        # Historical method name retained for11-test identity. Correct assertion:
        # actual over-cap interval MUST charge fully and flag the duration false.
        base=dict(interval_id="CPU_FIXTURE",actual_GO=True,actual_terminal_received=True,GO_epoch=0,terminal_epoch=100,charged_seconds=100,
            authority_generation="PROPOSED_MOD4_SINGLE_WRITER72_20261026",post_cutover_new_interval=True)
        for changed in ({"actual_GO":False},{"actual_terminal_received":False},{"charged_seconds":50}):
            with self.assertRaises(C.HandoffRejected):C.charge_sum_once_candidate([{**base,**changed}])
        over=C.charge_sum_once_candidate([{**base,"terminal_epoch":4000,"charged_seconds":4000}])
        self.assertEqual(over["charged_seconds"],Decimal(4000));self.assertFalse(over["duration_bound_passed"])
        self.assertFalse(over["intervals"][0]["duration_bound_passed"]);self.assertTrue(over["no_clamp_or_refund"])


if __name__=="__main__":
    here=Path(__file__).resolve().parent;trial="SINGLE_WRITER_PROPOSAL_CPU_V2_"+str(time.time_ns());out=here/trial;out.mkdir(exist_ok=False);source=[]
    for name in ("single_writer_handoff_contract_cpu_v1.py","single_writer_handoff_contract_cpu_v2.py","test_single_writer_handoff_cpu_v1.py","test_single_writer_handoff_cpu_v2.py"):
        data=(here/name).read_bytes();(out/name).write_bytes(data);source.append(dict(path=str(out/name),SHA256=hashlib.sha256(data).hexdigest()))
    result=unittest.TextTestRunner(verbosity=2,resultclass=previous.RecordingResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(CorrectedContracts))
    report=dict(trial_id=trial,status="PASS" if result.wasSuccessful() else "FAIL",tests=result.records,source=source,tests_run=result.testsRun,
        V1_prior_status="CPU_assertions_passed_but_overcap_charge_refusal_semantically_rejected_by_root;original_unchanged",
        correction="actual_overcap_GO_terminal_full_cost_sumonce_duration_bound_false_no_clamp_refund",
        no_scope_expansion=True,human_authorized=False,actual_account_or_authority_actions=False,git_archive_state="pending_root_archive")
    path=out/"CPU_PROPOSAL_REJECTION_TEST_RESULT_V2.json"
    with path.open("x",encoding="utf8") as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(path=str(path),SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),status=report["status"],tests=result.testsRun)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
