"""Ordinary supplement after consumed88 actual trial; no record/tag repetition."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=N/'archive_native88_nominal400_own_step_actual_stage_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed88_archive_definitions_for_bank_ordinary',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)/'ordinary_frozen_gas400_reset_bank17_next88C_plan'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'FROZEN_BANK17_NEXT88C_ORDINARY_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'FROZEN_BANK17_NEXT88C_ORDINARY_ARCHIVE_STARTED_ACTUAL.json'")
a=s.index(' def recgit(*args):');b=s.index(" head=git('rev-parse','HEAD');",a)
s=s[:a]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[b:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'frozen_bank17_ordinary_archive_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='a124b67be14ccf2d83318cfdf6dfb42e163e8ee5' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1461
 assert git('rev-parse','trial-20261027-mod4-native88-gas400-own-wheel-objective-continuation')=='f64656b2a31d6f3c4e4ced50262950ce8cbbd796'
 D=L/'native88_gas400_reset_bank_exact_compatibility_source_v1';index=D/'INDEX_SHA256_ACTUAL.json';assert hashlib.sha256(index.read_bytes()).hexdigest()=='24c84db75dbfab22eaad9de9497e639c3c2216aa1e080fd90da95361cb2f9a9e'
 for row in json.loads(index.read_bytes())['files']:
  p=D/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 ns['prior'](G/'versions/20261027_mod4-native88-gas400-own-wheel-objective-continuation/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 with (R/'ACTIVE88C_LIFECYCLE_SOURCE_EXPLICIT_PENDING_AFTER_BANK_ORDINARY_CAPTURE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pending_ordinary_after_frozen=str(L/'native88C_exact_reset_bank_lifecycle_source_v1'),reason='one sequential helper preparing exact stageC lifecycle source, not installed or executed; excluded from this bank-only capture',no88Cpayload_Task_GO=True),f,indent=2)
 note='''Preserve frozen exact nominal400N reset-bank compatibility repair after actual88B startup failure. Ordinary supplement to consumed88trial, no newtag or repeatedrecord. Actual88B both signedGO workers failed on original reset-bank contract hash guard before any new native control/Pi; originalfee161.60727643966675/closing569391.7559990883, ownallout/CNone/originallocks/durationtrue unchanged. Latestqualified methodmodels remain R5, native400N model/skill not achieved.

Frozen source helper INDEX24c84db75dbfab22eaad9de9497e639c3c2216aa1e080fd90da95361cb2f9a9e,16files+self,17sourceCPU checks. Exactly oldcbcd andnew517cd contract SHA and original resetbank157944B/48be349c producer pinned. Recursive diff only authorized2stiffness3500->2000+2uppercap changes. All133poses fit newgas limits, original74heightfiltered selection unchanged. Original source FK closure diagnostic~2.332e-10 is geometric consistency only, not newphysicalauditgate. Actual reset source selected/all/empty TorchCPU duck writes/cache/q/root/height/RNG literalexact; original sampler/physical2mm/resetalgorithm unchanged. New runtimehelper + exact oldcontractcopy, scut_flat_rescue only typed hash mismatch branch, SOURCE_FREEZE onlyscutSHA. No poseclamp/bankrewrite/broadignorehash/SDKscene/actor/WM/PT/USD/native/raw/160k rerun or actualtrainingclaim. New live SDK/PhysXreset stillrequired.

Root new88C plan explicitly pins qualified R5 native models separately from failed88B resources/cost/terminal/allout and latestsole72balance. New actualsourceCPU must execute exact bankhelper and compute flag; actualprecontrol must observe original resetcache/writebuffer after genuine VecEnvreset and forward actualfirstreset boolean plus separate source-only compatibility proof. Same native fullstate/64freshcontrols+64NEWwindowWM-only/640minNEWwm/nativeobjective/400Nfourattrs/physicalV8/clock/actions/fullsave/success retained. No88Cpayload/controller/Task/GO/fee or budgetmutation. One new stageC lifecyclehelper is explicitly pending ordinary capture afterfreeze, not claimed installed. All source/CPU/errors/oldfalse/readers/monitor/sourceplan captured in fullUTF8/plainordered; models/raw/binary only actualpathbytes/priorproducerSHA. All1461tags objects/peels retained; postGit conversation verification only, no reportchasingHEAD.
'''
 ns['run_stage']('fudan',[N,D],[],note,'Preserve exact gas400 reset-bank compatibility source and next typed continuation plan')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FROZEN_BANK_ORDINARY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(original_error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_repeated_record_or_tag=True),f,indent=2)
  raise
