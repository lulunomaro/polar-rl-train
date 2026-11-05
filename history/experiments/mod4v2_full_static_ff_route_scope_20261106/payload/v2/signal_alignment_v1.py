"""Bounded-history resampling of explicitly time-tagged PUBLIC observations.
Stdlib only. No simulator, DR, force model, controller, or hardware imports.
A common evaluation epoch is NOT instantaneous hardware synchronization.
No alpha/calibration/force authority is manufactured by this module.
"""
from bisect import bisect_left
from collections import deque
from dataclasses import dataclass
import math


def _finite(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def _vector(x,n,nonnegative=False):
    if not isinstance(x,(tuple,list)) or len(x)!=n:
        raise ValueError('vector shape')
    if not all(_finite(v) and (not nonnegative or v>=0) for v in x):
        raise ValueError('finite vector/bound required')
    return tuple(float(v) for v in x)


@dataclass(frozen=True,slots=True)
class ChannelSpec:
    name: str
    dimension: int
    rate_bound_abs: tuple|None=None
    curvature_bound_abs: tuple|None=None
    # Bounds are external assumptions/calibrations, NOT fitted from two samples.
    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name or type(self.dimension)!=int or not 1<=self.dimension<=64:
            raise ValueError('channel identity/dimension')
        for field in ('rate_bound_abs','curvature_bound_abs'):
            value=getattr(self,field)
            if value is not None:
                object.__setattr__(self,field,_vector(value,self.dimension,True))


@dataclass(frozen=True,slots=True)
class ChannelSample:
    timestamp_s: float
    values: tuple
    window_start_s: float
    window_end_s: float
    sample_count: int
    kind: str # 'point' or 'sampled_mean'; timestamp is the declared mean center.
    provenance: str
    clock_error_bound_s: float|None=None
    noise_bound_abs: tuple|None=None
    window_second_moment_s2: float|None=None


@dataclass(frozen=True,slots=True)
class AlignedChannel:
    values: tuple
    source_epochs_s: tuple
    source_windows_s: tuple
    weights: tuple
    error_bound_abs: tuple|None
    bound_reasons: tuple
    provenance: tuple


@dataclass(frozen=True,slots=True)
class AlignedFrame:
    evaluation_epoch_s: float
    arrival_age_s: float
    channels: dict
    numeric_bounds_complete: bool
    # This is only a signal resampler: no torque/proper/alpha binding is supplied.
    force_input_ready: bool=False
    alpha_B_rad_s2: None=None
    hardware_sync_proven: bool=False
    role: str='window_observation_interpolation_not_instantaneous_hardware_sync'


@dataclass(frozen=True,slots=True)
class QueryResult:
    status: str
    frame: AlignedFrame|None=None
    detail: str=''


class SignalAligner:
    def __init__(self,specs,capacity=8,max_age_s=.03,max_bracket_gap_s=.02):
        if type(capacity)!=int or not 2<=capacity<=64:
            raise ValueError('bounded capacity 2..64')
        if not _finite(max_age_s) or not _finite(max_bracket_gap_s) or not 0<max_bracket_gap_s<=max_age_s:
            raise ValueError('age/gap bounds')
        specs=tuple(specs)
        if not all(isinstance(s,ChannelSpec) for s in specs):raise ValueError('channel specs required')
        self.specs={s.name:s for s in specs}
        if not self.specs or len(self.specs)!=len(specs):
            raise ValueError('unique nonempty channels')
        self.capacity=capacity;self.max_age_s=float(max_age_s)
        self.max_bracket_gap_s=float(max_bracket_gap_s)
        self.reset()

    def reset(self):
        self.history={name:deque(maxlen=self.capacity) for name in self.specs}
        self.time_available={name:False for name in self.specs}
        self.fault=None;self.last_emitted_epoch_s=None

    def _bad(self,reason):
        self.fault=reason
        return reason

    def push(self,name,sample):
        """None explicitly declares absent metadata; never substitute packet epoch.
        Same-epoch identical samples are held views, not new independent samples.
        Changed duplicates/rollback latch until reset; no history is overwritten.
        """
        if self.fault:return 'LATCHED:'+self.fault
        if name not in self.specs:return self._bad('UNKNOWN_CHANNEL')
        if sample is None:
            self.time_available[name]=False
            return 'UNKNOWN_TIME_METADATA'
        if not isinstance(sample,ChannelSample):return self._bad('BAD_SAMPLE_SCHEMA')
        spec=self.specs[name]
        try:
            vals=_vector(sample.values,spec.dimension)
            a,t,b=sample.window_start_s,sample.timestamp_s,sample.window_end_s
            if not all(_finite(x) for x in (a,t,b)) or not a<=t<=b:
                raise ValueError('time/window')
            if type(sample.sample_count)!=int or sample.sample_count<1:
                raise ValueError('sample count')
            if sample.kind not in ('point','sampled_mean') or not isinstance(sample.provenance,str) or not sample.provenance:
                raise ValueError('source declaration')
            if sample.kind=='point' and (a!=t or b!=t or sample.sample_count!=1):
                raise ValueError('point is not a sampled window')
            for v in (sample.clock_error_bound_s,sample.window_second_moment_s2):
                if v is not None and (not _finite(v) or v<0):raise ValueError('unknown or finite nonnegative bound')
            if sample.window_second_moment_s2 is not None:
                # Centered second moment cannot exceed max squared sample offset.
                if sample.window_second_moment_s2>max((t-a)**2,(b-t)**2)+1e-15:
                    raise ValueError('second moment outside source window')
                if sample.kind=='point' and sample.window_second_moment_s2!=0:
                    raise ValueError('point second moment')
            noise=None if sample.noise_bound_abs is None else _vector(sample.noise_bound_abs,spec.dimension,True)
            # Canonical tuples make duplicate equality deterministic; never edit caller.
            s=ChannelSample(float(t),vals,float(a),float(b),sample.sample_count,sample.kind,
                sample.provenance,sample.clock_error_bound_s,noise,sample.window_second_moment_s2)
        except ValueError as exc:return self._bad('INVALID_SAMPLE:'+str(exc))
        h=self.history[name]
        if h and s.timestamp_s<h[-1].timestamp_s:return self._bad('CHANNEL_TIME_ROLLBACK:'+name)
        if h and s.timestamp_s==h[-1].timestamp_s:
            if s!=h[-1]:return self._bad('CHANGED_DUPLICATE:'+name)
            self.time_available[name]=True
            return 'HELD_IDENTICAL'
        h.append(s);self.time_available[name]=True
        return 'APPENDED'

    def _bound(self,spec,samples,weights,target):
        reasons=[]
        if spec.rate_bound_abs is None:reasons.append('RATE_BOUND_UNKNOWN')
        if spec.curvature_bound_abs is None:reasons.append('CURVATURE_BOUND_UNKNOWN')
        moments=[]
        for s in samples:
            if s.clock_error_bound_s is None:reasons.append('CLOCK_ERROR_BOUND_UNKNOWN')
            if s.noise_bound_abs is None:reasons.append('OBSERVATION_NOISE_BOUND_UNKNOWN')
            moment=0. if s.kind=='point' else s.window_second_moment_s2
            if moment is None:reasons.append('WINDOW_SECOND_MOMENT_UNKNOWN')
            moments.append(moment)
        if reasons:return None,tuple(dict.fromkeys(reasons))
        span_term=0.
        if len(samples)==2:
            span_term=(target-samples[0].timestamp_s)*(samples[1].timestamp_s-target)
        out=[]
        for k in range(spec.dimension):
            # Linear interpolation error + sampled-mean bias + declared clock/noise.
            window_term=sum(w*m for w,m in zip(weights,moments))
            curvature=.5*spec.curvature_bound_abs[k]*(span_term+window_term)
            clock=spec.rate_bound_abs[k]*sum(w*s.clock_error_bound_s for w,s in zip(weights,samples))
            noise=sum(w*s.noise_bound_abs[k] for w,s in zip(weights,samples))
            total=curvature+clock+noise
            if not math.isfinite(total):return None,('NUMERIC_ERROR_BOUND_UNAVAILABLE',)
            out.append(total)
        return tuple(out),()

    def query(self,now_s,at_s=None):
        if self.fault:return QueryResult('LATCHED',detail=self.fault)
        if not _finite(now_s) or (at_s is not None and not _finite(at_s)):
            return QueryResult('BAD_QUERY_TIME')
        missing=[name for name in self.specs if not self.time_available[name] or not self.history[name]]
        if missing:return QueryResult('MISSING_TIME_METADATA_OR_HISTORY',detail=','.join(missing))
        latest=[h[-1].timestamp_s for h in self.history.values()]
        if any(t>now_s for t in latest):return QueryResult('FUTURE_SOURCE_SAMPLE')
        target=min(latest) if at_s is None else float(at_s)
        if target>now_s or now_s-target>self.max_age_s:return QueryResult('STALE_OR_FUTURE_COMMON_TIME')
        if self.last_emitted_epoch_s is not None and target<=self.last_emitted_epoch_s:
            return QueryResult('NO_NEW_COMMON_TIME')
        aligned={}
        for name,spec in self.specs.items():
            h=list(self.history[name]);times=[s.timestamp_s for s in h];j=bisect_left(times,target)
            if j<len(h) and h[j].timestamp_s==target:
                used=(h[j],);weights=(1.,)
            elif j==0 or j==len(h):return QueryResult('NO_BRACKET_NO_EXTRAPOLATION',detail=name)
            else:
                lo,hi=h[j-1],h[j];gap=hi.timestamp_s-lo.timestamp_s
                if gap>self.max_bracket_gap_s:return QueryResult('BRACKET_GAP_TOO_LARGE',detail=name)
                u=(target-lo.timestamp_s)/gap;used=(lo,hi);weights=(1.-u,u)
            if any(s.window_start_s>now_s or now_s-s.window_start_s>self.max_age_s for s in used):
                return QueryResult('STALE_SOURCE_WINDOW',detail=name)
            values=tuple(sum(w*s.values[k] for w,s in zip(weights,used)) for k in range(spec.dimension))
            if not all(math.isfinite(v) for v in values):return QueryResult('NUMERIC_INTERPOLATION_UNAVAILABLE',detail=name)
            error,reasons=self._bound(spec,used,weights,target)
            aligned[name]=AlignedChannel(values,tuple(s.timestamp_s for s in used),
                tuple((s.window_start_s,s.window_end_s,s.sample_count,s.kind) for s in used),
                weights,error,reasons,tuple(s.provenance for s in used))
        frame=AlignedFrame(target,float(now_s-target),aligned,
            all(c.error_bound_abs is not None for c in aligned.values()))
        self.last_emitted_epoch_s=target
        return QueryResult('ALIGNED_OBSERVATIONS_ONLY',frame)
