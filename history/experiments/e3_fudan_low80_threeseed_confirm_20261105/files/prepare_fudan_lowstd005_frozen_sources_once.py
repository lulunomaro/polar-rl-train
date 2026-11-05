"""Metadata-only frozen source adapter. Never import a learner or touch model bytes."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent
oldn=D/'source_fudan_frozen_native_eval_v5_lowheightgate';oldp=D/'source_fudan_frozen_parent_v5_lowheightgate';newn=D/'source_fudan_frozen_native_eval_v6_lowstd005';newp=D/'source_fudan_frozen_parent_v6_lowstd005'
assert not newn.exists() and not newp.exists()
overlay=(D/'source_task_runtime_v4_passive_lowstd/e3_fudan_task_runtime_v1.py').read_bytes();oh=hashlib.sha256(overlay).hexdigest();oz=len(overlay)
old_branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_HEIGHTGATE';branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005';old_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8_heightgate';kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005'
old_overlay='a89ff5487e76a5d7256b4cf9e60d5c7292047e3d70ca681f02d8c9900f0c4c35';old_safe='560b95f916f9750be507beea71578b4591943851ce572ff7ccde528c2505bb9a'
bad_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_HEIGHTGATE_W9_20261105_024613_1793817973423106300/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt';bad_sha='bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2'
files={p: p.read_bytes()for root in(oldn,oldp)for p in root.glob('*.py')};assert len(files)==10
class Patch:
 def __init__(self,p):self.p=p;self.old=files[p];self.s=self.old.decode('utf8');self.edits=[]
 def edit(self,a,b,n=1):assert self.s.count(a)==n,(self.p.name,a,self.s.count(a),n);self.s=self.s.replace(a,b);self.edits.append((a,b,n));return self
 def common(self):return self.edit(old_branch,branch).edit(old_kind,kind).edit(old_overlay,oh)
 def end(self):
  back=self.s
  for a,b,n in reversed(self.edits):assert back.count(b)==n,(self.p.name,b);back=back.replace(b,a)
  assert back.encode('utf8')==self.old
  return self.s.encode('utf8')
a=Patch(oldn/'frozen_sequence_mean.py').common()
a.edit('TASK_RUNTIME_OVERLAY_BYTES = 12723','TASK_RUNTIME_OVERLAY_BYTES = '+str(oz)).edit('root["version"] == 5','root["version"] == 6').edit('wrong kind/version5','wrong kind/version6').edit('schema_version=5','schema_version=6').edit('dict(initial_std=.5, learning_rate=.001, encoder_learning_rate=.001)','dict(initial_std=.05, learning_rate=.001, encoder_learning_rate=.001)')
anchor='EXCLUDED_FRESH25_SHA = "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2"\n';a.edit(anchor,anchor+'EXCLUDED_HEIGHTGATE_PATH = '+json.dumps(bad_path)+'\nEXCLUDED_HEIGHTGATE_SHA = '+json.dumps(bad_sha)+'\n');mean=a.end()
a=Patch(oldn/'fudan_frozen_eval_safe.py')
a.edit('EXCLUDED_N4096_SHA, EXCLUDED_FRESH25_PATH, EXCLUDED_FRESH25_SHA)','EXCLUDED_N4096_SHA, EXCLUDED_FRESH25_PATH, EXCLUDED_FRESH25_SHA, EXCLUDED_HEIGHTGATE_PATH, EXCLUDED_HEIGHTGATE_SHA)').edit('EXCLUDED_TIMEOUT8_PATH, EXCLUDED_FRESH25_PATH))','EXCLUDED_TIMEOUT8_PATH, EXCLUDED_FRESH25_PATH, EXCLUDED_HEIGHTGATE_PATH))').edit('EXCLUDED_TIMEOUT8_SHA, EXCLUDED_FRESH25_SHA),','EXCLUDED_TIMEOUT8_SHA, EXCLUDED_FRESH25_SHA, EXCLUDED_HEIGHTGATE_SHA),').edit('Selected fresh1cd HEIGHTGATE save must not be 1cd, 47937, 8af4, 3e64 or 246ac6 old input','Selected fresh1cd LOWSTD005 save must not be 1cd, 47937, 8af4, 3e64, 246ac6 or bf824 old input');safe=a.end();sh=hashlib.sha256(safe).hexdigest()
a=Patch(oldp/'fudan_eval_parent_wait_contract_v1.py').common();a.edit(old_safe,sh,2).edit('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE','FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V6_LOWSTD005').edit('schema_version=5','schema_version=6').edit('dict(bytes=12723, sha256=','dict(bytes='+str(oz)+', sha256=').edit('dict(initial_std=.5, learning_rate=.001, encoder_learning_rate=.001)','dict(initial_std=.05, learning_rate=.001, encoder_learning_rate=.001)')
anchor='_EXCLUDED_FRESH25_SHA = "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2"\n';a.edit(anchor,anchor+'_EXCLUDED_HEIGHTGATE_PATH = '+json.dumps(bad_path)+'\n_EXCLUDED_HEIGHTGATE_SHA = '+json.dumps(bad_sha)+'\n').edit('_EXCLUDED_TIMEOUT8_SHA, _EXCLUDED_FRESH25_SHA))','_EXCLUDED_TIMEOUT8_SHA, _EXCLUDED_FRESH25_SHA, _EXCLUDED_HEIGHTGATE_SHA))').edit('_EXCLUDED_TIMEOUT8_PATH, _EXCLUDED_FRESH25_PATH)))','_EXCLUDED_TIMEOUT8_PATH, _EXCLUDED_FRESH25_PATH, _EXCLUDED_HEIGHTGATE_PATH)))');parent=a.end()
changes={oldn/'frozen_sequence_mean.py':mean,oldn/'fudan_frozen_eval_safe.py':safe,oldp/'fudan_eval_parent_wait_contract_v1.py':parent};outputs={}
for path,raw in files.items():
 dest=(newn if path.parent==oldn else newp)/path.name;new=changes.get(path,raw);ast.parse(new.decode('utf8'));compile(new.decode('utf8'),str(dest),'exec');outputs[dest]=new
assert sum(raw!=files[(oldn if path.parent==newn else oldp)/path.name]for path,raw in outputs.items())==3
for path,raw in outputs.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
print(json.dumps(dict(files={str(p.relative_to(D)):dict(bytes=len(r),sha256=hashlib.sha256(r).hexdigest())for p,r in outputs.items()},changed_metadata_modules=3,other_seven_byte_identical=True,one_AST_compile=True,model_SDK_Torch_CPUfixture_SSH_GPU_C_Git_operations=0),indent=2))
