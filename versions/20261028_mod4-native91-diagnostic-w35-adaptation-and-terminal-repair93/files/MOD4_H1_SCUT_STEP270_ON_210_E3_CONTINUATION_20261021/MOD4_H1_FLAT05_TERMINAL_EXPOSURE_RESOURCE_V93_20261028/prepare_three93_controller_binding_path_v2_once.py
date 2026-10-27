from pathlib import Path
import ast,json
N=Path(__file__).resolve().parent
with (N/'reports/THREE93_CONTROLLER_V1_BINDING_PATH_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_error='FileNotFoundError WinError2 OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json',cause='Binding belongs original88C payloads/h1 rather than controllers',partial_source_v1_retained=True,before_remote_or_GO=True),f,indent=2)
s=(N/'prepare_three93_original_writer_alias_dispatch_source_once.py').read_text('utf8')
s=s.replace("F=N/'controller_three93_source_v1'", "F=N/'controller_three93_source_v2'",1)
s=s.replace("OLD88/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'", "OLD88.parent/'payloads/h1/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'",1)
ast.parse(s)
p=N/'prepare_three93_original_writer_alias_dispatch_binding_V2_once.py'
with p.open('x',encoding='utf8') as f:f.write(s)
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
