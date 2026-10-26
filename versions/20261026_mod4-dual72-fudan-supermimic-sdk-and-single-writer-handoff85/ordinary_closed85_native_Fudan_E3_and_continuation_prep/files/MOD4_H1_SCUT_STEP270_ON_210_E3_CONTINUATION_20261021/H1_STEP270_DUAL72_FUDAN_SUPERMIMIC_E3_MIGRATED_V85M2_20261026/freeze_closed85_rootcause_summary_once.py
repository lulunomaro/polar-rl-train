from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';R=N/'reports'
out=R/'FUDAN_SUPERMIMIC_ZERO_TAKEOFF_FINAL_ROOT_INVESTIGATION_ACTUAL.json';assert not out.exists()
indices=[J/'agent_Fudan_SuperMimic_zero_takeoff_rootcause_cpu_20261026/FINAL_FROZEN_ROOTCAUSE_ARCHIVE_INDEX_ACTUAL.json',J/'agent_Fudan_SuperMimic_phase_replay_starvation_cpu_20261026/FINAL_FROZEN_PHASE_REPLAY_ARCHIVE_INDEX_ACTUAL.json']
verified=[]
for index in indices:
 value=json.loads(index.read_bytes());assert value['frozen'] and value['no_more_agent_writes_planned']
 for item in value['files']:
  f=Path(item['path']);assert f.stat().st_size==item['bytes']
  if f.suffix.lower() in ('.py','.json','.jsonl','.md','.txt','.csv','.patch','.log'):
   assert hashlib.sha256(f.read_bytes()).hexdigest()==item['SHA256']
  else:raise AssertionError('Unplanned fixture binary, retain original metadata, do not hash for Git: '+str(f))
 verified.append(dict(index=str(index),files=len(value['files']),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),text_bytes_verified=True))
phase_root=indices[1].parent
phase=json.loads(next(phase_root.glob('attempt_*/ACTUAL_SOURCE_PHASE_REPLAY_STARVATION_CPU.json')).read_bytes())
result=dict(epoch=time.time(),status='INVESTIGATION_COMPLETE_SOURCE_AND_ACTUAL_SAVED_WM_CPU_NOT_DEPLOYED',frozen_helper_indices=verified,
 facts=[
 'Actual85 native fullFINAL finite680WM/58Pi; completed34.02M transitions no takeoff/cross/landing/recovery, not only a selected snippet.',
 'First Pi after48warmup+11*24=312controls. Real source ring64 retains248..311 for no-reset path, discarding one-shot100..179jump segment before any Pi; actualCSV312 matches. A reset@200 fixture retains12jump rows, so not universal across all envs.',
 'Actual last retained snapshot medianage633 and98.61percent afterrequest; this does not reconstruct all58 Pi sampling histories.',
 'Main task autograd not detached. Real savedWM actionJac and taskJac nonzero with finite-difference agreement; does not establish realphysics gradient correctness.',
 'Actual source CPU counterexamples show missingstepdistance in actor/WM/critic and postapex preedge height-gradient gap; imagined dynamiccontact/torque/request fixed16steps unlike WM supervised context sequences.',
 'Quaternion pack initial hypothesis REFUTED by actualSDK3.x xyzw contract; old false, intermediate correction and finalcontrary reports preserved. No fix applied.'
 ],
 minimum_repair=dict(priority='Correct policy/replay/one-shot-reference timing first, without changing physical task or success criteria.',
   existing_candidate='agent_native_Fudan_continuation86_cpu, source-only frozen; preserve nativeFINAL weights/3optimizers/globaliteration68. New physical episode and freshreplay48, no repeated10WM-only iterations. Source fixture first Pi72 then96/120/144/168.',
   residual_risks='A single replay opportunity can still be sparse; log phase exposure and consider separately tested phase-aware replay. Missingdistance and fixeddynamiccontext need separate typed model feature/state contracts; static retarget feasibility is not dynamic actuation proof.',
   actual_runtime='No86payload/controller/Task/GO; must validate new actualsource/SDK/resources/original72soleauthority and currentclosed source before deployment.'),
 all_current_helpers_frozen=True,future_at_most_one_subagent=True,no_new_agent_or_training_or_remote_or_budget_change=True,
 preserved_errors=['wrong-premise quaternion report and corrections','original toyfixture/reader errors','source path typo/truncated reads and wrong folder reads classified in root reader-error notices'],
 git='Ordinary supplement to consumed85trial, no repeated record/tag. Archive all originalfalse and finalsource/CPU/closure/intent/fullreports together.')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
old=(R/'CURRENT_CLOSED85_ACTUAL_WM_PHASE_SCHEDULING_MONITOR_SOURCE_ACTUAL.txt').read_text('utf8')
latest='''LATEST_ROOTCAUSE_PHASE_FIXTURE_FROZEN_ALL_HELPERS_DONE_20261026. Root investigation is complete; read reports/FUDAN_SUPERMIMIC_ZERO_TAKEOFF_FINAL_ROOT_INVESTIGATION_ACTUAL.json first. Both source/gradient20file and phase/replay10file helper folders are frozen, root textSHAverified; no active helper or new delegation. Human afterthisround permits atmostONE subagent, no parallel/nestedagents.
Actual-source phase/ringCPU passed with actualCSV: fresh firstPi312, no-reset ring248..311 missesjump100..179; explicit reset@200 retains12jump rows, so neverclaim everyenv hadzeroexposure. Same actualtrainAST start68 continuation fixture firstPi72 then96/120/144/168, jump rows20/44/64at120/144/168. Existing nativecontinuation candidate is the smallest available scheduling fix, stillSOURCEONLY/uninstalled/unadmitted, no86payload/controller/Task/GO/fee. Preserve formalnative85weights/optimizers/globaliteration and actual72closedbalance; do not restartfresh10worldonlyagain. Add exactphasecoverage evidence before attributing learning gains. Missingdistance/frozenxi/static-vs-dynamic reference limitations persist, need separatetypedCPU/sourceadmission, neverblanketguardrelaxation. Old incorrectquaternionbug is explicitlyrefuted and mustnotbefixed.
RootactualWM diagnostic alreadyCONSUMED one newCPUread underuserdebugrequest: not oldreviewerreplay, noactor/GPU/physics/hash/raw/remote. The remaining work is source repair/admission and next properly scheduled authorizedtraining, not endless further speculative reads or blind identicalwindows. Do not rerun CPUfixtures merelyforGit. Currentresult qualifiedfinite models but zero taskevents, not skillgraduation.
All closure/errors/rootWMintent+partial+final/helpers/monitors ordinaryGit capture required; existing85tag1456 objects preserved, no repeatedrecord/tag. ActualGitreceipt outranks below pending wording. Samehourlymod4-10/currenttarget kept, unchangedpendingquiet; notifyonlynew material repair/result/resource/budget/network/useraction.
'''
(R/'CURRENT_CLOSED85_FINAL_DIAGNOSED_PHASE_FIXTURE_MONITOR_SOURCE_ACTUAL.txt').write_text(latest+'\n'+old,'utf8')
print(json.dumps({'passed':True,'frozen_text_files_verified':sum(x['files'] for x in verified),'summary':str(out),'no_GO':True}))
