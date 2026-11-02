"""One explicit late-admitted schema erratum before snapshot seal; no tests."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1];WT=P.parents[2]
S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    assert not (P/'SEAL.json').exists(),'Phase snapshot already sealed'
    manifest=P/'manifest.json';before=manifest.read_bytes();m=json.loads(before)
    rel='reports/STATE14_SCHEMA_ERRATUM.md';source=S/rel;st=source.stat();raw=source.read_bytes()
    dest=P/'snapshot'/rel;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    backup=P/'manifest_capture_initial.json';assert not backup.exists();backup.write_bytes(before)
    entry={'path':str(source),'bytes':len(raw),'mtime_ns':st.st_mtime_ns,'mtime_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),'source_relative':rel,'selection_reason':'parent_explicit_exact_state14_erratum_before_seal','original_sha256':sha(raw),'archive_path':dest.relative_to(WT).as_posix(),'archive_sha256':sha(raw),'capture_kind':'complete_text_byte_identical','archive_bytes':len(raw),'source_encoding':'utf-8','redactions':0,'stable_during_read':source.stat().st_mtime_ns==st.st_mtime_ns}
    assert entry['stable_during_read']
    m['schema_version']=2;m['entries'].append(entry);m['summary']['selected_entries']+=1;m['summary']['copied_text_files']+=1;m['summary']['copied_text_bytes']+=len(raw)
    m['late_admission']={'path':rel,'parent_explicit_authority':'Exact C1 README delta-vs-passive-knee schema erratum only; not R04/R05 reports','capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_manifest_file':'manifest_capture_initial.json','prior_manifest_sha256':sha(before),'C1_source_and_original_manifest_unchanged':True}
    manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    q=P/'LATE_ADMISSION_STATE14.json';assert not q.exists();q.write_text(json.dumps({'attempt_id':'C1-state14-doc-schema-erratum','status':'append_only_doc_correction_not_new_math_or_robot_test','file':entry,'incorrect_old_label':'Lknee/Rknee at state14 columns4/6 and derivatives11/13','correct_meaning':'crank minus hip delta, not passive linkage knee','actuator_order':['Lhip','Lcrank','Lwheel','Rhip','Rcrank','Rwheel'],'new_test_runs':0,'source_original_C1_preserved':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'late_admission':entry,'prior_manifest_sha256':sha(before),'current_manifest_sha256':sha(manifest.read_bytes())},indent=2))
if __name__=='__main__':main()
