from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
E=T/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V1_20261101';p=E/'INDEX_E2_FROM226_FROZEN.json'
b=p.read_bytes();assert len(b)==5787 and hashlib.sha256(b).hexdigest()=='01d1d8bb70448de04b3080d11ded5597be422d718351897b9da7541a525c2fa5'
row=dict(epoch=time.time(),kind='FROZEN_E2_TARGET_METADATA_AND_TYPED_EVIDENCE_SOURCE_ONLY',roots=[str(E)],INDEX=dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()),
 trials=[dict(ID='E2_FROM226_V1',status='SOURCE_ONLY4new+1embeddedAST/4PY-JSONSHA,oldfixture0/model-assets-raw-Torch-SDK-network-Git0')],
 ROOT_next='ReadHANDOFF_E2_FROM226_V1.md. Newactualmetadata purpose/ROOT freshexact227D authority orafterclosurefreshCNone/newresource+heldGPU+source-link are still pending. Targetonlyrunner is not SSH wrapper;noactualcase or trainingGO.',
 original_E2=dict(source_SHA='b3ae stored226qualified metadata',iteration=42822,Adam17=859300,LR=.000225,max_controls=1200,seconds=24,num_envs=20000),full_skill_or_SuperMimic=False)
(R/'CAPTURE227_ADDITIONAL_FROZEN_E2_SCOPE.json').write_text(json.dumps(row,indent=2,ensure_ascii=False),encoding='utf8')
old=read(R/'AUTOMATION_ACTUAL227D_FIRST_NORMAL_UPDATE_REQUEST.json')
header='''LATEST_E2_FROM226_SOURCE_FROZEN_NOT_RUNTIME. Independentlyfrozen T/E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V1_20261101/INDEX_E2_FROM226_FROZEN.json SHA01d1d8bb70448de04b3080d11ded5597be422d718351897b9da7541a525c2fa5/10files. SOURCEonly4new+1embeddedAST/4frozenPY-JSONSHA passed;old226probe/oldfixture/models/assets/raw/Torch/SDK/network/Git0. ReadHANDOFF_E2_FROM226_V1.md forRoot target-onlymetadata wrapper andJSON-onlytypedfinalizer. SupportsactualfreshEXACT227D_ACTIVE orFRESH_CNONE,neverfakeCNone;currentbinding merelyexpected andROOTmustfreshownerpid/create/exe/argv/cwd/run/fullGO/canonicalmatch. Actualmetadata purpose,resource+GPUheld/source-link/admission/fullrestore/native24/full24s1200controls skill stillPENDING. No newGO/writer orallSMclaim. ThisfrozenE2sourceincludedinactual227archive;original226/213unchanged.

'''
req=dict(old,prompt=header+old['prompt']);dest=R/'AUTOMATION_ACTUAL227D_FIRST_AND_FROZEN_E2_UPDATE_REQUEST_V2.json';dest.write_text(json.dumps(req,indent=2,ensure_ascii=False),encoding='utf8')
scope=read(R/'CAPTURE227_ACTUAL_FROZEN_SCOPE.json')
# Preserve original frozen capture value as V1; the new app request is the
# concrete final pre-record selection, not an overwritten error/result.
(R/'CAPTURE227_ACTUAL_FROZEN_SCOPE_V1_BEFORE_E2_APP_SUPPLEMENT.json').write_text(json.dumps(scope,indent=2,ensure_ascii=False),encoding='utf8')
scope['automation_request_file']=dest.name
(R/'CAPTURE227_ACTUAL_FROZEN_SCOPE.json').write_text(json.dumps(scope,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(passed=True,extra_source_frozen=True,new_app_request=str(dest))))
