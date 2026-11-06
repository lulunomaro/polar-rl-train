"""Diagnostic-only explicit metadata normalization; no controller/force binding.
Input values ONLY from the original public SensorPacket. Never read MjData/DR.
"""
import math
from signal_alignment_v1 import ChannelSpec,ChannelSample,SignalAligner,QueryResult
from SENSOR_TIME_METADATA_V1.publisher import ROLES
FIELDS={'encoder_q4':('joint_pos4',4),'encoder_qd4':('joint_vel4',4),
        'wheel_vel2':('wheel_vel2',2),'gyro_B':('gyro_body',3),
        'proper_imu_B':('accel_proper_body',3),'motor_tau6':('motor_torque6',6)}

class PublicSignalAdapter:
    def __init__(self):
        # No rate/curvature/noise/clock calibration has been established.
        self.aligner=SignalAligner([ChannelSpec(k,n)for k,(_,n)in FIELDS.items()])
        self.offers=0;self.aligned=0;self.status_counts={};self.normalization_errors=[]

    def observe(self,packet,metadata,now_s):
        self.offers+=1
        try:
            matching=isinstance(metadata,dict) and metadata.get('usable_for_alignment') is True
            if matching:
                matching=bool(abs(float(metadata['packet_epoch_s'])-float(packet.time_s))<=1e-8
                    and abs(float(metadata['packet_arrival_s'])-float(packet.arrival_s))<=1e-8
                    and getattr(packet,'validity',False) is True)
            for name,(field,n) in FIELDS.items():
                c=metadata.get('channels',{}).get(name,{}) if matching else {}
                t=c.get('timestamp_s');kind=c.get('kind')
                if not c.get('usable_for_alignment') or t is None:
                    self.aligner.push(name,None);continue
                if c.get('measurement_role')!=ROLES[name]:
                    raise ValueError('Public channel role mismatch: '+name)
                values=tuple(float(v)for v in getattr(packet,field))
                if len(values)!=n or not all(math.isfinite(v)for v in values):
                    raise ValueError('Finite public vector required: '+name)
                if kind in ('endpoint','held_command'):
                    start=end=float(t);count=1;moment=0.;normalized='point'
                elif kind=='sampled_boxcar':
                    start=c['window_start_s'];end=c['window_end_s'];count=c['sample_count']
                    moment=c.get('window_second_moment_s2');normalized='sampled_mean'
                else:raise ValueError('Unknown measurement aperture: '+name)
                sample=ChannelSample(float(t),values,start,end,count,normalized,
                    c['provenance']+';measurement_role='+c['measurement_role'],
                    c.get('clock_error_bound_s'),None,moment)
                self.aligner.push(name,sample)
            result=self.aligner.query(float(now_s))
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError)as exc:
            # Observe errors stay diagnostic; never replace engine inputs or rescue it.
            self.normalization_errors.append(dict(offer=self.offers,error=repr(exc)))
            for name in FIELDS:self.aligner.push(name,None)
            result=QueryResult('PUBLIC_METADATA_NORMALIZATION_ERROR',detail=repr(exc))
        self.status_counts[result.status]=self.status_counts.get(result.status,0)+1
        if result.frame is not None:
            if result.frame.force_input_ready or result.frame.hardware_sync_proven or result.frame.alpha_B_rad_s2 is not None:
                raise AssertionError('Observation adapter must not grant force or clock authority')
            self.aligned+=1
        return result

    def summary(self):
        return dict(offers=self.offers,aligned_frames=self.aligned,status_counts=self.status_counts,
            normalization_errors=self.normalization_errors,history_lengths={k:len(h)for k,h in self.aligner.history.items()},
            latched_fault=self.aligner.fault,rate_curvature_noise_clock_bounds_supplied=False,
            force_input_ready=False,controller_or_proxy_connections=0,
            query_phase='after original tick/physics; age includes this diagnostic transport delay')
