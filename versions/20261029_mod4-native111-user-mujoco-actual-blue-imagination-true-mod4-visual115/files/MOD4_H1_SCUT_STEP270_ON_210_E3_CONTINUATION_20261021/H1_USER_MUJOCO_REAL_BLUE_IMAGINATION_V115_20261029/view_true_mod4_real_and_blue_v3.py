"""Native visual V3: adapt mouse camera call to actual installed five-argument API.
All original collision-display and visualV2 source/error evidence remains intact.
"""
from pathlib import Path
import hashlib,json,time,traceback
HERE=Path(__file__).resolve().parent
v2=(HERE/'view_true_mod4_real_and_blue_v2.py').read_text(encoding='utf8')
needle="s=old.replace(a,b)"
assert v2.count(needle)==1
corrected=v2.replace(needle,"assert old.count(',scn,cam)')==3\nold=old.replace(',scn,cam)',',cam)')\ns=old.replace(a,b)")
corrected=corrected.replace('TRUE_MOD4_REAL_BLUE_INITIAL_FRAME.png','TRUE_MOD4_V3_REAL_BLUE_INITIAL_FRAME.png').replace('TRUE_MOD4_REAL_BLUE_LOW_HOP_FRAME.png','TRUE_MOD4_V3_REAL_BLUE_LOW_HOP_FRAME.png')
scope=dict(__name__='true_visual_v3_camera_interface',__file__=str(HERE/'view_true_mod4_real_and_blue_v3.py'))
exec(compile(corrected,str(HERE/'view_true_mod4_real_and_blue_v3.py'),'exec'),scope)
R=HERE/'reports/true_visual_v3';R.mkdir(exist_ok=True)
scope['R']=R;scope['ns']['R']=R
(R/'USER_DISPLAY_DATA_COMPLETE.json').write_bytes((HERE/'reports/USER_DISPLAY_DATA_COMPLETE.json').read_bytes())
(R/'CAMERA_SIGNATURE_EXACT_V3_REPAIR.json').write_text(json.dumps(dict(epoch=time.time(),v2_wrapper_SHA=hashlib.sha256(v2.encode()).hexdigest(),candidate_wrapper_SHA=hashlib.sha256(corrected.encode()).hexdigest(),change='Three mjv_moveCamera(model,action,dx,dy,scene,camera) calls -> installed API(model,action,dx,dy,camera)',model_or_pose_data_changed=False,new_model_or_raw_reads=0),indent=2),encoding='utf8')
if __name__=='__main__':
    try:scope['ns']['main']()
    except BaseException:
        (R/('V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
