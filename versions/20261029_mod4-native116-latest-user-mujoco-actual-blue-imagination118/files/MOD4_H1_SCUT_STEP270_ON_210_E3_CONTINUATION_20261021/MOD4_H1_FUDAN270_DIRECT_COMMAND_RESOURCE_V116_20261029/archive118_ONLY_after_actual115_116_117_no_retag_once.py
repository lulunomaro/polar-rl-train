"""Resume ONLY unused118 after115/116/117 were already pushed and verified.
OriginalV3 stopped at an indentation-sensitive raw-classifier source assertion.
No record/push of a prior phase is repeated.
"""
from pathlib import Path
import json,runpy,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
S=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029'
p=runpy.run_path(str(N/'archive_ACTUAL115_true_visual_and_ACTUAL116_direct_command_unique_phases_once.py'),run_name='definitions_only')
git=p['git'];ID='mod4-native116-latest-user-mujoco-actual-blue-imagination118'
def main():
    assert git('rev-parse','HEAD')=='12170aad09dccdad42e97258f1888e45e2d5383b' and not git('status','--porcelain')
    assert len(git('tag','--list').splitlines())==1483 and not git('tag','--list','trial-20261029-'+ID)
    assert git('rev-parse','trial-20261029-mod4-3060-readonly-plan-four4090-terminal-dashboard117')=='b9cb0e134a172a2fc3633cfcdd5fa86d88f1ea6b'
    s=p['old']['s'];lines=[x for x in s.splitlines() if "'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029' in p.parts" in x and "'actual_case_text' in p.parts" in x and "suffix='.mod4_raw_external'" in x];assert len(lines)==1
    line=lines[0];new=line.replace('H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029',S.name);assert s.count(line)==1;s=s.replace(line,line+'\n'+new)
    a="'fudan':'mod4-native111-fixed-world-wm-heading-repair114'";assert s.count(a)==1;s=s.replace(a,"'fudan':"+repr(ID))
    a="nr=T/'MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029'/'reports'";assert s.count(a)==1;s=s.replace(a,'nr=T/'+repr(S.name)+"/'reports'")
    assert s.count("'--kind','training'")==1;s=s.replace("'--kind','training'","'--kind','diagnostic'")
    ns=dict(__name__='capture_actual118_only',__file__=p['old']['ns']['__file__'],same_sha_entries={});exec(compile(s,ns['__file__'],'exec'),ns);ns['git']=git
    for name in ('mod4-native111-fixed-world-wm-heading-repair114',p['ID115'],p['ID116'],'mod4-3060-readonly-plan-four4090-terminal-dashboard117'):
        ns['prior'](G/('versions/20261029_'+name)/'COMPLETE_FILE_CAPTURE_INDEX.json')
    for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
    proof=json.loads((S/'display/reports/USER_DISPLAY_DATA_COMPLETE.json').read_bytes());assert proof['passed'] and proof['display_is_latest_qualified116'] and proof['actual_controls']==431
    report=(S/'reports/FINAL_ACTUAL118_LATEST116_VISUAL_USER_VIDEO_AND_REWARD_SCOPE.md').read_text(encoding='utf8')
    note='''NEW118 is a genuine user-requested latest116 physical motion+blue imagination+trueMOD4 MuJoCo display phase, separate from old115/case112. This controller resumes ONLY unused118 after actual115/116/117 remote verification; all1483existingtagobjects/peels protected. OriginalV3 failed before118record because its literalraw-classifier source assertion assumed wrongindentation; fulloriginaltrace retained. NEWresume identifies the exact existing112classification line by its complete literalpath/actual_case_text/rawfilenames, clones it for the exactnew118root withoriginalindentation, and changes no othercapturepolicy. Actual118 controls/400Hzraw JSONL neverread/hash FORGit; existingproducer pathbytesSHA only. AllcompleteUTF8/source/errors/receipts/derivedCSV retained; PT/USD/STL/NPZ/PNG/MP4/media metadataonly. OriginaluserMP4outsideworkspace notcopied/hashed. Newphysicalcase1modelread andnewCPUdisplay1modelread are distinctnecessarypurposes; no repeatGPUphysics/oldmodel/raw/initialCPU forGit. NewnecessaryderivedNPZ sequenceanalysis readsits3actualarraysonce, noPT/physicsraw. Nativevisiononly.

The attachedreview contains allactual116lineage/sourceSDK/resource/reset/preload/admission/clock/frozenweights/normalizers/4.31sclosure/15.894mm100Hzendpointscope/grayactual-blueimagined/windowcreation/277meshmetadatareuse/video111vs latest116/actiontimeline/endpointprocessrewardcounterexample. Goalreal270cross/fullfootprint/topcontact12+stable200=.5s UNACHIEVED. No newlearning/optimizer/GO/account/grant/refund/canonicalcopy/guardrelaxation. Humanreward-before-use nowincludesexplicitvalidjump/crossprocesscounterexamples, not merelyboundedmonotonicendpointscore. Userwindowremainsopen/active logs futureordinaryappend, do notcloseorstopitforGit. Existingmod4-10hourlytarget remainssame; currentappreceipt wascaptured116. Future118supplementsordinaryappend, neverretag115/116/117/118. Pushfailurecontinueexistingobjects. PostGitconversationonly,no reportchasingHEAD.
'''+report+'\nActualdisplayproof:\n'+json.dumps(proof,ensure_ascii=False)
    errors=sorted(R.glob('UNIQUE115_116_117_118_V3_ARCHIVE_ORIGINAL_ERROR_*.json'));assert errors
    ns['run_stage']('fudan',[S],[Path(__file__),*errors],note,'Show latest116 MOD4 motion blue imagination and audit observed backward-standing-reset failure')
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('UNIQUE118_ONLY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),resume_existing_objects_no_rerecord_retag=True),f,indent=2)
        raise
