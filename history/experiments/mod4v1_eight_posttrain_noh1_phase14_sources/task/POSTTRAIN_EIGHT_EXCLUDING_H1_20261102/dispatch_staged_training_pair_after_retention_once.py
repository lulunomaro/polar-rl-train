"""DispatchONLY anunconsumedpreparedpairafterrealpreviousfrozenassessment.
Launcherfreshreadonlygateisnotactualleaseadmission. OriginalsingleCparent
keepsallGO/actual4FD/budget/3900save/closewait/charge_values responsibilities.
No selectedPT/SDK/Cwritesbythislauncher; H1andfinishedfirstpairexcluded.
"""
from pathlib import Path
import argparse,json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
p=argparse.ArgumentParser();p.add_argument('--pair',type=int,required=True,choices=(2,3,4));p.add_argument('--prior-assessment',required=True);a=p.parse_args();assessment=json.loads(Path(a.prior_assessment).read_bytes());expected={2:{'E0','CURB_PROTECTED878'},3:{'E2','CURB_INDEPENDENT113'},4:{'E3','SLOPE135'}};assert assessment['retention_assessment_complete']and assessment['H1_excluded']and{r['role']for r in assessment['rows']}==expected[a.pair]
assert all(r['selection']in('CANDIDATE','FROZEN_MOTHER')and r['do_not_overwrite_mother_or_failed_candidate']for r in assessment['rows'])
marker=D/('PAIR'+str(a.pair)+'_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json');assert not marker.exists();stage=json.loads((D/'reports'/('PAIR'+str(a.pair)+'_GENERIC_V2_NONPT_STAGE_RESULT.json')).read_bytes());assert stage['actual_stage_passed']and stage['owner_launched']is False;root=stage['root'];roles=stage['roles'];assert not({'H1','E0','CURB_PROTECTED878'}&set(roles))
code="""from pathlib import Path
import json,subprocess,psutil,time,hashlib
B=Path(%r);O=Path('/home/lc01/Zonglin Li/zonglin2');assert not(B/'OWNER_STARTED.json').exists();plan=json.loads((B/'OWNER_PLAN.json').read_bytes());assert {x['role']for x in plan['entries']}==set(%r)
c=json.loads((O/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['active_segment']is None and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']+7800,'Originalresourceeligibilitychanged: noownerlaunch'
apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);snap=[]
for u in('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'):
 raw=subprocess.check_output(['/usr/bin/nvidia-smi','-i',u,'--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();x=[s.strip()for s in raw.split(',')];assert x[0]==u and int(x[1])>15669 and int(x[2])<=30 and u not in apps,'Originalauthorizedcardnotfreshlyeligible';snap.append(raw)
f=(B/'ORIGINAL_PARENT_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(O/'run-python.sh'),'-u','-B',str(B/'eight_posttrain_original_owner_v1.py')],cwd=B,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);f.close();print(json.dumps({'epoch':time.time(),'root':str(B),'parent_pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'roles':%r,'actual_owner_dispatched_not_trainingpass':True,'readonly_GPU_lines':snap,'launcher_is_not_actual_lease_admission':True,'models_SDK_Cwrites_or_GObylauncher':0}))
"""%(root,roles,roles);c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);v['prior_actual_retention_assessment']=str(Path(a.prior_assessment));marker.write_text(json.dumps(v,indent=2),encoding='utf-8');print(marker);print(json.dumps(v,indent=2))
finally:c.close()
