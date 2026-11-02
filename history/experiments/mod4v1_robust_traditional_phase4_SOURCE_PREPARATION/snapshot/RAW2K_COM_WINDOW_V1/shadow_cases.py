"""Consume exactly6 sensor-only manifest paths; no neighboring original files."""
from pathlib import Path
import hashlib,json,sys,math
import numpy as np
from raw_functional import Stitch,Prefix,endpoint_model,TASK
R=Path(__file__).resolve().parent;M=TASK/'RAW2K_SHADOW_V1/SENSOR_ONLY_MANIFEST.json';HORIZONS=(50000,100000,150000)
def clean(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x

def stats(x):
    a=np.asarray(list(x),float);return None if not len(a) else {'n':len(a),'min':float(a.min()),'p50':float(np.median(a)),'p95':float(np.percentile(a,95)),'max':float(a.max())}

def run_shadow(out):
    out=Path(out);assert not (out/'SUMMARY.json').exists();out.mkdir(parents=True,exist_ok=True);mraw=M.read_bytes();manifest=json.loads(mraw);assert len(manifest['files'])==6 and manifest['hardware_binding'] is False
    admitted={str(Path(x['path']).resolve()):x for x in manifest['files']};model=endpoint_model();summary=[];artifacts=[];reads=[]
    for filename,src in admitted.items():
        p=Path(filename);assert p.name=='sensor_shadow.jsonl';s=Stitch();hasher=hashlib.sha256();frames=0;size=0
        with p.open('rb') as f:
            for line in f:hasher.update(line);size+=len(line);s.add(json.loads(line));frames+=1
        assert frames==src['frames'] and size==src['bytes'] and hasher.hexdigest()==src['producer_SHA'];reads.append({'path':str(p),'frames':frames,'bytes':size,'producer_SHA_verified':src['producer_SHA']})
        pref=Prefix(s.points);bytime={x['sampled_us']:i for i,x in enumerate(s.points)};endpoint_cache={};errors=[]
        for e in s.ends:
            i=e['index'];x=s.points[i]
            try:endpoint_cache[i]=model.evaluate(x['joint_pos4'],x['joint_vel4'],x['gyro_body'],x['wheel_vel2'])
            except (ValueError,ArithmeticError) as exc:endpoint_cache[i]=None;errors.append({'source_sequence':e['sequence'],'time_us':x['sampled_us'],'reason':type(exc).__name__+': '+str(exc),'no_zero_filled':True})
        results=[]
        for e in s.ends:
            j=e['index'];last=s.points[j]['sampled_us']
            for T in HORIZONS:
                row={'id':src['id'],'source_sequence':e['sequence'],'source_epoch_us':e['source_epoch_us'],'arrival_us':e['arrival_us'],'last_raw_sample_us':last,'T_us':T,'trusted_cue':0,'confidence_cap':.50,'hardware_binding':False,'no_actual_continuous_COMtruth_comparison':True}
                i=bytime.get(last-T)
                if i is None or i not in endpoint_cache or pref.segment[i]!=pref.segment[j]:row['status']='INSUFFICIENT_CONTIGUOUS_SAME_TIME_ENDPOINT_WINDOW';results.append(row);continue
                a,b=endpoint_cache[i],endpoint_cache[j]
                if a is None or b is None:row['status']='NOMINAL_ENDPOINT_GEOMETRY_UNCERTAIN';results.append(row);continue
                sol=pref.evaluate(i,j,a['u_B3'],b['u_B3']);budget=pref.discrete_budget(i,j,sol,a,b)
                row.update(status='NEW_CORRELATED_RAW2K_DISCRETEFUNCTIONAL_SHADOW_ONLY',window_start_us=last-T,window_end_us=last,window_average_age_us=e['arrival_us']-(last-T/2),raw_point_epoch_alignment_difference_us=e['source_epoch_us']-last,comparison_definition='same rawpoint t0/t1 and u0/u1; oldauthoritative mean gyro/proper constant over original bins; not originalepoch endpoint-policy byte-replay',raw_discrete_vector3=sol['raw_discrete_average3'],raw_discrete_norm_m_s2=float(np.linalg.norm(sol['raw_discrete_average3'])),mean_bin_vector3=sol['mean_bin_same_raw_endpoint_average3'],mean_bin_norm_m_s2=float(np.linalg.norm(sol['mean_bin_same_raw_endpoint_average3'])),paired_vector_difference_norm_m_s2=sol['paired_vector_difference_norm_m_s2'],paired_norm_difference_m_s2=sol['paired_norm_difference_m_s2'],raw_relative_R_end=sol['raw_R_relative_end'],mean_relative_R_end=sol['mean_R_relative_end'],raw_force_average3=sol['raw_force3'],raw_boundary_average3=sol['raw_boundary3'],endpoint_u0=a['u_B3'],endpoint_u1=b['u_B3'],endpoint_u_error0_m_s=a['u_error_norm_m_s'],endpoint_u_error1_m_s=b['u_error_norm_m_s'],conditional_discrete_budget=budget)
                results.append(clean(row))
        case={'id':src['id'],'source_manifest_entry':src,'frames':frames,'total_samples_including_repeated_and_boot':s.total_samples,'unique_source_samples_including_instant_boot':s.unique_source_samples,'joined_steady_samples':len(s.points),'boot_frames_excluded':s.boots,'duplicate_source_frames_excluded':s.duplicates,'max_authoritative_mean_vs_raw_recompute_roundoff':s.mean_max_error,'authoritative_mean_old_packet_equality':'producer_claim; originalpacket/trace not admitted or independently read','epoch_endpoint_joint_q_minus_last_rawq_maxabs':stats(s.endpoint_q_time_difference),'endpoint_geometry_events':errors,'windows':{}}
        for T in HORIZONS:
            rr=[x for x in results if x['T_us']==T];g=[x for x in rr if 'conditional_discrete_budget' in x];case['windows'][str(T)]={'T_ms':T/1000,'fresh_end_frames':len(rr),'numeric_windows':len(g),'numeric_rate':len(g)/len(rr),'window_average_age_us':stats(x['window_average_age_us'] for x in g),'paired_raw_minus_mean_vector_difference_m_s2':stats(x['paired_vector_difference_norm_m_s2'] for x in g),'paired_norm_difference_m_s2':stats(x['paired_norm_difference_m_s2'] for x in g),'raw_discrete_norm_m_s2':stats(x['raw_discrete_norm_m_s2'] for x in g),'proposed_discrete_radius_m_s2':stats(x['conditional_discrete_budget']['proposed_discrete_functional_radius_m_s2'] for x in g),'mean_approx_radius_to_same_discretefunctional_m_s2':stats(x['conditional_discrete_budget']['paired_mean_approximation_radius_to_same_discretefunctional_m_s2'] for x in g),'continuous_true_COM_radius':None,'continuous_trusted_cue_rows':0,'all_trusted_cues_uncertain':True,'conditional_discrete_nonfreefall_interval_diagnostic_only':sum(x['conditional_discrete_budget']['conditional_interval_NOT_trusted_cue']=='nonfreefall_like_under_discrete_model_assumptions_only' for x in g),'same_old_model_noise_bounds_no_IID_reduction':True}
        dest=out/(src['id']+'_raw2k_window_shadow.jsonl');assert not dest.exists();buf=''.join(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n' for x in results).encode();dest.write_bytes(buf);artifacts.append({'path':str(dest),'bytes':len(buf),'producer_SHA':hashlib.sha256(buf).hexdigest(),'derived_not_original_trace':True});summary.append(case)
    data={'status':'RAW2K_OBSERVABLE_DISCRETE_FUNCTIONAL_NEW_CORRELATED_INFORMATION_BRANCH_ALL_TRUSTED_CUES_UNCERTAIN','input_manifest_SHA':hashlib.sha256(mraw).hexdigest(),'input_reads':reads,'cases':summary,'total_frames':sum(x['frames'] for x in summary),'total_samples':sum(x['total_samples_including_repeated_and_boot'] for x in summary),'unique_source_samples':sum(x['unique_source_samples_including_instant_boot'] for x in summary),'joined_steady_samples':sum(x['joined_steady_samples'] for x in summary),'discrete_functional_not_continuous_true_COM':'No independent2k worldCOM/contacttruth admitted. Sub-.5ms motion/correlation bound unbound. Observable paireddifference is not accuracy.','original_controller_input':'original100Hzpacket unchanged; newshadow rawnotactuated','same_time_raw_endpoints_no_epochq_meanrate_mix':True,'common_offset_correlations_not_IID_no_sqrt20':True,'confidence_cap':.50,'frozen_trusted_threshold':.60,'hardware_binding':False,'new_physics_Git_GPU_agents_realIO':False,'original_trace_result_DR_GT_reads':0,'artifacts':artifacts}
    (out/'SUMMARY.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return data
