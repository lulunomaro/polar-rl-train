"""Pure source preflight correction; preserve unexecuted v1 draft."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
old=HERE/'build_e2_mod4v1_sources_v1.py';text=old.read_text(encoding='utf-8')
replacements={
 'ITER, ADAM, PRIOR_UPDATES = 42822, 859300, 82':'ITER, ADAM, PRIOR_UPDATES = 42822, 859300, 92',
 '\\n   for receipt in receipts:':'\\n  for receipt in receipts:',
 '\\n    if receipt.name in required:':'\\n   if receipt.name in required:',
 '"   from gas400_reset_bank_exact_compatibility_v1':'"  from gas400_reset_bank_exact_compatibility_v1',
 '\\n   bankproof=check_runtime_source':'\\n  bankproof=check_runtime_source',
 '"   bankproof=real._mod4v1_e2_bank_compatibility':'"  bankproof=real._mod4v1_e2_bank_compatibility',
 '\\n   assert real._mod4v1_e2_nominal_guard':'\\n  assert real._mod4v1_e2_nominal_guard',
 '\\n    value[':'\\n   value[',
 '\\n   runner.current_learning_iteration=42823':'\\n  runner.current_learning_iteration=42823',
 '\\n   try:runner.learn':'\\n  try:runner.learn',
 '# E2 selected a92':'# E2 selected b3ae94df',
 'Source a92/14615089':'Source b3ae94df/14615089',
}
for a,b in replacements.items():
 if a not in text:raise ValueError('Missing preflight correction '+a)
 text=text.replace(a,b)
anchor="template,template_ref=read(STAGED/'E0_builder/build_e0_mod4v1_sources.py');driver,driver_ref=read(HERE/'derive_e2_builder_v1.py');refs.extend([template_ref,driver_ref])"
assert anchor in text
text=text.replace(anchor,anchor+"\n    draft,draft_ref=read(HERE/'build_e2_mod4v1_sources_v1.py');correction,correction_ref=read(HERE/'finalize_e2_builder_v2.py');refs.extend([draft_ref,correction_ref])")
ast.parse(text)
new=HERE/'build_e2_mod4v1_sources_v2.py'
with new.open('x',encoding='utf-8') as f:f.write(text)
print(json.dumps({'new_generator':str(new),'SHA':hashlib.sha256(text.encode()).hexdigest(),'source_AST_only':True,'SDK_PT_or_training':False},indent=2))
