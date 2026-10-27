"""One unique actual87 phase; all failed sources/CPU/GO/cost retained, no model reads."""
from pathlib import Path
import importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R3_20261027/archive_native86_full_single_frozen_replay_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed_archive_template_definitions_only87',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("'fudan':'mod4-native86-complete-single-frozen-replay'","'fudan':'mod4-own-fudan-h1-native87-source-and-available-gpu-startup'")
patch("nr=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R3_20261027'/'reports'","nr=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'/'reports'")
patch("prior_row=prior_entries.get((str(p),digest))","prior_row=prior_entries.get((str(p),digest)) or same_sha_entries.get(digest)")
patch("  entries.append(row)\n index=","  entries.append(row);same_sha_entries.setdefault(digest,row)\n index=")
patch("p.name in {'LICENSE','NOTICE','COPYING'}","p.name in {'LICENSE','NOTICE','COPYING','AUTHORS','METADATA','WHEEL','RECORD','py.typed'} or p.name.startswith(('LICENSE.','COPYING.')) or p.name.endswith('.json.partial')")
ns={'__name__':'native87_archive_definitions_only','__file__':str(m.engine),'same_sha_entries':{}}
exec(compile(s,str(m.engine),'exec'),ns);git=ns['git']

def main():
    assert git('rev-parse','HEAD')=='b99fb0228ea49dcd770ebf886f3becc8a001fce8' and not git('status','--porcelain')
    assert len(git('tag','--list').splitlines())==1458
    ID='mod4-own-fudan-h1-native87-source-and-available-gpu-startup';assert not git('tag','--list','trial-20261027-'+ID)
    assert json.loads((R/'CURRENT_ACTUAL87R3_GO_BUT_PRECONTROL_SDK_API_FAILURE_CLOSED_ORIGINAL_COST_WORK_ORDER.json').read_bytes())['sum_once']==139.45133090019226
    prior=G/'versions/20261027_mod4-native86-complete-single-frozen-replay'
    ns['prior'](prior/'COMPLETE_FILE_CAPTURE_INDEX.json')
    ns['prior'](prior/'ordinary_overnight_H1_goal_paper_and_adapter_source_repair/ORDINARY_CAPTURE_INDEX.json')
    for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
    active='native87_encoder_actual_SDK_API_fix_v1'
    pending=dict(epoch=time.time(),pending_ordinary_supplement=[str(L/active)],reason='One helper still authoring actual SDK encoder adapter at capture boundary; do not capture a mutable source as frozen',current_actual_stage_will_be_unique_once=True,poststage_new_reports_ordinary_only=True)
    with (R/'EXPLICIT_POST87_STAGE_ACTIVE_ADAPTER_PENDING_CAPTURE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(pending,f,indent=2)
    roots=[N]+[p for p in L.iterdir() if p.is_dir() and p.name!=active and p.name!='__pycache__']
    extras=[p for p in L.iterdir() if p.is_file()]+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(182,196)]
    note='''Native87 MOD4-owned converted Fudan jump: preserve complete source repairs and all actual startup outcomes. Goal remains active and unsuccessful; no new step success, native policy update, trained native FINAL or convergence claim.

Human requests SuperMimic paper/supplied open source, converts Fudan jumping to MOD4's own jump, and initially assigns all3cards solely to H1 repair. Later explicitly preserves the existing occupied16828 process and instructs use the TWO freecards. Unknown peer identity is not queried/stopped. Other experts and T2z remain paused. At most one sequential6.1Sol helper, no nested/parallel.

Qualified normal86 H1 source update138/17Adam832460 SHA0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394 is only a frozen policy/bootstrap witness. New native architecture, normalizers/threeoptimizers/replay/physical4096 episodes are fresh, no native86/exactPhysX restore or native-to-PPO promotion. Original joint30/action6, physical2.5ms/TGS32/4/100Hz/FP32, clip6/PD/delay/DR/true270dualwheelcross/topcontact+200callbacks stable recovery remain. Native objective is own converted-reference tracking on real and imagined state; original V8 physical reward and full trace remain separately recorded.

New seven-state WM uses physical73+dynamic54 packed127, true staticDR31, obs86 includes terrain-relative coordinates, goal146x10 carries value+known-mask. Dynamic54 includes contact18/torque30/oldprocessedtargets6 and evolves in WM rather than fixedxi. Original delayed ingress actions remain real executed controls, foreign Fudan transitions are never MOD4 WM truth. Explicit4096/horizon32/buffer1000/WM2048x3/Pi2048,1024,512,256/UTD.4/wm-only64/batches1024 differs from paper G1 reproduction settings; no causal convergence-speed guarantee or PPO auxiliary-loss assumption. Source-only failures/CRLF/shape/AST/readers and corrected modules are preserved.

Reference conversion preserves teacher ascent/tuck/orientation information, fits MOD4 closed-chain geometry, adds explicitly own step translation/contact recovery. Earlier controls-only ballistic candidate failed actual quarter-control FK sidewall clearance; false and original sources retained. Final reference9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3 uses constant horizontal flight speed, contact-phase braking, checked control/quarter-control wheel geometry margins. These are planning/kinematic results, not dynamics, motor-limit, actual contact or skill proof. No old raw/model/physics/render replay to generate this Git stage.

All real attempts preserved: transport182 installer sibling-import failure beforeSSH; V2 path source fix. Actual H1 source SDK CPU passed then dual16828 startup guard rejected occupied GPU before mkdir. Missing-only proof/resource audit retained H1 proof, showed c27 free; no unknown peer action. Free72 H1 source CPU itself passed, but parent identity proof failed because wrapper identity capture reused psutil Process.exe cache; actual approved wrapper/source/one no-SDK own-interpreter identity read and original failure retained. V4 fresh-instance exact pid/create/exe/argv/cwd capture and actual R2 sourceCPU/proofs passed. All source metadata checks remain exact; no blanket runtime inventory weakening.

R2 allout beforeGO: root packed h1 from e2 baseline and omitted H1-only OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json14271a0c033e98c88b434513fff7ad614996a94386e4a6fbbd6b926f319fd621. H1 remained ready locally but every control send failed FileNotFound; owner120s partial registration observed only recovery, then original timeout. Bothnodechildrenout, CNone, noGO/no fee, balance577055.9868602753 unchanged. Firstobserver NoSuchProcess error and missing-only original control errors remain original. New role closure requires file/Task/contract/manifest/schema plus actual installed325dependency SHA/import before sourceCPU pass; no secrets or network in this check.

R3 actual two source/SDK/RSL/whole bootstrap/strict roundtrip/tiny API/control dependency CPU and exact process proofs passed. Both actual signedGO and actual4096GPU/30joint/D0-D7 backend/TGS32/4 precontrol passed. Then both failed before first native control/Pi at root-added actual_encoder_joint_names: current ObservationManager has no get_term_cfg. The earlier source-only mock incorrectly supplied that nonexistent API; preserve it as a root integration error, not successful SDK semantics. Exact installed ObservationManager source34306bytes SHAde7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8 collected once for the specific observed failure. Next adapter is explicitly pending a separate ordinary supplement, not admitted/training-ready.

Original R3 sole72 writer independently settled47.77779150009155+91.67353940010071=139.45133090019226seconds. Both durationflags true, actual owner506728/nodes422253/506745/childrenout, COHORT_FINAL and canonicalNone. Closing576916.5355293751 is a snapshot. Worker rc0 caused by SDK close does not override original_errortrue/finalNone. No model or nativeFINAL exists from this attempt; no reviewer/model reload for a nonexistent FINAL. Partial text/error/log/cost/payload/source/proof preserved; no refund/rewrite/secondwriter/grant/old210account reactivation. Next scheduling must bind latest actual balance and allout, not the old577055 snapshot.

Sole72 finite authority original2268000/9historical, extensions[], strict86412.86069250107, each actualGO-terminal independent sumonce3900/3600/300 preserved. Original270mm success and single-env2mm resets unchanged; no FP64/bitwise/triangle extra gates. Old210 canonical permanently retired. Occupied16828 left alone. All reports/source/helpers/intentional rejection/partial/error/monitor receipts captured UTF8/plainordered; identical SHA text may reference existing committed full capture. Licenses/dependency text preserved. Model/raw/NPZ/etc only actualpath/stat/existingproducerSHA, unknown remainsunknown; no binary/GPU/host read forGit. Protect1458oldtagobjects/peels. One unique87phase tag now, no repeated record/tag; following source fixes/admission/results ordinary supplements. PostGit verification in conversation only.
'''
    ns['run_stage']('fudan',roots,extras,note,'Record native87 adaptation sources and truthful failed H1 startup costs')

if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NATIVE87_UNIQUE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_or_tag_twice=True),f,indent=2)
        raise
