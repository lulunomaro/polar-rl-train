from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
s=(D/'review_fullroute.py').read_text(encoding='utf8').replace('approved_E1_G1_complete_wave_route_behavior_v3','approved_E1_G1_complete_wave_route_behavior_v4').replace('FULL_ROUTE_COLLECTED','PROXY_ROUTE_COLLECTED').replace('FULL_ROUTE_REVIEW','PROXY_ROUTE_REVIEW').replace('0a9cd1755bf4bbb21b97b5813a55068110e44592d49718ea6366df2fce7cc54c','df378431ae186eb6d40eb6016095b42f03b077450c960916b8cef3ff0ef8de57')
s=s.replace("a['COM_link_pos'][:,i,wheelids,0]","a['COM_link_pos'][:,i,:,:][:,wheelids,0]")
s=s.replace("np.array(p['initial']['root'])[:,:2],starts","np.array(p['initial']['root'])[:,:2],starts.astype(np.float32)")
ast.parse(s);p=D/'review_proxy_fullroute.py';assert not p.exists();p.write_text(s,encoding='utf8')
(R/'PROXY_REVIEWER_CPU_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-CPU-FULLROUTE-READER-02',CPU_AST_passed=True,explicit_time_env_body_axis_index=True,requested_reset_compared_after_original_float32_SDK_representation=True,original_numeric_tolerances_unchanged=True,actual_result_pending=True),indent=2),encoding='utf8')
