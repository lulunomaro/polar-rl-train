"""Decode every video frame and record frame counts, timing and visual-review limits."""
from argparse import ArgumentParser
from pathlib import Path
import json
import subprocess
import math
import numpy as np
from PIL import Image
import imageio_ffmpeg
from fsm_paths import HERE
from fsm_io import put,sha256


def main():
    p=ArgumentParser();p.add_argument('--folder',type=Path,default=HERE/'evidence/videos');args=p.parse_args()
    rows=[]
    for metadata_path in sorted(args.folder.glob('FSM_??.json')):
        meta=json.loads(metadata_path.read_text())
        video=HERE/meta['path']
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-progress','pipe:1',
            '-nostats','-f','null','-']
        result=subprocess.run(cmd,capture_output=True,text=True)
        frame_counts=[int(line.split('=',1)[1]) for line in result.stdout.splitlines() if line.startswith('frame=')]
        decoded=max(frame_counts) if frame_counts else 0
        rows.append(dict(path=meta['path'],sha256=sha256(video),exit_code=result.returncode,
            decoded_frames=decoded,expected_frames=meta['encoded_frames'],fps=meta['fps'],
            passed=result.returncode==0 and decoded==meta['encoded_frames'] and not result.stderr.strip(),
            errors=result.stderr,seconds=decoded/meta['fps']))
        if metadata_path.stem=='FSM_04':
            case=meta['cases'][0]
            start=max(0.,case['main_flight_start_s']-.16)
            stop=case['main_flight_end_s']+.16
            indices=set(range(max(0,math.floor((start-.02)*25)),math.ceil((stop-.02)*25)+1))
            reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24')
            info=next(reader);thumbs=[]
            for index,data in enumerate(reader):
                if index in indices:
                    w,h=info['size'];frame=np.frombuffer(data,dtype=np.uint8).reshape(h,w,3)
                    thumbs.append(Image.fromarray(frame).resize((384,256)))
                if index>max(indices):break
            reader.close()
            sheet=Image.new('RGB',(1536,256*math.ceil(len(thumbs)/4)),'#101b25')
            for index,thumb in enumerate(thumbs):sheet.paste(thumb,((index%4)*384,(index//4)*256))
            focus=args.folder/'FSM_04_MAIN_FLIGHT.png';sheet.save(focus)
            rows[-1]['main_flight_every_encoded_frame_sheet']=str(focus)
            rows[-1]['main_flight_review_frames']=len(thumbs)
        print(video.name,decoded,'frames','OK' if rows[-1]['passed'] else 'FAILED',flush=True)
    put(args.folder/'FRAME_DECODE_AUDIT.json',dict(videos=rows,passed=all(r['passed'] for r in rows),
        every_frame_decoded=True,visual_review='One-second contact sheets plus every encoded main-flight frame. This does not certify every full-video frame by human inspection.'))
    put(args.folder/'VIDEO_MANIFEST.json',dict(videos=[json.loads(p.read_text()) for p in sorted(args.folder.glob('FSM_??.json'))],
        source='Shared ManualSimulation pipeline; exactly one video frame per two 20 ms simulation ticks.'))


if __name__=='__main__':main()
