"""New source-only landing trajectories from already-copied CPU rows, no current training change."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;M=T/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026';C=M/'candidate_v1'
assert not M.exists();M.mkdir();C.mkdir();(C/'reference_sources').mkdir();(M/'reports').mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=N/'payloads/h1';old=(base/'h1_lifetime_goal_counter_v1.py').read_text('utf8');fragment=(N/'landing_event_journal_fragment_v1.py').read_text('utf8');fragment=fragment[fragment.index('class LandingEventJournal:'):].replace('REPLACE_ORIGINAL_COUNTER_SHA',H(base/'h1_lifetime_goal_counter_v1.py'))
s=old;needle='self.invalid_rows=0;self.last_error=None;self.write_errors=[]';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        self.landing_journal=LandingEventJournal(self.n)',1)
needle='self.before_cross=cross.copy();self.before_cross[done]=False;self.rows+=1\n        return True';assert s.count(needle)==1;s=s.replace(needle,"self.before_cross=cross.copy();self.before_cross[done]=False;self.rows+=1\n        self.landing_journal.complete(row,np.flatnonzero(deltas['landing_count']>0),deltas['landing_count'],self.rows)\n        return True",1)
needle="tmp.write_text(json.dumps(self.snapshot(),indent=2),encoding='utf8');os.replace(tmp,p);return True";assert s.count(needle)==1;s=s.replace(needle,"tmp.write_text(json.dumps(self.snapshot(),indent=2),encoding='utf8');os.replace(tmp,p);self.landing_journal.save(folder);return True",1)
s=s+'\n\n'+fragment;ast.parse(s)
with (C/'h1_lifetime_goal_counter_v1.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
shutil.copy2(base/'h1_lifetime_goal_counter_v1.py',C/'reference_sources/actual79c_counter_original_bytes.txt')
for name in ('h1_production_control_prefix_trace_v1.py','sampling_trace_npz_lossless_v1.py'):shutil.copy2(base/name,C/name)
s=(base/'sampling_acceleration_installed_CPU_v2.py').read_text('utf8');oldSHA=H(base/'h1_lifetime_goal_counter_v1.py');assert s.count(oldSHA)==1;s=s.replace(oldSHA,H(C/'h1_lifetime_goal_counter_v1.py'),1)
needle="  'sampling_trace_npz_lossless_v1.py':";assert s.count(needle)==1;s=s.replace(needle,"  'reference_sources/actual79c_counter_original_bytes.txt':"+repr(H(C/'reference_sources/actual79c_counter_original_bytes.txt'))+",\n"+needle,1)
needle='        from h1_lifetime_goal_counter_v1 import installed_counter_CPU_checks';assert s.count(needle)==1;s=s.replace(needle,needle+',installed_landing_journal_CPU_checks',1)
needle="        result['lifetime_goal_diagnostic_CPU']=installed_counter_CPU_checks(B)";assert s.count(needle)==1;s=s.replace(needle,needle+"\n        result['landing_event_journal_CPU']=installed_landing_journal_CPU_checks(B)",1);ast.parse(s)
with (C/'sampling_acceleration_installed_CPU_v2.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
with (M/'reports/LANDING_JOURNAL_SOURCE_ONLY_CANDIDATE_V1_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,candidate_files={name:H(C/name) for name in ('h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','reference_sources/actual79c_counter_original_bytes.txt')},base_counter_SHA=oldSHA,base_sampler_SHA=H(base/'sampling_acceleration_installed_CPU_v2.py'),trace_bytes_unchanged=H(C/'h1_production_control_prefix_trace_v1.py')==H(base/'h1_production_control_prefix_trace_v1.py'),no_new_per_step_GPU_copy_actor_RNG_or_physics=True,only_optional_CPU_journal_first64_landing_records_pre16_post64=True,not_installed_or_runtime_evidence=True,not_reward_change_or_success_gate=True),f,indent=2)
print(json.dumps(dict(landing_journal_source_only=True,not_current79c=True)))
