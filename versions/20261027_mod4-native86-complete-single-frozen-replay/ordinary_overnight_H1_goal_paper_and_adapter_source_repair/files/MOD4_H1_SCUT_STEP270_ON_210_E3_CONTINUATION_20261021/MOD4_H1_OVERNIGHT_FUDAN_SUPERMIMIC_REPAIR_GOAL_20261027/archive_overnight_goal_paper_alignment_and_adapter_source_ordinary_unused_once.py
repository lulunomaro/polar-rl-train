from pathlib import Path
import importlib.util,json,time,traceback,hashlib
L=Path(__file__).resolve().parent;T=L.parent;W=T.parent;G=W/'polar-rl-train';R=L/'reports'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
A=J/'agent_native_Fudan_pre_request_semantics_review_20261027'
P=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R3_20261027/archive_native86_full_single_frozen_replay_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed_replay_archive_definitions_only',P)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s

def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b,1)
patch("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)/'ordinary_overnight_H1_goal_paper_and_adapter_source_repair'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("nr=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R3_20261027'/'reports'","nr=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'/'reports'")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_NIGHT_GOAL_AND_SOURCE_REPAIR_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_NIGHT_GOAL_AND_SOURCE_REPAIR_ARCHIVE_STARTED_ACTUAL.json'")
start=s.index(' def recgit(*args):');end=s.index(" head=git('rev-parse','HEAD');",start)
s=s[:start]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[end:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'overnight_H1_ordinary_definitions','__file__':str(m.engine)}
exec(compile(s,str(m.engine),'exec'),ns);git=ns['git']

def main():
 assert git('rev-parse','HEAD')=='c4001d23fc95dd34b32cb30be7daa64846974d9f'
 assert len(git('tag','--list').splitlines())==1458 and not git('status','--porcelain')
 for path,digest in [
  (A/'FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json','24476acd32301a5c04c831fd4fc491586872a1171374af7248286d113dac143e'),
  (L/'agent_static_dynamic_delay_contract_candidate/FROZEN_STATIC_DYNAMIC_DELAY_SHA_INDEX.json','5b50bb1ccb68e2463c45caa1e3fdf6e2d4bead80321ff00782364ae2d3b50b38'),
  (L/'agent_actual_DR_memory_getter_candidate_v1/FROZEN_ACTUAL_DR_MEMORY_GETTER_SHA_INDEX.json','0a317e10a99338ee4b36d6e4d07c71af2011b4d2d809e260b066e8061fc7bc51')]:
  assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,path
 assert json.loads((R/'V4_SEVEN_STATE_BPTT_WORLD_POLICY_CRITIC_SYNTHETIC_CPU_ACTUAL.json').read_bytes())['passed']
 assert json.loads((R/'NEW_VENDOR_ACTUAL_LEARNING_LOOP_AST_PRESERVATION_CPU_V3_ACTUAL.json').read_bytes())['passed']
 ns['prior'](G/'versions/20261027_mod4-native86-complete-single-frozen-replay/COMPLETE_FILE_CAPTURE_INDEX.json')
 note='''Ordinary source/preparation supplement to consumed native86 frozen replay stage; no new trial/tag, Task, payload, controller, GO, GPU learning, model reload or budget write.

Human sets one active overnight goal: all three4090 serve only MOD4 H1 step270 repair, other experts and T2z paused. Latest clarification follows SuperMimic paper and supplied pinned open-source learning loop rather than an assumed PPO auxiliary loss; Fudan jumping must be converted into MOD4 executable motion. Goal is active and not achieved. Current source-only work and monitor update do not claim cards are already training or any successful step case.

Paper2610.28480 and original project are distinguished from Motphys/Uni-SuperMimic's explicitly independent downstream reproduction, pinnedfaf7818e8abac3ec6abb8f00e6e904d3577f800b. New readonly source comparisons identify dynamic contact/torque/request misused as fixedxi in imagination, terrain-relative state omission and substantial smoke-scale config departures. Preserve root dimension transcription error contact12; actual history is18, so18+30+1=49. Refuted quaternion, time-scale, q/dq and initialheight bug claims remain refuted. Source evidence is not sole physical-cause proof or convergence benefit.

One sequential helper audits Fudan standing jump versus MOD4 phases and freezes10files including original NumPybool serialization failure/partialJSON and corrected full numbers. It implements new typed static/dynamic/delay contract: aux54 is18contact+30torque+6oldprocessedtargets, request analytic fromage.23CPUcases match original9leg/wheel lag combinations across3controls withselectedreset,648targetentries and correct gradients. Next frozen actual DR memory getter has15CPUcases using real pureCPU components plus clearly duck-typed D0 attributes; no actual SDK admission. All14fields, complete source lineages and errors captured; actual motor gains are6, old conceptual2-width catalog incompatible.

Root derives isolated seven-state worldmodel/replay/learner package, physical30 unchanged, packed127, auxiliary evolved by learned model, real staticxi and terrain-relative inputs separate. V1 CRLF literal source mismatch retained; V2 models/replay18CPU passed, then AST audit caught incomplete second policy/critic batch. V3 literal-count and dependent missing-derived-source verification errors retained. V4 changes both ranges6->7;14ASTchecks preserve original train/collect/BPTT/value/replay math, full new synthetic CPU integration steps WM/Pi/critic once with7checks. No saved MOD4 policy/model, GPU, simulation or native86 reload. Legacy native86 shapes/normalizers/optimizers are not silently exact resumed into new architecture. Compact31staticcontext source is only AST-reviewed, numerical/SDK integration pending. Qualified2536-byte CRLF metadata helper and old runtime untouched.

Next work remains actual getter/bridge/reset integration, coherent own reference/goal/objective and4090 schedule/source contract, then fresh SDK/resources/sole72 admission before new realGPUphase. Do not simply shift foreign floorreturn upward in flight, force actions, weaken success/health, claim reference playback is skill, or launch blind identical windows. Preserve sole72 finite authority and original costs/locks; old210 retired. Source-only no new tag. Full source/reports/errors/monitor and all failed variants captured UTF8; binaries producer-only indexing, no experiment/model/raw/GPU/host reads forGit. All1458oldtags objects/peels protected; postGit verification in conversation only.
'''
 ns['run_stage']('fudan',[L,A],[Path(__file__)],note,'Keep overnight H1 goal and repair SuperMimic wheel-leg source contracts')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY_NIGHT_GOAL_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
   json.dump({'epoch':time.time(),'error':traceback.format_exc(),'actual_HEAD':git('rev-parse','HEAD'),'no_repeated_record_or_tag':True},f,indent=2)
  raise

