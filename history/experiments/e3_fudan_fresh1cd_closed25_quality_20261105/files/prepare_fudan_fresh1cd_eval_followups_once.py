"""Create four unused assessment/export entry sources after the ten V4 inference modules exist."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent;folder='source_fudan_frozen_native_eval_v4_fresh1cd_timeout8';frozen=D/folder/'frozen_sequence_mean.py';digest=hashlib.sha256(frozen.read_bytes()).hexdigest()
outputs=('export_fudan_fresh1cd_pi_for_mujoco_once.py','dispatch_fudan_fresh1cd_frozen_original_once.py','collect_fudan_fresh1cd_frozen_original_once.py','evaluate_fudan_fresh1cd_pi_mujoco31_lowrise_once.py');assert not any((D/name).exists()for name in outputs)
BAD='3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e';result={}
s=(D/'stage_fudan_fresh1cd_frozen_original_once.py').read_text(encoding='utf8');tree=ast.parse(s)
t=(D/'export_fudan_timeout8_pi_for_mujoco_once.py').read_text(encoding='utf8');names=('KIND','BRANCH','BASE','COUNTERS','MOTHER_SHA','SOURCE_4K_SHA','LEARNER_SHA','SOURCE_KIND','OVERLAY_SHA','TASKS');assigns={target.id:node for node in tree.body if isinstance(node,ast.Assign)for target in node.targets if isinstance(target,ast.Name)}
header='\n'.join(ast.get_source_segment(s,assigns[name])for name in names)+'\nFROZEN_SOURCE_SHA = '+repr(digest)+'\nPREFIX = "FDNFRESH1CD_PI_ONLY_EXPORT_"\n\n'
a=t.index('KIND = ');b=t.index('# Parsed locally');t=t[:a]+header+t[b:]
start='    closed_path = Path(args.closed)';front=s[s.index(start):s.index('    # All closure validation above')];a=t.index(start);b=t.index('    # Every check above');t=t[:a]+front+t[b:]
t=t.replace('FDNTIMEOUT8_PI_ONLY_EXPORT_','FDNFRESH1CD_PI_ONLY_EXPORT_').replace('source_fudan_frozen_native_eval_v3_timeout8',folder).replace('fb4890c49cb79afc0aeedfc37cc8a489b72e4531aa0036a3055fef525ecd2bcd',digest)
a="source['sha256']not in(MOTHER_SHA,LEARNER_SOURCE_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d')";assert t.count(a)==1;t=t.replace(a,a[:-1]+",'"+BAD+"')")
remote_tree=ast.parse(t);remote=next(n.value.value for n in remote_tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='REMOTE_EXPORT'for x in n.targets));compile(ast.parse(remote),'fresh1cd-pi-export','exec');result[outputs[0]]=t
for old,new in(('dispatch_fudan_timeout8_frozen_original_once.py',outputs[1]),('collect_fudan_timeout8_frozen_original_once.py',outputs[2])):
 text=(D/old).read_text(encoding='utf8').replace('FDNTIMEOUT8_FROZEN_','FDNFRESH1CD_FROZEN_').replace('fdn_timeout8_frozen_outer_wait.py','fdn_fresh1cd_frozen_outer_wait.py')
 if old.startswith('collect_'):
  a='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V2_N20000';assert text.count(a)==1;text=text.replace(a,'FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD')
 result[new]=text
old=(D/'evaluate_fudan_timeout8_pi_mujoco31_lowrise_once.py').read_text(encoding='utf8');text=old.replace('source_fudan_frozen_native_eval_v3_timeout8',folder).replace('fb4890c49cb79afc0aeedfc37cc8a489b72e4531aa0036a3055fef525ecd2bcd',digest).replace('FDN_TIMEOUT8_MUJOCO31_','FDN_FRESH1CD_MUJOCO31_')
assert text.count("p['schema_version']==3")==1;text=text.replace("p['schema_version']==3","p['schema_version']==4")
a="r['source']['sha256']not in(MOTHER_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d','8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78')";assert text.count(a)==1;text=text.replace(a,a[:-1]+",'"+BAD+"')")
x,y=ast.parse(old),ast.parse(text)
for name in('body_contact_forces','reset_pose','run_case','MotherMean'):
 assert ast.dump(next(n for n in x.body if getattr(n,'name',None)==name))==ast.dump(next(n for n in y.body if getattr(n,'name',None)==name))
result[outputs[3]]=text
for name,text in result.items():ast.parse(text);compile(text,name,'exec')
for name,text in result.items():(D/name).write_text(text,encoding='utf8',newline='\n')
print('Prepared4 unused fresh1cd entries; original N80 resource/wait and nominal mechanics unchanged; exact V4_FRESH1CD collector kind; no SSH/model/SDK/export/assessment')
