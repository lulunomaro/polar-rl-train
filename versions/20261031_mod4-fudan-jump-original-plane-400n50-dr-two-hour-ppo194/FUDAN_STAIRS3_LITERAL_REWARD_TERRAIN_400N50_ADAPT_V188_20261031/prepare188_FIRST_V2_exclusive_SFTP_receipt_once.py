from pathlib import Path
import ast,json,time,hashlib,shutil
N=Path(__file__).resolve().parent
D=N/'control_v2';shutil.copytree(N/'control',D)
p=D/'stairs188_fullstate_slot_node.py';s=p.read_text(encoding='utf8').replace('FULLSTATE_REUSE_ADMISSION.json','FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json');p.write_text(s,encoding='utf8')
m=dict(files=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(D.iterdir()) if p.is_file()])
(N/'CONTROL188_V2_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
s=(N/'start188_literal_STAIRS3_single_forwarded4090_FIRST_once.py').read_text(encoding='utf8')
s=s.replace('ROOT188_FIRST_','ROOT188_FIRSTV2_').replace('start188_literal_STAIRS3_single_forwarded4090_FIRST_once','start188_literal_STAIRS3_single_forwarded4090_FIRST_V2_once')
s=s.replace("C=B/'control'","C=B/'control_v2'").replace("(B/'control').mkdir()","(B/'control_v2').mkdir()")
s=s.replace("N/'CONTROL188_MANIFEST.json'","N/'CONTROL188_V2_MANIFEST.json'")
s=s.replace("J+'/control/'","J+'/control_v2/'").replace("root=J+'/control'","root=J+'/control_v2'")
s=s.replace("N/'control/'","N/'control_v2/'").replace("N/'control'/","N/'control_v2'/")
s=s.replace('FULLSTATE_REUSE_ADMISSION.json','FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json')
s=s.replace("ADMISSION_ACTUAL_V2.json','x'","ADMISSION_ACTUAL_V2.json','wx'")
ast.parse(s);(N/'start188_literal_STAIRS3_single_forwarded4090_FIRST_V2_once.py').write_text(s,encoding='utf8')
with (N/'reports/ROOT188_FIRST_V1_SFTP_EXCLUSIVE_MODE_FAILURE_RETAINED.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_error="Paramiko SFTPFile mode='x' creates exclusive file but does not set write flag; OSError File not open for writing",before_owner_root_creation_or_GO=True,no_budget_write_or_model_read_or_update=True,old_empty_remote_receipt='FULLSTATE_REUSE_ADMISSION.json',old_control_source_retained=True,new_V2_control_namespace='control_v2',new_receipt='FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json',repair="Use exclusive writable mode wx; no policy, reward, terrain, physics or fee logic change"),f,indent=2)
