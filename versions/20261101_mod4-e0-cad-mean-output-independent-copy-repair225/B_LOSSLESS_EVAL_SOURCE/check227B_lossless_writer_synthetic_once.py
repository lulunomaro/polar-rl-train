"""Only NEW writer roundtrip/limit CPU purpose; no old observer fixture."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback
from positional_rows227 import PositionalRows227, FORMAT227, LIMIT227
from decode227_positional import header227, decode227

B = Path(__file__).resolve().parent
SOURCE = '343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'


def put(p, v):
    with p.open('x',encoding='utf8') as f:
        json.dump(v,f,indent=2,allow_nan=False)


def fingerprint(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


class VisibleSchemaFile:
    def __init__(self, raw_file, writer, counts):
        self.raw_file = raw_file
        self.writer = writer
        self.counts = counts
    def write(self, raw):
        # Synthetic only: every data write sees an already committed complete
        # header supporting that exact row. No actual capture is ever opened.
        h = header227(self.writer.header_path.read_bytes())
        self.counts['synthetic_header_reads'] += 1
        assert len(list(decode227(h,[raw]))) == 1
        return self.raw_file.write(raw)
    def __getattr__(self, name):
        return getattr(self.raw_file,name)


def load_synthetic(writer, counts):
    raw = writer.header_path.read_bytes()
    counts['synthetic_header_reads'] += 1
    h = header227(raw)
    data = writer.path.read_bytes()
    counts['synthetic_data_reads'] += 1
    return h, data, list(decode227(h,data.splitlines()))


def main():
    purpose = json.loads((B/'reports/CPU227B_PURPOSE_FROZEN.json').read_bytes())
    put(B/'reports/CPU227B_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=purpose['ID']))
    for r in purpose['sources']:
        raw=Path(r['path']).read_bytes()
        assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA']
        ast.parse(raw,filename=r['path'])
    counts = dict(synthetic_header_reads=0,synthetic_data_reads=0,actual_capture_reads=0)
    root = B/'reports/SYNTHETIC227B_ONLY'
    root.mkdir(exist_ok=False)
    d = root/'roundtrip'
    d.mkdir()
    base = dict(record_type='same_UID_original_RM70_command',end_reason='original_resample',
        signed_yaw_tolerance=.2,axis_semantics='Original heading,not an invented target',
        env_id=0,along_m=-0.0,cross_m=1.2345678901234567,terminated_before_reset=False,
        truncated_before_reset=False,natural_complete=True,kinematic_bounds_met=False,
        original_terminal_reason_union=False)
    inputs = [base, dict(base,env_id=1,along_m=1e-300,cross_m=1e200,kinematic_bounds_met=True),
        dict(base,env_id=2,unknown_future_field={'µ':[None,True,False,1,1.0,-0.0,2**100,'line\n二']},
             original_terminal_reason_base_contact=True,terminated_before_reset=True),
        dict(record_type='same_episode_original_catalog_route',end_reason='original_reset',env_id=3,
             original_route_x=[5.85,9.15],original_route_y=6.45,original_catalog_goal_radius=.35,
             terminated_before_reset=True,truncated_before_reset=False),
        dict(record_type='same_episode_original_catalog_route',end_reason='original_reset',env_id=4,
             original_route_x=[5.85,9.15],original_route_y=6.450000000000001,original_catalog_goal_radius=.35,
             terminated_before_reset=False,truncated_before_reset=True),
        dict(base,env_id=5,along_m=1.0,cross_m=1,unknown_null=None),
        dict(base,env_id=6,end_reason='window_end_partial',natural_complete=False,
             unknown_future_field={'新增':{'safe':False}},terminated_before_reset=True)]
    w = PositionalRows227(d,SOURCE,producer_metadata={'synthetic_only':True,'source_SHA':'synthetic-writer-purpose'})
    w.file = VisibleSchemaFile(w.file,w,counts)
    for row in inputs:
        w.append(row)
    result = w.finish()
    h,data,outputs = load_synthetic(w,counts)
    expected = [dict(source_SHA=SOURCE,**r) for r in inputs]
    assert fingerprint(outputs)==fingerprint(expected)
    assert result['rows']==len(inputs) and result['dropped_rows']==0 and not result['retention_limited']
    assert result['schema_count']>=5 and sum(result['rows_by_schema'])==len(inputs)
    assert hashlib.sha256(data).hexdigest()==result['SHA']
    assert result['retained_total_bytes']==result['bytes']+result['schema_bytes']<=LIMIT227
    assert 'unknown_future_field' in result['field_union'] and h['format']==FORMAT227
    decoder_refusals = 0
    for bad in (b'[999999,[]]', b'[0,[]]'):
        try:
            list(decode227(h,[bad]))
        except ValueError:
            decoder_refusals += 1
    assert decoder_refusals==2
    d = root/'limit'
    d.mkdir()
    w = PositionalRows227(d,SOURCE,limit_bytes=4096,producer_metadata={'synthetic_only':True})
    w.file = VisibleSchemaFile(w.file,w,counts)
    attempted = []
    for i in range(12):
        row=dict(record_type='synthetic_all_failures_kept_equally',env_id=i,payload='x'*1000,terminated_before_reset=True)
        attempted.append(row)
        w.append(row)
    before=(w.header_SHA,len(w.schemas),w.dropped)
    huge=dict(record_type='synthetic_unknown_fieldset',**{'future_'+str(i):i for i in range(250)})
    attempted.append(huge)
    w.append(huge)
    assert (w.header_SHA,len(w.schemas))==before[:2] and w.dropped==before[2]+1
    # Existing smaller rows may still fit after a drop, matching old policy.
    tail=dict(record_type='synthetic_all_failures_kept_equally',env_id=99,payload='',terminated_before_reset=True)
    attempted.append(tail)
    w.append(tail)
    limited = w.finish()
    hh,dd,oo = load_synthetic(w,counts)
    assert limited['retention_limited'] and limited['dropped_rows']>0
    assert limited['attempted_rows']==len(attempted)==14 and limited['rows']+limited['dropped_rows']==14
    assert limited['retained_total_bytes']<=4096 and 0<limited['rows']<14
    assert all(r['terminated_before_reset'] is True for r in oo) and oo[-1]['env_id']==99
    assert limited['rows']==sum(limited['rows_by_schema'])==len(oo)
    put(B/'reports/CPU227B_LOSSLESS_ROUNDTRIP_AND_LIMIT_ACTUAL.json',dict(passed=True,
        ID=purpose['ID'],groups=2,source_AST_count=len(purpose['sources']),
        exact_original_key_value_type_float_and_row_order_roundtrip=True,unknown_fields_registered=True,
        constants_changed_registered_without_loss=True,atomic_header_visible_before_every_row=True,
        decoder_unknown_schema_or_arity_refusals=decoder_refusals,
        original_192MiB_limit_preserved=LIMIT227==192*1024**2,
        roundtrip_producer=result,synthetic_4KiB_limit_producer=limited,read_counts=counts,
        actual_capture_byte_coverage='UNKNOWN_NOT_RUN',old_fixture_replays=0,
        PT_NPZ_USD_raw_actualJSONL_Torch_SDK_GPU_SSH_Git_calls=0))


if __name__=='__main__':
    try:
        main()
    except BaseException:
        put(B/'reports/CPU227B_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True))
        raise
