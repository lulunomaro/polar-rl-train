"""Real MOD4 mocap replay of actual242. No mj_step/Torch/inference."""
from pathlib import Path
from copy import deepcopy
import argparse,ctypes,hashlib,io,json,os,sys,time,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco,glfw
def main(base,out):
 B=Path(base);O=Path(out);O.mkdir(exist_ok=False);P=json.loads((B/'reports/FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json').read_bytes());Q=json.loads((B/'reports/ROOT243_SELECTED242_POSE_TRANSFERS_ACTUAL.json').read_bytes());assert Q['passed']
 cases=P['cases'];packets=[]
 for case,receipt in zip(cases,Q['cases'],strict=True):
  assert case['name']==receipt['name']and receipt['producer_and_transferred_same_stream_SHA_equal']
  with Path(receipt['path']).open('rb')as file:raw=file.read()
  assert len(raw)==receipt['bytes']and hashlib.sha256(raw).hexdigest()==receipt['SHA']
  with np.load(io.BytesIO(raw),allow_pickle=False)as z:packet={k:z[k].copy()for k in P['npz_members_selected']}
  del raw
  assert packet['body_position_w'].shape==(case['controls'],31,3)and packet['body_quat_xyzw'].shape==(case['controls'],31,4)
  assert all(np.isfinite(v).all()for v in packet.values());packets.append(packet)
 visual=P['visual_assets'];xml_path=Path(visual['xml']['path']);raw=xml_path.read_bytes();assert len(raw)==visual['xml']['bytes']and hashlib.sha256(raw).hexdigest()==visual['xml']['sha256']
 original=ET.fromstring(raw);body={b.attrib['name']:b for b in original.find('worldbody').findall('body')};names=P['body_names'];assert len(names)==31 and set(names)==set(body)
 root=ET.Element('mujoco',model='MODEL2050 trained240 iteration2135 actual242 recorded replay');ET.SubElement(root,'compiler',angle='radian');vis=ET.SubElement(root,'visual');ET.SubElement(vis,'headlight',ambient='.6 .6 .6',diffuse='.6 .6 .6')
 assets=ET.SubElement(root,'asset');meshes=0
 for item in original.find('asset'):
  copied=deepcopy(item)
  if copied.tag=='mesh':copied.set('file',str((Path(visual['mesh_directory'])/copied.attrib['file']).resolve()));meshes+=1
  elif 'file'in copied.attrib:copied.set('file',str((xml_path.parent/copied.attrib['file']).resolve()))
  assets.append(copied)
 assert meshes==277
 ET.SubElement(assets,'texture',name='grid243',type='2d',builtin='checker',rgb1='.29 .31 .34',rgb2='.39 .41 .44',width='512',height='512');ET.SubElement(assets,'material',name='floor243',texture='grid243',texrepeat='8 8')
 world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='0 -1 4',dir='0 0 -1',diffuse='.8 .8 .8');ET.SubElement(world,'geom',type='plane',pos='0 0 0',size='8 8 .05',material='floor243',contype='0',conaffinity='0')
 geoms=0
 for name in names:
  b=ET.SubElement(world,'body',name='actual_'+name,mocap='true',pos='0 0 -10')
  for item in body[name].findall('geom'):
   q=deepcopy(item);q.set('name','actual_'+q.attrib['name']);q.set('density','0');q.set('contype','0');q.set('conaffinity','0');q.set('rgba','.73 .77 .82 1');b.append(q);geoms+=1
 assert geoms==277
 xml=ET.tostring(root,encoding='unicode');(O/'DISPLAY243_TRUE_MOD4.xml').write_text(xml,encoding='utf8');model=mujoco.MjModel.from_xml_string(xml);data=mujoco.MjData(model);assert model.nq==model.nv==0 and model.nmocap==31
 assert glfw.init();window=glfw.create_window(1500,960,'MODEL2050 -> 400N50 / TRAINED2135 | ACTUAL242 REPLAY | NEW243',None,None);assert window;glfw.make_context_current(window);glfw.swap_interval(1);glfw.show_window(window);glfw.focus_window(window)
 camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera);camera.distance=2.7;camera.azimuth=130;camera.elevation=-22
 option=mujoco.MjvOption();mujoco.mjv_defaultOption(option);scene=mujoco.MjvScene(model,maxgeom=2000);context=mujoco.MjrContext(model,mujoco.mjtFontScale.mjFONTSCALE_150)
 ids=np.array([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'actual_'+n)]for n in names]);chassis=names.index('chassis')
 for packet in packets:
  origin=np.array([packet['root13'][0,0],packet['root13'][0,1],0.]);packet['display_pos']=packet['body_position_w']-origin;packet['display_quat']=packet['body_quat_xyzw'][...,[3,0,1,2]]
 camera.lookat[:]=packets[3]['display_pos'][0,chassis]+[0,0,.08]
 state=dict(case=3,clock=0.,speed=.1,paused=False,follow=True,cursor=(0.,0.))
 def key(w,k,scan,action,mods):
  if action not in(glfw.PRESS,glfw.REPEAT):return
  if k==glfw.KEY_ESCAPE:glfw.set_window_should_close(w,True)
  elif k==glfw.KEY_SPACE:state['paused']=not state['paused']
  elif k==glfw.KEY_R:state['clock']=0.
  elif k==glfw.KEY_F:state['follow']=not state['follow']
  elif glfw.KEY_1<=k<=glfw.KEY_4:state['case']=k-glfw.KEY_1;state['clock']=0.
  elif k in(glfw.KEY_Z,glfw.KEY_X,glfw.KEY_C):state['speed']={glfw.KEY_Z:1.,glfw.KEY_X:.25,glfw.KEY_C:.1}[k]
  elif k==glfw.KEY_LEFT:state['clock']=max(0.,state['clock']-.02)
  elif k==glfw.KEY_RIGHT:state['clock']=min(cases[state['case']]['seconds']-.0001,state['clock']+.02)
 def cursor(w,x,y):
  a,b=state['cursor'];state['cursor']=(x,y);_,h=glfw.get_window_size(w)
  if glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_LEFT)==glfw.PRESS:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ROTATE_V,(x-a)/h,(y-b)/h,camera)
  elif glfw.get_mouse_button(w,glfw.MOUSE_BUTTON_RIGHT)==glfw.PRESS:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_MOVE_V,(x-a)/h,(y-b)/h,camera)
 glfw.set_key_callback(window,key);glfw.set_cursor_pos_callback(window,cursor);glfw.set_scroll_callback(window,lambda w,x,y:mujoco.mjv_moveCamera(model,mujoco.mjtMouse.mjMOUSE_ZOOM,0,-.05*y,camera))
 class FT(ctypes.Structure):_fields_=[('low',ctypes.c_uint32),('high',ctypes.c_uint32)]
 kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p;kernel.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)];kernel.GetProcessTimes.restype=ctypes.c_int
 c,e,k,u=FT(),FT(),FT(),FT();assert kernel.GetProcessTimes(kernel.GetCurrentProcess(),ctypes.byref(c),ctypes.byref(e),ctypes.byref(k),ctypes.byref(u));creation=((c.high<<32)|c.low)/1e7-11644473600.
 (O/'DISPLAY243_SINGLE_PASS_POSE_MAPPING_ACTUAL.json').write_text(json.dumps(dict(raw_pose_byte_opens_each=1,raw_pose_integrity_passes_each=1,npz_members_each_read_once=P['npz_members_selected'],case_files=Q['cases'],body_names=names,source_quat='actual242 SDK xyzw',render_quat='wxyz',true_meshes=meshes,mocap_bodies=31,model_reads=0,NN_SDK_physics_steps=0,first_chassis_root_position_differences_m=[float(np.linalg.norm(p['body_position_w'][0,chassis]-p['root13'][0,:3]))for p in packets]),indent=2),encoding='utf8')
 started=time.monotonic();last=started;shot=False
 (O/'DISPLAY243_WINDOW_STARTED_ACTUAL.json').write_text(json.dumps(dict(pid=os.getpid(),creation=creation,exe=sys.executable,argv=[sys.executable,*sys.argv],cwd=os.getcwd(),epoch=time.time(),visible=True,model_iteration=2135,model_SHA=P['selected_model_SHA'],neural_inference=False,physics_steps=0,true_meshes=277,mocap_bodies=31,not_live=True,default_case='literal_jump',default_speed=.1),indent=2),encoding='utf8')
 while not glfw.window_should_close(window)and time.monotonic()-started<7200:
  now=time.monotonic();dt=min(now-last,.1);last=now;case=cases[state['case']];packet=packets[state['case']];duration=case['seconds']
  if not state['paused']:state['clock']=(state['clock']+dt*state['speed'])%(duration+.12)
  i=min(case['controls']-1,int(state['clock']*50));data.mocap_pos[ids]=packet['display_pos'][i];data.mocap_quat[ids]=packet['display_quat'][i];data.time=(i+1)*.02;mujoco.mj_forward(model,data)
  width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
  if state['follow']:camera.lookat[:]=packet['display_pos'][i,chassis]+[0,0,.08]
  mujoco.mjv_updateScene(model,data,option,None,camera,mujoco.mjtCatBit.mjCAT_ALL,scene);mujoco.mjr_render(viewport,scene,context)
  forces=np.linalg.norm(packet['wheel_contact_xyz'][i],axis=-1);bottom=packet['authored_wheel_bottom'][i];cue=case['command'];end=', '.join(k for k,v in case['original_terminal_flags'].items()if v)
  heading=f'MODEL2050 adaptation240 / TRAINED ITERATION2135 / ACTUAL PhysX242 REPLAY\nCASE {state["case"]+1}: {case["name"]} / recorded t={(i+1)*.02:.2f}s of {duration:.2f}s / {state["speed"]:.2f}x slow motion'
  heading+=f'\nReal MOD4 / nominal400N k2000 /50Hz policy /100Hz feedback /400Hz physics /fullD0-D7\nOriginal closure2mm /mimic.01; episode ended by {end}; requested10s NOT completed'
  heading+=f'\nControlled eval vx={cue["vx"]:+.2f}, yaw0, height={cue["height"]:.3f}m / world heading preserved'
  heading+=f'\nWheel force norms L/R={forces[0]:.1f}/{forces[1]:.1f}N / authored bottoms={bottom[0]*1000:.1f}/{bottom[1]*1000:.1f}mm'
  heading+='\nJUMP: original Fudan19 methods/16 weights unchanged; ground: separate originalE0 reward\nRECORDED / NOT LIVE / MuJoCo display only / no NN or mj_step / no270 success claim'
  helptext='1 standing | 2 forward | 3 reverse | 4 JUMP (default)\nZ real speed | X .25x | C .1x | SPACE pause | R replay | arrows seek | F follow\nMouse orbit/pan | wheel zoom | ESC close; last original pre-reset frame is held before loop'
  mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPLEFT,viewport,heading,'',context);mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,viewport,helptext,'',context)
  if not shot:
   from PIL import Image
   rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,context);Image.fromarray(np.flipud(rgb)).save(O/'MUJOCO243_TRAINED240_INITIAL_FRAME.png');shot=True
  glfw.swap_buffers(window);glfw.poll_events()
 context.free();glfw.destroy_window(window);glfw.terminate();(O/'DISPLAY243_WINDOW_EXIT_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),wall_seconds=time.monotonic()-started,only_own_user_window=True)),encoding='utf8')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 try:main(a.base,a.out)
 except BaseException:
  O=Path(a.out)
  if O.is_dir():(O/('DISPLAY243_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc()),indent=2),encoding='utf8')
  raise
