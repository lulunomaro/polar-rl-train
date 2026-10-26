from pathlib import Path
import importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;G=W/'polar-rl-train';R=J/'reports'
p=J/'archive_actual_Fudan_reference_and_all_pending_SM_unique_once.py';sp=importlib.util.spec_from_file_location('unique_archive_defs_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)/'ordinary_V3_helpers_mixed84_cold_handoff72'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_V3_MIXED84_COLD_HANDOFF72_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_V3_MIXED84_COLD_HANDOFF72_ARCHIVE_STARTED_ACTUAL.json'")
start=s.index(' def recgit(*args):');end=s.index(" head=git('rev-parse','HEAD');",start)
s=s[:start]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[end:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'ordinary_fudan_V3_cold_handoff_utilities_only','__file__':str(m.engine)};exec(compile(s,str(m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='945fe368ae1fd8abfbce7bf50f8c690385945064' and len(git('tag','--list').splitlines())==1455 and not git('status','--porcelain')
 ns['prior'](G/'versions/20261026_mod4-supermimic-fudan-jump-reference-and-pending-experts/COMPLETE_FILE_CAPTURE_INDEX.json')
 handoff=json.loads((R/'SINGLE4090_TO72_NEEDED_RUNTIME_HANDOFF_RETURNED_ACTUAL.json').read_bytes());assert handoff['passed'] and handoff['file_count']==2407 and handoff['all_transferred_file_bytes_and_fullSHA_verified'] and handoff['canonical_not_copied_or_replaced']
 assert not (T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026/reports/THREE_EXPERT_DEPLOY_STARTED_ACTUAL.json').exists()
 note='''Ordinary supplement to the consumed Fudan/SuperMimic preparation trial; no record_experiment or new tag. Capture all completed helper sources and rejected/failed/corrected CPU attempts, root integration, new84 local source/payload binding, independent observer path review, resource rejection/minimal NPZ safe relocation and human-requested temporary host-offline cold handoff. Original83B full qualified H1/E2/E3 and original fee10943.796510219574/closing595256.8240613937 remain current; no new training, model promotion, budget write or GPU experiment occurred.

Fudan partial V3 uses261 statically feasible10ms frames, explicit90percent limb-excursion attenuation, actual own30joint closedchain static fit; not own dynamic jump/step/collision/actuation success. Ascent-only demoZ/Vz masks after measured apex and separate own270mm support-height objective avoid a flat-ground reference pulling own landing down; sourceXY/XYvelocity and unobserved spins masked. Exact runtime joint names must be read/reordered before first native control/Pi; current proof is offline CPU only.21-test native finalization candidate remains uninstalled; prior82Q missing-final cause unproven. Integrated bridge preserves original class/action/step/WM/Pi/save lifecycle AST outside narrow reference/producer hooks. Mixed84 source binder consumed once, local three payloads/controllers prepared, but actual target SDK/source/nativeCPU and resources/valid_ready/GO/firstPi never run. Independent reviewer found original observer python-c import-path failure before execution; original template retained, new V2 minimal path fix and negative/corrected fixture preserved. No Fudan-native training claim.

Disk before84 source25454178304 below25GiB. First exact82Q83B-only minimum selection could not cover required headroom and returned zero files/no target process. New missing-only broader approved closed-NPZ set selected minimum5 files1764493688bytes from80/81O/83B, transferred existing passed TLS/HMAC/fullSHA/signedack protocol, retained full copies72 before removing source duplicates, sourcefree27218595840 snapshot. All source/receiver helpers out and original canonical unchanged. No PT/FINAL/log/error/cache or unique original deleted; old relocation entries consumed, no rehash for Git.

Human then said entire single4090 host/network will be offline briefly and requested needed assets on dual4090 first. Root did not execute84deployer or any newowner/node/TaskGO/fee. Using existing local complete models/source/runtime/reference,2407files were cold-staged to /home/lc01/Zonglin Li/zonglin2/staging/MOD4_SINGLE4090_DISCONNECT_HANDOFF_20261026, every actual byte/fullSHA checked. In-memory tar194056199bytes SHAb9687e6f16fbe7621631bc08afc790dd3905d911619a5e6b4f0a8969d1f45efd retained72, no new local weight archive. Original canonical stays210, not copied/replaced; no secondwriter/offline guessed billing. Actual transfer is source/data availability, not installed/admitted training or skill proof. User was told transfer complete and can disconnect; original monitor updated in place, hourly/ACTIVE/same target, planned-offline unchanged stays quiet. New training awaits actual restored original writer/account/resources. Source-only two-slot design cannot bypass original three-slot assertion or authorize ledger copying.

E2 next SuperMimic source/CPU15-fixture candidate preserves original arithmetic failure then correction, different175obs/history10 semantics and critic-base170; not PPO weight-compatible, actual delay/ingress vs motor action distinction explicit. No E2 new Task/GO or policy/environment execution. Human all-unfinished-expert SuperMimic queue/delegation remains authorized, original physical/save/retention/control/accounting constraints unchanged. All full saved sources/errors/reports captured; binaries only real paths/bytes/existing producer SHA, no model/raw/GPU/host read for Git. PostGit receipt remains conversation-only.
'''
 roots=[J,T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026']
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(144,150)]
 ns['run_stage']('fudan',roots,extras,note,'Prepare Fudan V3 SuperMimic and preserve verified dual4090 cold handoff')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY_V3_COLD_HANDOFF72_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_repeated_record_or_tag=True,resume_existing_commit_if_push_failed=True),f,indent=2)
  raise
