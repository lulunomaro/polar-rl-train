"""Measure full-map failure timing without changing the controller or terrain."""
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def main():
    folder=HERE/'evidence/stage2_final/stair';rows=[]
    for path in sorted((folder/'cases').glob('*rm27*.json')):
        case=json.loads(path.read_text())
        if case['dr'] or case['course'].endswith('400'):continue
        with np.load(folder/'traces'/(path.stem+'.npz')) as data:
            trace=data['reference_trace'];physics=data['physics']
        second=np.flatnonzero(trace[:,16]>.5)
        index=int(second[0]) if len(second) else None
        reentry=np.flatnonzero(physics[index:,1]==2)+index if index is not None else []
        rows.append(dict(id=case['id'],course=case['course'],speed=case['speed'],
            passed=case['passed'],physical_crossed=case['physical_crossed'],failure=case['failure'],
            initial_yaw_error_deg=float(trace[0,5]),initial_left_right_face_stagger_m=float(abs(trace[0,11]-trace[0,12])),
            peak_yaw_error_deg=float(abs(trace[:,5]).max()),first_contact_delay_ms=case['trigger_delay_ms'],
            intermediate_support_windows=case['longest_bilateral_support_windows_20ms'][0],
            second_contact_s=float(physics[index,0]) if index is not None else None,
            phase_at_second_contact=int(physics[index,1]) if index is not None else None,
            reentry_after_second_contact_ms=float((physics[reentry[0],0]-physics[index,0])*1000) if len(reentry) else None,
            final_e0_support_windows=case['final_deck_best_windows_20ms'],end_phase=case['end_phase'],
            trace=str((folder/'traces'/(path.stem+'.npz')).relative_to(HERE))))
    put(HERE/'evidence/STAGE2_RM27_FAILURE_DIAGNOSIS.json',dict(rows=rows,
        full_map_center_tread_m=dict(west=.730,east=.736),aa_center_tread_m=1.20,
        collision_difference='Original full map: tiled heightfields. A–A fixture: vertical mesh/box faces.',
        findings=['Initial headings match their reset commands; no spawn-heading error appears in these traces.',
                  'On several second-face encounters E_stair is already active, or reenters from TREAD_BRIDGE; those failures cannot be described as a missing second trigger.',
                  'Measured yaw drift, incomplete second-stage crossing, and failure to restore E0 support remain separate physical/control defects.'],
        causal_limit='These observations do not isolate a single cause. All six nominal full-map failures remain failures.'))


if __name__=='__main__':main()
