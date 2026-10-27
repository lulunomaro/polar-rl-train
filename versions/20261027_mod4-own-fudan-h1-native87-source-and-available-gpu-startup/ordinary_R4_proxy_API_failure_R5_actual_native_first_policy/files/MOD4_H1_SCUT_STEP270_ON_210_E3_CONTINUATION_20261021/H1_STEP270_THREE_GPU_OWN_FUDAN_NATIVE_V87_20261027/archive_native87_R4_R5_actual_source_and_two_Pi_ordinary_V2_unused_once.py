"""Ordinary supplement only; never repeat consumed87 record/tag."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
p=N/'archive_native87_source_and_actual_startup_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed_unique87_archive_definitions_only_for_ordinary_V2',p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s

def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)/'ordinary_R4_proxy_API_failure_R5_actual_native_first_policy'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_R4_R5_SOURCE_FIX_AND_FIRST_PI_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_R4_R5_SOURCE_AND_FIRST_PI_ARCHIVE_STARTED_ACTUAL.json'")
a=s.index(' def recgit(*args):');b=s.index(" head=git('rev-parse','HEAD');",a)
s=s[:a]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[b:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'native87_R4_R5_ordinary_archive_definitions_only','__file__':str(m.m.engine),'same_sha_entries':{}}
exec(compile(s,str(m.m.engine),'exec'),ns);git=ns['git']

def main():
 assert git('rev-parse','HEAD')=='1eb36ceaa1ef1bb0dcbc9f176684afe585630b6a' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1459
 assert git('rev-parse','trial-20261027-mod4-own-fudan-h1-native87-source-and-available-gpu-startup')=='353e675e3ff457bf505eedd483b2c637d3d26c2f'
 assert json.loads((R/'CURRENT_ACTUAL87R5_TWO_H1_FUDAN_NATIVE_GO_FIRST_POLICY_WORK_ORDER.json').read_bytes())['passed_actual_first_policy']
 assert json.loads((R/'R5_RECOVERY_MISSING_CRITICAL_INDEX_CORROBORATION_RETURNED_ACTUAL.json').read_bytes())['passed']
 for d in ('native87_encoder_actual_SDK_API_fix_v1','native87_SDK_tensor_ingress_fix_v1','native87R5_closing_typed_source','native87R5_closing_actual_GO_binding_v1'):
  index=json.loads((L/d/'INDEX.json').read_bytes())
  for row in index.get('files',[]):
   name=row.get('path') or row.get('relative')
   if name:
    p=L/d/name;assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 ns['prior'](G/'versions/20261027_mod4-own-fudan-h1-native87-source-and-available-gpu-startup/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 note=(R/'R4_R5_ORDINARY_CHANGE_NOTE_ACTUAL.md').read_text('utf8')
 ns['run_stage']('fudan',[N,L],[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(196,204)],note,'Preserve R4 SDK type failure and R5 actual two-card SuperMimic policy updates')

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY_R4_R5_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
   json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_repeated_trial_or_tag=True),f,indent=2)
  raise

