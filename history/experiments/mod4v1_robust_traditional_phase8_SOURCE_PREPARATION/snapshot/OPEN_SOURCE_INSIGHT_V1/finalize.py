"""Metadata-only closure of already-read reports; no archive/model/QA execution."""
from pathlib import Path
from urllib.parse import unquote
import hashlib,json,re
D=Path(__file__).resolve().parent
names=['REPORT.md','inspect_archives.py','ARCHIVES_CENTRAL_DIRECTORY.json','finalize.py',
       'SPR/REPORT.md','SPR/SELECTED_SOURCE_MANIFEST.json','SPR/RECEIPT.json',
       'QI_Q26/REPORT.md','QI_Q26/MANIFEST.json','QI_Q26/RECEIPT.json']
rows=[];links=[]
for name in names:
 p=D/name
 if not p.is_file():raise FileNotFoundError(str(p))
 rows.append({'path':name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()})
 if name.endswith('.md'):
  text=p.read_text(encoding='utf-8')
  for dest in re.findall(r'\]\(<([^>]+)>\)',text):
   raw=unquote(dest.split('#',1)[0])
   if raw.startswith(('http://','https://')):continue
   target=Path(raw)
   if not target.is_absolute():target=p.parent/target
   links.append({'source':name,'destination':dest,'exists':target.is_file()})
missing=[v for v in links if not v['exists']]
if missing:raise RuntimeError(json.dumps(missing,ensure_ascii=True))
q=json.loads((D/'QI_Q26/MANIFEST.json').read_text(encoding='utf-8'))
receipt={'status':'COMPLETE_TWO_ZIP_SOURCE_INSIGHTS_NO_DYNAMIC_TRIALS',
 'indexed_small_files':rows,'local_report_links_checked':len(links),'missing_links':missing,
 'Qi_PDF_pages_read':q['PDF_text']['pages_read'],
 'Qi_text_actual_CRLF_bytes':q['PDF_text']['actual_UTF8_CRLF_file_bytes'],
 'Qi_text_logical_LF_bytes':q['PDF_text']['constructed_UTF8_LF_bytes'],
 'original_large_archives_rehashed':False,'archive_programs_or_MATLAB_executed':False,
 'new_robot_model_FK_physics_train_old_QA':0,'old_controller_or_scores_changed':False,
 'qualification':'source mechanisms and hypotheses only, no new 270mm or board acceptance',
 'PH8pending':True}
with (D/'RECEIPT.json').open('x',encoding='utf-8',newline='\n') as f:
 json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False)
print(json.dumps({'status':receipt['status'],'indexed_files':len(rows),'links':len(links),
 'missing':len(missing),'new_physics':0,'report_SHA':rows[0]['SHA']},ensure_ascii=True))
