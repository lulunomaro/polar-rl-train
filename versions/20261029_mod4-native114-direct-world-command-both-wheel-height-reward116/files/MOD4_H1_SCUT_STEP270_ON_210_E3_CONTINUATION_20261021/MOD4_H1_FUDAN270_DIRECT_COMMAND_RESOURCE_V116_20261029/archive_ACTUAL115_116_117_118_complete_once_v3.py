"""Four actual phases once. Raw118 JSONL is indexed, never read/hashed forGit."""
from pathlib import Path
import json,runpy,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
S=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029'
v2=runpy.run_path(str(N/'archive_ACTUAL115_116_117_complete_sources_results_once_v2.py'),run_name='definitions_only')
ID118='mod4-native116-latest-user-mujoco-actual-blue-imagination118'
def main():
    review=S/'reports/FINAL_ACTUAL118_LATEST116_VISUAL_USER_VIDEO_AND_REWARD_SCOPE.md';assert review.is_file()
    proof=json.loads((S/'display/reports/USER_DISPLAY_DATA_COMPLETE.json').read_bytes());assert proof['display_is_latest_qualified116'] and proof['actual_controls']==431 and proof['read_counts']['controls_reads']==proof['read_counts']['checkpoint_decodes']==1
    endpoint=json.loads((S/'reports/USER_JUMP_VS_STANDING_ENDPOINT_HISTORY_COUNTEREXAMPLE_CPU_ACTUAL.json').read_bytes());assert endpoint['total'][0]==endpoint['total'][1]
    v2['main']()
    capture=v2['original_capture'];env=capture.__globals__;old=env['old'];source=old['s']
    a="   if 'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029' in p.parts and 'actual_case_text' in p.parts and p.name.endswith(('ACTUAL_100HZ_CONTROLS.jsonl','ACTUAL_400HZ_31BODY_FRAMES.jsonl')):suffix='.mod4_raw_external'"
    b=a+"\n   if 'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029' in p.parts and 'actual_case_text' in p.parts and p.name.endswith(('ACTUAL_100HZ_CONTROLS.jsonl','ACTUAL_400HZ_31BODY_FRAMES.jsonl')):suffix='.mod4_raw_external'"
    assert source.count(a)==1;old['s']=source.replace(a,b)
    note='''NEW118 is a genuine newly requested latest116 actualmotion/pairedWM plus trueMOD4 gray-blue MuJoCo display purpose. Original115111/case112 window is kept as history, not relabeledlatest. Qualified116h1SHA78f5840e...78d9976/global20809-208090WM-19977Pi is input; newfixedseed20260928 originalown400N N1 case. ActualfreshSDK/RSL/source/reset/preload/20smax/request/locks/lightGPU/CNone before oneNEWpurpose checkpointload. Originalgeneratedsuffixv112draft NOT_SELECTED;selectedV2changesonlynewunusedremote namespace116v118 beforeexecution, alloldonceuntouched. Actualcase originalclosure termination at431controls1724callbacks4.31s; othercachedterm flagsfalse;1originalcontactrelease/0crosslandrecovery/skillfalse. No training/optimizer/normupdate/account/learningGO/forces/script/fakeairreset. Original2mmperenvguard maintained. Case/helperwait0/environmentclose/lockrelease returned beforelocalvisualstage.

OneNEWlocalCPUvisualpurpose one new118controlsread+one116checkpointdecode/integrity, CPU Torch2.7.0+cu128/CUDAuninitialized. No old112/111/108 model/raw, no normal86/critic/optimizer construction. Eightyclosedloop32step bluebranchesfromactualstate/context/tenactorobservations, nofutureactualactions/states. FirstCPUvsGPUactionmax1.66893e-6,rootorientationmapping8.94e-8. Same116Pi/WM/normsliteral. All277trueMOD4visualmeshes/554gray-bluegeoms/31namedbodies reused fromimmutable111/116assetmanifest byte/SHAmetadata equality, no collisionprimitive substitute/newmeshbake. Gray is actual118 PhysXrecording4.31s; blue same116prediction. MuJoCoDISPLAYONLY, not MuJoCophysics/livehardware/newtraining. ActualnativewindowPID73512/create19:23:08.935167BJT titlelatest116/actual118, GUIvisible/nativeframebuffer visuallychecked, correctfive-argmousecamera appliedbeforelaunch. Sourcefile/screenshot/owncreationreceipts preserved. Old111windowPID53896 observedout, nokill; activeuserwindowfutureexit/log explicitpendingordinaryappend. NoGPU/host/model/binaryquery forGit.

Latesthuman supplied17:38NVIDIA MP419,135,989B/19.066989s and questioned reward definition, then describedbackward-lean-stand-charge-reset. Nativeframeanalysis19frames/contactsheet only, noexternalvision/Luna. HUDproves111/case112,.25xspeed,lateepisode16.84s→0.05s jump then1.31/2.81s;notcontinuous19sphysicalcoverage. Grayhasflexion/standing/smallmotion but no visiblecoordinatedpush-offflighttuckcrossland;bluenotphysicalproof. This oldvideo and current116failure keptseparately, notusedtohideongoingfailure.

NEWexplicitnecessaryderivedposeCPUdiagnostic reads onlygenerateddisplayNPZ once/threeactualarraysonce, no originalphysicsraw orPT. Actual116first2srequestOFF rootx.056039→-.166173 (~22.2cmbackward),bodyrise.13803m while maxbothwheelheight.00029587m;bodyrise≠jump. AfterrequestON reachesrootx.255109/bodyz.40712at4.14s whilewheels~floor;closureends4.31s/rootx.135551. Peakbothwheelbottom15.894mm at100Hzendpoints, not full400Hzpeak/contact-provenflight/270success. ViewerloopsONEendedcase, notmultipleindependentresets. Originalexactcachedtermination/fullnewderivedCSV retained. Neverrelaxguardorblameuniquereward/WM/policy/mechanicalcausewithoutnecessaryevidence.

Current116isCUSTOMdirectworldvelocity/bothwheel270height/top-supportobjective, notunmodifiedFudanjumpPPO. Sourceexplicitlyleavestuck/extension/flight/bodyheightpositive termsdiagnosticonly. Newsource-onlyanalyticalendpointcounterexample givesidentical.15976035594940186 quiettoprewardforpastvalidtakeoff/crossfalsevs true labelsbecausehistorynotconsumed. Samecurrentstate, notsimulatedfeasibleclimbnoruniquephysicalcause. Priorbounds/gradients/approachmonotonicchecks didnotqualifyfulljump-processdefinition. Humanreward-before-use remains: no newlearninguntilowngeometry/validjump-cross-landprocess acceptancealignment addressed; no blindtuckbonus/script/force/fakeairreset/coldrestart/unchangedwindow. Goalstillreal270dualwheelcross/fullfootprint/topcontact12+stable200*.0025=.5s UNACHIEVED.

Allrawnew118jsonl uses exact metadata-only classification beforeanyread/hash:existingproducerpathbytesSHA retained. Every originalsource/false/error/fullUTF8/derivedCSV/video-reviewreport/receipt retained; originalMP4outsideworkspace pathbytesunknownSHA only. PT/raw/USD/STL/NPZ/mediaonlyactualpathbytesexistingproducerSHA/unknown. Fouractualunique115/116/117/118 tagsviarecord_experimenteachONCE;protect1480priorobjectspeels+new115/116/117;pushfailurecontinueexistingobjects, neverrerecord/retag. Samehourlymod4-10target/no newGoal/newautomation; source/appreceiptcurrentreviewbeforeGit. PostGitverificationconversationonly,no fileschasingHEAD.
'''+review.read_text(encoding='utf8')+'\nActual display:\n'+json.dumps(proof,ensure_ascii=False)+'\nSourcecounterexample:\n'+json.dumps(endpoint,ensure_ascii=False)
    prior=v2['base']['G']/('versions/20261029_'+v2['ID117'])/'COMPLETE_FILE_CAPTURE_INDEX.json'
    capture(ID118,S,[S],note,'Show latest116 actual MOD4 motion and blue imagination and audit user-observed failure','diagnostic',prior)
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('UNIQUE115_116_117_118_V3_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),resume_existing_objects_no_rerecord_retag=True),f,indent=2)
        raise
