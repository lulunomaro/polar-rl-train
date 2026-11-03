"""Precomputed nominal STATIC spring counter-compensation withdrawal. No FK/SDK.
Output torques stay in absolute-joint motor coordinates. Default disabled.
Reference q4 is an endpoint REFERENCE, not a measured/actual-DR state.
"""
from pathlib import Path
from dataclasses import dataclass
from types import MappingProxyType
import json,math,hashlib,numbers,struct

LEGS=(0,1,3,4)
SOURCES=('CONTACT_PROXY_NOMINAL_V1/nominal_model.py','CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json','JUMP270_V1/GAIN_BANK.json','TALL_ROUGH_BANK_V1/gain_delta20.json','TALL_ROUGH_BANK_V1/gain_delta0.json')

def vector(x,n,label):
    if isinstance(x,(str,bytes,bytearray)):raise ValueError(label+' numeric vector, not text/bytes')
    try:a=tuple(x)
    except TypeError:raise ValueError(label+' shape')from None
    if len(a)!=n or any(isinstance(v,bool)or not isinstance(v,numbers.Real)for v in a):raise ValueError(label+' real numeric shape')
    try:a=tuple(float(v)for v in a)
    except (TypeError,ValueError,OverflowError):raise ValueError(label+' finite real conversion')from None
    if not all(math.isfinite(v)for v in a):raise ValueError(label+' finite')
    return a

def bits(x):return struct.pack('<d',float(x))

def delta14_to_absolute_q4_qd4(state14):
    s=vector(state14,14,'state14 crank-minus-hip')
    q=vector((s[3],s[3]+s[4],s[5],s[5]+s[6]),4,'absolute q4')
    v=vector((s[10],s[10]+s[11],s[12],s[12]+s[13]),4,'absolute qd4')
    return q,v

def absolute_q4_into_delta14(q_absolute4,template_state14):
    q=vector(q_absolute4,4,'absolute q4');s=list(vector(template_state14,14,'template state14'))
    s[3],s[4],s[5],s[6]=q[0],q[1]-q[0],q[2],q[3]-q[2]
    return vector(s,14,'mapped state14')

def absolute_tau4_to_delta_generalized(tau_absolute4):
    """Diagnostic covector A.T@tau. NOT physical row6 motor torques."""
    t=vector(tau_absolute4,4,'absolute torque4')
    return vector((t[0]+t[1],t[1],t[2]+t[3],t[3]),4,'delta generalized torque4')

@dataclass(frozen=True,slots=True)
class Endpoint:
    name:str
    reference_absolute_q4_rad:tuple
    original_trim6_Nm:tuple
    tauGas4_Nm:tuple
    tauGas6_Nm:tuple
    new_static_FF6_Nm:tuple

class EndpointBook:
    def __init__(self,entries,source_reads):
        self.entries=MappingProxyType(dict(entries));self.source_reads=source_reads
    def endpoint(self,name):return self.entries[name]
    def timed_push_ff6(self,name,original_ff6,reference_absolute_q4,*,phase,enabled=False):
        """No interpolation. Active request requires exact frozen endpoint binding.
        Other phases/default-off return independent immutable copies, no motor send.
        """
        e=self.endpoint(name);old=vector(original_ff6,6,'original row6 FF');q=vector(reference_absolute_q4,4,'reference absolute q4')
        if type(enabled)is not bool or not isinstance(phase,str)or not phase:raise ValueError('explicit enable/phase')
        if not enabled or phase!='timed_push':return tuple(v for v in old)
        if any(bits(a)!=bits(b)for a,b in zip(q,e.reference_absolute_q4_rad)):raise ValueError('not this precomputed absolute endpoint; no online FK/interpolation')
        if any(bits(a)!=bits(b)for a,b in zip(old,e.original_trim6_Nm)):raise ValueError('old trim differs from frozen endpoint')
        result=list(old)
        for row,gas in zip(LEGS,e.tauGas4_Nm):result[row]=old[row]+gas
        return vector(result,6,'new static FF')

def load_precomputed():
    """One load: verifies five old small files and parses bound public/gains once.
    Never imports NominalModel, runs FK, modifies model/gains, or reads DR.
    """
    out=Path(__file__).resolve().parent;root=out.parent
    data=json.loads((out/'ENDPOINTS.json').read_bytes())
    if data['status']!='PASS_NOMINAL_ENDPOINT_SIGN_AND_FD_ONLY':raise ValueError('endpoint result not admitted')
    refs=data['source_records']
    if len(refs)!=5 or {r['relative']for r in refs}!=set(SOURCES):raise ValueError('source allowlist')
    parsed={}
    for r in refs:
        b=(root/r['relative']).read_bytes()
        if hashlib.sha256(b).hexdigest()!=r['SHA']:raise ValueError('frozen public/gain source changed')
        if r['relative'].endswith('.json'):parsed[r['relative']]=json.loads(b)
    pub=parsed[SOURCES[1]]
    if pub['source_xml_sha256']!='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324':raise ValueError('public model provenance')
    gains={'crouch':parsed[SOURCES[2]]['gains']['crouch'],'pushend':parsed[SOURCES[3]]['gain'],'landing':parsed[SOURCES[4]]['gain']}
    entries={}
    for row in data['endpoints']:
        name=row['name'];g=gains[name];s=vector(tuple(g['q'])+(0.,)*7,14,'gain q7+zero fixture rates');q,_=delta14_to_absolute_q4_qd4(s)
        old=vector(row['original_trim6_Nm'],6,'old trim');t4=vector(row['tauGas4_Nm'],4,'gas4');t6=vector(row['tauGas6_Nm'],6,'gas6');new=vector(row['new_static_FF6_Nm'],6,'new FF')
        if old!=vector(g['tau'],6,'gain torque')or q!=vector(row['reference_absolute_q4_rad'],4,'endpoint q'):raise ValueError('gain/endpoint binding')
        if t6!=(t4[0],t4[1],0.,t4[2],t4[3],0.):raise ValueError('absolute motor row map')
        expected=list(old)
        for k,t in zip(LEGS,t4):expected[k]+=t
        if any(bits(a)!=bits(b)for a,b in zip(expected,new)):raise ValueError('plus-gas sign/result')
        entries[name]=Endpoint(name,q,old,t4,t6,new)
    if set(entries)!={'crouch','pushend','landing'}:raise ValueError('exactly three endpoints')
    return EndpointBook(entries,len(refs))
