"""Read only the human-selected DSH session; never credentials/config files."""
from pathlib import Path
from compression import zstd
import collections,json,re,time
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True)
P=Path('C:/Users/lulu/.dsh/sessions/--F-RMPOLAR-RL--/session-5ee9dc9d-5a3d-49a8-ae31-5c022b269a22/session.v4.jsonl.zstd')
before=P.stat();counts=collections.Counter();schemas={};selected=[];header=None
deny=re.compile(r'password|passwd|api.?key|secret|credential|authorization|bearer|\btoken\b|凭据|密码|os\.environ|sk-[A-Za-z0-9]',re.I)
relevant=re.compile(r'LQR|MPC|270|台阶|10\.24\.0\.72|分支|[Gg]it|SuperMimic|交付')
def texts(v):
 if isinstance(v,str):return v
 if isinstance(v,list):return '\n'.join(texts(x)for x in v if isinstance(x,str)or isinstance(x,dict)and x.get('type')in('text','output_text','input_text'))
 if isinstance(v,dict):
  for key in('text','content'):
   if key in v:return texts(v[key])
 return ''
def messages(v):
 if isinstance(v,dict):
  if v.get('role')in('assistant','user'):
   value=texts(v.get('content',v.get('text','')))
   if value:yield v['role'],value
  for key,value in v.items():
   if key not in('tool_calls','arguments','outputs','output')and isinstance(value,(dict,list)):yield from messages(value)
 elif isinstance(v,list):
  for value in v:
   if isinstance(value,(dict,list)):yield from messages(value)
with zstd.open(P,'rt',encoding='utf8')as f:
 for lineno,line in enumerate(f,1):
  j=json.loads(line);kind=j.get('type','UNKNOWN');counts[kind]+=1
  if kind=='session':header={k:j.get(k)for k in('id','createdAt','cwd','version')}
  if kind not in schemas:schemas[kind]=dict(keys=list(j),data_keys=list(j['data'])if isinstance(j.get('data'),dict)else None)
  for role,value in messages(j):
   clean='\n'.join(s for s in value.splitlines()if not deny.search(s))
   if relevant.search(clean):selected.append(dict(seq=j.get('seq'),time=j.get('time'),line=lineno,role=role,text=clean))
after=P.stat();assist=[x for x in selected if x['role']=='assistant'];users=[x for x in selected if x['role']=='user']
# Keep bounded source excerpts, not raw tool transcripts or session secrets.
last=assist[-9:]+users[-5:]
for row in last:row['text']=row['text'][:4200]
result=dict(epoch=time.time(),passed=True,human_selected_session='session-5ee9dc9d-5a3d-49a8-ae31-5c022b269a22',source_path=str(P),source_bytes_before=before.st_size,source_bytes_after=after.st_size,source_changed_during_read=before.st_mtime_ns!=after.st_mtime_ns,header=header,event_counts=dict(counts),schemas=schemas,matching_assistant_messages=len(assist),matching_user_messages=len(users),bounded_sanitized_excerpts=last,tool_output_or_argument_values_saved=False,credential_config_store_reads=0,SDK_model_raw_physics_optimizer_remote_reads=0)
with(R/'ROOT278_SELECTED_DSH_SESSION_LOCAL_TEXT_LOOKUP.json').open('x',encoding='utf8')as out:json.dump(result,out,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps(dict(passed=True,header=header,event_counts=dict(counts),matching_assistant_messages=len(assist),matching_user_messages=len(users),excerpts=last),ensure_ascii=False))
