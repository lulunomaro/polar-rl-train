"""User supplied video: CPU metadata/frame extraction for native visual analysis."""
from pathlib import Path
import subprocess,shutil,json,hashlib,re,time,math
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parent;T=S.parent
D=T/'MOD4_FUDAN_USER_UPSTEP_VIDEO_NATIVE_VISUAL_20261027'
INPUT=Path(r'C:/Users/lulu/Downloads/42168288822-1-192 (1).mp4')
def main():
 assert not D.exists();D.mkdir();(D/'reports').mkdir();frames=D/'overview_frames';frames.mkdir()
 before=INPUT.stat();probe=subprocess.run([shutil.which('ffprobe'),'-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames','-of','json',str(INPUT)],check=True,capture_output=True,text=True)
 metadata=json.loads(probe.stdout)
 run=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-i',str(INPUT),'-vf','select=not(mod(n\\,30)),scale=320:180,showinfo','-fps_mode','passthrough','-q:v','3',str(frames/'frame_%04d.jpg')],check=True,capture_output=True,text=True)
 (D/'reports/FFMPEG_OVERVIEW_STDERR_ACTUAL.txt').write_text(run.stderr,encoding='utf8')
 pts=[float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.]+)',run.stderr)]
 files=sorted(frames.glob('*.jpg'));assert len(files)==len(pts)>0
 sheets=[]
 for page in range(math.ceil(len(files)/24)):
  selected=files[page*24:(page+1)*24];canvas=Image.new('RGB',(1280,1260),'white');draw=ImageDraw.Draw(canvas)
  for i,p in enumerate(selected):
   x=(i%4)*320;y=(i//4)*210;canvas.paste(Image.open(p),(x,y+26));draw.text((x+8,y+7),f'video t={pts[page*24+i]:.3f} s',fill='black')
  path=D/f'USER_FUDAN_VIDEO_OVERVIEW_{page+1}.jpg';canvas.save(path,quality=92);sheets.append(dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest()))
 after=INPUT.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 report=dict(epoch=time.time(),input=dict(path=str(INPUT),bytes=before.st_size,mtime_ns=before.st_mtime_ns,SHA=None,SHA_not_computed_for_Git=True,user_supplied=True),probe=metadata,frame_selection='every30originalframes; exact selected PTS from ffmpeg showinfo',frames=[dict(path=str(p),pts_time_s=t,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p,t in zip(files,pts)],sheets=sheets,native_vision_only_no_Luna=True,no_policy_model_physics_GPU_or_source_video_overwrite=True)
 with (D/'reports/USER_VIDEO_METADATA_AND_OVERVIEW_FRAME_PRODUCER_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed=True,duration=metadata['format']['duration'],frames=len(files),sheets=sheets)))
if __name__=='__main__':main()
