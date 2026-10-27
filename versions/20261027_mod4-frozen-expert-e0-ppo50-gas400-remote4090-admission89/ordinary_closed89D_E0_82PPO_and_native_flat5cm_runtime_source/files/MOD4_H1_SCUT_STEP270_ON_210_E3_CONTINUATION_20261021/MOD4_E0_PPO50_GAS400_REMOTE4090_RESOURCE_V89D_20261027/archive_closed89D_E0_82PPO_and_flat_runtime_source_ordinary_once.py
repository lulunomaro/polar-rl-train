"""Ordinary closed89D and new flat-source supplement; no record/tag."""
from pathlib import Path
import importlib.util,json,time,hashlib,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
p=N/'archive_actual89C_failure_89D_first_PPO_and_flat_course_ordinary_once.py'
sp=importlib.util.spec_from_file_location('old_archive_definitions_only_not_main',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
s=m.s
s=s.replace('ordinary_actual89C_logger_failure_89D_first_PPO_and_flat5cm_course','ordinary_closed89D_E0_82PPO_and_native_flat5cm_runtime_source')
s=s.replace('ACTUAL89D_FIRST_PPO_ORDINARY_GIT_NOTE.md','CLOSED89D_FLAT_SOURCE_ORDINARY_GIT_NOTE.md').replace('ORDINARY_FIRST_PPO_COURSE_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED89D_FLAT_SOURCE_CAPTURE_STARTED_ACTUAL.json')
ns={'__name__':'ordinary_closed89D_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']

def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)

def main():
 assert git('rev-parse','HEAD')=='a69875c6ed3b4989ee5a2d37911e9cbc5e2543e4' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1463
 assert json.loads((R/'E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json').read_bytes())['passed']
 ns['prior'](G/'versions/20261027_mod4-frozen-expert-e0-ppo50-gas400-remote4090-admission89/ordinary_actual89C_logger_failure_89D_first_PPO_and_flat5cm_course/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 F=L/'H1_FLAT_JUMP_CURRICULUM_20261027'
 root_index=F/'runtime_adapter_candidate_v1/ROOT_FLAT_ADAPTER_FROZEN_SOURCE_INDEX_ACTUAL.json'
 assert root_index.is_file(),'freeze root source first'
 helper=F/'native88C_to_flat_source_contract_candidate_v1/INDEX.json'
 assert helper.is_file(),'current helper source must finish/freeze before capture'
 state=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 prompt=R/'CURRENT_CLOSED89D_E0_82PPO_FLAT5CM_SOURCE_ONLY_MONITOR_SOURCE.txt'
 assert state['prompt']==prompt.read_text(encoding='utf8').rstrip('\n') and state['status']=='ACTIVE' and state['rrule']=='FREQ=HOURLY;INTERVAL=1'
 roots=[N,F,L/'E0_89D_formal_FINAL_initial_CPU_reviewer_source_20261027',L/'E0_89D_formal_FINAL_reader_close_schema_fix_v2']
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v243.py']
 note="Ordinary supplement of consumed89, no new actual flat trial/tag. Original E0 baseline PPO50/gas400 closed normally on remote4090 with82 NEW updates/17Adam641200. Complete formal model14031973B/a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a twohost producerSHA and initial wholeCPU passed. Actual fee3664.132122516632s, closed558113.8296625614; canonicalNone/original owner/node/worker waited-out and locksfree at collection. Full original formal/text/clock/gas/source/D1-D7/curve/error records captured. No skill graduation, E0 original frozen label unchanged and no WM transition tap claimed.\n\nInitial wholeCPU reviewer required APP_CLOSED, which actual ending did not publish. That attempt failed before any torch import or PT load. Worker source does attempt APP_CLOSED after app.close; absence cause remains unproven. V2 uses original APP_CLOSING plus genuine waited worker exit0, original error=false and original allownwaited receipts, retaining all independent closure/producer/cost/model checks. Formal model initial CPUload total1; no input weight/normal86 reread. A root source-derivation assertion incorrectly assumed APP_CLOSED absent from worker source, corrected and preserved in append-only report. No training/account change.\n\nLatest direct human asks whether flat jump has started: NO. Root explicitly corrected the earlier ambiguous 'start' wording. Native own flat5cm source/provider/MDP/privateframebridge/realphysicscounter/entry/finalizer are prepared and CPU-tested as scoped, not installed/GO/actual optimizer updates. Private frame preserves actual public age and deterministic-ID delay without changing learner/replay/RNG/reset. Goal146x10/obs86/packed127/xi31 and WM/Pi/Critic/3opts architecture unchanged. Reference is an own low-jump task primitive and neutral-shape witness, with unmeasured joint trajectories masked; it is not measured Fudan successful joint motion. Physical counter uses existing actual collider/force caches, authored preedge floor and signed5ms Fz, no extra queries/manifold-ID claim. Takeoff/height50mm/12landing/200stable callbacks required; standing cannot credit. Original V2 mistakenly added maxbottom1mm, V3 removes only that invented upper bound to match original support logic; lower skin/support/actualheight/stability remain. Original source/errors/tests kept.\n\nRoot analytic adapter sourceCPU tests actual named30 neutral geometry,goal1460/actor86/critic165, desired root-height gradient, dynamic force context and privateframe exact parent action/return. Original missing local counter import failed before any derived-data/model action; V2 fixes source path only and passes. Added ground angular/heading costs address stability and have separate new tiny gradient tests, not oldcase repeats or real learning evidence. New phase-sampling observer decodes private encoded frames; sampler/RNG/error/return forwarding unchanged. Current native127 already predicts/supervises aux54 and terrain-relative3, advancing imagined frames; old legacy128 missingdistance/frozencontext counterexamples are not a current127 rootcause. Saved WM/action/autograd not rerun or called broken.\n\nQualified native88C fullstates remain distinct method sources, not E0/PPO. New88C-to-flat typed validator/restore contract is source-only and frozen separately. Genuine next nativeflat stage still requires exact unused source/target SDK/fullnativeCPU/reset400/command0/source binding, fresh resources/current sole72 finite account and GO/actual NEW WM+Pi. No oldR5-only loader blind reuse, oldonce/hotpatch/newwriter or speculative current GPU claims. One sequential helper only; all source/fixture/error/scope-index mistakes preserved. Same hourlymod4-10/no continuousGoal, original finite3900/3600/300/reserves/thirdparty/old210 retired rules intact. No localGPU/249 training or new weights/binary reads forGit. All1463 tags objects/peels protected; full UTF8/source/errors/reports and binaryexisting path/bytes/producerSHA only. PostGit conversation-only.\n"
 ns['run_stage']('fudan',roots,extras,note,'Qualify closed E0 PPO50 gas400 and prepare honest native flat-jump integration')
if __name__=='__main__':
 try:main()
 except BaseException:put('ORDINARY_CLOSED89D_FLAT_SOURCE_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True));raise
