"""Render the shared player at 25 fps: one frame per two 20 ms ticks, exactly 1x."""
from argparse import ArgumentParser
from pathlib import Path
import math
import numpy as np
import mujoco as mj
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from fsm_paths import HERE
from fsm_io import put,sha256
from fsm_evaluation import run_case
from eval_fsm_jump import run_jump
from manual_fsm_core import LABELS


class Video:
    def __init__(self,path,title):
        self.path=path;self.title=title;self.renderer=None;self.sim=None
        self.writer=imageio_ffmpeg.write_frames(str(path),(960,640),fps=25,codec='libx264',
            pix_fmt_in='rgb24',output_params=['-crf','20','-preset','fast'])
        self.writer.send(None)
        self.font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
        self.small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
        self.frames=0;self.thumbs=[];self.last_second=None

    def capture(self,sim,judge,tick):
        if tick%2:return
        if sim is not self.sim:
            if self.renderer is not None:self.renderer.close()
            self.renderer=mj.Renderer(sim.m,height=640,width=960)
            self.sim=sim;self.last_second=None
        camera=mj.MjvCamera()
        R=sim.d.xmat[sim.env.base_id].reshape(3,3)
        yaw=math.degrees(math.atan2(R[1,0],R[0,0]))
        camera.lookat[:]=sim.d.qpos[:3]+np.r_[.25*R[:2,0],.03]
        camera.distance=2.7;camera.azimuth=yaw+115.;camera.elevation=-18.
        opt=mj.MjvOption();opt.geomgroup[3]=0
        opt.geomgroup[5]=0 if sim.scene_meta.get('hide_group5') else 1
        self.renderer.update_scene(sim.d,camera,scene_option=opt)
        image=Image.fromarray(self.renderer.render())
        draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,960,88),fill='#101b25')
        phase=int(sim.unified.fsm.phase[0])
        draw.text((18,8),self.title+' · 1x / 400 Hz',font=self.font,fill='#eaf5ff')
        draw.text((18,39),f'{sim.d.time:5.2f} s   {LABELS[phase]}   E_stair={sim.route["e1"]:.0%}   '
            f'v={judge.trace[-1][2]:+.2f} m/s   pitch={judge.trace[-1][4]:+.1f}°',font=self.small,fill='#72e4c5')
        draw.rectangle((0,570,960,640),fill='#101b25')
        loads=judge.trace[-1][21:25]
        label='一级台面' if len(judge.levels)>1 else '台面' if judge.levels else '地面'
        load_text=f'{label} L/R: {loads[0]:.1f} / {loads[1]:.1f} N'
        if len(judge.levels)>1:load_text+=f'   二级台面 L/R: {loads[2]:.1f} / {loads[3]:.1f} N'
        draw.text((18,577),load_text,font=self.small,fill='#eaf5ff')
        draw.text((18,605),f'连续承载最长: {judge.physics_best.tolist()} 子步   '
            f'末段顶面: {judge.final_deck_best} 子步   无时间加速',font=self.small,fill='#eaf5ff')
        self.writer.send(np.asarray(image))
        self.frames+=1
        second=int(sim.d.time)
        if second!=self.last_second:
            thumb=image.resize((384,240))
            self.thumbs.append(thumb);self.last_second=second

    def close(self):
        self.writer.close()
        if self.renderer is not None:self.renderer.close()
        cols=4;rows=math.ceil(len(self.thumbs)/cols)
        sheet=Image.new('RGB',(cols*384,rows*240),'#101b25')
        for k,img in enumerate(self.thumbs):sheet.paste(img,(k%cols*384,k//cols*240))
        sheet.save(self.path.with_suffix('.png'))
        return dict(path=str(self.path.relative_to(HERE)),sha256=sha256(self.path),fps=25,
            encoded_frames=self.frames,playback_seconds=self.frames/25.,time_scale=1.,
            contact_sheet=str(self.path.with_suffix('.png').relative_to(HERE)))


def case(course,speed,offset,**kwargs):
    return dict(id='video',course=course,speed=speed,height=.39,yaw_deg=0.,offset=offset,
        seconds=10.,settle_s=.8,wz=0.,task='',edge_sign=1,armed=True,**kwargs)


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,default=HERE/'evidence/fsm_r5/train/model_024m.pt')
    p.add_argument('--only',type=int,choices=(1,2,3,4))
    p.add_argument('--out',type=Path,default=HERE/'evidence/videos')
    args=p.parse_args();folder=args.out.resolve();folder.mkdir(parents=True,exist_ok=True)
    videos=[]
    for number,title,jobs in (
        (1,'提前 2.5m 开 C · 200mm 单阶',[case('step_20',1.2,[-1.8,0.])]),
        (2,'A–A 西入口 · 200 → 400 → 360mm',[case('rm27_west_400',1.6,[-2.1,0.])]),
        (3,'200mm ±25° 斜入 / 贴阶强起',[dict(case('step_20',1.2,[.2,0.]),yaw_deg=-25.,seconds=6.),
             dict(case('step_20',1.2,[.2,0.]),yaw_deg=25.,seconds=6.),
             dict(case('step_20',.6,[.68,0.]),force_at_s=.2,seconds=7.,restart=True,settle_s=0.)]),
        (4,'实速 2.8m/s 跑动大跳 · 380mm 高台',[dict(id='video_jump',course='platform_380',speed=2.8,
             height=.28,yaw_deg=0.,offset=[-5.,0.],seconds=10.,settle_s=.8,front_gap=.85,
             wz=0.,task='',armed=False,hold_ticks=31)])):
        if args.only is not None and args.only!=number:continue
        video=Video(folder/f'FSM_{number:02d}_1x.mp4',title)
        rows=[]
        try:
            for job in jobs:
                row,trace=run_jump(job,frames=video.capture,checkpoint=args.checkpoint) if number==4 else run_case(job,
                    checkpoint=args.checkpoint,frames=video.capture)
                rows.append(row)
        finally:
            metadata=video.close()
        metadata.update(cases=rows,stair_checkpoint=str(args.checkpoint),stair_sha256=sha256(args.checkpoint))
        put(folder/f'FSM_{number:02d}.json',metadata)
        videos.append(metadata)
        print(number,'frames',metadata['encoded_frames'],'strict',[r['passed'] for r in rows],flush=True)
    put(folder/'VIDEO_MANIFEST.json',dict(videos=videos,source='same ManualSimulation as WASD',
        note='Video rendering itself is not a claim that strict benchmarks passed.'))


if __name__=='__main__':main()
