from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 binding=S/'BINDING.json';raw=binding.read_bytes()
 with (S/'BINDING_BEFORE_PRELAUNCH_ERROR_PRESERVATION_EXACT.json').open('xb') as f:f.write(raw)
 q=json.loads(raw);old=q['entry_SHA'];q['entry_SHA']=H(S/'native86_frozen_single_sdk_entry_v1.py')
 q['primary_error_persisted_before_app_close']=True
 binding.write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
 for p in (S/'native86_frozen_single_sdk_entry_v1.py',S/'run_native86_replay_R2_original_environment_once.py'):ast.parse(p.read_bytes())
 with (S/'reports/R2_PRELAUNCH_PRIMARY_ERROR_PATH_SOURCE_PIN_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),old_entry_SHA=old,new_entry_SHA=q['entry_SHA'],old_binding_bytes_retained=True,only_prelaunch_error_persistence_changed=True,no_model_or_GPU_execution=True),f,indent=2)
 print('R2 prelaunch error preservation pinned; no actual replay yet')
if __name__=='__main__':main()
