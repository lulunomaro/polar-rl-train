"""One newfinite3900 original-owner window after actual80 save/full32/trace decision.
No CPUproof relabelling, old2d template source or PTcopy. Existingcanonical solewriter only.
"""
from pathlib import Path
import ast,hashlib,json,time,datetime,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;O=R/'staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V3';BASE='/home/lc01/Zonglin Li/zonglin2';stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');run='MOD4V1_W35_RESUME89ACA_ADAPT_V3_'+stamp;job=BASE+'/tasks/'+run+'_'+str(time.time_ns());SRC='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_POSTADAPT_EVAL_20261102_031914_1793560754280025200';NATIVE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NATIVE0PT_GPU0_V3_20261101_235935_1793548775362947200';PRODUCER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_ADAPT_V2_20261102_021542_1793556942487949000';TRACE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_MOTION_TRACE200_20261102_044043_1793565643213592100';SHA='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f'
CTRL=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101\A_PPO_SOURCE\control227');AUTH=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\REFERENCE_TRACKING_BPTT_V300_20261101\control300\single_writer72_authority_V85M_source.py')
files=[('w35_mod4v1_finite_original_owner_v3.py',R/'w35_mod4v1_finite_original_owner_v3.py'),('three_slot_common_v1.py',CTRL/'three_slot_common_v1.py'),('single_writer72_authority_V85M_source.py',AUTH)]+[(p.relative_to(O).as_posix(),p)for p in O.rglob('*')if p.is_file()]+[('evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json',R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE/FULLRESTORE227_BEFORE_CONTROL.json'),('evidence/ACTUAL_POST80_FULL32_DECISION.json',R/'reports/W35_FULL32_BEFORE_AFTER_PPO80_DECISION_V1.json'),('evidence/ACTUAL_POST80_TRACE_SIGNED.json',R/'reports/W35_MOTION_TRACE_SIGNED_CHECK_V2.json')]
for _,p in files:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
prepare="""from pathlib import Path
import shutil,json,hashlib
B=Path(%r);S=Path(%r);N=Path(%r);P=Path(%r);T=Path(%r)
e=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes());f=json.loads((S/'FINAL.json').read_bytes());trace=json.loads((T/'PARENT_EXIT_SCOPE.json').read_bytes());tf=json.loads((T/'FINAL.json').read_bytes());owner=json.loads((P/'OWNER_EXIT_ACTUAL.json').read_bytes());model=json.loads((P/'production/FINAL.json').read_bytes())['final']
assert e['all_own_children_waited']and e['owned_private_validation_locks_released']and e['error']is None and f['passed_execution']and f['bounded32s_complete']and f['optimizer_updates']==0
assert trace['all_own_children_waited']and trace['owned_private_validation_locks_released']and trace['error']is None and tf['passed_execution']and tf['optimizer_updates']==0
assert owner['original_cost_settled']and owner['all_own_children_waited']and owner['private_finite_leases_released']and owner['error']is None
assert model['SHA']==%r and model['saved_iteration']==32561 and model['Adam_min']==model['Adam_max']==652860 and model['actual_new_PPO_updates']==80
with(P/'RESUME89ACA_FINITE_WINDOW_PURPOSE_CONSUMED.json').open('x')as q:json.dump({'purpose':B.name,'source_SHA':model['SHA'],'max_parent_seconds':3900,'no_automatic_tail_or_duplicate_window':True},q)
assert not B.exists();B.mkdir();(B/'evidence').mkdir()
def ignore(path,names):return[n for n in names if n=='__pycache__'or Path(n).suffix.lower()in('.pt','.pth','.pyc')]
for name in('runtime','original_field','train','data'):
 if(S/name).is_dir():shutil.copytree(S/name,B/name,ignore=ignore)
for name in('original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_ASSET_DIFF.json'):
 if(S/name).is_file():shutil.copy2(S/name,B/name)
shutil.copy2(N/'FINAL.json',B/'evidence/NEW_ASSET_NATIVE_ACTUAL.json');shutil.copy2(S/'FINAL.json',B/'evidence/NEW_TARGET_SDK_FULL32_ACTUAL.json');shutil.copy2(T/'PARENT_EXIT_SCOPE.json',B/'evidence/ACTUAL_POST80_TRACE_EXIT.json')
old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72');field=[]
for rel,expected in [('assets/arena_collision.usdc','9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'),('data/arena_collision.npz','f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954')]:
 p=B/'original_field'/rel;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;field.append({'relative':rel,'bytes':len(raw),'SHA':expected})
p=B/'runtime/isaac/mod4/field214.py';q=old/'runtime/isaac/mod4/field214.py';same=hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(q.read_bytes()).hexdigest();assert same
(B/'evidence/RM70_SCOPE_REUSE_ACTUAL.json').write_text(json.dumps({'actual_original_geometry_fullSHA_verified':True,'files':field,'actual_shared_material_source_reused_unchanged':same,'field214_SHA':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'OriginalCAD/sharedmaterialexact; newsource89acaactualGPUfullrestore/full32 andtrace, NOTRM70graduation'},indent=2));print(json.dumps({'new_job':str(B),'runtime_source':str(S),'PT_copies':0,'source_SHA':model['SHA'],'owner_or_GO_started':False}))
"""%(job,SRC,NATIVE,PRODUCER,TRACE,SHA)
c=connect72();sf=c.open_sftp();record={'status':'STAGING','run_id':run,'new_job':job,'source_model_SHA':SHA,'PPO_window_requested_seconds':3900,'new_budget_seconds':0,'decision':'Afteractualnegativefull32 andactual4scommand/targetwiringtrace, oneboundedunchangedoriginalPPO/geometry/reward/STDcontinuation; mustnewsave/replay/indepassessmentbeforequalification'}
try:
 def remote(code,timeout=180):
  i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=timeout);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);return json.loads(text)
 record['prepare']=remote(prepare)
 for rel,p in files:
  parent=job+'/'+str(Path(rel).parent).replace('\\','/');cur=''
  for part in parent.split('/'):
   if not part:continue
   cur+='/'+part
   try:sf.mkdir(cur)
   except OSError:sf.stat(cur)
  sf.put(str(p),job+'/'+rel)
 for name,obj in [('OWNER_PLAN.json',{'run_id':run,'source':'HumanfullDR/RM70goal; actualpost80longmovingdeficit andtracecommand+targetwiringintact; oneoriginal3900boundedadaptation from89aca, noautomaticextension','one_original_writer':True}),('SCHEDULE_PUBLIC.json',{'experts':{'w35_72':{'max_parent_seconds':3900,'GPU_UUID':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}}})]:
  with sf.open(job+'/'+name,'wx')as f:f.write(json.dumps(obj,indent=2))
 finalize="""from pathlib import Path
import json,hashlib
B=Path(%r);files=[]
for root in('runtime','original_field','train','data','evidence'):
 p=B/root
 if p.is_dir():
  for f in sorted(p.rglob('*')):
   if f.is_file()and f.suffix.lower()not in('.pt','.pth','.pyc')and'__pycache__'not in f.parts:files.append({'relative':f.relative_to(B).as_posix(),'bytes':f.stat().st_size,'SHA':hashlib.sha256(f.read_bytes()).hexdigest()})
for f in sorted(B.glob('*.py')):files.append({'relative':f.name,'bytes':f.stat().st_size,'SHA':hashlib.sha256(f.read_bytes()).hexdigest()})
for f in sorted(B.glob('*.json')):
 if f.name!='INSTALL_MOD4V1_ACTUAL.json':files.append({'relative':f.name,'bytes':f.stat().st_size,'SHA':hashlib.sha256(f.read_bytes()).hexdigest()})
manifest={'kind':'MOD4V1_W35_INSTALL_ACTUAL_V1','source_model_metadata':{'SHA':%r,'bytes':17621509},'asset_USD_SHA':'2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3','asset_contract_SHA':'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','derivation_index_SHA':hashlib.sha256((B/'MOD4V1_DERIVATION_INDEX.json').read_bytes()).hexdigest(),'files':files,'postcopy_fullSHA_actual':True,'model_copies':0}
(B/'INSTALL_MOD4V1_ACTUAL.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'files':len(files),'manifest_SHA':hashlib.sha256((B/'INSTALL_MOD4V1_ACTUAL.json').read_bytes()).hexdigest()}))
"""%(job,SHA)
 record['installed']=remote(finalize)
 code="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);log=(B/'OWNER_CONSOLE.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'w35_mod4v1_finite_original_owner_v3.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);q=psutil.Process(p.pid);print(json.dumps({'pid':p.pid,'creation':q.create_time(),'root':str(B),'actual_budget_GO_not_yet_claimed':True}))"%(job,BASE+'/run-python.sh');record.update(status='ORIGINAL_FINITE_OWNER_DISPATCHED',parent=remote(code,90))
finally:sf.close();c.close()
p=R/'reports'/('W35_resume89aca_adaptation_dispatch_'+stamp+'.json');p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(record,ensure_ascii=False,indent=2))
