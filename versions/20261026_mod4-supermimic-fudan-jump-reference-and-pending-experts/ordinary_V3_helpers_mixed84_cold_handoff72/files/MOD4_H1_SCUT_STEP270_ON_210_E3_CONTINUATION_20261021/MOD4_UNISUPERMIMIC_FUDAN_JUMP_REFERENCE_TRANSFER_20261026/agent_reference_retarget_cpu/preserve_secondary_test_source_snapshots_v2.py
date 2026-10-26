"""Exact-SHA repair of source preservation reader; does not rerun CPU experiments.

V1 rejected its reconstruction because removing a later method left one extra
blank line. A follow-up one-line shell diagnostic also hit quote SyntaxError.
Both reader failures remain recorded; only an exact recorded SHA may be saved.
"""
from pathlib import Path
import hashlib,json,re,time,traceback

HERE=Path(__file__).resolve().parent
REPORTS=[HERE/"CPU_REFERENCE_CONTRACT_1793004103564099300.json",HERE/"CPU_REFERENCE_CONTRACT_1793004103555146100.json"]
PRIOR=HERE/"ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/source_snapshot"


def main():
    out=HERE/("source_snapshot_secondary_CPU_attempts_repair_"+str(time.time_ns()));out.mkdir(exist_ok=False)
    reports=[json.loads(p.read_text(encoding="utf8")) for p in REPORTS];records=[]
    try:
        for row in reports[0]["source"]:
            name=Path(row["path"]).name
            path=PRIOR/name if (PRIOR/name).exists() else HERE/name
            if name=="test_reference_contract_cpu_v1.py":path=HERE/"test_reference_contract_cpu_before_phase_V3_preserved.py"
            s=path.read_bytes().decode("utf8")
            expected={next(x["SHA256"] for x in r["source"] if Path(x["path"]).name==name) for r in reports}
            if name=="supermimic_reference_adapter_v1.py":
                s=s.replace("from dataclasses import asdict, dataclass\n","from dataclasses import dataclass\n",1)
                start=s.index("    def contract_manifest(self):\n");end=s.index("\n\ndef read_json_reference",start);s=s[:start]+s[end:]
                s=s.replace("        self.first_time_s=float(reference.times_s[0]);self.last_time_s=float(reference.times_s[-1])\n","",1)
                s=s.replace('        if frames.is_floating_point():\n            require(bool(torch.isfinite(frames).all()),"non-finite frame query")\n',
                            '        require(bool(torch.isfinite(frames).all()),"non-finite frame query")\n',1)
                s=s.replace('.clamp(self.first_time_s,self.last_time_s)\n','.clamp(float(self.times[0]),float(self.times[-1]))\n',1)
                # Preserve original exact bytes; do not accept a semantic-only match.
                matches=[]
                for blank_count in range(2,7):
                    candidate=re.sub(r"\n+def read_json_reference",lambda _:"\n"*blank_count+"def read_json_reference",s,count=1)
                    if {hashlib.sha256(candidate.encode("utf8")).hexdigest()}==expected:matches.append(candidate)
                assert len(matches)==1,"exact original recorded source not recovered";s=matches[0]
            elif name=="own_usd_closed_chain_ik_v1.py":
                s=s.replace('                  closed_chain_IK="static_all_exported_frames_fit_dynamic_feasibility_pending",\n','',1)
                block='''                  source_contact_reference=dict(time_s=t.tolist(),left_right_contact=taskspace.wheel_contact.tolist(),
                                                phase=list(taskspace.contact_phase),
                                                used_for="phase_metadata_and_own_rolling_reference_only_not_applied_physical_gate"),
'''
                assert s.count(block)==1;s=s.replace(block,"",1)
            raw=s.encode("utf8");sha=hashlib.sha256(raw).hexdigest();assert expected=={sha},(name,"source SHA mismatch")
            with (out/name).open("xb") as stream:stream.write(raw)
            records.append(dict(path=str(out/name),SHA256=sha,bytes=len(raw),recovery_input=str(path)))
        report=dict(status="PASS_EXACT_ORIGINAL_SOURCE_SHA_PRESERVED",records=records,original_reports=[str(p) for p in REPORTS],
            no_experiment_rerun=True,prior_reader_failures_preserved=True,
            prior_reader_failure_notes=["V1 original-SHA assertion rejected a reconstruction with extra blank line; mismatched source not admitted",
                                        "Follow-up shell one-line quote SyntaxError occurred during diagnosis; no experiment executed"],
            git_archive_state="pending_root_stage_archive")
        with (out/"SOURCE_PRESERVATION_REPAIR_RECEIPT.json").open("x",encoding="utf8") as stream:json.dump(report,stream,indent=2)
        print(json.dumps(dict(out=str(out),status=report["status"],files=len(records))))
    except BaseException:
        with (out/"SOURCE_PRESERVATION_REPAIR_ORIGINAL_ERROR.json").open("x",encoding="utf8") as stream:json.dump(dict(error=traceback.format_exc(),git_archive_state="pending_root_stage_archive"),stream,indent=2)
        raise


if __name__=="__main__":main()
