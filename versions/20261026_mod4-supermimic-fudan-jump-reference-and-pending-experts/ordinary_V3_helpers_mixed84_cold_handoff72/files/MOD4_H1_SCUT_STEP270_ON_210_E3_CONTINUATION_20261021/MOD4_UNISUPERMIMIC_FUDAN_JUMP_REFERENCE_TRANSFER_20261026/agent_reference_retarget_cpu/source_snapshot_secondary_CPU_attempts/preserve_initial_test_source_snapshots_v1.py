"""Preserve source bytes of initial CPU attempts and subsequent source-only revision.

The first two reports contain source SHA256s. This script reconstructs only the
four small importer/clock-interface edits made immediately after those tests,
then checks the original recorded SHA before saving. No experiment is rerun.
"""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent
REPORTS=[HERE/"CPU_REFERENCE_CONTRACT_1793003750623298400.json",HERE/"CPU_REFERENCE_CONTRACT_1793003750657793300.json"]
FILES=("supermimic_reference_adapter_v1.py","own_usd_closed_chain_ik_v1.py","test_reference_contract_cpu_v1.py")

def main():
    before=HERE/"source_snapshot_before_partial_imitation_objective";before.mkdir(exist_ok=False)
    attempt=HERE/"source_snapshot_initial_CPU_attempts";attempt.mkdir(exist_ok=False)
    reports=[json.loads(p.read_text(encoding="utf8")) for p in REPORTS]
    records=[]
    for name in FILES:
        data=(HERE/name).read_bytes()
        with (before/name).open("xb") as stream:stream.write(data)
        original=data.decode("utf8")
        if name=="supermimic_reference_adapter_v1.py":
            blocks=[
'''    require(Path(producer_receipt.get("artifact_path","")).resolve()==Path(npz_path).resolve(),
            "capture path differs from the explicitly authorized receipt")
    sha=producer_receipt.get("artifact_sha256","")
    require(isinstance(sha,str) and len(sha)==64 and all(c in "0123456789abcdef" for c in sha),"verified artifact SHA256 required in receipt")
''',
'''    require(t.ndim==1 and len(t)>=2 and np.isfinite(t).all() and (np.diff(t)>0).all(),"capture needs finite increasing measured sample times")
''',
'''        dt=metadata.get("target_control_dt_s")
        require(isinstance(dt,(int,float)) and np.isfinite(dt) and dt>0,"explicit positive target control clock required")
''',
'''    def align_control_clock(self,*,native_frame_anchor,reference_time_anchor_s):
        """Explicit reviewed phase alignment; no reading of future plant gates/actions."""
        require(np.isfinite(native_frame_anchor) and np.isfinite(reference_time_anchor_s),"finite reference clock anchors required")
        require(self.times_s[0]<=reference_time_anchor_s<=self.times_s[-1],"reference clock anchor outside clip")
        offset=float(reference_time_anchor_s)-float(native_frame_anchor)*float(self.metadata["target_control_dt_s"])
        meta=dict(self.metadata,native_frame_zero_reference_time_s=offset,
                  clock_alignment=dict(native_frame_anchor=float(native_frame_anchor),reference_time_anchor_s=float(reference_time_anchor_s),
                                       uses_future_actions_or_gate_choices=False))
        return NativeReference(self.times_s,self.states,self.joint_names,meta,allow_fixture=self.allow_fixture)

''']
            for block in blocks:
                assert original.count(block)==1,"source-only revision block mismatch"
                original=original.replace(block,"",1)
        raw=original.encode("utf8");sha=hashlib.sha256(raw).hexdigest()
        expected=[next(row["SHA256"] for row in r["source"] if Path(row["path"]).name==name) for r in reports]
        assert set(expected)=={sha},(name,"original test-source SHA mismatch")
        with (attempt/name).open("xb") as stream:stream.write(raw)
        records.append(dict(name=name,original_test_source_SHA256=sha,
                            preserved_original_path=str(attempt/name),
                            next_source_only_revision_path=str(before/name),
                            next_source_only_revision_SHA256=hashlib.sha256(data).hexdigest()))
    path=HERE/("INITIAL_CPU_SOURCE_PRESERVATION_"+str(time.time_ns())+".json")
    with path.open("x",encoding="utf8") as stream:json.dump(dict(records=records,original_reports=[str(p) for p in REPORTS],
        exact_original_recorded_source_SHA_verified=True,no_experiment_rerun=True,git_archive_state="pending_root_stage_archive"),stream,indent=2)
    print(path)

if __name__=="__main__":main()
