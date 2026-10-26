"""Preserve exact source of the second CPU pair from immutable actual-V1 snapshots.
No experiment is rerun; original reports' source hashes must match before writing.
"""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent
REPORTS=[HERE/"CPU_REFERENCE_CONTRACT_1793004103564099300.json",HERE/"CPU_REFERENCE_CONTRACT_1793004103555146100.json"]
PRIOR=HERE/"ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/source_snapshot"

def main():
    reports=[json.loads(p.read_text(encoding="utf8")) for p in REPORTS]
    out=HERE/"source_snapshot_secondary_CPU_attempts";out.mkdir(exist_ok=False);records=[]
    for row in reports[0]["source"]:
        name=Path(row["path"]).name
        path=PRIOR/name if (PRIOR/name).exists() else HERE/name
        data=path.read_bytes();s=data.decode("utf8")
        if name=="supermimic_reference_adapter_v1.py":
            s=s.replace("from dataclasses import asdict, dataclass\n","from dataclasses import dataclass\n",1)
            start=s.index("    def contract_manifest(self):\n");end=s.index("\n\ndef read_json_reference",start)
            s=s[:start]+s[end:]
            s=s.replace("        self.first_time_s=float(reference.times_s[0]);self.last_time_s=float(reference.times_s[-1])\n","",1)
            s=s.replace('        if frames.is_floating_point():\n            require(bool(torch.isfinite(frames).all()),"non-finite frame query")\n',
                        '        require(bool(torch.isfinite(frames).all()),"non-finite frame query")\n',1)
            s=s.replace('.clamp(self.first_time_s,self.last_time_s)\n','.clamp(float(self.times[0]),float(self.times[-1]))\n',1)
        elif name=="own_usd_closed_chain_ik_v1.py":
            s=s.replace('                  closed_chain_IK="static_all_exported_frames_fit_dynamic_feasibility_pending",\n','',1)
            block='''                  source_contact_reference=dict(time_s=t.tolist(),left_right_contact=taskspace.wheel_contact.tolist(),
                                                phase=list(taskspace.contact_phase),
                                                used_for="phase_metadata_and_own_rolling_reference_only_not_applied_physical_gate"),
'''
            assert s.count(block)==1;s=s.replace(block,"",1)
        raw=s.encode("utf8");sha=hashlib.sha256(raw).hexdigest()
        expected=[next(x["SHA256"] for x in r["source"] if Path(x["path"]).name==name) for r in reports]
        assert set(expected)=={sha},(name,"original recorded SHA mismatch",sha,expected)
        with (out/name).open("xb") as stream:stream.write(raw)
        records.append(dict(path=str(out/name),SHA256=sha,bytes=len(raw)))
    path=HERE/("SECONDARY_CPU_SOURCE_PRESERVATION_"+str(time.time_ns())+".json")
    with path.open("x",encoding="utf8") as stream:json.dump(dict(records=records,original_reports=[str(p) for p in REPORTS],
        original_test_source_SHA_verified=True,no_experiment_rerun=True,git_archive_state="pending_root_stage_archive"),stream,indent=2)
    print(path)

if __name__=="__main__":main()
