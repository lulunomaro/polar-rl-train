"""Read original assistant conversation context, separate from human directives."""
from pathlib import Path
import sys,json,re,time,hashlib
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B.parent/'polar-rl-train/archive_tools'))
from capture_history import redact
SOURCES=[(Path('C:/Users/lulu/.codex/sessions/2026/09/07/rollout-2026-09-07T12-43-21-01a07a2d-9036-7531-a012-692df9f56353.jsonl'),[(38700,39000),(85900,86600),(136300,136700)]),(Path('C:/Users/lulu/.codex/sessions/2026/10/15/rollout-2026-10-15T21-33-55-01a07a2d-9036-7531-a012-692df9f56353_01a13fc4-f5ba-7c52-8bb5-301275e18a75.jsonl'),[(21300,21500),(23000,25000)])]
PAT=re.compile(r'FP32|FP64|float32|float64|双精度|单精度|num_envs|20000|20k|学习率|1e-4|0\.0001|2ms|2mm|参数|TGS|STD|1800|参考',re.I)
def main():
 rows=[]
 for path,ranges in SOURCES:
  with path.open('rb') as f:
   for ln,raw in enumerate(f,1):
    if not any(a<=ln<=z for a,z in ranges):continue
    if b'"assistant"' not in raw or b'"message"' not in raw:continue
    j=json.loads(raw);p=j.get('payload',{})
    if j.get('type')!='response_item' or p.get('type')!='message' or p.get('role')!='assistant' or p.get('channel') not in ('final','commentary'):continue
    txt='\n'.join(x.get('text','') for x in p.get('content',[]) if x.get('type') in ('output_text','text'))
    if not PAT.search(txt):continue
    safe,n=redact(txt)
    rows.append(dict(timestamp=j.get('timestamp'),source_path=str(path),source_line=ln,channel=p.get('channel'),original_text_SHA=hashlib.sha256(txt.encode()).hexdigest(),redactions=n,assistant_text_not_human_instruction=safe))
 out=dict(epoch=time.time(),rows=rows,reference_only_not_human_approval=True,original_chat_read_no_host_or_GPU=True,local_retrieval_errors_retained=['read_thread turnLimit12 rejected actual max10, then turnLimit10 worked','V1 event_msg/user_message empty; actual user messages are response_item role=user','broad recursive source rg produced truncated output; precise selected files used subsequently'])
 with (B/'reports/ORIGINAL_ASSISTANT_TRAINING_CONFIG_AND_AUDIT_REFERENCE_CONTEXT_V3_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
 print(json.dumps([dict(timestamp=r['timestamp'],line=r['source_line'],text=r['assistant_text_not_human_instruction'][:3500]) for r in rows],ensure_ascii=False))
if __name__=='__main__':main()
