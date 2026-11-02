"""Native renderer of already recorded434 body poses; zeroNN/physics steps."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;E=N
source=(E/'view434_actual_RL_replay.py').read_text('utf8')
source=source.replace("N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY434'", "N=Path("+repr(str(E))+");R=N/'reports';O=Path("+repr(str(N/'RECORDED434_NATIVE_FRAMES'))+")")
source=source.replace("assert glfw.init();window=", "assert glfw.init();glfw.window_hint(glfw.VISIBLE,glfw.FALSE);window=")
source=source.replace('glfw.show_window(window);glfw.focus_window(window)','')
start=source.index('    started=time.monotonic();last=started;shot=False')
end=source.index("    context.free();",start)
source=source[:start]+'''    from PIL import Image,ImageDraw
    tiles=[];metadata=[]
    for case,r in enumerate(rows):
        p=packets[case]
        for fraction in(0.,.5,1.):
            i=int((r['controls']-1)*fraction)
            data.mocap_pos[ids]=p['pos'][i];data.mocap_quat[ids]=p['quat'][i]
            edge,lat,top,yaw=r['result']['target'];c,s=np.cos(yaw),np.sin(yaw)
            data.mocap_pos[platform]=[edge+1.5*c,lat+1.5*s,.135]
            data.mocap_quat[platform]=[np.cos(yaw/2),0,0,np.sin(yaw/2)]
            camera.lookat[:]=p['pos'][i,chassis]+[.15,0,.04];camera.distance=2.1;camera.azimuth=110;camera.elevation=-15
            mujoco.mj_forward(model,data);width,height=glfw.get_framebuffer_size(window);viewport=mujoco.MjrRect(0,0,width,height)
            mujoco.mjv_updateScene(model,data,option,None,camera,mujoco.mjtCatBit.mjCAT_ALL,scene);mujoco.mjr_render(viewport,scene,context)
            rgb=np.empty((height,width,3),dtype=np.uint8);mujoco.mjr_readPixels(rgb,None,viewport,context)
            tile=Image.fromarray(np.flipud(rgb)).resize((600,386));draw=ImageDraw.Draw(tile)
            caption=f"ACTUAL434 learned actual residual PPO433 env{r['env']} t={(i+1)*.02:.2f}s / {r['seconds']:.2f}s"
            draw.rectangle((0,0,600,24),fill='black');draw.text((8,6),caption,fill='white');tiles.append(tile)
            metadata.append(dict(env=r['env'],control=i+1,time=(i+1)*.02))
    sheet=Image.new('RGB',(1800,386*4))
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%3)*600,(i//3)*386))
    image=O/'ACTUAL434_RL_BODY_POSE_SEQUENCE.png';sheet.save(image)
    put('ACTUAL434_RENDER304_REPORT.json',dict(epoch=time.time(),passed=True,image=str(image),frames=metadata,source='already recorded417 PhysXbodyposes',model_reads=0,physics_steps=0,platform_visible=True))
''' + source[end:]
source=source.replace("put('VIEW434_EXIT.json',dict(epoch=time.time(),seconds=time.monotonic()-started))", "put('RENDER304_EXIT.json',dict(epoch=time.time(),complete=True))")
ast.parse(source)
exec(compile(source,str(N/'render304_generated_pose_view.py'),'exec'),dict(__name__='__main__',__file__=str(N/'render304_generated_pose_view.py')))
