"""Unique actual77 training stage; original76 closure is an already committed ordinary supplement."""
from pathlib import Path
import json, time, tomllib, traceback

N=Path(__file__).resolve().parent; T=N.parent; W=T.parent; G=W/'polar-rl-train'; R=N/'reports'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s=engine.read_text('utf8')
def patch(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage77':'mod4-three4090-same-v8-qualified76-continuation77'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)", "TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'", "'--kind','training'")
ns={'__name__':'archive77_utilities_only','__file__':str(engine)}
exec(compile(s,str(engine),'exec'),ns); git=ns['git']

def main():
    assert git('rev-parse','HEAD')=='dc3b960800a79e0fbc6bb9d1504b8bd58a4d0905'
    assert len(git('tag','--list').splitlines())==1448 and not git('status','--porcelain')
    first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
    assert first['H1_V8_sampled_excess_reward_and_original_success_standard']
    cpu=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
    assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
    assert cpu['sampling_acceleration_CPU']['V8_reward_publication_AST']['passed']
    proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert a['prompt']==(R/'CURRENT_ACTUAL77_THREE4090_SAME_V8_MONITOR_SOURCE.txt').read_text('utf8')
    assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    for p in [G/'versions/20261026_mod4-three4090-same-v8-qualified75-continuation76/COMPLETE_FILE_CAPTURE_INDEX.json',
              G/'versions/20261026_mod4-three4090-same-v8-qualified75-continuation76/ordinary_closed76_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json']:
        ns['prior'](p)
    note='Continue all three4090 cards on H1 step270, E2 world-moving and E3 recovery from complete76 fullstate models. H1 129/Adam811340 SHA8c2f34c521c292c6016e0c98292e030bbb28fd960bedfc52bf2dae104e0d1f59, E2 88/848660 SHAf59b556badebdfb4f701fd7cfbcc418dc9ef9149c3e8da02d261ae100c89bf96, E3 83/849160 SHAe2c17401553c7abc8b8bfc5000f6ad1178f8d6570f1f1c5fff5b958b6e6bcde8 passed full twohostSHA, wholeCPU finite fullstate17Adam x20, actor9 inclsixSTD/critic8 changes,270phase and50Hz checks. The same initial reviewerV3 model load adds raw saved distributionparams and current retained callbackticks without another checkpoint read. Original singlewriter independent fees3630.1116061210632+3652.2982087135315+3636.821255683899=10919.231070518494s, closed snapshot668508.0938296318; all normalduration flags true and ownprocesses/children/canonical/locks actually closed. Closed76 and new diagnostics already ordinary-committed at dc3b960800a79e0fbc6bb9d1504b8bd58a4d0905, no repeated trial.\n\nNew actual77 keeps the same V8 reward, original actor35/sixSTD/17Adam/PPO/DR/commands/clip6/PD/delay/physics2.5ms/TGS32/4/fullsave/success criteria. New guard is exact prior76 guard except unique77 auth filename; E2 installer only exact target77/previous76 owned paths differ, original copyloop/source/closure/resources retained. Prior76 H1 helper already asserts non-migration and is now reused unchanged. Allthree actual installed source/SDK/RSL CPU, payload-after-copy25GiB/GPU/RAM, original valid_ready, GO and firstcompletePPO passed; ownUUIDs and precise process identity verified, H1 existing traceindex V8term/Taskrecipe present. These are initial execution snapshots, not complete77 FINALs, continuous utilization or skill success. Current77 original fees pending, complete76 remains source.\n\nClosed76 saved48controls across20k have347 takeoff increments,1875 recordedbothcrossed envframes and no landing/recovery/success.100 selected cases include88 continuous. A new descriptive geometry comparison separates leading-edge crossing from the ORIGINAL complete wheel footprint inside top condition: case7242 has4 sampledframes of fullfootprint geometry while high, ending rearx.388878/frontx.517673/bothbottom.270002m, but no proven actual platformcontact/12landingcallbacks/200stablecallbacks. Other selected leading-cross cases still have rear beforeedge. A short fragment may end before landing, so no causal rootcause/learning gain or changed criterion is inferred. FINAL currently-retained episode flags/callbackticks are not wholewindow or frozen evaluation. V8 recorded scalar matches raw formula to9.313e-10; executed actions exactclip(raw,-6,6). STD rawparams and generic commandvelocity success metrics do not establish expert graduation or causality.\n\nA separate unused CPU-only lifetime goal counter candidate accounts original event deltas across known selected resets using already copied complete rows and one initialcounterread. Eight synthetic20k cases passed, including input immutability, reset events, no duplicates, invalid diagnostics and atomic text. It has no installed tracehook and is absent from77 payload; the current strict guard continues rejecting addedPython. Future integration needs exact source-hook/ordering/persistence/error review and actual SDK/source admission in a new unused namespace, not a blanket guard relaxation or hotpatch. Counts would describe completed stochastic training controls rather than frozen-policy graduation. This improves preparation without claiming another runtime change.\n\nAll sources, exact histories, reports and original errors remain. The wrong local H1phase source path and unapplied preparation patch syntax refusal were recorded as local reader/builder errors in the76 ordinary supplement; V2 preparation succeeded, no training failure or fee inferred. No budgetgrant/refund/copiedcanonical/clearactive/secondwriter/oldonce replay. Budget2268000/9 and strict86412.86069250107 three-slot guard unchanged. No subagents, automatic T2-z training, new model downloads or binary rehash for Git. Existing hourly monitor updated to actual77 timing and quiet unless meaningful. Binary originals indexed only by actualpath/bytes/previousproducerSHA. One unique actual77 stage; later saved additions ordinary only.\n'
    ns['run_stage']('stage77',[N],[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v119.py',engine],note,'Continue three experts from complete76 with the same H1 V8 and sampling acceleration')

if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('ARCHIVE77_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeated_record_tag_or_training=True),f,ensure_ascii=False,indent=2)
        raise
