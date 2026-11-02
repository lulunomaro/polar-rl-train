"""Originalunchangedownerwait1800admission, notfreshcardadmitted/noPTretry.
TheearlierlauncherfailedbeforePopen/GO; exactstagedoriginalparentperformsevery
originalEX/SH/host/GPU/budgetcheckbeforeANYGO, releasingpartialleaseswhilebusy.
No GPUsharing/signals/lockclear/lowerthreshold/newledger/SDKcodechange.
"""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
out=D/'PAIR3_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json';assert not out.exists();stage=json.loads((D/'reports/PAIR3_GENERIC_V2_NONPT_STAGE_RESULT.json').read_bytes());assessment=json.loads((D/'reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json').read_bytes());assert stage['actual_stage_passed']and stage['owner_launched']is False and assessment['retention_assessment_complete']and assessment['H1_excluded']and{r['role']for r in assessment['rows']}=={'E2','CURB_INDEPENDENT113'};assert all(r['selection']in('CANDIDATE','FROZEN_MOTHER')and r['do_not_overwrite_mother_or_failed_candidate']for r in assessment['rows']);root=stage['root'];err=D/'reports/PAIR3_LAUNCHER_FRESH_CARD_GATE_ERROR_BEFORE_PARENT.json';assert not err.exists();err.write_text(json.dumps({'kind':'PRELAUNCH_READONLY_FRESH_CARD_GATE_BUSY_NOT_PPO_FAILURE','original_tool_job':'pwsh-7cfd6397febe4f74','error':'AssertionError: Originalauthorizedcardnotfreshlyeligible','root':root,'parent_or_SDK_PT_GO_Cwrites_started':False,'diagnosis_ref':str(D/'reports/PAIR3_LAUNCHER_GPU_BUSY_DIAGNOSIS_ONCE.json'),'next':'Originalunchangedparentboundedwaitwithalloriginalleases/checks, notweakenedresourceadmission'},indent=2),encoding='utf-8');code="""from pathlib import Path
import json,subprocess,psutil,time
B=Path(%r);O=Path('/home/lc01/Zonglin Li/zonglin2');assert not(B/'OWNER_STARTED.json').exists()and not(B/'ORIGINAL_PARENT_STDOUT_STDERR.log').exists();p=json.loads((B/'OWNER_PLAN.json').read_bytes());assert {e['role']for e in p['entries']}=={'E3','SLOPE135'}and all(not(Path(e['job_root'])/'GO_PRODUCTION.json').exists()for e in p['entries'])
c=json.loads((O/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']+7800,'Ifanotheractualownerstartednow,nolaunch'
f=(B/'ORIGINAL_PARENT_STDOUT_STDERR.log').open('xb');w=subprocess.Popen([str(O/'run-python.sh'),'-u','-B',str(B/'eight_posttrain_original_owner_v1.py')],cwd=B,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);f.close();print(json.dumps({'epoch':time.time(),'root':str(B),'parent_pid':w.pid,'creation':psutil.Process(w.pid).create_time(),'roles':['E3','SLOPE135'],'original_bounded_resource_wait1800_before_anyGO':True,'not_actual_GPU_or_budget_admission_yet':True,'launcher_models_SDK_GO_locks_Cwrites':0}))
"""%root;c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);v=json.loads(text);v['prior_actual_retention_assessment']=str(D/'reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json');out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
finally:c.close()
