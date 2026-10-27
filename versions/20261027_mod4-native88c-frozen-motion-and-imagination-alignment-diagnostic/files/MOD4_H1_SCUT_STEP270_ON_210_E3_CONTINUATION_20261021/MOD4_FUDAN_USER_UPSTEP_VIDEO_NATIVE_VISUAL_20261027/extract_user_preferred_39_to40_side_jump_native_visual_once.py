"""All original frames around user's selected jump; no inference or fake trajectory."""
from pathlib import Path
import subprocess,shutil,re,json,time,hashlib,math
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D/'reports';INPUT=Path(r'C:/Users/lulu/Downloads/42168288822-1-192 (1).mp4')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 frames=D/'selected_jump_38_to_40p5_full_frames';frames.mkdir()
 run=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-i',str(INPUT),'-vf','select=between(t\\,38.0\\,40.5),showinfo','-fps_mode','passthrough','-q:v','2',str(frames/'frame_%04d.jpg')],check=True,capture_output=True,text=True)
 (R/'FFMPEG_USER_PREFERRED_SIDE_JUMP_39_TO40_STDERR_ACTUAL.txt').write_text(run.stderr,encoding='utf8')
 pts=[float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.]+)',run.stderr)];files=sorted(frames.glob('*.jpg'));assert len(files)==len(pts)
 sheets=[]
 for page in range(math.ceil(len(files)/20)):
  selected=files[page*20:(page+1)*20];canvas=Image.new('RGB',(1600,1000),'white');draw=ImageDraw.Draw(canvas)
  for i,p in enumerate(selected):
   x=i%4*400;y=i//4*200;im=Image.open(p);im.thumbnail((400,175));canvas.paste(im,(x,y+24));draw.text((x+8,y+5),f'original video {pts[page*20+i]:.3f}s',fill='black')
  out=D/f'PREFERRED_SIDE_JUMP_EVERY_ORIGINAL_FRAME_{page+1}.jpg';canvas.save(out,quality=93);sheets.append(dict(path=str(out),bytes=out.stat().st_size,SHA=H(out)))
 report=dict(epoch=time.time(),input_path=str(INPUT),exact_requested_focus=[39,40],context=[38.,40.5],frames=[dict(path=str(p),pts_time_s=t,bytes=p.stat().st_size,SHA=H(p)) for p,t in zip(files,pts)],sheets=sheets,all_original_frames_retained_no_interpolation=True,native_vision_only_no_Luna=True,no_policy_model_physics_or_source_modification=True)
 with (R/'USER_PREFERRED_39_TO40_SIDE_JUMP_ORIGINAL_FRAMES_PRODUCER_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(frames=len(files),time_range=[pts[0],pts[-1]],sheets=sheets)))
if __name__=='__main__':main()
