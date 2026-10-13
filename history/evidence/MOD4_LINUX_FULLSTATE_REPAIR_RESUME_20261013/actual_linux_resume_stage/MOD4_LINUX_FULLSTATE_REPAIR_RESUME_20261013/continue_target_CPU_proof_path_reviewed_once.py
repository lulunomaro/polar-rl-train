"""Continue only the unexecuted CPU proof/plan after upload path rejection."""
from pathlib import Path
import ast,hashlib,inspect,json,time
import upload_v2_and_verify_target_cpu_once as original
D=Path(__file__).resolve().parent
def main():
    proof=D/'port_cpu/actual_CPU_17b_20000_v2_metadata_anchor/LINUX20000_PORT_CPU_ACTUAL_REVIEW.json'
    assert proof.is_file()
    (D/'reports/ORIGINAL_TARGET_CPU_PROOF_PATH_REJECTION_PRESERVED.json').write_text(json.dumps(dict(epoch=time.time(),error='FileNotFoundError for actual_CPU_17b_20000_v2; real directory actual_CPU_17b_20000_v2_metadata_anchor',payload_upload_completed=True,CPU_plan_and_probe_not_executed=True,no_GPU_or_budget=True,original_source=str(Path(original.__file__))),indent=2))
    text=inspect.getsource(original.main)
    text=text.replace("sf.mkdir(S+'/payload_v2')", "assert sf.stat(S+'/payload_v2')")
    text=text.replace("for p in P.iterdir():sf.put(str(p),S+'/payload_v2/'+p.name)", "for p in P.iterdir():\n            with sf.file(S+'/payload_v2/'+p.name, 'rb') as remote:\n                assert hashlib.sha256(remote.read()).hexdigest()==hashlib.sha256(p.read_bytes()).hexdigest()")
    text=text.replace('actual_CPU_17b_20000_v2/LINUX20000_PORT_CPU_ACTUAL_REVIEW.json','actual_CPU_17b_20000_v2_metadata_anchor/LINUX20000_PORT_CPU_ACTUAL_REVIEW.json')
    ns=dict(vars(original));exec(compile(text,str(__file__)+'#independent-unexecuted-CPU-continuation','exec'),ns);ns['main']()
if __name__=='__main__':main()
