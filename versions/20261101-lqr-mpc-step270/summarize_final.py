"""Verify final saved evidence, summarize matched DR trials, export review data."""
from pathlib import Path
import collections,csv,hashlib,json,math
ROOT=Path(__file__).resolve().parent

def end_success(r):return bool(r.get('success') and r.get('stop_reason')=='complete' and r.get('stable_at_end',0)>=.5)
def wilson(k,n):
    z=1.95996398454;p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]

if __name__=='__main__':
    evidence=ROOT/'results/FINAL_EVIDENCE_V2';manifest=json.load(open(evidence/'manifest.json'))
    for name,sha in manifest['source_sha256'].items():assert hashlib.sha256((evidence/name).read_bytes()).hexdigest()==sha,name
    proofs=[]
    for case in manifest['cases']:
        folder=evidence/case['case'];result=json.load(open(folder/'result.json'));rows=json.load(open(folder/'trajectory.json'));run=0;maxrun=0;qualified=[]
        for r in rows:
            qv=r['qvel'];linear=math.sqrt(sum(v*v for v in qv[:3]));angular=math.sqrt(sum(v*v for v in qv[3:6]))
            valid=(r['tops']==2 and min(r['wheel_top_force_N2'])>=1 and r['nonwheel']==0 and r['footprint_margin_m']>0 and r['within_top'] and r['upright_cos']>.95 and linear<.3 and angular<.5)
            run=run+1 if valid else 0;maxrun=max(maxrun,run)
            if run>=50:qualified.append(r)
        if result['success']:
            assert result['cross']['flight_id']==1
            crossrow=min(rows,key=lambda r:abs(r['time']-result['cross']['time']))
            assert abs(crossrow['time']-result['cross']['time'])<1e-8
            assert crossrow['support_wheels']==0 and crossrow['nonwheel']==0 and crossrow['footprint_margin_m']>0
            assert min(p[2]-.0625 for p in crossrow['wheel_xyz'])>.268
            assert maxrun>=50 and len(qualified)>0
            assert not result['returned_ground_after_cross'] and not result['edge_return_after_cross']
        assert abs(rows[-1]['time']-result['last']['time'])<1e-8
        last=qualified[-1] if qualified else None
        proofs.append({'case':case['case'],'success':result['success'],'seed':result['config']['seed'],'dr':result['config']['full_dr'],'mpc':result['config']['mpc'],'sample_hz':100,'verified_contact_stable_max_s':maxrun*.01,'stable_max_s':result['stable_time'],'stable_at_end_s':result['stable_at_end'],'cross':result['cross'],'last_stable_top_force_N2':last['wheel_top_force_N2'] if last else None,'last_stable_footprint_m':last['footprint_margin_m'] if last else None,'nonwheel_controls':result['nonwheel_contact_controls'],'stop':result['stop_reason']})
    batch=json.load(open(ROOT/'results/FINAL_FULLDR_MATCHED_V2/summary.json'));raw=[r['result'] for r in batch['rows'] if r['result']['config']['full_dr']];groups={};csvrows=[]
    for mode in [False,True]:
        rr=sorted([r for r in raw if r['config']['mpc']==mode],key=lambda r:r['config']['seed']);assert len(rr)==64 and len({r['config']['seed'] for r in rr})==64
        ever=sum(r['success'] for r in rr);end=sum(end_success(r) for r in rr);cross=sum(bool(r['cross'] and r['cross']['flight_id']==1) for r in rr)
        d3={}
        for delay in [0,1]:
            gg=[r for r in rr if r['DR']['D3']['shared_feedback_delay_ticks100Hz']==delay]
            d3[str(delay*10)]={'n':len(gg),'ever':sum(r['success'] for r in gg),'end':sum(end_success(r) for r in gg),'health':sum(r['stop_reason']=='health' for r in gg)}
        groups['MPC' if mode else 'LQR']={'n':64,'ever':ever,'ever_CI95':wilson(ever,64),'end':end,'end_CI95':wilson(end,64),'cross_first':cross,'health':sum(r['stop_reason']=='health' for r in rr),'success_then_health':sum(r['success'] and r['stop_reason']=='health' for r in rr),'D3_delay_ms':d3,'max_closure_m':max(r['max_closure'] for r in rr),'max_mimic_rad':max(r['max_mimic'] for r in rr)}
        for r in rr:
            csvrows.append({'controller':'MPC' if mode else 'LQR','seed':r['config']['seed'],'success_ever':r['success'],'success_at_end':end_success(r),'stable_max_s':r['stable_time'],'stable_at_end_s':r['stable_at_end'],'stop':r['stop_reason'],'first_flight_cross':bool(r['cross'] and r['cross']['flight_id']==1),'nonwheel_controls':r['nonwheel_contact_controls'],'observation_delay_ms':r['DR']['D3']['requested_delay_us']/1000,'leg_target_delay_ms':r['DR']['D4']['action_delay_us6'][0]/1000,'wheel_target_delay_ms':r['DR']['D4']['action_delay_us6'][2]/1000,'mass_factor':r['DR']['D0']['all_moving_bodies_shared_mass_inertia_factor'],'closure_max_m':r['max_closure'],'mimic_max_rad':r['max_mimic'],'mpc_solve_median_ms':r['mpc_solve_ms_median'],'mpc_solve_max_ms':r['mpc_solve_ms_max']})
    with open(ROOT/'FINAL_DR_TRIALS.csv','w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    out={'verified_frozen_source_hashes':len(manifest['source_sha256']),'all_selected_evidence_checks_passed':True,'scope':'saved 100Hz control samples; not every 0.5ms physics tick','groups':groups,'selected_evidence':proofs}
    (ROOT/'FINAL_METRICS.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
