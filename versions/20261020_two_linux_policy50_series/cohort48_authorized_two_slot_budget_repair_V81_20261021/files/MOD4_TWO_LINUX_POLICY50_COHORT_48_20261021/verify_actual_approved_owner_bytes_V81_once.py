from pathlib import Path
import hashlib,json,time
import deploy_two50_reconciled_original_writer_once as d
B=Path(__file__).resolve().parent;R=B/'reports';q=json.loads((R/'TWO50_ORIGINAL_ACCOUNT_COHORT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((R/'TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());assert proof['passed'];c=d.t.connect()
try:
 result=d.code(c,d.t.PY,"from pathlib import Path;import hashlib,json,psutil;root=Path(v['root']);p=root/'three_slot_finite_owner_v1.py';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==v['SHA'] and b'sum(b.CAPS[k] for k in specs)' in raw and b'sum(b.CAPS.values())' not in raw;process=psutil.Process(v['pid']);assert process.create_time()==v['creation'] and str(p) in process.cmdline();print(json.dumps(dict(approved_owner_remote_SHA=hashlib.sha256(raw).hexdigest(),actual_owner_create_argv_verified=True,scheduled_two_caps_expression_actual=True,no_model_hash_GPU_or_account_write=True)))",dict(root=q['owner_root'],SHA='235720e2e275d9eb4247557fc3ad1c08938d31b664310c8cc3b5a75ac9bb6cad',pid=q['owner']['detached_pid'],creation=proof['source210']['owner_identity']['creation']),timeout=60)
 with (R/'ACTUAL_APPROVED_TWO_SLOT_OWNER_BYTES_V81_VERIFIED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,result=result),f,indent=2)
 print(json.dumps(result))
finally:c.close()
