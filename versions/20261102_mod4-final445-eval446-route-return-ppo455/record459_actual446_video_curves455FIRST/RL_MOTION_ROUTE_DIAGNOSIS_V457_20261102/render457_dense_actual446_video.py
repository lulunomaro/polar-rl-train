"""Dense actual446 saved-body-pose video, not a new rollout or simulated reconstruction."""
from pathlib import Path
from copy import deepcopy
import ast
import hashlib
import json
import shutil
import subprocess
import time
N=Path(__file__).resolve().parent;T=N.parent
C=T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102'
source=(C/'view451_actual446_savedposes.py').read_text('utf8')
source=source.replace("N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY451'", "N=Path("+repr(str(C))+");R=N/'reports';O=Path("+repr(str(N/'DENSE457_NATIVE_RECORDED_POSES'))+")")
source=source.replace("assert glfw.init();window=", "assert glfw.init();glfw.window_hint(glfw.VISIBLE,glfw.FALSE);window=")
source=source.replace('glfw.show_window(window);glfw.focus_window(window)','')
source=source.replace("glfw.create_window(1400,900,", "glfw.create_window(640,400,")
start=source.index('    started=time.monotonic();last=started;shot=False')
end=source.index('    context.free();',start)
source=source[:start]+'''    from PIL import Image,ImageDraw,ImageFont
    import subprocess,shutil
    frames=O/'frames';frames.mkdir()
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
    samples=[0,4,9,19,29,34,39,44,49,54,59,74,99,199,399]
    side_samples={};top_samples={};metadata=[]
    count=max(row['controls']for row in rows)
    def render(case,i,topview=False):
        r=rows[case];p=packets[case];i=min(i,r['controls']-1)
        data.mocap_pos[ids]=p['pos'][i];data.mocap_quat[ids]=p['quat'][i]
        edge,lat,top,yaw=r['result']['target'];c,s=np.cos(yaw),np.sin(yaw)
        data.mocap_pos[platform]=[edge+1.5*c,lat+1.5*s,.135]
        data.mocap_quat[platform]=[np.cos(yaw/2),0,0,np.sin(yaw/2)]
        camera.lookat[:]=[.50,.05,.21]
        camera.distance=1.9;camera.azimuth=100;camera.elevation=-17
        if topview:camera.distance=2.05;camera.azimuth=90;camera.elevation=-89
        mujoco.mj_forward(model,data);width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
        mujoco.mjv_updateScene(model,data,option,None,camera,mujoco.mjtCatBit.mjCAT_ALL,scene);mujoco.mjr_render(viewport,scene,context)
        rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,context)
        tile=Image.fromarray(np.flipud(rgb)).resize((640,400));draw=ImageDraw.Draw(tile)
        caption=f"Actual RL445 / evaluation446 | env{r['env']} | t={(i+1)*.02:.2f}s"
        draw.rectangle((0,0,640,27),fill='#121820');draw.text((8,5),caption,font=font,fill='white')
        draw.rectangle((0,372,640,400),fill='#121820');draw.text((8,377),'270mm platform | saved PhysX body poses | no new physics',font=small,fill='white')
        return tile
    for i in range(count):
        sheet=Image.new('RGB',(1280,800))
        for case,r in enumerate(rows):
            tile=render(case,i);sheet.paste(tile,((case%2)*640,(case//2)*400))
            if i in samples:
                side_samples[(case,i)]=tile.copy();top_samples[(case,i)]=render(case,i,True)
        sheet.save(frames/f'frame_{i:04d}.png')
        if i%50==0:print('rendered actual446',i+1,'/',count,flush=True)
    def save_sheet(name,case,indices,views):
        sheet=Image.new('RGB',(640*3,400*((len(indices)+2)//3)))
        for slot,i in enumerate(indices):sheet.paste(views[(case,i)],((slot%3)*640,(slot//3)*400))
        path=O/name;sheet.save(path);return str(path)
    contact=[]
    for case,r in enumerate(rows):
        contact.append(save_sheet(f'env{r["env"]}_side_dense_0_to_8s.png',case,samples,side_samples))
        contact.append(save_sheet(f'env{r["env"]}_top_dense_0_to_8s.png',case,samples,top_samples))
    ffmpeg=shutil.which('ffmpeg');assert ffmpeg
    video=O/'ACTUAL446_RL445_four_cases_half_speed.mp4'
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-framerate','25','-i',str(frames/'frame_%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    gif=O/'ACTUAL446_RL445_takeoff_quarter_speed.gif'
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-framerate','12.5','-i',str(frames/'frame_%04d.png'),'-frames:v','76','-vf','scale=768:-1:flags=lanczos','-loop','0',str(gif)],check=True)
    media=[]
    for path in [video,gif,*map(__import__('pathlib').Path,contact)]:
        media.append(dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest()))
    put('DENSE457_RECORDED446_VIDEO_RENDER_REPORT.json',dict(epoch=time.time(),passed=True,source='PhysX446 recovered actual451 packets, not copied old437 packets',modelSHA=receipt['model_SHA'],
        media=media,cases=[r['env']for r in rows],frames_per_case=count,pose_sample_hz=50,video_fps25_half_speed=True,gif_fps12_5_quarter_speed=True,
        camera_poses_fixed=True,actual_bodypose_only=True,NN_model_reads=0,SDK=0,physics_steps=0,render_forward_only=True,
        actual_solver_support_result='all80 top contact peak0 and strict0; visual replay itself is not solver acceptance'))
''' +source[end:]
source=source.replace("put('VIEW446_EXIT.json',dict(epoch=time.time(),seconds=time.monotonic()-started))","put('DENSE457_RENDER_EXIT.json',dict(epoch=time.time(),complete=True))")
ast.parse(source)
exec(compile(source,str(N/'generated457_native_replay.py'),'exec'),dict(__name__='__main__',__file__=str(N/'generated457_native_replay.py')))
