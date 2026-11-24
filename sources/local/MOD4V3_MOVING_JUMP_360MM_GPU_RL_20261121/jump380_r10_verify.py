"""Decode each delivered frame and verify the R10 archive hashes."""

from datetime import datetime
import json
import math
from pathlib import Path

import imageio.v2 as imageio
from PIL import Image, ImageDraw

from jump360_scene import HERE, json_save, sha
from jump380_r10_policy import RUN


def verify_videos():
    video = json.loads((RUN/"VIDEO.json").read_text(encoding="utf-8"))
    reports = []
    sheet = Image.new("RGB", (960, len(video["videos"])*164), "#101820")
    labels = ImageDraw.Draw(sheet)
    for index, entry in enumerate(video["videos"]):
        path = RUN/entry["file"]
        case = entry["case"]
        fps = entry["fps"]
        if sha(path) != entry["sha256"]:
            raise ValueError(f"Video SHA-256 mismatch for {path.name}")
        key = case["trigger_tick"]*.02 if case["triggered"] else 0.
        liftoff = key + (case["takeoff_after_press_s"] or .12)
        apex = key + (case["apex_after_press_s"] or .28)
        touchdown = key + (case["first_touch_after_press_s"] or .60)
        targets = [round(seconds*fps) for seconds in (key - .22, liftoff, apex, touchdown, touchdown + .34)]
        targets.append(entry["frames"]-1)
        targets = [max(0, min(frame, entry["frames"] - 1)) for frame in targets]
        sampled = {}
        reader = imageio.get_reader(str(path))
        try:
            meta = reader.get_meta_data()
            count = 0
            for i, frame in enumerate(reader):
                if frame.shape != (432, 768, 3) or frame[::16, ::16].std() < 4.:
                    raise ValueError(f"Unexpected frame {i} in {path.name}")
                if i in targets:
                    sampled[i] = Image.fromarray(frame).resize((160, 90), Image.Resampling.LANCZOS)
                count += 1
        finally:
            reader.close()
        if count != entry["frames"] or meta["fps"] != fps or meta["codec"] != "h264":
            raise ValueError(f"Unexpected decoded video metadata for {path.name}")
        if not math.isclose(meta["duration"], count/fps, abs_tol=.02):
            raise ValueError(f"Unexpected video duration for {path.name}")
        if not case["fall"] and case["triggered"] and count != (case["trigger_tick"] + 125)//2:
            raise ValueError(f"Unexpected frame count for the 1x replay {path.name}")
        offset = index*164
        labels.text((5, offset+7), path.name, fill="#e9f2f9")
        for j, frame in enumerate(targets):
            sheet.paste(sampled[frame], (160*j, offset+27))
            labels.text((160*j+5, offset+124), f"Frame {frame:03d}  {frame/fps:.2f}s", fill="#e9f2f9")
        reports.append(dict(file=path.name, sha256=entry["sha256"], decoded_frames=count,
                            width=768, height=432, fps=fps, duration_s=meta["duration"], codec=meta["codec"],
                            playback_speed=entry["playback_speed"], visual_check_frames=targets,
                            strict_direct=case["strict_direct"], flat_qualified=case["qualified"]))
    sheet.save(RUN/"VIDEO_FRAME_CHECK.jpg", quality=92)
    json_save(RUN/"VIDEO_VERIFICATION.json", dict(checkpoint_sha256=video["checkpoint_sha256"], videos=reports))


def verify_archives():
    baseline = json.loads((RUN/"PROTECTION_BASELINE.json").read_text(encoding="utf-8"))
    changed, missing = [], []
    for name, checksum in baseline.items():
        path = HERE/Path(name)
        if not path.is_file():
            missing.append(name)
        elif sha(path) != checksum:
            changed.append(name)
    passed = not changed and not missing
    json_save(RUN/"PROTECTION_VERIFICATION.json",
              dict(verified_at=datetime.now().astimezone().isoformat(), files=len(baseline),
                   changed=changed, missing=missing, passed=passed))
    if not passed:
        raise ValueError(f"Protected archive mismatch: {changed}, missing: {missing}")
    print(f"Verified {len(baseline)} protected files")


if __name__ == "__main__":
    verify_videos()
    verify_archives()
