from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';src=C/'append_current_clearance_v4_closed63_pair64_ordinary_once.py';s=src.read_text('utf8');ID='mod4-budget-add200h-ninth-pair64v2';TAG='trial-20261024-'+ID
g=json.loads((R/'NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json').read_bytes());a=json.loads((T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_NINTH_V2_20261024/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert g['passed'] and a['passed']
note='Human explicitly requested 预算增加200小时. USER_ADD200H_20261024_9TH added exactly720000seconds once under both original fcntl locks at the fully closed63 boundary; canonical total1548000 to2268000 seconds,430 to630hours,8 to9 extensions. Charged1465916.3691596985seconds,376 completed segments/digest and all eight prior extension records preserved. Remaining802083.6308403015 is only pre-next-GO snapshot. Original82512.86069250107 guard,7800 next-pair reserve,64800 safety, Windows9400.860692501068 pending and unknown512 preserved. Original metadata budget amendment synchronized with protected master/recipe/approval bytes unchanged. Nine pure contract CPU checks and14 actual owner admission/accounting checks passed; only unused controller total/count, receipt binding and exact common-source budget AST changed. TLS protocolV5 only binds authorized total/count, all transport/HMAC/flow AST otherwise identical; original passed tests reused. First probe failed before host query because runpy lacked sibling import path; V2 corrected with original source/trace retained. First storage receiver bootstrap referenced old protocol basename; failure occurred before receiver ready, empty target and actual allout checked; new V2 namespace reused full SHA only under fresh matching size/mtime/inode, selected4 necessary files copied and full target SHA/signedack verified before releasing true source duplicates. Old62 control0/116/117 and old26 control118 now retained on72. Initial64 installed full source CPU checks but strict common-source SHA admission rejected authorized budget binding; no owner,GO or training charge; both hosts actual no-GO/allout verified. Never rerun failed64 root. New64_NINTH_V2 namespace adds only explicit ninth receipt plus exact common AST budget replacement to the loader, all remaining checks unchanged. One additional closed63 control0 moved with full SHA/signedack for real second-copy headroom; source selected old SHA reused only under fresh stat equality; copy planning is not a new training gate and fresh original25GiB passed after real payload copy. New actual H1/E3 use full latest closed63 checkpoints SHA9edf8126fff4609aa270c388be49931d28d1a18def25f9cbc5bdc2ebb575010a and cb6071f1ecd9d25b7fb58e328bb1c6c176b0122ee9a7e8481f6e1e090d7c2d1d, Adam780640/831160, no reset or freezing. Actual GO and positive first PPO identities/UUID/exe/argv/create verified; not whole-window FINAL or jump skill. Runtime0ec7/reward42a6/target/physics/mesh/actor inputs unchanged. Reserved65 source only after actual64 GO/PPO; one-time720000 compensation removed from successor preparer, future balances use actual predecessor closure. Preserve all original errors, false states, unused source, fee/accounting, signed receipts and complete ordered UTF8 text. No local policy/physics rollout, new reward/S8/input/unknown-peer action, budget refund or second writer. Current run '+a['run_id']+'.'
for name in ('STAGE_NOTE.md','TAG_NOTE.txt'):
 p=B/name;assert not p.exists();p.write_text(note+'\n','utf8')
trace='''Traceback (most recent call last):
  File "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\H1_STEP270_REWARD_PATH_V1_20261022\\same_authorized_session_compressed_transport_v37.py", line 95, in <module>
    main()
  File "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\H1_STEP270_REWARD_PATH_V1_20261022\\same_authorized_session_compressed_transport_v37.py", line 88, in main
    runpy.run_path(str(target), run_name='__main__')
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOD4_BUDGET_ADD200H_NINTH_20261024\\probe_original_budget_ninth_boundary_once.py", line 1, in <module>
    from ninth_budget_ops import *
ModuleNotFoundError: No module named 'ninth_budget_ops'
'''
with (R/'FIRST_PROBE_ORIGINAL_TOOL_TRACEBACK_RETAINED_ACTUAL.txt').open('x',encoding='utf8') as f:f.write(trace)
s=s.replace(s.splitlines()[0],'"""Unique authorized ninth200h extension, budget-only source bindings and actual64V2 continuation."""',1)
s=s.replace('ordinary_followup_only=True','ordinary_followup_only=False,explicit_ninth_extension_receipt=json.loads((T/\'MOD4_BUDGET_ADD200H_NINTH_20261024/reports/NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json\').read_bytes()),unique_trial_id=\''+ID+'\'')
start=s.index(' paths=list(newfiles);');end=s.index(" for line in tags.splitlines():",start)
block=""" paths=list(newfiles)
 import importlib
 rec=importlib.import_module('record_experiment');ID='mod4-budget-add200h-ninth-pair64v2';TAG='trial-20261024-'+ID;budget=T/'MOD4_BUDGET_ADD200H_NINTH_20261024';note=(budget/'STAGE_NOTE.md').read_text('utf8')
 def record_git(*args):
  if args[:2]==('add','--'):
   raw=b'\\0'.join(x.encode('utf8') for x in args[2:])+b'\\0';return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=raw)
  if args[:2]==('tag','-a'):assert args[2]==TAG;return git('tag','-a',TAG,'-F',str(budget/'TAG_NOTE.txt'))
  if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*args)
 assert not git('tag','--list',TAG);rec.git=record_git;sys.argv=['record_experiment.py','--id',ID,'--title',cfg['title'],'--kind','deployment','--note-file',str(budget/'STAGE_NOTE.md'),'--files',*paths,'--validation','See complete evidence index, ninth contract9/owner14CPU checks, actual transaction, storage SHA/allout, failed64 noGO and actual64V2 GO/PPO receipts.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 after_tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(after_tags.splitlines())==1431 and set(tags.splitlines()).issubset(set(after_tags.splitlines()))
 record='history/experiments/20261024-'+ID+'.json';newfiles[record]=H((G/record).read_bytes())
"""
s=s[:start]+block+s[end:];s=s.replace('ordinary_commit_only=True','ordinary_commit_only=False,unique_trial_tag=TAG,tag_object=obj,peeled=head').replace('total_tags=len(tags.splitlines())','total_tags=1431').replace('no_record_or_new_tag=True','one_new_unique_record_and_tag=True');ast.parse(s)
dest=C/'archive_ninth200h_closed63_pair64V2_unique_once.py';assert not dest.exists();dest.write_text(s,'utf8')
cfg=dict(destination='ninth_budget200h_closed63_pair64V2_20261024',base_HEAD='438fc608a703d713649c0ddee625aadf0ebc51af',title='Add authorized ninth200h budget and resume pair64 in unused namespace')
with (C/'reports/NINTH_200H_CLOSED63_PAIR64V2_UNIQUE_CONFIG.json').open('x',encoding='utf8') as f:json.dump(cfg,f,indent=2)
with (R/'NINTH_UNIQUE_ARCHIVE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),unique_helper=str(dest),SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),unique_tag=TAG,part_aware_capture_index=True,NUL_stdin_git_add_avoids_OS_argument_limit=True,record_experiment_single_invocation=True,all1430_old_objects_peels_to_verify=True,ordinary_helper_not_executed=True),f,indent=2)
print(json.dumps(dict(helper=str(dest),tag=TAG,AST=True)))
