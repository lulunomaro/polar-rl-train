"""Prepare unused follow-up sources, without dispatch/evaluation/model or SDK activity."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent
pairs=(('dispatch_fudan_n20000_frozen_original_once.py','dispatch_fudan_timeout8_frozen_original_once.py'),('collect_fudan_n20000_frozen_original_once.py','collect_fudan_timeout8_frozen_original_once.py'))
outname='evaluate_fudan_timeout8_pi_mujoco31_lowrise_once.py'
assert all(not(D/b).exists()for a,b in pairs)and not(D/outname).exists()
sha=hashlib.sha256((D/'source_fudan_frozen_native_eval_v3_timeout8/frozen_sequence_mean.py').read_bytes()).hexdigest()
results=[]
for a,b in pairs:
 old=(D/a).read_text(encoding='utf8');new=old.replace('FDNN20000_FROZEN_','FDNTIMEOUT8_FROZEN_').replace('fdn_n20000_frozen_outer_wait.py','fdn_timeout8_frozen_outer_wait.py')
 assert new!=old
 compile(ast.parse(new),b,'exec');results.append((b,new))
a='evaluate_fudan_pi_mujoco31_lowrise_once.py';old=(D/a).read_text(encoding='utf8');new=old.replace('source_fudan_frozen_native_eval_v2_n20000','source_fudan_frozen_native_eval_v3_timeout8').replace('edaa8867f38ca8f75c8e5f65c2c8c21b74c9a3f7d8d66fdd354f4270f26f8a4d',sha).replace('FDN_N20000_MUJOCO31_','FDN_TIMEOUT8_MUJOCO31_')
assert new.count("p['schema_version']==2")==1;new=new.replace("p['schema_version']==2","p['schema_version']==3")
needle="r['source']['sha256']not in(MOTHER_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d')"
assert new.count(needle)==1;new=new.replace(needle,"r['source']['sha256']not in(MOTHER_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d','8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78')")
oldast=ast.parse(old);newast=ast.parse(new)
for name in('body_contact_forces','reset_pose','run_case','MotherMean'):
 x=next(node for node in oldast.body if getattr(node,'name',None)==name);y=next(node for node in newast.body if getattr(node,'name',None)==name)
 assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False),name
compile(newast,outname,'exec');results.append((outname,new))
for name,text in results:
 p=D/name;p.write_text(text,encoding='utf8',newline='\n');print(name+' source-only AST/compile PASS SHA='+hashlib.sha256(p.read_bytes()).hexdigest())
print('Unchanged original N80 scope/parent resources/waits and nominal five-pose mechanics; no execution or model operations')
