"""Exact completed-newsource GPU-fullrestore metadata bytes, not relabelled old CPU proof."""
from pathlib import Path
import json,hashlib
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE';assert not D.exists();d=json.loads((R/'reports/W35_postadapt_eval_dispatch_20261102_031914.json').read_bytes());job=d['new_job'];c=connect72();s=c.open_sftp()
try:
 blobs={}
 for rel in ('PARENT_EXIT_SCOPE.json','FINAL.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json'):
  with s.open(job+'/'+rel,'rb')as f:blobs[rel]=f.read()
finally:s.close();c.close()
end=json.loads(blobs['PARENT_EXIT_SCOPE.json']);final=json.loads(blobs['FINAL.json']);proof=json.loads(blobs['actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json']);assert end['all_own_children_waited'] and end['owned_private_validation_locks_released'] and end['error']is None and final['passed_execution'] and final['bounded32s_complete'] and final['optimizer_updates']==0 and proof['passed'] and proof['source_SHA']==d['new_source_model']['SHA'] and proof['iteration']==32561 and proof['Adam17']==652860 and proof['actual_LR']==.00011390625000000006 and proof['actor_critic_STD_optimizer_verified']
D.mkdir();rows=[]
for rel,raw in blobs.items():
 p=D/Path(rel).name;p.write_bytes(raw);rows.append({'source_path':job+'/'+rel,'local_path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
v={'kind':'EXACT89ACA_EXISTING_GPU_FULLRESTORE_CERTIFICATE_NOT_CPU_PROOF','source':d['new_source_model'],'source_actual_LR':proof['actual_LR'],'rows':rows,'restore_proof_SHA':hashlib.sha256(blobs['actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json']).hexdigest(),'PT_opens':0,'SDK_or_canonical_access':False,'evidence_scope':'ExistingactualGPU20kfullstate+native24+full32 core/STD17Adamexact +savedLR, notnewCPUdecode orRM70graduation'};(D/'CERTIFICATE_INDEX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
