from pathlib import Path
import ast,copy,hashlib,json,os,shutil,time
N=Path(__file__).resolve().parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf8')
def main():
 prep=json.loads((R/'TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json').read_bytes());actual=json.loads((N.parent/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029/reports/TWO106_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').read_bytes())
 for mode,spec in prep['payloads'].items():
  A=Path(spec['payload']);B=N/'payloads_v2'/mode;B.mkdir(parents=True);m=json.loads((A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
  for row in m['files']:
   src=A/row['relative'];dst=B/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
   else:shutil.copy2(src,dst)
  value=actual['results'][mode];raw=json.dumps(value['value'],indent=2,allow_nan=False).encode();proof=json.dumps(value['proof'],indent=2,allow_nan=False).encode();assert hashlib.sha256(raw).hexdigest()==value['proof']['report_SHA'] and hashlib.sha256(proof).hexdigest()==value['proof_SHA']
  (B/'source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json').write_bytes(raw);(B/'source/ORIGINAL106_CPU_WAITED_PROOF_ACTUAL.json').write_bytes(proof)
  for row in m['files']:
   if row['relative'] in ('source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json','source/ORIGINAL106_CPU_WAITED_PROOF_ACTUAL.json'):p=B/row['relative'];row.update(bytes=p.stat().st_size,SHA=H(p))
  write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2));spec.update(payload=str(B),job_root=spec['job_root'].replace('2610v107/','2610v107CPUv2/'),manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
 with (R/'TWO107_COHERENT20S_SEALED_PAYLOADS_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(prep,f,indent=2)
 s=(N/'install_TWO107_exact_producer_frame_metadata_extension_CPU_UNUSED_once.py').read_text('utf8').replace('TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json','TWO107_COHERENT20S_SEALED_PAYLOADS_V2_ACTUAL.json').replace('NATIVE107_V3_','NATIVE107_V4_').replace('TWO107_V3_ACTUAL','TWO107_V4_ACTUAL').replace('TWO107_INSTALL_V2','TWO107_INSTALL_V4').replace('TWO107_SOURCE_INSTALL_V2','TWO107_SOURCE_INSTALL_V4');ast.parse(s);write(N/'install_TWO107_CPUv2_exact_original_JSON_bytes_metadata_extension_UNUSED_once.py',s)
 s=(N/'prepare_TWO107_actual_CPU_original_writer_and_readers_SOURCE_ONLY_once.py').read_text('utf8').replace('TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json','TWO107_COHERENT20S_SEALED_PAYLOADS_V2_ACTUAL.json').replace('TWO107_V3_ACTUAL','TWO107_V4_ACTUAL').replace('NATIVE107_V3','NATIVE107_V4').replace("N/'payloads/","N/'payloads_v2/")
 write(N/'prepare_TWO107_CPUv2_actual_original_writer_and_readers_SOURCE_ONLY_once.py',s)
 with (R/'FROZEN_UNUSED107_CPUv2_REPORT_BYTES_AND_INSTALLER_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),frozen=True,original_CPUv1_false_preserved=True,original_report_bytes_are_exact=True,original_error='Windows text writer emitted CRLF rather than original Linux LF; changed only evidence byte writing before newnamespace',zero_model_loads_this_extension=True,entry_SHA=H(N/'install_TWO107_CPUv2_exact_original_JSON_bytes_metadata_extension_UNUSED_once.py')),f,indent=2)
 print(json.dumps(dict(prepared=True,exact_original_evidence_bytes=True,new_remote_namespace=True)))
if __name__=='__main__':main()
