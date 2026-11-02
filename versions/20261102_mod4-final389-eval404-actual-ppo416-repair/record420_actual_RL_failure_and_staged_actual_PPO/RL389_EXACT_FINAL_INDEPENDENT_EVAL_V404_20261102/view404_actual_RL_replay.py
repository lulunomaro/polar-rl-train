"""Visible replay of actual frozen final389 PhysX404, no inference or mj_step."""
from pathlib import Path
from copy import deepcopy
import ctypes,hashlib,io,json,os,sys,time,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco,glfw
N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY404'

def put(n,v):
    with(O/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
    O.mkdir(exist_ok=False)
    receipt=json.loads((R/'ROOT404_SELECTED_REPLAY_TRANSFERS.json').read_bytes());assert receipt['passed']
    old=json.loads((N.parent/'MODEL2050_TRAINED240_USER_MUJOCO_V243_20261101/reports/FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json').read_bytes())
    asset=old['visual_assets'];xml=Path(asset['xml']['path']).read_bytes();assert hashlib.sha256(xml).hexdigest()==asset['xml']['sha256']
    original=ET.fromstring(xml);source={b.attrib['name']:b for b in original.find('worldbody').findall('body')}
    rows=receipt['cases'];names=rows[0]['body_names'];packets=[]
    for r in rows:
        data=Path(r['local_path']).read_bytes();assert len(data)==r['bytes']and hashlib.sha256(data).hexdigest()==r['SHA']
        with np.load(io.BytesIO(data),allow_pickle=False)as z:p={k:z[k].copy()for k in z.files}
        p['pos']=p['body_position_w']-np.array(r['origin']);p['quat']=p['body_quat_xyzw'][...,[3,0,1,2]]
        packets.append(p)
    root=ET.Element('mujoco',model='Learned RL389 recorded motion actual404 replay');ET.SubElement(root,'compiler',angle='radian')
    vis=ET.SubElement(root,'visual');ET.SubElement(vis,'headlight',ambient='.6 .6 .6',diffuse='.6 .6 .6')
    assets=ET.SubElement(root,'asset')
    for item in original.find('asset'):
        q=deepcopy(item)
        if q.tag=='mesh':q.set('file',str((Path(asset['mesh_directory'])/q.attrib['file']).resolve()))
        assets.append(q)
    world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='0 -1 3',dir='0 0 -1')
    ET.SubElement(world,'geom',type='plane',size='6 6 .1',rgba='.25 .28 .32 1',contype='0',conaffinity='0')
    step=ET.SubElement(world,'body',name='platform',mocap='true',pos='1.5 0 .135')
    ET.SubElement(step,'geom',type='box',size='1.5 1 .135',rgba='.25 .5 .75 1',contype='0',conaffinity='0')
    for name in names:
        body=ET.SubElement(world,'body',name='actual_'+name,mocap='true',pos='0 0 -10')
        for item in source[name].findall('geom'):
            q=deepcopy(item);q.set('name','actual_'+q.attrib['name']);q.set('contype','0');q.set('conaffinity','0');q.set('density','0');q.set('rgba','.73 .77 .82 1');body.append(q)
    model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'));data=mujoco.MjData(model)
    ids=np.array([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'actual_'+n)]for n in names]);platform=model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'platform')]
    assert model.nq==0 and model.nmocap==32
    assert glfw.init();window=glfw.create_window(1400,900,'Learned RL389 recorded motion / reference tracking / recorded PhysX404',None,None);assert window
    glfw.make_context_current(window);glfw.swap_interval(1);glfw.show_window(window);glfw.focus_window(window)
    camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera);camera.distance=2.5;camera.azimuth=135;camera.elevation=-18
    option=mujoco.MjvOption();mujoco.mjv_defaultOption(option);scene=mujoco.MjvScene(model,maxgeom=2000);context=mujoco.MjrContext(model,mujoco.mjtFontScale.mjFONTSCALE_150)
    state=dict(case=0,clock=0.,speed=.1,paused=False,cursor=(0.,0.));chassis=names.index('chassis')
    def key(w,k,scan,action,mods):
        if action not in(glfw.PRESS,glfw.REPEAT):return
        if k==glfw.KEY_ESCAPE:glfw.set_window_should_close(w,True)
        elif k==glfw.KEY_SPACE:state['paused']=not state['paused']
        elif glfw.KEY_1<=k<=glfw.KEY_4:state['case']=k-glfw.KEY_1;state['clock']=0.
        elif k==glfw.KEY_R:state['clock']=0.
        elif k in(glfw.KEY_Z,glfw.KEY_X,glfw.KEY_C):state['speed']={glfw.KEY_Z:1.,glfw.KEY_X:.25,glfw.KEY_C:.1}[k]
    def cursor(w,x,y):
        a,b=state['cursor'];state['cursor']=(x,y);_,height=glfw.get_window_size(w)
        if glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_LEFT)==glfw.PRESS:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ROTATE_V,(x-a)/height,(y-b)/height,camera)
    glfw.set_key_callback(window,key);glfw.set_cursor_pos_callback(window,cursor)
    glfw.set_scroll_callback(window,lambda w,x,y:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ZOOM,0,-.05*y,camera))
    put('VIEW404_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),visible=True,actual_model_SHA=receipt['model_SHA'],
      actual_source='PhysX404 RL389 first episodes',policy_updates=3508,physics_steps=0,NN_model_reads=0,mocap_bodies=32))
    started=time.monotonic();last=started;shot=False
    while not glfw.window_should_close(window)and time.monotonic()-started<1800:
        now=time.monotonic();delta=min(.1,now-last);last=now;r=rows[state['case']];p=packets[state['case']]
        if not state['paused']:state['clock']=(state['clock']+delta*state['speed'])%(r['seconds']+.05)
        i=min(r['controls']-1,int(state['clock']*50));data.mocap_pos[ids]=p['pos'][i];data.mocap_quat[ids]=p['quat'][i]
        edge,lat,top,yaw=r['result']['target'];c,s=np.cos(yaw),np.sin(yaw)
        data.mocap_pos[platform]=[edge+1.5*c,lat+1.5*s,.135]
        data.mocap_quat[platform]=[np.cos(yaw/2),0,0,np.sin(yaw/2)];camera.lookat[:]=p['pos'][i,chassis]+[0,0,.04]
        mujoco.mj_forward(model,data);width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
        mujoco.mjv_updateScene(model,data,option,None,camera,mujoco.mjtCatBit.mjCAT_ALL,scene);mujoco.mjr_render(viewport,scene,context)
        heading=f'LEARNED RESIDUAL RL389 / ACTOR ONLY / actual PhysX404 RECORDED REPLAY\nCase {state["case"]+1}: {r["result"]["kind"]} env{r["env"]} / t={(i+1)*.02:.2f}s of {r["seconds"]:.2f}s / {state["speed"]:.2f}x\n404N /50Hz policy /100Hz feedback /2.5ms physics /TGS32-4 /full DR\nClosure10mm /mimic.01rad / planned motor targets / source vs bounded wheel request\nMPC50Hz / full D0-D7 matched pairs / actual solver contact acceptance\nMuJoCo display only; NO inference or physics rerun'
        helptext='1 env1 | 2 env0 | 3 env10 | 4 env20\nZ real speed | X .25x | C .1x | SPACE pause | R replay | ESC close\nMouse drag orbit / wheel zoom'
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPLEFT,viewport,heading,'',context)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,viewport,helptext,'',context)
        if not shot and i>=min(max(0,r['controls']-2),15):
            from PIL import Image
            rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,context);Image.fromarray(np.flipud(rgb)).save(O/'FINAL324_ACTUAL404_REPLAY.png');shot=True
        glfw.swap_buffers(window);glfw.poll_events()
    context.free();glfw.destroy_window(window);glfw.terminate();put('VIEW404_EXIT.json',dict(epoch=time.time(),seconds=time.monotonic()-started))
if __name__=='__main__':
    try:main()
    except BaseException:
        if O.is_dir():put('VIEW404_ERROR.json',dict(error=traceback.format_exc()))
        raise
