"""Four unapproved counter mutations rejected without editing candidate bytes."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
from unittest import mock
N=Path(__file__).resolve().parent;M=N.parent/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026';C=M/'candidate_v1';R=M/'reports';p=C/'h1_lifetime_goal_counter_v1.py';raw=p.read_bytes();text=raw.decode('utf8')
sys.path.insert(0,str(C));s=importlib.util.spec_from_file_location('landing_journal_counter_negative_CPU',p);mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
read=Path.read_text;rejected=[]
needle="self.landing_journal.complete(row,np.flatnonzero(deltas['landing_count']>0),deltas['landing_count'],self.rows)"
cases=[('original_counter_reset',text.replace('self.before[k][done]=0','self.before[k][done]=1',1)),('duplicate_journal_hook',text.replace(needle,needle+';'+needle,1)),('wrong_output_folder',text.replace('self.landing_journal.save(folder)','self.landing_journal.save(Path(folder).parent)',1)),('missing_initialization',text.replace('        self.landing_journal=LandingEventJournal(self.n)\n','',1))]
for name,bad in cases:
 assert bad!=text
 with (R/(name+'.negative_source.txt')).open('x',encoding='utf8') as f:f.write(bad)
 def intercepted(path,*a,**kw):return bad if path.resolve()==p.resolve() else read(path,*a,**kw)
 with mock.patch.object(Path,'read_text',new=intercepted):
  try:mod.validate_landing_journal_extension_AST(C)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Unreviewed counter accepted: '+name)
assert p.read_bytes()==raw
with (R/'LANDING_JOURNAL_ORIGINAL_COUNTER_AST_FOUR_NEGATIVE_CASES_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_source_only_CPU=True,rejected=rejected,original_candidate_bytes_unchanged=True,source_SHA=hashlib.sha256(raw).hexdigest(),no_GPU_policy_physics_checkpoint_raw_or_current79c_change=True),f,indent=2)
print(json.dumps(dict(source_only_CPU_negatives=rejected)))
