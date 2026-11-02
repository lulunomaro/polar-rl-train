"""50/100/150ms math shadow on sealed sensor-only projections, no originals."""
from pathlib import Path
from dataclasses import asdict
import hashlib,json,sys,math
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent;sys.path.insert(0,str(TASK))
from COM_SENSOR_CAPTURE_AUDIT_V1.shadow_audit import validate,window,TOP
from DYNAMIC_COM_MOTION_V1.com_motion import Geometry,Config as FrozenCOMConfig
from window_math import EndpointModel,BudgetAssumptions,piecewise_constant_window,capture_budget
PROJ=TASK/'SENSOR_CAPTURE_CLOOP_V1';HORIZONS=(50000,100000,150000)
def clean(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def stats(x):
    a=np.asarray(list(x),float)
    return None if not len(a) else {'n':len(a),'min':float(a.min()),'p50':float(np.median(a)),'p95':float(np.percentile(a,95)),'max':float(a.max())}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_projection(p,expected):
    p=Path(p).resolve();assert p.parent==PROJ.resolve() and p.name.endswith('_sensor_only.jsonl'),'No original trace or unrelated input path'
    raw=p.read_bytes();assert sha(raw)==expected['SHA'] and len(raw)==expected['bytes'];rows=[json.loads(x) for x in raw.splitlines()];assert len(rows)==expected['rows'];return rows

def run_shadow(out):
    out=Path(out);assert not (out/'SUMMARY.json').exists();out.mkdir(parents=True,exist_ok=True);manifest_raw=(PROJ/'MANIFEST.json').read_bytes();manifest=json.loads(manifest_raw);assert set(manifest['allowed_keys'])==TOP and sum(x['rows'] for x in manifest['sources'])==4400
    a=BudgetAssumptions();cfg=FrozenCOMConfig();assert a.frozen_cue_min_confidence==cfg.min_cue_confidence and a.freefall_max_g==cfg.freefall_max_g and a.nonfreefall_min_g==cfg.nonfreefall_min_g
    g=Geometry();endmodel=EndpointModel(g,assumptions=a);summaries=[];derived=[];inputmeta=[]
    for source in manifest['sources']:
        rows=read_projection(source['path'],source);history={};previous=None;payload_old=None;allout=[];dup=boot=firstmean=0;endpoint_errors=[]
        for i,row in enumerate(rows):
            p=validate(row,i);w=window(p);t=p['sampled_us'];arrival=p['arrival_us'];key=(t,p['sequence']);payload=json.dumps({k:v for k,v in p.items() if k!='arrival_us'},sort_keys=True)
            common={'capture_index':i,'sampled_us':t,'arrival_us':arrival,'hardware_binding':False,'strict_cue':0,'conditional_cue':0,'confidence':0.}
            if previous==key:
                assert payload_old==payload;dup+=1
                for T in HORIZONS:allout.append(dict(common,T_us=T,status='DUPLICATE_EPOCH_NO_NEW_WINDOW',strict_radius=None))
                continue
            if previous is not None:assert t>previous[0] and p['sequence']>previous[1]
            previous=key;payload_old=payload
            if w['kind']=='instant':
                boot+=1
                for T in HORIZONS:allout.append(dict(common,T_us=T,status='BOOT_INSTANT_NOT_MEAN_WINDOW',strict_radius=None))
                continue
            if not history:firstmean+=1
            try:ep=endmodel.evaluate(p['joint_q4'],p['joint_dq4'],p['gyro_body'],p['wheel_spin2']);ep_error=None
            except (ValueError,ArithmeticError) as exc:ep=None;ep_error=type(exc).__name__+': '+str(exc);endpoint_errors.append({'capture_index':i,'error':ep_error,'not_physical_failure':True})
            history[t]={'packet':p,'endpoint':ep,'window':w,'error':ep_error}
            for T in HORIZONS:
                start=t-T;n=T//10000;need=[start+10000*j for j in range(n+1)]
                if any(x not in history for x in need):allout.append(dict(common,T_us=T,status='INSUFFICIENT_CONTIGUOUS_MEAN_EPOCHS_NO_BOOT_MIX',strict_radius=None));continue
                if any(history[x]['endpoint'] is None for x in need):allout.append(dict(common,T_us=T,status='ENDPOINT_GEOMETRY_UNCERTAIN',strict_radius=None));continue
                bins=[history[x]['packet'] for x in need[1:]]
                if any(b['window_begin_us']!=need[j] for j,b in enumerate(bins)):allout.append(dict(common,T_us=T,status='APERTURE_GAP_NOT_INTERPOLATED',strict_radius=None));continue
                omega=np.asarray([b['gyro_body'] for b in bins]);proper=np.asarray([b['proper_accel_body'] for b in bins]);h=[.01]*n;e0=history[start]['endpoint'];e1=history[t]['endpoint'];solution=piecewise_constant_window(omega,proper,h,e0['u_B3'],e1['u_B3']);budget=capture_budget(solution,e0,e1,proper,h,a)
                allout.append(clean(dict(common,T_us=T,status='CONDITIONAL_BOX_MODEL_AND_DECLARED_TRANSPORT_BUDGET_ONLY',window_start_us=start,window_end_us=t,window_midpoint_us=(start+t)/2,nominal_window_average_age_us=arrival-(start+t)/2,discrete_weighted_sample_time_us=(start+t)/2-250,discrete_first_moment_age_us=arrival-(start+t)/2+250,no_current_instantaneous_claim=True,relative_frame='BODY_at_window_start_gauge_no_world_yaw_input',numeric_average_COM_proper_start_frame3=solution['average_COM_proper_start_frame3'],numeric_average_norm_m_s2=float(np.linalg.norm(solution['average_COM_proper_start_frame3'])),force_transport_average3=solution['force_transport_average3'],velocity_boundary_average3=solution['velocity_boundary_average3'],R_relative_end=solution['R_relative_end'],u_start=e0['u_B3'],u_end=e1['u_B3'],endpoint_start_u_error_m_s=e0['u_error_norm_m_s'],endpoint_end_u_error_m_s=e1['u_error_norm_m_s'],endpoint_start_wheel_bound=e0['wheel_bound'],endpoint_end_wheel_bound=e1['wheel_bound'],strict_radius=None,strict_reasons=['MISSING_INTRAWINDOW_R_F_CORRELATION_BOUND','ENDPOINT_MEAN_RATE_IS_NOT_INSTANT','NO_MEASURED_CALIBRATION_OR_GLOBAL_MODEL_BOUND'],conditional=budget,confidence=budget['conditional_confidence'])))
        case={'case':source['case'],'source_projection_SHA':source['SHA'],'original_case_sourceSHA_reference_only':source['source_trace_SHA'],'rows':len(rows),'duplicate_sensor_epochs':dup,'boot_instant_epochs':boot,'first_mean_epochs':firstmean,'endpoint_model_events':endpoint_errors,'windows':{}}
        for T in HORIZONS:
            aout=[x for x in allout if x['T_us']==T];good=[x for x in aout if 'conditional' in x];cname=lambda x:x['conditional']['conditional_interval_NOT_trusted_cue']
            case['windows'][str(T)]={'T_ms':T/1000,'rows_total':len(aout),'numeric_conditional_windows':len(good),'numeric_rate':len(good)/len(aout),'strict_trusted_windows':0,'conditional_trusted_windows':0,'all_returned_cues_uncertain':True,'proposed_radius_m_s2':stats(x['conditional']['proposed_error_radius_m_s2'] for x in good),'numeric_norm_m_s2':stats(x['numeric_average_norm_m_s2'] for x in good),'window_average_age_us':stats(x['nominal_window_average_age_us'] for x in good),'force_noise_term_m_s2':stats(x['conditional']['proper_noise_not_reduced_with_N_m_s2'] for x in good),'missing_transport_term_m_s2':stats(x['conditional']['missing_proper_transport_sampling_m_s2']+x['conditional']['gyro_orientation_transport_m_s2'] for x in good),'boundary_term_m_s2':stats(x['conditional']['boundary_endpoint_error_m_s2'] for x in good),'conditional_interval_nonfreefall_diagnostic_only':sum(cname(x)=='nonfreefall_like_under_declared_radius_only' for x in good),'conditional_interval_freefall_diagnostic_only':sum(cname(x)=='freefall_like_under_declared_radius_only' for x in good),'conditional_interval_overlap':sum(cname(x)=='overlap' for x in good),'assumed_confidence_max':.5,'no_threshold_lowering':True}
        dest=out/(source['case']+'_integrated_shadow.jsonl');blob=''.join(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n' for x in allout).encode();assert not dest.exists();dest.write_bytes(blob);derived.append({'path':str(dest),'bytes':len(blob),'SHA':sha(blob),'producer_hashed_from_output_buffer':True,'not_original_rawtrace':True});summaries.append(case);inputmeta.append({'path':source['path'],'SHA':source['SHA'],'bytes':source['bytes'],'rows':source['rows'],'original_case_only_sourceSHA':source['source_trace_SHA']})
    summary={'status':'FINITE_WINDOW_IDENTITY_MATH_SHADOW_ONLY_NO_HARDWARE_CUE_QUALIFICATION','projection_manifest_SHA':sha(manifest_raw),'projection_rows':4400,'window_lengths_ms':[50,100,150],'cases':summaries,'assumptions':asdict(a),'frozen_cue_configuration':{'min_confidence':cfg.min_cue_confidence,'freefall_max_g':cfg.freefall_max_g,'nonfreefall_min_g':cfg.nonfreefall_min_g},'publicD1_source_reference':'sealed COM_SENSOR_CAPTURE_AUDIT_V1/ASSUMPTIONS.json; samehalfwidths allcases, no episode receipt','continuous_transport_not_observed_from_boxcar':True,'midpoint_shortcut_not_claimed_exact':True,'all_cues_uncertain_hardware_binding_false':True,'fixed_model_error_default_sum_bound_not_independence_or_cancellation':True,'alpha_qdd_estimated_or_differenced_for_algorithm':False,'original_trace_DR_GT_reads':0,'new_physics_Git_agents_realIO':False,'input_projection_provenance':inputmeta,'derived_artifacts':derived,'comparison_caveat':'Different temporal target/transport assumptions from earlier point-COM audit. A smaller conditional sphere is not truth accuracy or oldbenchmark/hardware graduation.'}
    (out/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return summary
