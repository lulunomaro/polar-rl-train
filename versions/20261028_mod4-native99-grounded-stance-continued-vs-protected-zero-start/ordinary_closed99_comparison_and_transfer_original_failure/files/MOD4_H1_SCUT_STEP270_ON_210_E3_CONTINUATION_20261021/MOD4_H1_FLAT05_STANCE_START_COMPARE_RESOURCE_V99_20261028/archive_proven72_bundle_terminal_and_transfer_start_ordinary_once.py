from pathlib import Path
import runpy,json,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
previous=runpy.run_path(str(T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028/archive_closed97_two_formals_stage10_failure_ordinary_once.py'),run_name='ordinary97_definitions_only');s=previous['s'];ID='mod4-native99-grounded-stance-continued-vs-protected-zero-start'
for a,b in [("'fudan':'mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'/'reports'","nr=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028'/'reports'"),('ordinary_closed97_formals_and_stage10_runtime_conflict','ordinary_proven72_bundle_terminal_and_transfer_start'),('CLOSED97_STAGE10_ORDINARY_GIT_NOTE.md','PROVEN72_BUNDLE_TRANSFER_START_ORDINARY_GIT_NOTE.md'),('ORDINARY_CLOSED97_STAGE10_CAPTURE_STARTED_ACTUAL.json','ORDINARY_PROVEN72_TRANSFER_START_CAPTURE_STARTED_ACTUAL.json')]:
 assert s.count(a)==1;s=s.replace(a,b,1)
ns={'__name__':'proven72_transfer_ordinary_definitions_only','__file__':previous['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='6b4e4fa9d80eb5ef980900ea7c8bc5eb9ac526fc' and not git('status','--porcelain') and len(git('tag','--list').splitlines())==1470
 P=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1';v=json.loads((P/'reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json').read_bytes());assert v['bundle_passed'] and v['terminal_observed'] and v['all_original_recorded_out']
 transfer=L/'NEW_HOST_PROVEN72_RUNTIME_TRANSFER_AND_RELOCATION_SOURCE_V1'
 indexes=[transfer/'FROZEN_FIRST_BATCH_DOWNLOAD_UPLOAD_SOURCE_INDEX_V1.json',transfer/'FROZEN_T128_PREFIX_PRESERVING_SOURCE_INDEX_V2.json'];assert all(p.is_file() for p in indexes)
 assert any((transfer/'reports').glob('BATCH_*_RETURNED_ACTUAL.json')),'first actual returned copy required'
 ns['prior'](G/('versions/20261028_'+ID+'/COMPLETE_FILE_CAPTURE_INDEX.json'))
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[N,P,L/'FROZEN_EXPERTS_REMAINING40050_METADATA_INVENTORY_SOURCE_V1'];assert all(p.is_dir() for p in roots)
 frozen_names=['download_verified_runtime_chunks_to_F_bounded_batch_once_v1.py','upload_verified_F_runtime_batch_to86_stdin_once_v1.py','download_verified_runtime_chunks_to_F_resume128_bounded_batch_once_v2.py','derive_T128_prefix_preserving_transport_once_v2.py']
 extras=[*indexes,*[transfer/x for x in frozen_names],*[p for p in (transfer/'reports').iterdir() if p.is_file() and ('0000_01' in p.name or p.name.startswith(('DOWNLOAD_ORIGINAL_ERROR_','FRESH_EXACT_CIM_')))]];assert all(p.is_file() for p in extras)
 note='''Ordinary append to already consumed actual99 phase, never record/tag99 again. Proven72 environment bundle now actually completed, producer passed and ownsupervisor/worker/recordedtar-pigz allout, originalownedlock released. Compressed15,158,703,068B in29chunks with producer c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36. Fullsource/terminal/exit/ABI/footprint texts preserved. No sourcearchive reread forGit; archive/chunks outsideworkspace indexed only by existingproducer metadata. Existingworkingruntime dependencies are cloned with declaredmetadata inconsistencies, not claimedjointpipchecksuccess. Actualsource/SDKpy preserved; laterNEWcopyrelocation only inside86project, no global/system changes.

Bounded transfer source and actual returned batch receipts preserved in full. Source72connection closed before86connection; Fnewartifactdirectory capacity checked, each chunk streamingSHA/stat checked againstoriginalproducer, noCbigcopy/noexistingdata cleanup. Pipelined bounded16prefetch/defaultcount1 review incorporated beforeexecution toavoid serialSFTProundtrip stalls. UploadSTDINmemory credential, originalhostpinbeforeauth, receivercapacity/path/marker guard, .partial retained onfailure and atomicpromotiononlyafterfullSHA. No remoteGPU/model/training/account action from copying. Actual receipts outrank this capture note for which batches reached86; do not infer all29chunks/extraction/SDK/fullrestore/PPO readiness from first returned copy. Futurebatch/relocation/SDKoutputs explicitlypending afterfreeze ordinaryappend, no blindpipresolve/no rerunoldinstallers.

Partialremainingexpertcatalog source frozen as UNEXECUTED; prior18 means evaluationseed/profiles not18independentactors, no inventedcatalog report. Known E0/W35/E2/E3 adaptedfullmodel qualifications andE0shortfrozenregression remainseparatefromfullskillgraduation orcompleteWMdataset. Typedtransitiontap/remainingfuturepreparations mutableexcluded untilfreeze. Twoactual99nativejumpbranches keepindependentoriginalsave/exit/cost procedures; no hotpatch/stop/newwriter/refund or sourcepromotion. Source0 andcontinuationcomparisons firstNEW700WM6Pi each were already unique99; no new firstmetadata queries, no final/jumpsuccess inferred. All1470tags/peels protected. Fullsavedsource/errors/false/receipts/reports captured, binaries onlyactualpathbytesexistingproducerSHA/unknown. PostGitverificationconversationonly, no filechasingHEAD.
'''
 ns['run_stage']('fudan',roots,extras,note,'Preserve completed proven72 runtime export and first verified migration batches')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ORDINARY_PROVEN72_TRANSFER_START_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True),f,indent=2)
  raise
