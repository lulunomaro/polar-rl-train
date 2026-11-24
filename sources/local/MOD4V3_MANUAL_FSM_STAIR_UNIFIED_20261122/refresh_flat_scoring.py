"""Re-score retained traces with the reference flat/rough tracking protocol."""
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put

def main():
    for name in ('flat_r3','flat60_r2'):
        folder=HERE/'evidence'/name
        original=json.loads((folder/'RESULT.json').read_text(encoding='utf-8'))
        rows=[]
        for raw in original['rows']:
            row=dict(raw)
            trace=np.load(folder/'traces'/(row['id']+'.npz'))['reference_trace']
            tail=trace[-400:]
            if row['course']!='flat60':
                row['passed']=bool(row['failure'] is None and np.abs(tail[:,2]-row['speed']).mean()<=.25
                    and abs(tail[:,20].mean()-row['wz'])<=.60)
            row['strict_support_400hz']=bool(row['failure'] is None and
                np.all(np.array(row['longest_bilateral_support_substeps'])>=row['required_support_substeps']))
            rows.append(row)
        result=dict(passed=sum(r['passed'] for r in rows),total=len(rows),
            flat_passed=sum(r['passed'] for r in rows if r['course']=='flat'),
            rough_passed=sum(r['passed'] for r in rows if r['course']=='rough_L9'),rows=rows,
            source='Retained unmodified 400 Hz trajectories',
            protocol='Reference flat16/rough16: speed MAE<=.25 and yaw error<=.60; flat60 retains original task thresholds',
            support_criteria_independent_of_tracking=True)
        put(folder/'CORRECTED_SCORING.json',result)
        print(name,result['passed'],'/',result['total'],'flat',result['flat_passed'],'rough',result['rough_passed'])

if __name__=='__main__':main()
