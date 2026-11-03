"""Saved raw-plan/addendum checks only. No compiler, source reparse or guessed argv."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
p=load('RAW_TU_PLAN_01.json');a=load('PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json');profiles=p['profiles'];target=profiles['target']['raw']['TargetArmAds'];nonempty=[];invalid=[];fields={}
for key,profile in profiles.items():
 if key=='target':continue
 raw=profile['raw']
 for language in ('Cads','Aads'):
  block=raw.get(language)
  if block is None:continue
  for field,value in block.get('VariousControls',{}).items():
   if value:nonempty.append(dict(profile=key,xpath=profile['xpath'],language=language,field=field,value=value,target_value=target[language]['VariousControls'].get(field),different=value!=target[language]['VariousControls'].get(field)))
for language in ('Cads','Aads'):
 block=target[language]
 fields[language]={k:v for k,v in block.items()if isinstance(v,str)}
 for key,profile in profiles.items():
  raw=target if key=='target'else profile['raw'];b=raw.get(language)
  if b is None:continue
  for field,value in b.items():
   if not isinstance(value,str)or field in ('Optim','oTime','wLevel','v6Lang','v6LangP'):continue
   allowed=('0','1')if key=='target'else('0','1','2')
   if value not in allowed:invalid.append(dict(profile=key,language=language,field=field,value=value))
r=dict(status='ADDENDUM_RAW_VALUE_PRECHECK_NO_NATIVE_INVOCATION',addendum=rec(O/'PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json'),raw_plan=rec(O/'RAW_TU_PLAN_01.json'),nonempty_group_file_text=nonempty,unsupported_numeric_values=invalid,target_checkbox_values=fields,new_native_tool_invocations=0,new_TU_compiles=0,source_XML_reparses=0)
with(O/'ADDENDUM_PRECHECK_01.json').open('x',encoding='utf-8')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(r,ensure_ascii=False,indent=2))
