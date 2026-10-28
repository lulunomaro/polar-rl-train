from pathlib import Path
import runpy,subprocess,json,traceback,time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=runpy.run_path(str(T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028/archive_closed99_comparison_and_original_transfer_failure_ordinary_once.py'),run_name='definitions_only');s=old['s']
for a,b in [("'fudan':'mod4-native99-grounded-stance-continued-vs-protected-zero-start'","'fudan':'mod4-native-flat20-source99-producer-reference-repair101'"),("nr=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028'/'reports'","nr=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028'/'reports'"),('ordinary_closed99_comparison_and_transfer_original_failure','ordinary_closed101_formals_full_curves_and_runtime_clone'),('CLOSED99_COMPARISON_TRANSFER_FAILURE_ORDINARY_GIT_NOTE.md','CLOSED101_FULL_RESULTS_RUNTIME_CLONE_ORDINARY_GIT_NOTE.md'),('ORDINARY_CLOSED99_COMPARISON_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED101_FULL_RESULTS_CAPTURE_STARTED_ACTUAL.json')]:
 assert s.count(a)==1;s=s.replace(a,b)
ns={'__name__':'closed101_ordinary_definitions_only','__file__':old['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns)
def git(*args,input=None):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').rstrip('\r\n')
ns['git']=git
def main():
 assert git('rev-parse','HEAD')=='bee60f6520f652db8f8dec71ddfd6b9a6858b965' and not git('status','--porcelain') and len(git('tag','--list').splitlines())==1471
 C=L/'TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1';Q=L/'TWO101_TWO_NATIVE20_FORMAL_INITIAL_CPU_SOURCE_V1'
 records=[]
 for key,sha in [('h1','35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f'),('h1_seed28','fdbe4f1375a57832785cf671bf286cb73bacbbba1885dcecbfb21f392be77b84')]:
  p=C/'current_closed101_models'/key/'formal/model_final.pt';assert p.stat().st_size==256232393;records.append(dict(path=str(p),bytes=256232393,SHA=sha,SHA_source='existing actual collector101 and initialCPU receipts',no_binary_content_read=True))
 with (R/'CLOSED101_EXISTING_PRODUCER_BINARY_INDEX_FOR_ORDINARY_CAPTURE.json').open('x',encoding='utf8') as f:json.dump(records,f,indent=2)
 ns['prior'](G/'versions/20261028_mod4-native-flat20-source99-producer-reference-repair101/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[N,C,Q,L/'NEW_HOST_DIRECT_HTTPS_BUNDLE_PULL_CANDIDATE_SOURCE_V1',L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1']
 ns['run_stage']('fudan',roots,[Path(__file__)],'''Ordinary supplement to consumed101 tag, no new101 trial/tag. Both original101 native20cm jobs fully closed. Original owner611142/nodes/workers actual wait/out, COHORT_FINAL/OWNER_EXIT/CNone/private/shared locks and unique original fee segment passed. Independently charged3612.8719108104706+3612.5692155361176=7225.441126346588 rawseconds sumonce, closing516855.9703772068 is a closed snapshot. Two NEW formal transfers/twohostSHA and two initialfullnativeCPU loads plus ONEsharednormal86 witness passed; inputnative99PT0. Latest native METHOD source h1=35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f/256232393B/global14784/147840WM/14272Pi, not normalPPO nor skill graduation. Seed28 formalfdbe4f... preserved. Full actual3451/3376controls; flat20 attempts33681/32486, takeoffs3174/2576, 20cm height/landing/recovery all0; invalid410/152 stay invalid. Full original139240126B and136139175B curve texts captured as ordered UTF8 parts, never replaced with summaries. Collector/initialCPU consumed, no rerun.

New86 directall29 bundle transfer completed with all perchunk and whole15158703068B producer SHA c0d830...; exact foregroundwait0/source service out and allSSHclosed. Verified extract/newcopy narrow finder/shebang relocation passed, sourceSDK bodies/oldvenvs retained, no model/GPU success inferred. All fullsource/errors/false/readers/partial metadata and runtime clone receipts preserved. Latest V16 same original ACTIVE/hourly app update is included; later103 Fudan task CPU and new86 primitiveSDK are explicitly separate actual states, no training claim from sourceCPU. Protect1471 objects/peels. Binary stat/path/existingproducerSHA only, no host/GPU/model/raw content read for Git. PostGit verification conversation only.''','Preserve closed native101 full results and verified runtime migration')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLOSED101_ORDINARY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True),f,indent=2)
  raise
