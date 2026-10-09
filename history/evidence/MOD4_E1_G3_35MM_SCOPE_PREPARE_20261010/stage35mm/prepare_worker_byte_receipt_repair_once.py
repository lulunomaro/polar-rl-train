"""Retain pre-admission LF/CRLF receipt mismatch and bind exact delivered source bytes."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode('utf8'))
assert not (R/'BYTE_RECEIPT_REPAIR_STARTED.json').exists()
save('BYTE_RECEIPT_REPAIR_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-WORKER-BYTE-RECEIPT-REPAIR-03'))
raw=(D/'eval_worker_e1_g3_package_review.py').read_bytes();ast.parse(raw.decode('utf8'))
old=json.loads((R/'G3_WORKER_EXPECTED.json').read_bytes())
assert H(raw)!=old['new_source_sha256'] and H(raw.replace(b'\r\n',b'\n'))==old['new_source_sha256']
error=json.loads((R/'G3_PACKAGE_WORKER_DEPLOY_ERROR.json').read_bytes())
assert "expected['new_source_sha256']" in error['error']
save('WORKER_BYTE_RECEIPT_REJECTION_REVIEW.json',dict(epoch=time.time(),trial_id='E1-G3-WORKER-BYTE-RECEIPT-REJECTION-02',original_expected=old,actual_delivered_source_sha256=H(raw),cause='Receipt hashed LF in-memory text, Windows saved CRLF bytes; admission rejected before process/lock/task authority.',original_error=error,no_worker_or_gpu_started_by_rejected_admission=True,source_bytes_preserved=True))
new=dict(old);new.update(epoch=time.time(),new_source_sha256=H(raw),original_LF_text_sha256=old['new_source_sha256'],exact_delivered_CRLF_source_bytes_bound=True)
save('G3_WORKER_BYTES_EXPECTED.json',new)
s=(D/'admit_e1_g3_package_review_once.py').read_text(encoding='utf8').replace('E1_G3_WORKER_EXPECTED.json','E1_G3_WORKER_BYTES_EXPECTED.json').replace('admit_e1_g3_package_review_once.py','admit_e1_g3_exact_bytes_review_once.py')
ast.parse(s);(D/'admit_e1_g3_exact_bytes_review_once.py').write_bytes(s.encode('utf8'))
s=(D/'deploy_g3_package_worker_once.py').read_text(encoding='utf8')
a=s.index("  for source,dest in ");b=s.index("   raw=source.read_bytes()",a)
s=s[:a]+"  for source,dest in [(D/'admit_e1_g3_exact_bytes_review_once.py','admit_e1_g3_exact_bytes_review_once.py'),(R/'G3_WORKER_BYTES_EXPECTED.json','E1_G3_WORKER_BYTES_EXPECTED.json')]:\n"+s[b:]
s=s.replace('admit_e1_g3_package_review_once.py','admit_e1_g3_exact_bytes_review_once.py').replace('G3_PACKAGE_WORKER_DEPLOY','G3_EXACT_BYTES_WORKER_DEPLOY')
ast.parse(s);(D/'deploy_g3_exact_bytes_worker_once.py').write_bytes(s.encode('utf8'))
print(json.dumps(dict(actual_source_sha256=H(raw),original_rejection_retained=True,no_source_mutation=True)))
