from pathlib import Path
import ast,copy,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';R.mkdir(exist_ok=True)
old=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/budget_eighth_contract.py';s=old.read_text('utf8')
changes={'eighth':'ninth','Eighth':'Ninth','USER_ADD100H_20261021_8TH':'USER_ADD200H_20261024_9TH','ADDED_SECONDS = 360000':'ADDED_SECONDS = 720000','BEFORE_TOTAL = 1188000':'BEFORE_TOTAL = 1548000','AFTER_TOTAL = 1548000':'AFTER_TOTAL = 2268000',"!= 7:":"!= 8:",'Original seven extension records':'Original eight extension records'}
pat=re.compile('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)));s=pat.sub(lambda m:changes[m[0]],s)
s=re.sub(r"after\['budget_scope'\] = .*", "after['budget_scope'] = 'Original10h plus eight historical applied extensions plus ninth200h; actual charged learning time; no automatic addition'",s);ast.parse(s)
dest=B/'budget_ninth_contract.py';assert not dest.exists();dest.write_text(s,'utf8')
p=json.loads((R/'ORIGINAL_BUDGET_NINTH_BEFORE_ACTUAL.json').read_bytes())['source210'];assert p['authorized']==1548000 and len(p['extension_records'])==8 and p['active_segment'] is None
a=dict(approved=True,authorization_basis='direct_human_user_message',human_message='预算增加200小时',extension_id='USER_ADD200H_20261024_9TH',added_seconds=720000,recorded_epoch=time.time(),historical_master_sha256=p['historical_master_SHA'],central_approval_path='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/USER_ADD200H_20261024_9TH_APPROVAL.json',no_new_training_scope=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068)
with (R/'DIRECT_HUMAN_APPROVAL.json').open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
ns={};exec(compile(s,str(dest),'exec'),ns);c=dict(authorized_training_seconds=p['authorized'],charged_training_seconds=p['charged'],remaining_training_seconds=p['remaining'],budget_extensions=p['extension_records'],active_segment=None,completed_segments=[dict(run_id='CPU_HISTORY_FIXTURE',charged_seconds=3.25)],unrelated=dict(immutable=True));rows=[]
def test(name,b,ap,expected):
 before=copy.deepcopy(b)
 try:out=ns['extend_once'](b,ap,time.time(),'CPU_RECEIPT');passed=True
 except (ValueError,KeyError):out=None;passed=False
 assert b==before and passed==expected
 if passed:assert out['charged_training_seconds']==b['charged_training_seconds'] and out['completed_segments']==b['completed_segments'] and out['budget_extensions'][:-1]==b['budget_extensions'] and abs(out['remaining_training_seconds']-b['remaining_training_seconds']-720000)<1e-8 and out['unrelated']==b['unrelated']
 rows.append(dict(name=name,passed=True,admitted=passed));return out
new=test('actual8to9_preserve_history_add720000',c,a,True);test('duplicate_rejected',new,a,False)
x=copy.deepcopy(c);x['active_segment']={'id':'active'};test('active_rejected',x,a,False)
x=copy.deepcopy(c);x['authorized_training_seconds']+=1;test('unregistered_total_rejected',x,a,False)
x=copy.deepcopy(c);x['budget_extensions'][0]['extension_id']=x['budget_extensions'][1]['extension_id'];test('duplicate_history_rejected',x,a,False)
x=copy.deepcopy(c);x['budget_extensions'][0]['state']='pending';test('unapplied_history_rejected',x,a,False)
x=copy.deepcopy(c);x['charged_training_seconds']=float('nan');test('nonfinite_rejected',x,a,False)
test('wrong_amount_rejected',c,dict(a,added_seconds=360000),False);test('missing_approval_rejected',c,dict(a,approved=False),False)
with (R/'NINTH_EXTENSION_CONTRACT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,cases=rows,source_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),expected_total=2268000,expected_extensions=9,expected_remaining_snapshot=new['remaining_training_seconds'],no_remote_mutation=True),f,indent=2)
print(json.dumps(dict(passed=True,cases=len(rows),expected_total=2268000,expected_remaining=new['remaining_training_seconds'])))
