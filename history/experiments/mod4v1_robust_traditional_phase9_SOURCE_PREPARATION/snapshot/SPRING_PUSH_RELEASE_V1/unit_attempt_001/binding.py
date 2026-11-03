"""Pre-plant binding of sealed nominal endpoint data. No FK/SDK/DR access."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent.parent
DATA_PATH=ROOT/'SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json'
EXPECTED_DATA_SHA='1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e'
EXPECTED_HELPER_SHA='5732a0b3ba3338ec8d573a66fb9884871bc2abda7f960db2cd9deb6e7708bde9'

def record(p):
    p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())

def prepare(cfg):
    hop=cfg.get('hop',{});requested=hop.get('release_spring_compensation_during_push',False);operator=hop.get('operator_enable',False)
    if type(requested)is not bool or type(operator)is not bool:raise ValueError('release/operator flag must be bool')
    if any('air_pitch'in k and v not in(False,None)for k,v in hop.items()):raise ValueError('AIR002 feature is excluded from this push-only entry')
    b=dict(requested=requested,operator=operator,active=bool(requested and operator),data_record=None,helper_record=None,book=None)
    if not b['active']:return b # No compensation-data read/default-off model requirement.
    if (ROOT/cfg['end_gain_file']).resolve()!=ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json':raise ValueError('push endpoint source path differs')
    if cfg['landing_gain']!={'file':'TALL_ROUGH_BANK_V1/gain_delta0.json'}:raise ValueError('landing source profile differs')
    data=record(DATA_PATH);helper=record(ROOT/'SPRING_PUSH_DECOMPOSITION_V1/spring_push.py')
    if data['SHA']!=EXPECTED_DATA_SHA or helper['SHA']!=EXPECTED_HELPER_SHA:raise ValueError('nominal endpoint data/helper SHA mismatch')
    from SPRING_PUSH_DECOMPOSITION_V1.spring_push import load_precomputed
    b.update(data_record=data,helper_record=helper,book=load_precomputed())
    return b

def ctor_kwargs(b,start,end,landing):
    if not b['active']:return {}
    from SPRING_PUSH_DECOMPOSITION_V1.spring_push import vector,bits,delta14_to_absolute_q4_qd4
    for name,g in(('crouch',start),('pushend',end),('landing',landing)):
        ep=b['book'].endpoint(name);q,_=delta14_to_absolute_q4_qd4(vector(g['q'],7,'gain q7')+(0.,)*7);tau=vector(g['tau'],6,'gain row6')
        if any(bits(a)!=bits(c)for a,c in zip(q,ep.reference_absolute_q4_rad))or any(bits(a)!=bits(c)for a,c in zip(tau,ep.original_trim6_Nm)):raise ValueError(name+' actual loaded q/tau endpoint binding differs')
    return dict(start_gas_tau6=b['book'].endpoint('crouch').tauGas6_Nm,end_gas_tau6=b['book'].endpoint('pushend').tauGas6_Nm)

def data_sha(b):return None if b['data_record']is None else b['data_record']['SHA']
