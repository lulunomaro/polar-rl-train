"""Read the user-referenced video once for temporal pose/action analysis, no training."""
from pathlib import Path
import subprocess,json,re
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;O=D/'video_reference';assert not O.exists();O.mkdir();src=Path(r'C:\Users\lulu\Downloads\43171186822-1-192.mp4');ff=Path(r'C:\Users\lulu\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe');assert src.is_file()and ff.is_file()
with(O/'DECODE.log').open('w',encoding='utf8')as log:r=subprocess.run([str(ff),'-nostdin','-hide_banner','-n','-i',str(src),'-vf',"select='not(mod(n,15))',showinfo",'-fps_mode','vfr','-an','-frames:v','20',str(O/'frame_%03d.png')],stdout=subprocess.DEVNULL,stderr=log)
assert r.returncode==0;rlog=(O/'DECODE.log').read_text(encoding='utf8');times=[float(x)for x in re.findall(r'\bn:\s*\d+\s+pts:\s*[-\d]+\s+pts_time:([\d.]+)',rlog)];frames=sorted(O.glob('frame_*.png'));assert len(frames)==20;assert len(times)>=len(frames);sheet=Image.new('RGB',(1600,4*208),(24,24,24));draw=ImageDraw.Draw(sheet)
for i,p in enumerate(frames):
 with Image.open(p)as im:small=im.resize((320,180));sheet.paste(small,((i%5)*320,(i//5)*208))
 draw.text(((i%5)*320+8,(i//5)*208+184),f'{i+1:02d}   t={times[i]:.3f}s',fill='white')
sheet.save(O/'TEMPORAL_CONTACT_SHEET.png');meta=dict(source=str(src),duration_seconds=9.866625,width=1280,height=720,decoded_original_resolution_frames=[dict(path=str(p),source_time_seconds=times[i])for i,p in enumerate(frames)],purpose='Understand requested low belly rear-leg recovery from user video; not our robot identity or performance proof');(O/'REFERENCE.json').write_text(json.dumps(meta,indent=2),encoding='utf8');print(json.dumps(dict(frames=len(frames),times=times[:len(frames)],contact_sheet=str(O/'TEMPORAL_CONTACT_SHEET.png')),indent=2))
