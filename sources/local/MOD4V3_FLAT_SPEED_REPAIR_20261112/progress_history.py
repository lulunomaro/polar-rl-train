from pathlib import Path
import json,time
T=Path(__file__).resolve().parent;J=T/'training_round';E=T/'evidence';seen=set()
for name in ('FIRST_UPDATE.json','LATEST_PROGRESS.json'):
 p=J/name
 if p.exists():
  d=json.loads(p.read_text());seen.add(d['iteration'])
  with (E/'TRAINING_PROGRESS_HISTORY.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(d,ensure_ascii=False)+'\n')
while not (J/'SAFE_CLOSED.json').exists():
 try:
  d=json.loads((J/'LATEST_PROGRESS.json').read_text())
  if d['iteration'] not in seen:
   with (E/'TRAINING_PROGRESS_HISTORY.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(d,ensure_ascii=False)+'\n')
   seen.add(d['iteration'])
 except (FileNotFoundError,json.JSONDecodeError):pass
 time.sleep(3)
