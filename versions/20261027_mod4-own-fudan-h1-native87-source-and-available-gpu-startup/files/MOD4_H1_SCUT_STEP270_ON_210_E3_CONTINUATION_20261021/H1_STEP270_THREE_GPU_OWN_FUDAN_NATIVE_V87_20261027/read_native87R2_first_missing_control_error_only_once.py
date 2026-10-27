"""Only previously uncollected own control-error files and missing binding stat."""
from pathlib import Path
import sys,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def main():
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    c=route.connect()
    try:
        value=d.code(c,route.PY,"""from pathlib import Path
import json
B=Path('/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87r2/h1')
paths=sorted(B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'));selected=paths[:1]+paths[-1:] if len(paths)>1 else paths
errors={}
for p in selected:
 assert p.stat().st_size<100000;errors[p.name]=json.loads(p.read_bytes())
binding=B/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'
print(json.dumps(dict(root=str(B),control_error_file_count=len(paths),first_and_last_missing_error_text=errors,required_binding_present=binding.is_file(),no_PT_raw_model_peer_or_account_query=True)))""",{},timeout=45)
        p=R/'NATIVE87R2_FIRST_CONTROL_ERROR_AND_BINDING_MISSING_RETURNED_ACTUAL.json'
        with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_finite_returned=True,**value),f,indent=2)
        print(json.dumps(value))
    finally:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NATIVE87R2_CONTROL_MISSING_READER_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
