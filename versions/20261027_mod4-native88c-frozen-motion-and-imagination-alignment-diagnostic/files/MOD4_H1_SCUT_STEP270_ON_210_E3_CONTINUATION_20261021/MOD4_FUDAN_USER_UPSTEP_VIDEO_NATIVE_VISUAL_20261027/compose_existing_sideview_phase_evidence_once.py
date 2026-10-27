"""Scientific video contact sheet from already extracted original frames only."""
from pathlib import Path
import json, hashlib, time
from PIL import Image, ImageDraw, ImageFont

V = Path(__file__).resolve().parent
R = V / 'reports'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p): return dict(path=str(p), bytes=p.stat().st_size, SHA=sha(p))

def main():
    consumed = R / 'SIDEVIEW_PHASE_PRESENTATION_CONSUMED_ACTUAL.json'
    with consumed.open('x', encoding='utf8') as f:
        json.dump(dict(epoch=time.time(), purpose='User requested real Fudan upstep phase comparison',
                       only_existing_extracted_JPEG_frames=True, no_video_decode_or_policy=True), f, indent=2)
    source = R / 'USER_PREFERRED_39_TO40_SIDE_JUMP_ORIGINAL_FRAMES_PRODUCER_ACTUAL.json'
    receipt = json.loads(source.read_bytes())
    phases = [
        (38.400, '接近台阶', '轮子仍在地面，机器人向画面左侧接近。'),
        (38.567, '蹬伸抬身', '机身快速上升，腿展开；不能把抬身当作已越台阶。'),
        (38.700, '腾空收腿', '轮子随腿抬高，机身与轮子都向平台上方移动。'),
        (38.800, '越边缘', '轮子接近或越过平台前沿，开始过渡到落地。'),
        (38.900, '落台过渡', '轮子到达平台附近；精确接触时刻受遮挡和帧率限制。'),
        (39.033, '平台上恢复', '视频显示机器人继续在平台上支撑和移动。'),
    ]
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    tiny = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    canvas = Image.new('RGB', (1536, 840), '#f8fafc')
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 8), '复旦真实上台阶：用户提供视频的侧视过程（时间标在每帧上方）', font=font, fill='#162f48')
    draw.text((20, 40), '约38.4–39.0秒包含接近、蹬伸、腾空与落台；39–40秒主要显示平台上的后续恢复。', font=small, fill='#364e63')
    chosen = []
    for i, (target, label, note) in enumerate(phases):
        row = min(receipt['frames'], key=lambda r: abs(r['pts_time_s'] - target))
        p = Path(row['path'])
        assert p.is_file() and p.stat().st_size == row['bytes']
        x, y = (i % 3) * 512, 80 + (i // 3) * 360
        draw.text((x+10, y), f"原视频 {row['pts_time_s']:.3f}s | {label}", font=small, fill='#162f48')
        frame = Image.open(p).convert('RGB').resize((500, 281))
        canvas.paste(frame, (x+6, y+30))
        # Deliberately no inferred joint or contact annotations on the image.
        chosen.append(dict(target_s=target, label=label, approximate_visual_observation=note, source=row))
    draw.text((16, 805), '原始画面；非3D重建。台阶高度、关节角度、力矩与精确接触时刻未由本视频测得。', font=small, fill='#4b5563')
    sheet = V / 'FUDAN_REAL_UPSTEP_SIDEVIEW_PHASE_KEYFRAMES.png'
    assert not sheet.exists()
    canvas.save(sheet)
    selected = [r for r in receipt['frames'] if 38.30 <= r['pts_time_s'] <= 39.20]
    images = []
    for row in selected:
        frame = Image.open(row['path']).convert('RGB').resize((960, 540))
        panel = Image.new('RGB', (960, 595), '#f8fafc'); panel.paste(frame, (0, 55))
        d = ImageDraw.Draw(panel)
        d.text((12, 7), f"复旦真实视频  t={row['pts_time_s']:.3f}s  |  4倍慢放  |  原始画面", font=font, fill='#162f48')
        images.append(panel)
    gif = V / 'FUDAN_REAL_UPSTEP_SIDEVIEW_4X_SLOW.gif'
    assert not gif.exists()
    images[0].save(gif, save_all=True, append_images=images[1:], duration=133, loop=0, optimize=False)
    result = dict(epoch=time.time(), passed=True, input_video_path=receipt['input_path'],
        original_input_video_SHA_unknown=True, source_frame_receipt=record(source),
        selected_keyframes=chosen, all_GIF_original_frame_receipts=selected,
        observations_scope='Qualitative native visual inspection, not metric motion capture',
        motion_direction_in_image='right_to_left', phase_times_approximate=True,
        original_teacher_standing_jump_is_not_this_real_upstep=True,
        previous_active_9223_goal_not_verified_as_this_motion=True,
        no_3D_joint_torque_contact_or_270mm_measurement_from_video=True,
        no_policy_physics_GPU_or_new_original_video_read=True,
        outputs=[record(sheet), record(gif)])
    with (R / 'REAL_FUDAN_SIDEVIEW_PHASE_KEYFRAMES_AND_SLOW_VIDEO_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(dict(passed=True, outputs=result['outputs']), ensure_ascii=False))

if __name__ == '__main__': main()
