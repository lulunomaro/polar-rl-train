"""User-requested local video review; original video metadata only for Git."""
from pathlib import Path
import json,subprocess,time
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parent;D=S/'user_video_review_1738';assert not D.exists();(D/'frames').mkdir(parents=True)
src=Path('C:/Users/lulu/Videos/NVIDIA/Dassault Systemes SolidWorks 2019 and above/Dassault Systemes SolidWorks 2019 and above 2026.10.29 - 17.38.00.03.mp4')
bin=Path('C:/Users/lulu/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
probe=subprocess.run([str(bin/'ffprobe.exe'),'-v','error','-show_format','-show_streams','-of','json',str(src)],capture_output=True,check=True);meta=json.loads(probe.stdout)
(D/'ORIGINAL_VIDEO_METADATA_AND_NEW_REVIEW_PURPOSE.json').write_text(json.dumps(dict(epoch=time.time(),user_requested_video_review=True,source_path=str(src),source_bytes=src.stat().st_size,source_SHA='unknown; not hashed forGit',ffprobe=meta,no_model_or_physical_raw_or_GPU_or_network=True),indent=2),encoding='utf8')
r=subprocess.run([str(bin/'ffmpeg.exe'),'-hide_banner','-loglevel','error','-i',str(src),'-vf','fps=1,scale=1280:-2','-an',str(D/'frames/frame_%03d.png')],capture_output=True)
(D/'FRAME_EXTRACTION_STDERR_UTF8.txt').write_bytes(r.stderr);assert r.returncode==0
files=sorted((D/'frames').glob('*.png'));thumbs=[]
for i,p in enumerate(files):
    with Image.open(p) as im:thumb=im.convert('RGB').resize((640,360))
    canvas=Image.new('RGB',(640,384),'black');canvas.paste(thumb,(0,24));ImageDraw.Draw(canvas).text((8,5),f'Video t ~ {i}s',fill='white');thumbs.append(canvas)
sheet=Image.new('RGB',(640*4,384*((len(thumbs)+3)//4)),(22,22,22))
for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*640,(i//4)*384))
sheet.save(D/'VIDEO_NATIVE_REVIEW_CONTACT_SHEET.png')
(D/'DERIVED_FRAMES_METADATA_ONLY_INDEX.json').write_text(json.dumps(dict(frames=[dict(path=str(p),bytes=p.stat().st_size,SHA='unknown') for p in files],sheet=str(D/'VIDEO_NATIVE_REVIEW_CONTACT_SHEET.png'),original_video_not_modified=True,no_Luna_OpenRouter_or_external_vision=True),indent=2),encoding='utf8')
print(json.dumps(dict(frames=len(files),duration=meta['format']['duration'],sheet=str(D/'VIDEO_NATIVE_REVIEW_CONTACT_SHEET.png'))))
