from pathlib import Path
import importlib.util,json,time,traceback
H=Path(__file__).resolve().parent;T=H.parent;W=T.parent;G=W/'polar-rl-train';R=H/'reports'
p=H/'archive_unisupermimic_real_H1_method_first_stage_unique_once.py';sp=importlib.util.spec_from_file_location('prior_unique_archive_source_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)/'ordinary_closed81o_disk_relocation82q_native_first_policy'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_CLOSED81O_82Q_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_CLOSED81O_82Q_ARCHIVE_STARTED_ACTUAL.json'")
start=s.index(' def recgit(*args):');end=s.index(" head=git('rev-parse','HEAD');",start)
s=s[:start]+''' git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')
 git('commit','-F',str(note_file));git('push','origin','HEAD:main')
'''+s[end:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'ordinary_archive_utilities_only','__file__':str(m.engine)};exec(compile(s,str(m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='d04ef12dba9bb437b0bc4fff628842457e532ea1' and len(git('tag','--list').splitlines())==1453 and not git('status','--porcelain')
 prior=G/'versions/20261026_mod4-unisupermimic-h1-step270-single4090-convergence-test';ns['prior'](prior/'COMPLETE_FILE_CAPTURE_INDEX.json')
 N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';first=json.loads((N/'reports/MIXED82Q_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert first['passed'] and first['actual_finite_returned'];native=first['target72']['e2']['native_H1_method_first_policy'];assert native['policy_updates']>0
 note='Ordinary supplement to the existing Uni-SuperMimic trial; no record_experiment or new tag.81O closed with qualified healthy H1129/Adam824520 and E380/857360 complete models, wholeCPU finite17Adamx20/actor9STDcritic8 changed/clock/allout/normaldurations, and failed native method with no model. All three original costs preserved sum7716.581540822983s, closed balance617100.3632164001; no refund or secondwriter. New82P passed actual target72 source/SDK/nativeCPU but rejected H1 startup source disk25432158208<25GiB before owner/GO/fee. Exact partial noNODE/GO/out and missing CPU text returned. Existing approved NPZ-only TLS/HMAC/fullSHA protocol chose minimum5 old closed80/79c files1754545974bytes, retained full copies on72 and removed source duplicates only after signed fullSHA acknowledgment; no PT/FINAL/model/log/error touched or account write. Sourceafter27186651136 snapshot; new82Q payload-postcopy actual25GiB passed. Windowsfcntl import-only CPU fixture failed after localcopy, preserved; a new actual purevalidready AST-only check passed without stub/runtime changes.82Q source metadata CRLF2536byte exact, sourcecurrent healthy H1 metadata label corrected, original charge_values AST and owner bytes unchanged; full targetSDK/RSL/nativeCPU/resources/validready/3GO and real native policy proof passed. Native20k real270mm H1 on dual72 GPU16828 has110WM/1Pi update and312completecontrols=6.24M transitions at first proof, original takeoff/landing/recovery/cross0. Immutable producer checkpoint140498700bytes SHA2d797e46eadc07d9f80650b643620cfdf369166f8d92e5ed116d8b2851f66ecb, not downloaded or production source. Other cards continue H1PPO/E3. This proves optimizer/runtime path, not convergence/skill/frozen success/causalPPO speedup. New first-policy observer allowance1200sec did not change3900lifecycle/3600save/300exit or original close900gates. New future one-load nativefullstate/productionpair CPU review and true event/time curve readers are source-only until actual closure. Current82Q fees pending. Full monitor preserves original IDs/target/budget/physics/secrets/no-subagents. All source/CPU/errors/preGO histories/transfer/actualfirstpolicy/monitors appended; publicclone.git excluded, licenses retained, binaries only existing producer metadata.\n'
 roots=[T/n for n in ['H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026','H1_STEP270_CLOSED80_LANDING_JOURNAL_READONLY_20261026','MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026','MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81M_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026']]
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(130,136)]
 ns['run_stage']('usm',roots,extras,note,'Record closed81O, disk-safe relocation and real H1 SuperMimic first policy update')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY81O_82Q_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_or_tag=True,resume_existing_commit_if_push_failed=True),f,indent=2)
  raise
