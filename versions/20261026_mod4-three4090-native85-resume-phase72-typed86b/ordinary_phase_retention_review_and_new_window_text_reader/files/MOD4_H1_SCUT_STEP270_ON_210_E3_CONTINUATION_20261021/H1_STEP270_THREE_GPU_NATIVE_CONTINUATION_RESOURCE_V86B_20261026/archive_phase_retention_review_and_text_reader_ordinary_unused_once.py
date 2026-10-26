from pathlib import Path
import importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
A=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_native_phase_retention_next_candidate_cpu_20261026'
p=N/'archive_actual86B_three_gpu_native_resume_phase72_unique_once.py'
sp=importlib.util.spec_from_file_location('actual86_unique_definitions_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)/'ordinary_phase_retention_review_and_new_window_text_reader'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_PHASE_RETENTION_REVIEW_AND_TEXT_READER_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_PHASE_RETENTION_REVIEW_AND_TEXT_READER_ARCHIVE_STARTED_ACTUAL.json'")
start=s.index(' def recgit(*args):');end=s.index(" head=git('rev-parse','HEAD');",start)
s=s[:start]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[end:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'phase_retention_ordinary_only','__file__':str(m.m.engine)};exec(compile(s,str(m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='6376b8f0cc24d4c4d35f7fda2c3636f68c8d676b' and len(git('tag','--list').splitlines())==1457 and not git('status','--porcelain')
 assert any(A.glob('*HANDOFF*.md')) and any(A.glob('*INDEX*.json')),'Wait for the only helper to freeze'
 ns['prior'](G/'versions/20261026_mod4-three4090-native85-resume-phase72-typed86b/COMPLETE_FILE_CAPTURE_INDEX.json')
 note='''Ordinary supplement to consumed86B actual three4090/native continuation trial, no new record/tag or training change. The single remaining helper reviews future phase retention only from already available source and first86B phase metadata; all candidate boundary tests and failures are preserved. It never changes the active ring, sampling distribution, age/reset/reward/actions/physics or model. The next implementation must depend on complete86B phase and physical-event coverage plus fresh source/resource/admission; no blind identical windows or claimed convergence.

Root prepares text-only86B closing analysis by reusing pinned original85 curve-reader source unchanged and adding explicit source68/680WM/58Pi baselines. Four CPU counter-boundary fixtures prove that inherited positive cumulativePi58 is not mislabelled as a new update, and preserve interval-censored first-positive timing and source-counter regression rejection. Actual86B closing curve/model is not read by those fixtures. The actual curve entry is UNUSED until close, never opens model paths, and distinguishes original physical completed-control events from WM/Pi losses and velocity metrics. Unused close/reviewer remain gated at original900 seconds with sole72 cost and model roles intact. Saved local guessed-filename read errors are source-reader issues, not runtime failures. All saved new source/reports/errors/monitor text captured; producer-only binary indexing and all1457 oldtagobjects/peels remain. PostGit verification stays in conversation, no report chasingHEAD.
'''
 ns['run_stage']('fudan',[N,A],[Path(__file__)],note,'Review bounded phase retention and prepare native new-window text analysis')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PHASE_RETENTION_ORDINARY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_tag=True),f,indent=2)
  raise
