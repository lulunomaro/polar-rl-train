"""V3 used channel; desktop rollouts actually store message phase. Preserve V3."""
import audit_original_assistant_config_context_v3_once as a
def main():
 rows=[]
 for path,ranges in a.SOURCES:
  with path.open('rb') as f:
   for ln,raw in enumerate(f,1):
    if not any(lo<=ln<=hi for lo,hi in ranges) or b'"assistant"' not in raw:continue
    j=a.json.loads(raw);p=j.get('payload',{})
    if j.get('type')!='response_item' or p.get('type')!='message' or p.get('role')!='assistant':continue
    txt='\n'.join(x.get('text','') for x in p.get('content',[]) if x.get('type') in ('output_text','text'))
    if not a.PAT.search(txt):continue
    safe,n=a.redact(txt)
    rows.append(dict(timestamp=j.get('timestamp'),source_path=str(path),source_line=ln,phase=p.get('phase'),original_text_SHA=a.hashlib.sha256(txt.encode()).hexdigest(),redactions=n,assistant_text_not_human_instruction=safe))
 out=dict(epoch=a.time.time(),rows=rows,assistant_not_human_authorization=True,original_V3_empty_channel_lookup_preserved=True,no_host_GPU_budget_changes=True)
 with (a.B/'reports/ORIGINAL_ASSISTANT_TRAINING_CONFIG_AND_AUDIT_REFERENCE_CONTEXT_V4_ACTUAL.json').open('x',encoding='utf8') as f:a.json.dump(out,f,ensure_ascii=False,indent=2)
 print(a.json.dumps([dict(timestamp=r['timestamp'],line=r['source_line'],text=r['assistant_text_not_human_instruction'][:3000]) for r in rows],ensure_ascii=False))
if __name__=='__main__':main()
