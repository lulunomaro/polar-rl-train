"""Local synthetic files only. Keep all attempts/fault fixtures; no real authority IO."""
from pathlib import Path
from dataclasses import replace
import ast,hashlib,json,os,time,traceback,unittest
import retire_old210_authority_core_v1 as C

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
SOURCE=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1"
AUTH=T/"H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026/reports/HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json"
OUT=None


def raw_fixture(**changes):
    data=dict(active_segment=None,authorized_training_seconds=2268000,remaining_training_seconds=595256.8240613937,
              charged_training_seconds=1672743.1759386063,budget_extensions=[{"fixture":i} for i in range(9)],
              completed_segments=[{"fixture_only":True,"id":"not_real_history"}])
    data.update(changes)
    # Whitespace/order/CRLF are intentional: exact bytes must survive, not JSON reserialization.
    return (json.dumps(data,indent=3)+"\r\n").encode("utf8")


class RetirementContracts(unittest.TestCase):
    def setUp(self):
        self.folder=OUT/(self._testMethodName+"_fixture");self.folder.mkdir(exist_ok=False)
        self.source=self.folder/"SYNTHETIC_ORIGINAL_ACCOUNT_FIXTURE.json";self.raw=raw_fixture();self.source.write_bytes(self.raw)
        self.expected=replace(C.Expected(),source_sha=C.sha(self.raw));self.history=C.history_path(self.source,self.expected)

    def test01_authorization_real_raw_SHA_is_pinned_and_valid(self):
        raw=AUTH.read_bytes();self.assertEqual(C.sha(raw),C.AUTH_SHA);self.assertTrue(C.validate_authorization(raw)["approved"])
        with self.assertRaisesRegex(C.RetirementRejected,"SHA mismatch"):C.validate_authorization(raw+b" ")

    def test02_SHA_or_each_original_field_mismatch_is_rejected_without_mutation(self):
        with self.assertRaisesRegex(C.RetirementRejected,"exact SHA mismatch"):C.validate_original(self.raw,C.Expected())
        for changes in ({"active_segment":{"pid":"unknown"}},{"authorized_training_seconds":2268001},
                        {"remaining_training_seconds":595256.8},{"budget_extensions":[]},{"completed_segments":None}):
            raw=raw_fixture(**changes);expected=replace(self.expected,source_sha=C.sha(raw))
            with self.assertRaises(C.RetirementRejected):C.validate_original(raw,expected)
        self.assertEqual(self.source.read_bytes(),self.raw);self.assertFalse(self.history.exists())

    def test03_dry_review_or_missing_original_lock_proof_never_writes(self):
        r=C.transaction_under_owned_locks(self.source,self.expected)
        self.assertEqual(r["status"],"DRY_REVIEW_NO_MUTATION");self.assertEqual(self.source.read_bytes(),self.raw)
        with self.assertRaisesRegex(C.RetirementRejected,"both original owner locks"):
            C.transaction_under_owned_locks(self.source,self.expected,execute=True)
        self.assertFalse(self.history.exists())

    def test04_exact_bytes_inode_and_old_cost_survive_atomic_rename(self):
        before=self.source.stat();r=C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)
        self.assertIn("TOMBSTONE_INSTALLED",r["status"]);self.assertEqual(self.history.read_bytes(),self.raw)
        self.assertEqual(self.history.stat().st_ino,before.st_ino)
        self.assertEqual(self.history.stat().st_mode,before.st_mode)
        self.assertEqual(json.loads(self.history.read_bytes())["remaining_training_seconds"],595256.8240613937)
        tomb=json.loads(self.source.read_bytes());self.assertEqual(set(tomb),C.TOMBSTONE_KEYS)
        for forbidden in ("active_segment","active","authorized_training_seconds","remaining_training_seconds","budget_extensions","completed_segments"):
            self.assertNotIn(forbidden,tomb)

    def test05_original_validate_budget_and_actual_owner_access_reject_tombstone(self):
        C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True);tomb=json.loads(self.source.read_bytes())
        validator_path=SOURCE/"job0/runtime/isaac/mod4/budget_authority.py";tree=ast.parse(validator_path.read_text(encoding="utf8"))
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="validate_budget")
        ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(validator_path),"exec"),ns)
        with self.assertRaises(KeyError):ns["validate_budget"](tomb)
        owner_path=SOURCE/"three_slot_finite_owner_v1.py";tree=ast.parse(owner_path.read_text(encoding="utf8"))
        owner=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="owner")
        expression=next(n for n in ast.walk(owner) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=="c"
                        and isinstance(n.slice,ast.Constant) and n.slice.value=="active_segment")
        # Execute only the exact real admission expression, never owner/thread/HTTP code.
        code=compile(ast.fix_missing_locations(ast.Expression(expression)),str(owner_path)+":required_admission_field","eval")
        with self.assertRaises(KeyError):eval(code,{"c":tomb})

    def test06_post_rename_interruption_resumes_same_history_without_copy(self):
        def fault(event):
            if event=="after_original_rename":raise RuntimeError("CPU_INJECTED_INTERRUPT_AFTER_RENAME")
        with self.assertRaisesRegex(RuntimeError,"CPU_INJECTED"):
            C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True,event=fault)
        self.assertFalse(self.source.exists());self.assertEqual(self.history.read_bytes(),self.raw);inode=self.history.stat().st_ino
        r=C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)
        self.assertIn("TOMBSTONE_INSTALLED",r["status"]);self.assertEqual(self.history.stat().st_ino,inode)

    def test07_unexpected_C_in_gap_is_never_overwritten_and_history_remains(self):
        unexpected=b'{"UNEXPECTED_PEER_FILE":true}\n'
        def interference(event):
            if event=="before_tombstone_install":self.source.write_bytes(unexpected)
        with self.assertRaises(OSError):C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True,event=interference)
        self.assertEqual(self.source.read_bytes(),unexpected);self.assertEqual(self.history.read_bytes(),self.raw)
        self.assertEqual(len(list(self.folder.glob("*.partial"))),1)

    def test08_already_retired_is_idempotent_and_mismatch_never_repaired_by_guess(self):
        C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)
        before=self.source.read_bytes();inode=self.history.stat().st_ino
        self.assertEqual(C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)["status"],"ALREADY_RETIRED_EXACT_IDEMPOTENT")
        self.assertEqual(self.source.read_bytes(),before);self.assertEqual(self.history.stat().st_ino,inode)
        self.history.write_bytes(b"CPU_CORRUPTED_FIXTURE")
        with self.assertRaises(C.RetirementRejected):C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)
        self.assertEqual(self.source.read_bytes(),before)

    def test09_duplicate_source_and_history_or_destination_never_overwrite(self):
        self.history.write_bytes(b"EXISTING_HISTORY_FIXTURE")
        with self.assertRaisesRegex(C.RetirementRejected,"ambiguous"):
            C.transaction_under_owned_locks(self.source,self.expected,execute=True,locks_held=True)
        self.assertEqual(self.history.read_bytes(),b"EXISTING_HISTORY_FIXTURE");self.assertEqual(self.source.read_bytes(),self.raw)

    def test10_process_identity_rejects_live_old_owner_and_allows_absent_or_reused(self):
        rows=[dict(pid=p,exists=False) for p in (C.OWNER_PID,C.OLD_SOURCE_NODE_PID,C.OLD_SOURCE_WORKER_PID)]
        self.assertEqual(len(C.validate_targeted_old_process_rows(rows)),3)
        rows[0]=dict(pid=C.OWNER_PID,exists=True,creation=C.OWNER_CREATION)
        with self.assertRaisesRegex(C.RetirementRejected,"still be alive"):C.validate_targeted_old_process_rows(rows)
        rows[0]["creation"]=C.OLD_SCOPE_ENDED+1000
        self.assertTrue(C.validate_targeted_old_process_rows(rows)[0]["old_identity_out"])

    def test11_first_observer_must_have_returned_and_72_is_data_reference_only(self):
        receipt=dict(schema="mod4.root.serial_source210_retirement_clearance.v1",root_first_observer_actual_returned=False,
            root_serial_execution_on_source210=True,new72_generation=C.GENERATION,new72_canonical_path=C.NEW_C,
            new72_authority_already_active=True,old83B_all_owner_children_out_receipt=True)
        with self.assertRaisesRegex(C.RetirementRejected,"observer still live"):C.validate_serial_clearance(receipt)
        receipt["root_first_observer_actual_returned"]=True;C.validate_serial_clearance(receipt)
        receipt["fixture"]=True
        with self.assertRaisesRegex(C.RetirementRejected,"fixture clearance"):C.validate_serial_clearance(receipt)
        core=(HERE/"retire_old210_authority_core_v1.py").read_text(encoding="utf8")
        executor=(HERE/"retire_old210_authority_local_executor_v1.py").read_text(encoding="utf8")
        for forbidden in ("chmod(","unlink(","shutil.copy","torch.load","nvidia-smi","paramiko","ssh "):
            self.assertNotIn(forbidden,core+executor)


class Result(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.records=[]
    def addSuccess(self,t):super().addSuccess(t);self.records.append(dict(test=t.id(),status="PASS"))
    def addFailure(self,t,e):super().addFailure(t,e);self.records.append(dict(test=t.id(),status="FAIL",error=self._exc_info_to_string(e,t)))
    def addError(self,t,e):super().addError(t,e);self.records.append(dict(test=t.id(),status="ERROR",error=self._exc_info_to_string(e,t)))


if __name__=="__main__":
    trial="OLD210_RETIREMENT_CPU_"+str(time.time_ns());OUT=HERE/trial;OUT.mkdir(exist_ok=False);source=[]
    snapshot=OUT/"source_snapshot";snapshot.mkdir()
    for p in sorted(HERE.glob("*.py")):
        raw=p.read_bytes();(snapshot/p.name).write_bytes(raw);source.append(dict(path=str(snapshot/p.name),SHA256=C.sha(raw)))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromTestCase(RetirementContracts))
    report=dict(trial_id=trial,status="PASS" if result.wasSuccessful() else "FAIL",tests=result.records,source=source,tests_run=result.testsRun,
        production_old_canonical_not_opened_or_mutated=True,all_filesystem_transactions_synthetic_under_this_trial=True,
        old_authorization_raw_validated=C.AUTH_SHA,real72_account_or_owner_or_network_touched=False,
        old_budget_validator_and_owner_admission_AST_only=True,original_fcntl_and_runtime_process_probe_not_executed_here=True,
        git_archive_state="pending_root_archive",root_execute_only_serial_after_first_observer_returned=True)
    path=OUT/"OLD210_RETIREMENT_CPU_RESULT.json"
    with path.open("x",encoding="utf8") as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(report=str(path),SHA256=C.sha(path.read_bytes()),status=report["status"],tests=result.testsRun)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
