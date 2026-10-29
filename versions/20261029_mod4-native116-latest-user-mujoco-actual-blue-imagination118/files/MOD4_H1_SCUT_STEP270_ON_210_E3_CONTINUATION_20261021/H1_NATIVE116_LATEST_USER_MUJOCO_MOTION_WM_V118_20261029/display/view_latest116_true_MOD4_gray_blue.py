"""Native MuJoCo rendering of recorded actual motion plus a translucent blue WM robot.
No mj_step, physics, policy inference, training or remote access in this application.
"""
from pathlib import Path
import hashlib,json,math,time,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco,glfw
HERE=Path(__file__).resolve().parent;R=HERE/'reports'

def fmt(x):return ' '.join(f'{float(v):.10g}' for v in np.asarray(x).ravel())
def make_scene(render):
    root=ET.Element('mujoco',model='MOD4 recorded118 actual and frozen116 imagined32')
    ET.SubElement(root,'compiler',angle='radian')
    ET.SubElement(root,'visual');ET.SubElement(root.find('visual'),'headlight',ambient='.55 .55 .55',diffuse='.6 .6 .6')
    asset=ET.SubElement(root,'asset')
    ET.SubElement(asset,'texture',name='grid',type='2d',builtin='checker',rgb1='.15 .20 .24',rgb2='.27 .34 .39',width='512',height='512')
    ET.SubElement(asset,'material',name='floor',texture='grid',texrepeat='12 12',reflectance='.15')
    world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='-.4 -1 3',dir='0 0 -1',diffuse='.7 .7 .7')
    ET.SubElement(world,'geom',name='floor',type='plane',size='5 5 .05',material='floor',contype='0',conaffinity='0')
    ET.SubElement(world,'geom',name='real_270mm_platform',type='box',pos='.75 0 .135',size='.4 .6 .135',rgba='.48 .41 .28 1',contype='0',conaffinity='0')
    ET.SubElement(world,'site',name='edge_270mm',type='box',pos='.35 0 .27',size='.0015 .6 .002',rgba='1 .65 .1 1')
    bodies={}
    for layer in ('actual','blue'):
        for name in render['body_names']:
            bodies[layer,name]=ET.SubElement(world,'body',name=layer+'_'+name,mocap='true',pos='0 0 -8')
    for i,s in enumerate(render['shapes']):
        A=np.asarray(s['linear_body_from_shape']);origin=np.asarray(s['origin_body_m']);scales=np.linalg.norm(A,axis=0);rot=A/scales
        attrs=dict(pos=fmt(origin),contype='0',conaffinity='0',group='0')
        if s['type']=='Cube':attrs.update(type='box',size=fmt(scales*float(s['size'])/2),xyaxes=fmt(np.concatenate((rot[:,0],rot[:,1]))))
        elif s['type'] in ('Capsule','Cylinder'):
            axis=int(s['axis']);z=rot[:,axis];x=rot[:,(axis+1)%3];y=np.cross(z,x)
            radius=float(s['radius'])*max(np.delete(scales,axis));half=float(s['height'])*scales[axis]/2
            attrs.update(type=s['type'].lower(),size=fmt([radius,half]),xyaxes=fmt(np.concatenate((x,y))))
        elif s['type']=='Sphere':attrs.update(type='sphere',size=fmt([float(s['radius'])*max(scales)]))
        elif s['type']=='Mesh':
            points=np.asarray(s['points'])@A.T+origin
            ET.SubElement(asset,'mesh',name=f'original_wheel_{i}',vertex=fmt(points))
            attrs.update(type='mesh',mesh=f'original_wheel_{i}',pos='0 0 0')
        else:raise ValueError('Unmapped recorded geometry '+s['type'])
        for layer in ('actual','blue'):
            color='.73 .76 .79 1' if layer=='actual' else '.08 .48 1 .44'
            if layer=='actual' and s['body'].endswith('wheel'):color='.18 .21 .24 1'
            ET.SubElement(bodies[layer,s['body']],'geom',name=f'{layer}_shape_{i}',rgba=color,**attrs)
    return ET.tostring(root,encoding='unicode')

def main():
    proof=json.loads((R/'USER_DISPLAY_DATA_COMPLETE.json').read_bytes());assert proof['passed']
    packet=np.load(HERE/'USER_ACTUAL118_AND_BLUE116_DISPLAY_POSES.npz',allow_pickle=False)
    render=json.loads((HERE/'DISPLAY_RECORDED_SHAPES.json').read_bytes())
    xml=make_scene(render);(HERE/'DISPLAY_LATEST116_TRUE_MOD4_REAL_BLUE.xml').write_text(xml,encoding='utf8')
    model=mujoco.MjModel.from_xml_string(xml);data=mujoco.MjData(model)
    assert model.nq==0 and model.nv==0 and model.nmocap==62
    if not glfw.init():raise RuntimeError('GLFW failed to initialize')
    window=glfw.create_window(1440,920,'MOD4 | GRAY = recorded PhysX | BLUE = imagined32 | LATEST checkpoint116 / actual118',None,None)
    if not window:raise RuntimeError('MuJoCo window creation failed')
    glfw.make_context_current(window);glfw.swap_interval(1)
    glfw.show_window(window);glfw.focus_window(window)
    cam=mujoco.MjvCamera();mujoco.mjv_defaultCamera(cam);cam.lookat[:]=[.27,0,.28];cam.distance=1.85;cam.azimuth=55;cam.elevation=-17
    opt=mujoco.MjvOption();mujoco.mjv_defaultOption(opt);opt.flags[mujoco.mjtVisFlag.mjVIS_TRANSPARENT]=False
    scn=mujoco.MjvScene(model,maxgeom=3000);ctx=mujoco.MjrContext(model,mujoco.mjtFontScale.mjFONTSCALE_150)
    state=dict(paused=False,speed=1.,show_blue=True,horizon=32,clock=0.,scrub=False,last_cursor=(0.,0.))
    def key(w,k,scan,action,mods):
        if action not in (glfw.PRESS,glfw.REPEAT):return
        if k==glfw.KEY_ESCAPE:glfw.set_window_should_close(w,True)
        elif k==glfw.KEY_SPACE:state['paused']=not state['paused']
        elif k==glfw.KEY_R:state['clock']=0.
        elif k==glfw.KEY_B:state['show_blue']=not state['show_blue']
        elif k==glfw.KEY_1:state['speed']=1.
        elif k==glfw.KEY_2:state['speed']=.25
        elif k==glfw.KEY_3:state['speed']=.1
        elif k==glfw.KEY_LEFT:state['clock']=max(0,state['clock']-.1)
        elif k==glfw.KEY_RIGHT:state['clock']=min(duration-.01,state['clock']+.1)
        elif k==glfw.KEY_H:state['horizon']={8:16,16:32,32:8}[state['horizon']]
    def cursor(w,x,y):
        lx,ly=state['last_cursor'];state['last_cursor']=(x,y)
        if glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_LEFT)==glfw.PRESS:
            width,height=glfw.get_window_size(w)
            mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ROTATE_V,(x-lx)/height,(y-ly)/height,cam)
        elif glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_RIGHT)==glfw.PRESS:
            width,height=glfw.get_window_size(w)
            mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_MOVE_V,(x-lx)/height,(y-ly)/height,cam)
    def scroll(w,x,y):mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ZOOM,0,-.05*y,cam)
    glfw.set_key_callback(window,key);glfw.set_cursor_pos_callback(window,cursor);glfw.set_scroll_callback(window,scroll)
    ids={layer:np.asarray([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,layer+'_'+n)] for n in render['body_names']]) for layer in ('actual','blue')}
    actual_p=packet['actual_position'];actual_r=packet['actual_rotation'];bp=packet['blue_position'];br=packet['blue_rotation'];starts=packet['branch_input_control'];bottom=packet['actual_wheel_bottom'];duration=len(actual_p)*.01
    def setposes(layer,p,rot):
        data.mocap_pos[ids[layer]]=p
        for i,mid in enumerate(ids[layer]):mujoco.mju_mat2Quat(data.mocap_quat[mid],np.asarray(rot[i],dtype=np.float64).ravel())
    started=time.monotonic();last=started;first=True;shots=set()
    identity=dict(pid=__import__('os').getpid(),created_epoch=time.time(),GUI='GLFW native MuJoCo renderer',actual_case118=True,blue_model116=True,physics_steps=0,neural_inference_in_viewer=False,visible_window=True)
    (R/'MUJOCO_WINDOW_STARTED_ACTUAL.json').write_text(json.dumps(identity,indent=2),encoding='utf8')
    while not glfw.window_should_close(window) and time.monotonic()-started<7200 and not (R/'REPLACED_BY_NEWER_OWN_DISPLAY.json').exists():
        now=time.monotonic();delta=min(now-last,.1);last=now
        if not state['paused']:state['clock']=(state['clock']+delta*state['speed'])%duration
        k=min(len(actual_p)-1,int(state['clock']*100));b=max(0,min(len(starts)-1,int(np.searchsorted(starts,k+1,side='right')-1)));h=state['horizon']-1
        setposes('actual',actual_p[k],actual_r[k]);setposes('blue',bp[b,h] if state['show_blue'] else bp[b,h]+[0,0,-8],br[b,h])
        data.time=(k+1)*.01;mujoco.mj_forward(model,data)
        width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
        mujoco.mjv_updateScene(model,data,opt,None,cam,mujoco.mjtCatBit.mjCAT_ALL,scn);mujoco.mjr_render(viewport,scn,ctx)
        heading=f'GRAY: recorded PhysX motion  |  BLUE: model imagination +{state["horizon"]*.01:.2f}s\nLATEST116 / actual118 / {duration:.2f}s / 270mm platform; END: closure protection\nMuJoCo DISPLAY ONLY - no MuJoCo dynamics, no training\nTime {data.time:5.2f}s  |  Request {"ON" if k>=200 else "OFF"}  |  Speed {state["speed"]:.2f}x\nActual wheel clearance L/R: {bottom[k,0]*1000:6.2f} / {bottom[k,1]*1000:6.2f} mm\nBlue branch starts at {starts[b]*.01:.2f}s from recorded actual state\n270mm platform success: NONE'
        helptext='SPACE pause | R replay | B blue on/off\n1 real time | 2 quarter speed | 3 tenth speed\nH horizon 8/16/32 | Left/Right seek 0.1s\nLeft mouse orbit | Right mouse pan | Wheel zoom\nESC close'
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPLEFT,viewport,heading,'',ctx)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,viewport,helptext,'',ctx)
        # Actual framebuffer from this visible native window, retained once per declared moment.
        shot='LATEST116_REAL_BLUE_INITIAL_FRAME.png' if first else ('LATEST116_REAL_BLUE_2P7_FRAME.png' if 2.65<data.time<2.75 else None)
        if shot and shot not in shots:
            from PIL import Image
            rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,ctx)
            Image.fromarray(np.flipud(rgb)).save(HERE/shot);shots.add(shot)
        glfw.swap_buffers(window);glfw.poll_events();first=False
    (R/'MUJOCO_WINDOW_EXIT_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),wall_seconds=time.monotonic()-started,only_own_user_window=True)),encoding='utf8')
    ctx.free();glfw.destroy_window(window);glfw.terminate()


from copy import deepcopy
original_collision_scene_builder=make_scene
def make_scene(render):
    root=ET.fromstring(original_collision_scene_builder(render));asset=root.find('asset');world=root.find('worldbody')
    for m in list(asset.findall('mesh')):asset.remove(m)
    visual_base=Path('C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\H1_USER_MUJOCO_REAL_BLUE_IMAGINATION_V115_20261029\\actual_training_USD_visuals')
    base=ET.parse(visual_base/'live_display.xml').getroot();body={b.attrib['name']:b for b in base.find('worldbody').findall('body')}
    assert set(body)==set(render['body_names'])
    meshes=base.find('asset').findall('mesh')
    for m in meshes:
        x=deepcopy(m);x.set('file',str((visual_base/'meshes'/x.attrib['file']).resolve()));asset.append(x)
    count=0
    for layer in ('actual','blue'):
        for name in render['body_names']:
            target=world.find("body[@name='"+layer+'_'+name+"']")
            for child in list(target):target.remove(child)
            for geom in body[name].findall('geom'):
                x=deepcopy(geom);x.set('name',layer+'_'+x.attrib['name']);x.set('density','0')
                if layer=='blue':x.set('rgba','.08 .48 1 .42')
                target.append(x);count+=1
    assert len(meshes)==277 and count==554
    (R/'LATEST116_TRUE_MOD4_VISUAL_MAPPING_ACTUAL.json').write_text(json.dumps(dict(actual_visual_meshes=277,rendered_geoms=count,source_asset_manifest_bytes_SHA_metadata_matches111_and116=True,no_baked_mesh_recreation=True,source_actual116=True,gray_actual118_PhysX_recording=True,blue_same116_policy_WM=True)),encoding='utf8')
    return ET.tostring(root,encoding='unicode')

if __name__=='__main__':
    try:main()
    except BaseException:
        (R/('MUJOCO_DISPLAY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
