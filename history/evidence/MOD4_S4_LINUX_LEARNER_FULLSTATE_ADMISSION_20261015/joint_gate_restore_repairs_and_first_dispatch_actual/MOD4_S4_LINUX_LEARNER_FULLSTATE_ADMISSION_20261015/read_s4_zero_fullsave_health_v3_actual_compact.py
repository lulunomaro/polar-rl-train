"""Pure bounded read of the health-schema V3 namespace."""
from pathlib import Path
import sys,io,json,contextlib
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
import read_s4_missing_native_fullstate_actual_compact_v1 as reader
old='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_NATIVE_FULLSTATE_V1_20261015'
new='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_HEALTH_V3_20261015'
assert reader.CODE.count(old)==1
reader.CODE=reader.CODE.replace(old,new).replace('own_native120','own_first_fullsave0_healthschema').replace('own_fullrestore0','own_fullrestore0_healthschema')
if __name__=='__main__':
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):reader.main()
    v=json.loads(capture.getvalue());v['stages']={k:{a:b for a,b in z.items() if a in ('EXIT_ACTUAL.json','S4_COMPLETE_ACTUAL.json','S4_ORIGINAL_ERROR.json')} for k,z in v['stages'].items()}
    print(json.dumps(v))
