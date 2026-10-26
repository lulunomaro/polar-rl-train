from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';old=N/'observe_three_gpu86B_first_GO_updates_phase_finite_unused_once.py';new=N/'observe_three_gpu86B_first_GO_updates_phase_finite_V2_unused_once.py'
assert not new.exists();text=old.read_text('utf8')
bad="for k in ('h1','recovery'))\n phase_exposure=";good="for k in ('h1','recovery')))\n phase_exposure="
assert text.count(bad)==1;text=text.replace(bad,good,1)
text=text.replace('THREE_GPU86B_FIRST_GO_POLICY_OBSERVER_STARTED_ACTUAL.json','THREE_GPU86B_FIRST_GO_POLICY_OBSERVER_V2_STARTED_ACTUAL.json').replace('THREE_GPU86B_FIRST_OBSERVER_ORIGINAL_ERROR_','THREE_GPU86B_FIRST_OBSERVER_V2_ORIGINAL_ERROR_')
tree=ast.parse(text);sources={}
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('OWNER_READ','TARGET_READ') for t in node.targets):
  source=ast.literal_eval(node.value);compile(source,'<new observer remote '+node.targets[0].id+'>','exec');sources[node.targets[0].id]=hashlib.sha256(source.encode()).hexdigest()
assert set(sources)=={'OWNER_READ','TARGET_READ'}
new.write_bytes(text.encode('utf8'))
with (R/'FIRST_OBSERVER_V1_EMBEDDED_REMOTE_SYNTAX_ERROR_AND_V2_CPU_CLASSIFICATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),classification='LOCAL_READER_REMOTE_CODE_PARSE_ERROR_BEFORE_ANY_OWNER_METADATA_READ',original_error_preserved=True,new_V2_filename=True,only_parenthesis_and_unique_started_error_names_changed=True,embedded_owner_and_target_sources_compile_CPU=True,remote_source_SHAs=sources,no_training_or_account_change_or_first_metadata_repeat=True),f,indent=2)
print(json.dumps({'embedded_sources_compile':True,'V2_ready':True,'training_untouched':True}))
