"""Source-only future full32 evaluation of the complete checkpoint of next89aca resumewindow.
Bound tospecificsourceparent89aca/base32561/652860, dynamicactual newN/savedLR; no Task/SDK/PT yet.
"""
from pathlib import Path
import ast,json,hashlib,shutil
R=Path(__file__).resolve().parent;S=R/'staged_sources/W35_MOD4V1_POSTADAPT_EVAL_V1';D=R/'staged_sources/W35_MOD4V1_AFTER_RESUME89ACA_EVAL_V1';assert not D.exists();D.mkdir();oldsha='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b';source='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f';oldkind='MOD4V1_W35_POSTADAPT_SAVEDMODEL_FULL32_EVAL_V1';kind='MOD4V1_W35_AFTER_RESUME89ACA_SAVEDMODEL_FULL32_EVAL_V1'
for p in S.iterdir():
 if not p.is_file():continue
 raw=p.read_bytes()
 if p.suffix=='.py':
  text=raw.decode('utf-8')
  if p.name=='postadapt_eval_contract.py':text=text.replace(oldsha,source).replace('ITER==32481+UPDATES','ITER==32561+UPDATES').replace('651260+20*UPDATES','652860+20*UPDATES').replace(oldkind,kind)
  if p.name=='evaluate_mod4v1_w35.py':text=text.replace('MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2','MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3').replace(oldsha,source)
  ast.parse(text);raw=text.encode('utf-8')
 (D/p.name).write_bytes(raw)
s=(R/'deploy_postadapt_w35_eval_ROOT_v2_once.py').read_text(encoding='utf-8').replace('W35_MOD4V1_POSTADAPT_EVAL_V1','W35_MOD4V1_AFTER_RESUME89ACA_EVAL_V1').replace('W35_adaptation_dispatch_','W35_resume89aca_wait_dispatch_').replace('ROOT_POSTADAPT_SAVEDMODEL_EVAL_ONLY','ROOT_AFTER_RESUME89ACA_SAVEDMODEL_FULL32_EVAL_ONLY').replace('MOD4V1_W35_POSTADAPT_EVAL_','MOD4V1_W35_AFTER_RESUME89ACA_EVAL_').replace('POSTADAPT_EVAL_PURPOSE_CONSUMED.json','AFTER_RESUME89ACA_FULL32_EVAL_PURPOSE_CONSUMED.json').replace('POSTADAPT_NEW_SAVEDMODEL_','AFTER_RESUME89ACA_NEW_SAVEDMODEL_').replace(oldkind,kind).replace(oldsha,source).replace('651260+20*source[\'actual_new_PPO_updates\']','652860+20*source[\'actual_new_PPO_updates\']').replace('W35_postadapt_eval_dispatch_','W35_after_resume89aca_eval_dispatch_')
matches=[l for l in s.splitlines()if l.strip()=="assert source['path']==producer+'/production/model_final_complete.pt'"];assert len(matches)==1;a=matches[0];s=s.replace(a,a+" and source['saved_iteration']==32561+source['actual_new_PPO_updates']")
ast.parse(s);dep=R/'deploy_w35_after_resume89aca_full32_eval_v1_once.py';assert not dep.exists();dep.write_text(s,encoding='utf-8');rows=[]
for p in D.iterdir():
 if p.is_file():rows.append({'relative':p.name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()})
v={'kind':'UNUSED_SOURCE_ONLY_FUTURE_NEW_SAVEDMODEL_FULL32_AFTER_RESUME89ACA','input_parent89aca':source,'base_iteration':32561,'base17Adam':652860,'future_actual_new_updates':'ProducerFINAL rowandcachedsource mustagree; notassumed80','future_actual_savedLR':'Readexactfromonecachednewsourceoptimizer notassumedpriorLR','scope':[20000,1600,12800,3200,32],'parent_resource_wait_mode':'OriginalGPU0privateEX+finitevalidationEX, bounded600wait releasingpartialleases/zeroSDKPT; originalparentunchanged','sourcekind_expected':'MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3','files':rows,'deployer_SHA':hashlib.sha256(dep.read_bytes()).hexdigest(),'original_trainer_SHA':'bbda08da09bbb12cae8b80e8ff9be2b7a1f19dddd42200d5ec2bdfb6bca45ee2','PT_or_SDK_or_GO_or_budget_actions':0,'after_genuine_complete_save_settled_waited_exit_only':True};(D/'SOURCE_ONLY_INDEX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');out=R/'reports/W35_AFTER_RESUME89ACA_EVAL_SOURCE_ONLY_PREPARED.json';assert not out.exists();out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
