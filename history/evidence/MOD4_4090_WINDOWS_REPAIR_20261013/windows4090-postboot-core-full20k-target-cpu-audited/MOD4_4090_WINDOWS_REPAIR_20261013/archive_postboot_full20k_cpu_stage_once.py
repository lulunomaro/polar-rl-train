"""One real CPU repair/admission stage; no GPU or original stage replay."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import importlib,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
ID='windows4090-postboot-core-full20k-target-cpu-audited'
DEST=REPO/'history/evidence'/D.name/ID
def main():
    sys.path.insert(0,str(D));import append_large_install_evidence_import_reviewed_git as safe
    g=safe.g
    assert not g('status','--porcelain') and not g('tag','--list','*'+ID) and not DEST.exists()
    for name in ['V6A_TARGET_CPU_AND_UNGRANTED_SDK_ACTUAL_COLLECTION.json','BOUNDED_WEB_FROMLIST_CPU_ADMISSION_ACTUAL.json','V6A_AUDITED_CPU_HANDOFF_ACTUAL.json','APPS_LINEEND_REVIEWED_CPU_CONTINUATION_ACTUAL.json']:
        assert json.loads((D/'reports'/name).read_bytes())['passed']
    note=D/'POSTBOOT_CORE_FULL20K_CPU_ACTUAL_STAGE_REPORT.md';assert not note.exists()
    note.write_text('''# Post-boot Windows4090 core and complete20k CPU target admission

Human authorized independent Windows environment repair/training and enabled127.0.0.1:7897 proxy. Official missing NVIDIA artifacts actual downloaded/CRC/metadata/SHA reviewed, minimum offline Pythonbase and native wheelhouse kept. Old Task terminated by actual Windows reboot immediately after pip began;04C had STARTED only/noENDED, parent-child absent/Task0x41306/System1074+6006/6005 and actualboot reviewed. Not native/PPO failure or permanentnetwork failure. Independent actualmissing-set180packages installed, exact4editableLab/metadata/sourcepaths/nativeTorch-TD-NMS CPU passed, noCUDA/Kit/PPO.

Original dependencyfalse retained. Click corrected to official8.1.7. Kernel5.1 strictFastAPI.115.7 conflicts with exactLabStarlette.49.1; actualFastAPI.121/Starlette.49.1 explicitly retained for bounded headless scope. InstalledSDKsource/distributionmetadata not patched. Wholepipcheck remains false for this single pin; independent32 actualconsumer imports and inprocessASGI endpoints/modelvalidation/OpenAPI CPU pass are a scoped exception, not wholeHTTP/streaming/CAD or physicalGPU qualification. First remote test refused because postboot proxy port not listening; originalerror retained, two officialpublishedSHA artifacts transferredoffline. Staticfiles hasattr-only reader false corrected using actualPython fromlist semantics without reinstalling prior artifacts.

Apps21/.kit/renderconfig missing from original fourpkg-source package were added from testedlocalLabHEADb0542fe, exactworking-tree bytes. FirstHEADraw-byte assertion rejected beforewrite because Gitworkingtree CRLF vsHEADLF; originalsource/error preserved. Independent21file line-ending-only proof and targetCPU exactworkingtree extraction pass; noHEADraw-byteequivalence claimed. Actualsource SHA/sourcecompile/provenance retained.

OriginalV5 and savedV6 preparation bytes retained. IndependentV6a adds actual-substep-only contact integral/bin/COM/link/hardware readback and finite resource bounds, noextra step/reset/obs/RNG/actor input. COM oracle uses declaredAPI float32 storage and localCOM leverarm; rawdouble diagnostic separate, originaltolerances unchanged. CPU actual20k savedspawn/SDKquat source math/closedAST wrappers pass; observer GPUstillpending. max256updates pluswall3600s firstreached limit, manualsave2+final<=129, incrementalNPZ O(U)/retentionRAM7.864GB. OriginalRAM50.042GB/GPU22.993GB floors preserved; conservative pipeline2x+2GiB durable35.286GB. No speed-derived updatebound, no installedSDK/hyperparameter/DR/reward/geometry/route/clock edits.

New realtarget scope training_scope_full20k_left_repair_audited_v6a_20261013 actual materialize+verify-targetCPU once passed: originald05c19043064B/full20k107floating/99perenv actorcriticstdAdam/allD0D7/globalnamed+dictprivateCPU state, five explicitABI-onlymetadata paths, diskCPUroundtrip and strictnegative fixtures,1453frozen runtime/payload/SDK/app sourcefiles. UngrantedSDK draft actualprepared, approvedGPUfalse; noTask/GPU/SDK/native/CUDA/fullrestore/PPO launched orfuturepass fabricated. LatestavailableRAM33.935GB below50.042GB by16.107GB; userresource action requested, noMATLAB/otherAI/GUIkill or guardlower/delete. Newcurrentworkorder/solehourlymonitor ACTIVE/sametarget content verified, no extraobserver.

Existing native3060 fullpairedfeedback actual2/7 to3/7 onlyenv4/zero-delay negativecontrol/raw failures preserved; no productionDR change or50/70qualification. LocalGPU and oldLinuxmain remainpaused,旧RPC/TUI retired; WASD untouched. Soleoriginal0051188000/sevenextensions unchanged. CPU/SDK/noPPO costs excluded, pendinglocal6060.857uniqueparent cost and futureWindowsparentloadlearnsaveexit are evidence awaiting originalcanonical reconciliation, not secondledger/refund/extension/reserve. Allactualsource/successfalse/error/rejection/unusedprep/resource/receipt/monitor preserved; weights/NPZ/USD/ZIP/whl largeoriginals path-size-streamSHA indexonly/credentials excluded. Laterreceipt ordinarysupplement; pushfailure resumesexistingobjects, no experiment/record/tag replay.
''',encoding='utf8')
    old=safe.a.gitio.refs();rows,files=safe.capture_streaming(DEST)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def recorded_git(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(str(x).encode()+b'\0' for x in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
        return g(*args)
    rec.git=recorded_git
    sys.argv=['record_experiment.py','--id',ID,'--title','Admit post-boot Windows4090 core and coherent20k CPU target with retained failures','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Core actualCPU imports/sourceversions pass; originalpipcheckfalse explicitweb-pin exception. All21apps workingtreeexact/HEADCRLF-only, V5/V6 originals retained/newV6a closedsource math and realtargetCPU107/99/1453freeze pass, ungrantedSDK noGPU. Resource floor notlowered/RAMactionpending, solehourlymonitor actualverified, originalcanonical/localpause unchanged.','--push']
    rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
    head,obj=g('rev-parse','HEAD'),g('rev-parse',tag);safe.a.verify(rows,old,head,tag,obj)
    v=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_and_tracked_SHA_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),later_receipts_require_ordinary_supplement=True)
    (D/'reports/POSTBOOT_FULL20K_CPU_STAGE_GIT_RECORDED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('POSTBOOT_CPU_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_objects_no_record_tag_commit_GPU_replay=True),indent=2),encoding='utf8')
        raise
