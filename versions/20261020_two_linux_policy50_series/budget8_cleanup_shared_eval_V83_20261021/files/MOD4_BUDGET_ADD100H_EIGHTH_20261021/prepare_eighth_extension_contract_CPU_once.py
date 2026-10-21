from pathlib import Path
import ast,copy,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
old=W/'MOD4_BUDGET_RETRAIN_100H_20261011/budget_retrain_contract.py'
s=old.read_text('utf8').replace('seventh','eighth').replace('Seventh','Eighth').replace('USER_ADD100H_20261011_7TH','USER_ADD100H_20261021_8TH').replace('BEFORE_TOTAL = 828000','BEFORE_TOTAL = 1188000').replace('AFTER_TOTAL = 1188000','AFTER_TOTAL = 1548000').replace("!= 6:","!= 7:").replace('Original six extension records','Original seven extension records').replace('seventh100h;','seventh100h + eighth100h;')
ast.parse(s)
with (B/'budget_eighth_contract.py').open('x',encoding='utf8') as f:f.write(s)
p=json.loads((R/'ORIGINAL_BUDGET_EIGHTH_BEFORE_ACTUAL.json').read_bytes());assert p['authorized']==1188000 and len(p['extension_records'])==7 and p['active_segment'] is None
a=dict(approved=True,authorization_basis='direct_human_user_message',human_message='余额增加100小时',extension_id='USER_ADD100H_20261021_8TH',added_seconds=360000,recorded_epoch=time.time(),historical_master_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',central_approval_path='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/USER_ADD100H_20261021_8TH_APPROVAL.json',no_new_training_scope=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068)
with (R/'DIRECT_HUMAN_APPROVAL.json').open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
ns={};exec(compile(s,str(B/'budget_eighth_contract.py'),'exec'),ns)
c=dict(authorized_training_seconds=p['authorized'],charged_training_seconds=p['charged'],remaining_training_seconds=p['remaining'],budget_extensions=p['extension_records'],active_segment=None,completed_segments=[dict(run_id='CPU_HISTORY_PRESERVATION_FIXTURE',charged_seconds=3.25)],unrelated=dict(immutable=True))
rows=[]
def test(name,b,ap,expected):
 before=copy.deepcopy(b)
 try:out=ns['extend_once'](b,ap,time.time(),'CPU_RECEIPT');passed=True
 except (ValueError,KeyError):out=None;passed=False
 assert b==before and passed==expected
 if passed:assert out['charged_training_seconds']==b['charged_training_seconds'] and out['completed_segments']==b['completed_segments'] and out['budget_extensions'][:-1]==b['budget_extensions'] and out['remaining_training_seconds']-b['remaining_training_seconds']==360000 and out['unrelated']==b['unrelated']
 rows.append(dict(name=name,passed=True,admitted=passed));return out
new=test('actual_7_to_8_preserve_charge_history_and_add_360000',c,a,True)
test('duplicate_rejected',new,a,False)
x=copy.deepcopy(c);x['active_segment']={'id':'active'};test('active_segment_rejected',x,a,False)
x=copy.deepcopy(c);x['authorized_training_seconds']+=1;test('unregistered_total_rejected',x,a,False)
x=copy.deepcopy(c);x['budget_extensions'][0]['extension_id']=x['budget_extensions'][1]['extension_id'];test('duplicate_history_id_rejected',x,a,False)
x=copy.deepcopy(c);x['budget_extensions'][0]['state']='pending';test('unapplied_history_rejected',x,a,False)
x=copy.deepcopy(c);x['charged_training_seconds']=float('nan');test('nonfinite_charge_rejected',x,a,False)
x=dict(a,added_seconds=720000);test('scope_amount_mismatch_rejected',c,x,False)
x=dict(a,approved=False);test('missing_approval_rejected',c,x,False)
with (R/'EIGHTH_EXTENSION_CONTRACT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,cases=rows,source_SHA=hashlib.sha256(s.encode()).hexdigest(),expected_total=1548000,expected_extensions=8,remaining_before_snapshot=p['remaining'],remaining_after_expected_snapshot=new['remaining_training_seconds'],no_remote_mutation=True),f,indent=2)
print(json.dumps(dict(passed=True,cases=len(rows),expected_total=1548000,expected_remaining=new['remaining_training_seconds'])))
