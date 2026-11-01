"""User-requested new real-pose playback. True277 MOD4 meshes; no mj_step/NN."""
from pathlib import Path
from copy import deepcopy
import argparse,ctypes,hashlib,io,json,os,sys,time,traceback
import xml.etree.ElementTree as ET
import numpy as np
import mujoco,glfw

def fmt(value):return ' '.join(f'{float(x):.9g}' for x in np.asarray(value).ravel())

def main(base,out):
    base=Path(base);out=Path(out);out.mkdir(exist_ok=False)
    purpose=json.loads((base/'reports/FROZEN237_FRESH_USER_E0_DISPLAY_PURPOSE_BEFORE_IO.json').read_bytes())
    receipt=json.loads((base/'reports/ROOT237_ONE_SELECTED230_POSE_TRANSFER_INTEGRITY_ACTUAL.json').read_bytes())
    assert receipt['passed'] and receipt['producer_and_transferred_same_stream_SHA_equal']
    case=purpose['selected_case'];case=dict(case,model_SHA=purpose['selected_model_SHA'],epoch=receipt['epoch'])
    with Path(receipt['path']).open('rb') as file:raw=file.read()
    assert len(raw)==receipt['bytes'] and hashlib.sha256(raw).hexdigest()==receipt['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False) as archive:
        packet={key:archive[key].copy() for key in purpose['npz_members_selected']}
    del raw
    previous=base.parent/'H1_NATIVE178_LATEST_USER_MUJOCO_MOTION_WM_V180_20261031/CPU_DISPLAY180_ACTUAL_V2/USER180_DISPLAY_DATA_COMPLETE.json'
    visual=json.loads(previous.read_bytes())['visual_assets']
    xml_path=Path(visual['xml']['path']);xmlraw=xml_path.read_bytes()
    assert len(xmlraw)==visual['xml']['bytes'] and hashlib.sha256(xmlraw).hexdigest()==visual['xml']['sha256']
    original=ET.fromstring(xmlraw);body={item.attrib['name']:item for item in original.find('worldbody').findall('body')}
    names=purpose['body_names'];assert len(names)==31 and set(names)==set(body)
    origin=np.array([packet['root13'][0,0],packet['root13'][0,1],0.],dtype=np.float64)
    root=ET.Element('mujoco',model='E0 branch repaired copy225 from32341 actual PhysX recorded230')
    ET.SubElement(root,'compiler',angle='radian')
    vis=ET.SubElement(root,'visual');ET.SubElement(vis,'headlight',ambient='.6 .6 .6',diffuse='.6 .6 .6')
    assets=ET.SubElement(root,'asset');mesh_count=0
    for item in original.find('asset'):
        copied=deepcopy(item)
        if copied.tag=='mesh':copied.set('file',str((Path(visual['mesh_directory'])/copied.attrib['file']).resolve()));mesh_count+=1
        elif 'file' in copied.attrib:copied.set('file',str((xml_path.parent/copied.attrib['file']).resolve()))
        assets.append(copied)
    assert mesh_count==277
    world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='0 -1 4',dir='0 0 -1',diffuse='.8 .8 .8')
    ET.SubElement(assets,'texture',name='floor_grid237',type='2d',builtin='checker',rgb1='.34 .32 .29',rgb2='.44 .42 .38',width='512',height='512')
    ET.SubElement(assets,'material',name='floor237',texture='floor_grid237',texrepeat='8 8',reflectance='.05')
    ET.SubElement(world,'geom',name='original_native_plane_top0',type='plane',pos='0 0 0',size='8 8 .05',material='floor237',contype='0',conaffinity='0')
    geometries=0
    for name in names:
        target=ET.SubElement(world,'body',name='actual_'+name,mocap='true',pos='0 0 -10')
        for item in body[name].findall('geom'):
            copied=deepcopy(item);copied.set('name','actual_'+copied.attrib['name']);copied.set('density','0')
            copied.set('contype','0');copied.set('conaffinity','0');copied.set('rgba','.73 .77 .82 1')
            target.append(copied);geometries+=1
    assert geometries==277
    xml=ET.tostring(root,encoding='unicode');(out/'DISPLAY237_TRUE_MOD4_ORIGINAL_FUDAN.xml').write_text(xml,encoding='utf8')
    model=mujoco.MjModel.from_xml_string(xml);data=mujoco.MjData(model)
    assert model.nq==model.nv==0 and model.nmocap==31
    assert glfw.init();window=glfw.create_window(1500,960,'E0 BRANCH 32341 + REPAIR COPY225 | ACTUAL PhysX REPLAY230 | NEW237',None,None)
    assert window;glfw.make_context_current(window);glfw.swap_interval(1);glfw.show_window(window);glfw.focus_window(window)
    camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera)
    camera.lookat[:]=packet['root13'][0,:3]-origin+[0,0,.08];camera.distance=3.5;camera.azimuth=130;camera.elevation=-24
    option=mujoco.MjvOption();mujoco.mjv_defaultOption(option)
    scene=mujoco.MjvScene(model,maxgeom=2000);context=mujoco.MjrContext(model,mujoco.mjtFontScale.mjFONTSCALE_150)
    ids=np.asarray([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'actual_'+name)] for name in names])
    state=dict(paused=False,clock=0.,speed=1.,cursor=(0.,0.),follow=True)
    duration=case['seconds'];positions=packet['body_position_w']-origin
    quats=packet['body_quat_xyzw'][...,[3,0,1,2]]
    assert positions.shape==(case['controls'],31,3) and quats.shape==(case['controls'],31,4)
    chassis=names.index('chassis')
    (out/'DISPLAY237_SINGLE_PASS_POSE_MAPPING_ACTUAL.json').write_text(json.dumps(dict(
        raw_visual_byte_opens=1,raw_visual_integrity_passes=1,npz_member_reads={key:1 for key in packet},
        local_model_reads=0,local_neural_CUDA=False,visual_meshes=277,mocap_bodies=31,
        raw_pose_quaternion_convention='Actual230 SDK xyzw, shared exact210 package body order from actual220',render_quaternion='wxyz',
        first_chassis_root_position_difference_m=float(np.linalg.norm(packet['body_position_w'][0,chassis]-packet['root13'][0,:3])),
        first_chassis_root_quaternion_abs_dot=float(abs(np.dot(packet['body_quat_xyzw'][0,chassis],packet['root13'][0,3:7])))),indent=2),encoding='utf8')
    def key(w,k,scan,action,mods):
        if action not in (glfw.PRESS,glfw.REPEAT):return
        if k==glfw.KEY_ESCAPE:glfw.set_window_should_close(w,True)
        elif k==glfw.KEY_SPACE:state['paused']=not state['paused']
        elif k==glfw.KEY_R:state['clock']=0.
        elif k==glfw.KEY_F:state['follow']=not state['follow']
        elif k in (glfw.KEY_1,glfw.KEY_2,glfw.KEY_3):state['speed']={glfw.KEY_1:1.,glfw.KEY_2:.25,glfw.KEY_3:.1}[k]
        elif k==glfw.KEY_LEFT:state['clock']=max(0.,state['clock']-.02)
        elif k==glfw.KEY_RIGHT:state['clock']=min(duration-.02,state['clock']+.02)
    def cursor(w,x,y):
        a,b=state['cursor'];state['cursor']=(x,y);_,height=glfw.get_window_size(w)
        if glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_LEFT)==glfw.PRESS:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ROTATE_V,(x-a)/height,(y-b)/height,camera)
        elif glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_RIGHT)==glfw.PRESS:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_MOVE_V,(x-a)/height,(y-b)/height,camera)
    def scroll(w,x,y):mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ZOOM,0,-.05*y,camera)
    glfw.set_key_callback(window,key);glfw.set_cursor_pos_callback(window,cursor);glfw.set_scroll_callback(window,scroll)
    class FT(ctypes.Structure):_fields_=[('low',ctypes.c_uint32),('high',ctypes.c_uint32)]
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)];kernel.GetProcessTimes.restype=ctypes.c_int
    created,exited,k,u=FT(),FT(),FT(),FT();assert kernel.GetProcessTimes(kernel.GetCurrentProcess(),ctypes.byref(created),ctypes.byref(exited),ctypes.byref(k),ctypes.byref(u))
    creation=((created.high<<32)|created.low)/10000000.-11644473600.
    started=time.monotonic();last=started;shot=False
    (out/'DISPLAY237_WINDOW_STARTED_ACTUAL.json').write_text(json.dumps(dict(pid=os.getpid(),creation=creation,exe=sys.executable,argv=[sys.executable,*sys.argv],cwd=os.getcwd(),recorded_epoch=time.time(),visible=True,model_iteration=32341,model_SHA=case['model_SHA'],neural_inference=False,physics_steps=0,true_meshes=277,mocap_bodies=31,source230_capture_epoch=case['epoch'],independent_repair_copy225=True,not_live=True,source_case=case),indent=2),encoding='utf8')
    end=', '.join(name for name,value in case['first_episode_original_terminal_flags'].items() if value) or 'original10s evaluation bound'
    while not glfw.window_should_close(window) and time.monotonic()-started<7200:
        now=time.monotonic();dt=min(now-last,.1);last=now
        if not state['paused']:state['clock']=(state['clock']+dt*state['speed'])%duration
        index=min(len(positions)-1,int(state['clock']*50))
        data.mocap_pos[ids]=positions[index];data.mocap_quat[ids]=quats[index];data.time=state['clock']
        mujoco.mj_forward(model,data);width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
        if state['follow']:camera.lookat[:]=positions[index,chassis]+[0,0,.08]
        mujoco.mjv_updateScene(model,data,option,None,camera,mujoco.mjtCatBit.mjCAT_ALL,scene);mujoco.mjr_render(viewport,scene,context)
        forces=np.linalg.norm(packet['wheel_contact_xyz'][index],axis=-1)
        bottoms=packet['authored_wheel_bottom'][index]
        heading=f'E0 JUMP BRANCH / trained parent32341 + independent REPAIR COPY225 / NEW237 VIEW\nGRAY: recorded actual PhysX230 t={(index+1)*.02:.2f}s / {duration:.2f}s; original flags all false at case end'
        heading+='\nOriginal Fudan JUMP19 /16 original weights /flat plane; actor repair copy is explicitly separate'
        cue=case['command']
        heading+=f'\nTrue MOD4 /400N engineering /50Hz policy /400Hz PhysX /TGS32-4 /D0-D7\nControlled eval vx={cue["vx"]:.3f}m/s, yaw=0; speed {state["speed"]:.2f}x; camera follow={state["follow"]}'
        heading+=f'\nWheel force norms L/R={forces[0]:.1f}/{forces[1]:.1f}N | authored bottoms={bottoms[0]*1000:.1f}/{bottoms[1]*1000:.1f}mm'
        heading+='\nRECORDED EVAL / NOT LIVE TRAINING / wheel-air observations do not certify stable landing or270'
        heading+='\nMuJoCo DISPLAY ONLY / no mj_step, NN or WM prediction / world heading preserved'
        helptext='SPACE pause | R replay230 | 1 real /2 quarter /3 tenth speed | F camera follow\nLeft-right seek | mouse orbit/pan | wheel zoom | ESC close'
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPLEFT,viewport,heading,'',context)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,viewport,helptext,'',context)
        if not shot:
            from PIL import Image
            rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,context)
            Image.fromarray(np.flipud(rgb)).save(out/'MUJOCO237_E0_COPY225_INITIAL_FRAME.png');shot=True
        glfw.swap_buffers(window);glfw.poll_events()
    context.free();glfw.destroy_window(window);glfw.terminate()
    (out/'DISPLAY237_WINDOW_EXIT_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),wall_seconds=time.monotonic()-started,only_own_user_window=True)),encoding='utf8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
    try:main(args.base,args.out)
    except BaseException:
        out=Path(args.out)
        if out.is_dir():(out/('DISPLAY237_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc()),indent=2),encoding='utf8')
        raise
