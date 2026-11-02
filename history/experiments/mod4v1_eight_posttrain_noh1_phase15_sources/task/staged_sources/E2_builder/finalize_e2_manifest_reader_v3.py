"""Keep historical SOURCE_FREEZE false row; bind active E2 installer SHA instead."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
old=HERE/'build_e2_mod4v1_sources_v2.py';s=old.read_text(encoding='utf-8')
a="read(old/'train/deploy/contract_rm2025_later.json',freeze.get('train/deploy/contract_rm2025_later.json'))"
b="read(old/'train/deploy/contract_rm2025_later.json',rows['runtime/train/deploy/contract_rm2025_later.json']['SHA'])"
assert a in s;s=s.replace(a,b)
anchor="draft,draft_ref=read(HERE/'build_e2_mod4v1_sources_v1.py');correction,correction_ref=read(HERE/'finalize_e2_builder_v2.py');refs.extend([draft_ref,correction_ref])"
assert anchor in s
s=s.replace(anchor,anchor+"\n    prior,prior_ref=read(HERE/'build_e2_mod4v1_sources_v2.py');reader,reader_ref=read(HERE/'finalize_e2_manifest_reader_v3.py');refs.extend([prior_ref,reader_ref])\n    history=[]\n    for file in sorted(HERE.glob('E2_CPU_GENERATION_ERROR_*.json')):\n        error,error_ref=read(file);refs.append(error_ref);history.append(json.loads(error))\n    files['E2_CPU_GENERATION_HISTORY.json']=J(dict(scope='CPU_SOURCE_ONLY',errors=history,historical_SOURCE_FREEZE_delivery_SHA='bbb71edefa122f37efe7a8fe0271ae987dc3741a33d5697464db73d8a382b00a',active_E2_complete_manifest_delivery_SHA=dep_ref['SHA'],frozen_history_not_rewritten=True))")
a='Source/CPU checks are not expert adaptation or graduation.'
b='Selected historical full_original_skill_accepted=false and complete_SuperMimic_conversion=false remain gaps; complete-cycle world tracking and skill acceptance are not established by this new source. Source/CPU checks are not expert adaptation or graduation.'
assert a in s;s=s.replace(a,b)
ast.parse(s)
new=HERE/'build_e2_mod4v1_sources_v3.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'active_dependency_source':'E2_COMPLETE_INSTALL_MANIFEST actual SHA, not inherited historical SOURCE_FREEZE row','PT_or_SDK_or_training':False},indent=2))
