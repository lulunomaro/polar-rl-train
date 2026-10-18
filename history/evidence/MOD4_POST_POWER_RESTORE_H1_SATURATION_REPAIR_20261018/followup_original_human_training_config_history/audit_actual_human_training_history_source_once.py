"""Read original chat user turns, separating synthetic heartbeat and assistant questions."""
from pathlib import Path
import json,re,time,sys,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;sys.path.insert(0,str(W/'polar-rl-train/archive_tools'))
from capture_history import redact
SOURCES=[Path('C:/Users/lulu/.codex/sessions/2026/09/07/rollout-2026-09-07T12-43-21-01a07a2d-9036-7531-a012-692df9f56353.jsonl'),Path('C:/Users/lulu/.codex/sessions/2026/10/15/rollout-2026-10-15T21-33-55-01a07a2d-9036-7531-a012-692df9f56353_01a13fc4-f5ba-7c52-8bb5-301275e18a75.jsonl')]
PAT=re.compile(r'FP32|FP64|float32|float64|混合精度|单精度|双精度|20000|20[kK]|60928|1e-4|0\.0001|STD|学习率|参数|330|预算|小时|开训|继续训练|确认|批准|恢复|reward|PPO|训练',re.I)

def main():
 rows=[];seen=set();statistics=[]
 for path in SOURCES:
  count=hb=human=bad=0
  with path.open('rb') as f:
   for number,raw in enumerate(f,1):
    # Event user_message avoids duplicating the same text in response_item snapshots.
    if b'"user_message"' not in raw:continue
    try:j=json.loads(raw)
    except (json.JSONDecodeError,UnicodeDecodeError):bad+=1;continue
    p=j.get('payload',{})
    if j.get('type')!='event_msg' or p.get('type')!='user_message':continue
    count+=1;text=p.get('message','')
    if not isinstance(text,str):continue
    t=text.strip()
    if t.startswith('<heartbeat>'):hb+=1;continue
    if t.startswith(('<environment_context>','# AGENTS.md','<permissions instructions>')):continue
    question=None
    if t.startswith('<send_user_message_question_reply>'):
     body=t.split('>',1)[1].rsplit('</send_user_message_question_reply>',1)[0].strip()
     try:replies=json.loads(body)
     except json.JSONDecodeError:continue
     text='\n'.join(x.get('answer','') for x in replies);question='\n'.join(x.get('question','') for x in replies)
    key=(j.get('timestamp'),text)
    if key in seen:continue
    seen.add(key);human+=1
    if not PAT.search(text):continue
    safe,n=redact(text);q,qn=redact(question) if question else (None,0)
    matches=list(PAT.finditer(text));excerpts=[]
    for m in matches[:12]:
     a=max(0,m.start()-100);z=min(len(safe),m.end()+240);frag=safe[a:z]
     if not any(frag in x for x in excerpts):excerpts.append(frag)
    rows.append(dict(timestamp=j.get('timestamp'),source_path=str(path),source_line=number,source_kind='original_event_user_message',actual_human_answer_only=safe,assistant_question_context_not_user_instruction=q,original_user_text_SHA=hashlib.sha256(text.encode()).hexdigest(),redaction_count=n,question_redaction_count=qn,excerpts=excerpts))
  statistics.append(dict(path=str(path),bytes=path.stat().st_size,event_user_messages=count,synthetic_heartbeats_excluded=hb,actual_human_unique=human,parse_errors=bad))
 out=dict(epoch=time.time(),actual_original_chat_scan=True,sources=statistics,rows=rows,synthetic_heartbeat_not_human_authorization=True,assistant_questions_separated_from_actual_answers=True,credentials_redacted_in_capture_only=True,no_host_GPU_or_budget_changes=True)
 p=R/'ACTUAL_ORIGINAL_HUMAN_TRAINING_PARAMETERS_AND_AUTH_HISTORY_CAPTURE_ACTUAL.json'
 with p.open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(statistics=statistics,matched_human_turns=len(rows),precision_turns=[dict(timestamp=r['timestamp'],line=r['source_line'],text=r['actual_human_answer_only'][:4000]) for r in rows if re.search(r'FP32|FP64|float32|float64|混合精度|单精度|双精度',r['actual_human_answer_only'],re.I)],last_human_turns=[dict(timestamp=r['timestamp'],line=r['source_line'],text=r['actual_human_answer_only'][:1700]) for r in rows[-24:]]),ensure_ascii=False))

if __name__=='__main__':main()
