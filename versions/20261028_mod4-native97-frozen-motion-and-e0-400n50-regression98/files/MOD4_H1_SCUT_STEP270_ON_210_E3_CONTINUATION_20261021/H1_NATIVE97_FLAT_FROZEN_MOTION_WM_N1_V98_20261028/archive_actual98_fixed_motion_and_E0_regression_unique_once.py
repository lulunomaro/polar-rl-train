from pathlib import Path
import runpy,json,traceback,tomllib
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=S/'reports';N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'
previous=runpy.run_path(str(N/'archive_actual97_two_first_learning_slots_unique_once.py'),run_name='old97_unique_definitions_only');s=previous['s'];ID='mod4-native97-frozen-motion-and-e0-400n50-regression98'
for a,b in [("'fudan':'mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'/'reports'","nr=T/'H1_NATIVE97_FLAT_FROZEN_MOTION_WM_N1_V98_20261028'/'reports'")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
# Never archive new raw body/control traces as text; only their existing producers' metadata.
needle="   digest=producer.get(str(p));origin='existing_producer_receipt' if digest else None"
position=s.index(needle);line_start=s.rfind('\n',0,position-1)+1;condition=s[line_start:position]
assert condition.lstrip().startswith('if suffix not in ') and condition.rstrip().endswith(':')
replacement=condition.rstrip()[:-1]+" or (p.name.endswith(('ACTUAL_400HZ_31BODY_FRAMES.jsonl','ACTUAL_100HZ_CONTROLS.jsonl')) and 'actual_case_text' in p.parts and 'H1_NATIVE97_FLAT_FROZEN_MOTION_WM_N1_V98_20261028' in p.parts):\n"
s=s[:line_start]+replacement+s[position:]
ns={'__name__':'actual98_unique_definitions_only','__file__':previous['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='7dc61dea431ea662d04af6150de6fb11c6b92aeb' and not git('status','--porcelain') and len(git('tag','--list').splitlines())==1468
 case=json.loads((R/'NEW98_SAME_CASE_MOTION_GOAL_AND_WM_TEXT_ANALYSIS_UNITS_V2_ACTUAL.json').read_bytes());assert case['passed'] and case['controls']==500 and case['flat_events']['takeoffs']==0
 assert json.loads((L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1/reports/E0_210_BOUNDED_FROZEN_REGRESSION_ORIGINAL_RESULT_RETURNED_ACTUAL.json').read_bytes())
 for p in [L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1/FROZEN_ACTUAL_E0_SOURCE_CASE_COMPLETE_HANDOFF_INDEX_V1.json',L/'NEW_HOST_STAGE11_COHERENT_VENDOR_TORCH211_SOURCE_V1/FROZEN_STAGE11_SOURCE_AND_ACTUAL_STARTUP_COMPLETE_INDEX_V1.json',L/'NEW_HOST_STAGE11_READONLY_TERMINAL_FULL_LOG_SOURCE_V1/FROZEN_UNUSED_STAGE11_READONLY_TERMINAL_INDEX_V1.json']:
  assert p.is_file(),p
 seed=G/'versions/20261028_mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning/ordinary_closed97_formals_and_stage10_runtime_conflict/ORDINARY_CAPTURE_INDEX.json';ns['prior'](seed)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[S,L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1',L/'NEW_HOST_STAGE11_COHERENT_VENDOR_TORCH211_SOURCE_V1',L/'NEW_HOST_STAGE11_READONLY_TERMINAL_FULL_LOG_SOURCE_V1']
 extras=[T/'prepare_NEW98_qualified97_fixed_frozen_motion_and_WM_case_once.py']
 note='''New actual98 fixed frozen-motion and E0 regression phase, one annotated trial only. Qualifiednative97 formal6b3c... tested in one fresh N1 fixedseed20260928 mean episode, original done or max500controls/2000callbacks5s, actual onlytime_out. Two flat requests, no takeoff/height/landing/recovery/invalid. FullPi+WM parameters andnormalizers literally unchanged, no learner/optimizer/learningGO/account writer. One NEW97 model load for this concrete frozen case, no old91/93 PT. Exactsource97 payload andfreshSDK/RSL/source/400backend/reset/preload/clock/privatec27 resource/CNone guards before forward. Fullbody andactualactions collected once, originalcase kept. Rawbody/controlJSONLs metadata only forGit, no replay/model/raw rerun forarchive.

Derived same-case text-only evidence: actualsimultaneous bothwheelminimum peak1.028746mm against50mm. Body changes stance while wheels stayground. Fixed rootheightgoal.247...297m is5.693...11.378cm below actual body during both requestedflight intervals. This is a concrete reference/conditioning geometry candidate, NOTproven solecause or mechanicalimpossibility. Teacheractual-action WM maxwheelheight1steperror.589mm/8step1.128mm only this grounded case; no airborne/counterfactual/closedloop policy accuracy proved. Allsource, actualcase, sourceReader missingfilename error, initialsnapshot cache KeyError andpuretextcorrection, initialfigurewrong normalized-actionlabel andcorrected rad/rad_s figure retained. No physics/model replay for these reader/label fixes. Actualpublic_request is original270phase; plot derivesprivateflatphase from admittedsource, avoiding a false phase mismatch diagnosis. No jumpgraduation fromreward/update/GPUutil. Ultimate270goal remains unachieved; nextH1 source consistency repair before newtyped admission, not unchangedblindwindow.

DelegatedE0 source210 actualfrozen20k mean regression120controls2.4s960callbacks passed, original82update a92 lineage/17Adam641200/D1-D7/40050/physicaldelay restored andunchanged. Whole120controltermination/truncation0. WholewindowtrackingMAEforward.073575m/s andyaw.159532rad/s includesstartup; laststep.027569/.073039 distinct. PrefixNPZ930438B existingproducerSHA andselected32before/terminalstates notcompleteWMdataset orwholeexpertgraduation. Full27originaltexts/sourceV1missing700USDdependency refusal andV2complete464input admission/actualCIM/fresh937 UUID/NTFSrw/account97closedreadonly/resource/wait0/privateEX release retained. No newPPO/normupdate/ledgerwriter/fee/refund. Thirdpartyuntouched, no unknownPID queries.

New86 actualStage11detached1800s aftercoherentofficialTorch2.11cu128/vision.26 primarymetadata andpublishedSHA proofs. Explicit NEWvendorenvironment, originalTorch210env andexactLab runtime.py unchanged; previous typedcoverage-test-extra andpackaging26metadata deltas retained. Allrequireddependencies jointresolve/install/pipcheck, no runtimeignore. ParenthesizedRequires-Dist metadata-selector false andoffline semanticfix retainoriginalfullbytes. Source/readylifecycle exactCPUinverse audit, startup8991return0, sup510728/create1793181031.11 installer510729/.16. This isonlyinstallerstartup, NOTSDK/GPU/fullrestore/PPOreadiness. Newexactreadonly terminalreader frozenunused, boundafterepoch1793182832.880596=18:20:32.88BJT. Neverrerunoldlauncher/earlypoll. Futureterminal/runtimeoutputs explicitlypending ordinaryappendafteractualreturn. Only/data/robemo/polar-rl-train, no system/globalpip/driver/DNS/outsidewrites; secretstdinmemoryonly.

Priorclosed97 fullformalCPU/fees/events/Stage10failurealreadyordinaryremote7dc61dea431ea662d04af6150de6fb11c6b92aeb, unique97tagnotrepeated. Thisnewactual98phase uniquelyrecords actualfrozenH1/E0cases plusboundedStage11deploymentstartup, protecting1468oldtagobjects/peels. Samehourlymod4-10/noGoal. AllfullUTF8/source/errors/false/reports retained; PT/raw/USD/NPZ/media only realpathbytes existingproducerSHA/unknownexplicit, no binary/GPU/host readsforGit. Active remaining-expert inventory andfullWMtap are pendinguntilfrozen; no fabricateddataset or4cardsconcurrenttraining. Pushfailure resumesexistingobjects, no retag. PostGit verification conversationonly.
'''
 ns['run_stage']('fudan',roots,extras,note,'Diagnose real native97 non-jumping motion and verify E0 400N 50Hz frozen regression')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ACTUAL98_UNIQUE_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_tag_again=True),f,indent=2)
  raise
