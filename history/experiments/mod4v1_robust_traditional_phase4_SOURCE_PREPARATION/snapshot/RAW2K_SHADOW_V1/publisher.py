"""PRODUCER ONLY: correlated-noise 2k shadow information-enhancement branch.
Clean samples and post-mean noise offsets remain private to this publisher.
The consumer projection contains noisy sensor values only. Not hardware IO.
"""
from collections import OrderedDict
import copy
import hashlib
import json
import math
import numpy as np

CHANNELS={'gyro_body':3,'accel_proper_body':3,'joint_pos4':4,'joint_vel4':4,'wheel_vel2':2}
ROOT_KEYS={'kind','sequence','source_epoch_us','arrival_us','window_begin_us','window_end_us','aperture_us','mean_mode','count','sample_weight_us','dropped_count','duplicate_source','correlated_postmean_noise','extra_information_branch','hardware_binding','actuation_used','mean','endpoint_joint_pos4','samples','payload_SHA'}
MEAN_KEYS={'gyro_body','accel_proper_body','joint_vel4','wheel_vel2'}
SAMPLE_KEYS=set(CHANNELS)|{'sampled_us','encoder_pos_sampled_us','encoder_rate_sampled_us','weight_us','valid'}

def vector(value,n):
    out=np.asarray(value,dtype=float)
    if out.shape!=(n,) or not np.isfinite(out).all():
        raise ValueError('finite sensor vector required')
    return out.copy()

def integer(value):
    if type(value)is not int or value<0:
        raise ValueError('nonnegative integer timestamp/count required')
    return value

def body_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate_projection(value):
    if set(value)!=ROOT_KEYS or set(value['mean'])!=MEAN_KEYS:
        raise ValueError('non-allowlisted root/mean field')
    if value['kind']!='RAW2K_CORRELATED_SHADOW_NOT_OLD_BENCHMARK' or value['extra_information_branch']is not True or value['correlated_postmean_noise']is not True or value['hardware_binding']is not False or value['actuation_used']is not False or type(value['duplicate_source'])is not bool:
        raise ValueError('invalid branch/actuation claim')
    for name in ('sequence','source_epoch_us','arrival_us','window_begin_us','window_end_us','aperture_us','mean_mode','count','sample_weight_us','dropped_count'):
        integer(value[name])
    if value['sequence']==0 or value['dropped_count']!=0 or value['source_epoch_us']!=value['window_end_us'] or value['window_end_us']-value['window_begin_us']!=value['aperture_us'] or value['arrival_us']-value['source_epoch_us']not in(0,10000):
        raise ValueError('invalid window epoch/quality')
    mode=value['mean_mode']
    if mode not in(0,1) or value['count']!=len(value['samples']) or (mode==0 and (value['count']!=1 or value['aperture_us']!=0 or value['sample_weight_us']!=0)) or (mode==1 and (value['count']!=20 or value['aperture_us']!=10000 or value['sample_weight_us']!=500)):
        raise ValueError('invalid mode/count/aperture')
    for i,sample in enumerate(value['samples']):
        if set(sample)!=SAMPLE_KEYS:
            raise ValueError('non-allowlisted sample field')
        expected=value['source_epoch_us']if mode==0 else value['window_begin_us']+500*i
        if any(type(sample[k])is not int or sample[k]!=expected for k in ('sampled_us','encoder_pos_sampled_us','encoder_rate_sampled_us')) or sample['weight_us']!=value['sample_weight_us'] or sample['valid']is not True:
            raise ValueError('invalid sample time/weight/quality')
        for name,n in CHANNELS.items():vector(sample[name],n)
    for name in MEAN_KEYS:vector(value['mean'][name],CHANNELS[name])
    vector(value['endpoint_joint_pos4'],4)
    body={k:v for k,v in value.items()if k not in('arrival_us','duplicate_source','payload_SHA')}
    if body_hash(body)!=value['payload_SHA']:
        raise ValueError('payload hash mismatch')
    return True


class ShadowPublisher:
    """Noisy packet must be the original 100Hz authoritative result of D1/D3.
    register() is simulator-provider private. publish() resolves its actual source
    epoch before adding a common channel offset, so D3 delays the whole window.
    """
    def __init__(self,max_windows=3):
        if type(max_windows)is not int or max_windows<3:
            raise ValueError('history must cover boot and one-window delay')
        self.max_windows=max_windows
        self._windows=OrderedDict()
        self._published={}
        self._next_sequence=1
        self._last_arrival=None
        self._last_source=None
        self.fault_latched=False
        self.frames=0
        self.duplicates=0
        self.maximum_mean_roundoff={k:0. for k in MEAN_KEYS}
        self.maximum_common_offset_roundoff={k:0. for k in CHANNELS}

    def register(self,epoch_us,begin_us,records,clean_mean,endpoint_q4,instant=False):
        epoch_us=integer(epoch_us);begin_us=integer(begin_us)
        if self._windows and epoch_us<=next(reversed(self._windows)):
            raise ValueError('source epochs strictly increase')
        if begin_us>epoch_us or not records:
            raise ValueError('empty/inverted source window')
        mode=0 if instant else 1
        if (instant and (len(records)!=1 or begin_us!=epoch_us)) or (not instant and (len(records)!=20 or epoch_us-begin_us!=10000)):
            raise ValueError('source aperture/count mismatch')
        mean={k:vector(clean_mean[k],n)for k,n in CHANNELS.items()if k!='joint_pos4'}
        mean['joint_pos4']=vector(endpoint_q4,4)
        kept=[]
        for i,record in enumerate(records):
            expected=epoch_us if instant else begin_us+500*i
            if integer(record['sampled_us'])!=expected or integer(record['encoder_pos_sampled_us'])!=expected or integer(record['encoder_rate_sampled_us'])!=expected:
                raise ValueError('raw channel source time mismatch')
            r={k:vector(record[k],n)for k,n in CHANNELS.items()}
            r.update(sampled_us=expected,encoder_pos_sampled_us=expected,encoder_rate_sampled_us=expected)
            kept.append(r)
        if instant and not np.array_equal(kept[0]['joint_pos4'],mean['joint_pos4']):
            raise ValueError('instant endpoint position mismatch')
        for k in MEAN_KEYS:
            raw=np.mean([r[k]for r in kept],axis=0)
            tolerance=2e-12*(1.+float(np.max(np.abs(mean[k]))))
            if np.max(np.abs(raw-mean[k]))>tolerance:
                raise ValueError('private raw not original source mean')
        self._windows[epoch_us]=dict(sequence=self._next_sequence,epoch=epoch_us,begin=begin_us,mode=mode,records=kept,mean=mean)
        self._next_sequence+=1
        while len(self._windows)>self.max_windows:
            removed,_=self._windows.popitem(last=False)
            self._published.pop(removed,None)

    def publish(self,packet):
        if self.fault_latched:
            raise ValueError('publisher fault latched')
        try:
            return self._publish(packet)
        except Exception:
            self.fault_latched=True
            raise

    def _publish(self,packet):
        if not packet.validity or not math.isfinite(packet.time_s) or not math.isfinite(packet.arrival_s):
            raise ValueError('invalid authoritative packet')
        source=int(round(packet.time_s*1e6));arrival=int(round(packet.arrival_s*1e6))
        if source not in self._windows or arrival-source not in(0,10000) or (self._last_arrival is not None and arrival<self._last_arrival) or (self._last_source is not None and source<self._last_source):
            raise ValueError('unknown/stale/out-of-order source epoch')
        source_window=self._windows[source]
        observed={k:vector(getattr(packet,k),n)for k,n in CHANNELS.items()}
        observed_hash=body_hash({k:v.tolist()for k,v in observed.items()})
        duplicate=source in self._published
        if duplicate:
            saved=self._published[source]
            if saved['observed_hash']!=observed_hash:
                raise ValueError('changed duplicate source payload')
            payload=copy.deepcopy(saved['payload'])
            self.duplicates+=1
        else:
            # Private distribution of the ALREADY drawn 100Hz D1/D2 offset.
            # This subtracts the producer's own clean source, not a consumer
            # cancellation or access to episode DR coefficients.
            offsets={k:observed[k]-source_window['mean'][k]for k in CHANNELS}
            noisy=[]
            for r in source_window['records']:
                item={k:(r[k]+offsets[k]).tolist()for k in CHANNELS}
                item.update(sampled_us=r['sampled_us'],encoder_pos_sampled_us=r['encoder_pos_sampled_us'],encoder_rate_sampled_us=r['encoder_rate_sampled_us'],weight_us=0 if source_window['mode']==0 else 500,valid=True)
                noisy.append(item)
                for k in CHANNELS:
                    error=float(np.max(np.abs(np.asarray(item[k])-r[k]-offsets[k])))
                    self.maximum_common_offset_roundoff[k]=max(self.maximum_common_offset_roundoff[k],error)
            for k in MEAN_KEYS:
                error=float(np.max(np.abs(np.mean([s[k]for s in noisy],axis=0)-observed[k])))
                self.maximum_mean_roundoff[k]=max(self.maximum_mean_roundoff[k],error)
                if error>4e-12*(1.+float(np.max(np.abs(observed[k])))):
                    raise ValueError('mean preservation exceeds declared roundoff')
            payload=dict(kind='RAW2K_CORRELATED_SHADOW_NOT_OLD_BENCHMARK',sequence=source_window['sequence'],source_epoch_us=source,window_begin_us=source_window['begin'],window_end_us=source,aperture_us=source-source_window['begin'],mean_mode=source_window['mode'],count=len(noisy),sample_weight_us=0 if source_window['mode']==0 else 500,dropped_count=0,correlated_postmean_noise=True,extra_information_branch=True,hardware_binding=False,actuation_used=False,mean={k:observed[k].tolist()for k in MEAN_KEYS},endpoint_joint_pos4=observed['joint_pos4'].tolist(),samples=noisy)
            payload['payload_SHA']=body_hash(payload)
            self._published[source]=dict(observed_hash=observed_hash,payload=copy.deepcopy(payload))
        payload.update(arrival_us=arrival,duplicate_source=duplicate)
        validate_projection(payload)
        self.frames+=1
        self._last_arrival=arrival;self._last_source=source
        return payload

    def receipt(self):
        return dict(kind='PRODUCER_PRIVATE_NUMERIC_CHECK_SUMMARY_NO_CLEAN_OR_OFFSETS',frames=self.frames,duplicate_frames=self.duplicates,fault_latched=self.fault_latched,maximum_mean_roundoff=self.maximum_mean_roundoff,maximum_common_offset_roundoff=self.maximum_common_offset_roundoff,mean_bit_identity_claimed=False,independent_2k_noise_claimed=False,hardware_binding=False,actuation_used=False)
