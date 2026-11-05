"""Build a new-purpose pi export with exactly the new frozen stager's closure gate.
Source parsing only; do not export or open any model here.
"""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent;dest=D/'export_fudan_timeout8_pi_for_mujoco_once.py';assert not dest.exists()
s=(D/'stage_fudan_timeout8_frozen_original_once.py').read_text(encoding='utf8');st=ast.parse(s)
frozen=D/'source_fudan_frozen_native_eval_v3_timeout8/frozen_sequence_mean.py';digest=hashlib.sha256(frozen.read_bytes()).hexdigest()
t=(D/'export_fudan_pi_for_nominal_mujoco_once.py').read_text(encoding='utf8')
names=('KIND','BRANCH','BASE','COUNTERS','MOTHER_SHA','SOURCE_4K_SHA','LEARNER_SHA','SOURCE_KIND','OVERLAY_SHA','TASKS')
assigns={target.id:node for node in st.body if isinstance(node,ast.Assign)for target in node.targets if isinstance(target,ast.Name)}
header='\n'.join(ast.get_source_segment(s,assigns[name])for name in names)+'\nFROZEN_SOURCE_SHA = '+repr(digest)+'\nPREFIX = "FDNTIMEOUT8_PI_ONLY_EXPORT_"\n\n'
a=t.index('KIND = ');b=t.index('# Parsed locally');t=t[:a]+header+t[b:]
start='    closed_path = Path(args.closed)'
newfront=s[s.index(start):s.index('    # All closure validation above')]
a=t.index(start);b=t.index('    # Every check above');t=t[:a]+newfront+t[b:]
old='edaa8867f38ca8f75c8e5f65c2c8c21b74c9a3f7d8d66fdd354f4270f26f8a4d';assert t.count(old)==1;t=t.replace(old,digest)
t=t.replace('FDNN20000_PI_ONLY_EXPORT_','FDNTIMEOUT8_PI_ONLY_EXPORT_')
assert t.count('source_fudan_frozen_native_eval_v2_n20000')==1;t=t.replace('source_fudan_frozen_native_eval_v2_n20000','source_fudan_frozen_native_eval_v3_timeout8')
a="input_model_stat_operations=0,original_mother_reads=0,ancestor_N4096_reads=0)";b="input_model_stat_operations=0,original_mother_reads=0,ancestor_N4096_reads=0,ancestor_N20000_reads=0)";assert t.count(a)==1;t=t.replace(a,b)
a="source['sha256']not in(MOTHER_SHA,LEARNER_SOURCE_SHA)";b="source['sha256']not in(MOTHER_SHA,LEARNER_SOURCE_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d')";assert t.count(a)==1;t=t.replace(a,b)
a='receipt["source_IO"]["ancestor_N4096_reads"] == 0';b='receipt["source_IO"]["ancestor_N4096_reads"] == receipt["source_IO"]["ancestor_N20000_reads"] == 0';assert t.count(a)==1;t=t.replace(a,b)
tree=ast.parse(t);compile(tree,str(dest),'exec');remote=next(node.value.value for node in tree.body if isinstance(node,ast.Assign)and any(isinstance(target,ast.Name)and target.id=='REMOTE_EXPORT'for target in node.targets));compile(ast.parse(remote),'cpu_export_timeout8.py','exec')
dest.write_text(t,encoding='utf8',newline='\n');print(str(dest)+' ; closed-gate matches new stage; outer+remote AST/compile PASS; frozen SHA '+digest+'; model/SSH/SDK/export operations0')
