from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent
old=(B/'prepare_fudan103_native270_payloads_once.py').read_text('utf8')
assert old.count("pub['native_iteration']")==1 and not any((B/'payloads').iterdir())
new=old.replace("pub['native_iteration']","pub['updates']").replace("N/'payloads'","N/'payloads_v2'")
ast.parse(new)
with (B/'prepare_fudan103_native270_payloads_v2_once.py').open('x',encoding='utf8') as f:f.write(new)
with (B/'reports/READER103_ORIGINAL_UPDATES_KEY_CORRECTION_BEFORE_PAYLOAD_COPY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error_retained=True,actual_original_producer_schema_field='updates',native_iteration_field_exists_in_embedded_publication_not_this_descriptor=True,original_payloads_empty=True,new_namespace='payloads_v2',no_model_read_or_remote_or_GPU=True),f,indent=2)
