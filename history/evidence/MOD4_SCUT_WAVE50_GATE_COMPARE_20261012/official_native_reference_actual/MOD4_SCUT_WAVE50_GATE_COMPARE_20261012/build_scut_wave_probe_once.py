from scut_wave_io import *

def main():
    source=W/'MOD4_SCUT_CLOSURE_REVIEW_20261007/scut_closure_api_review18.py';old=source.read_text(encoding='utf8')
    head=old[:old.index(' env=WheelbipeV14Env(cfg=cfg)')]
    head=head.replace("O=Path('D:/MOD4_async_eval/scut_closure_review_20261007/original')","O=D/'original'")
    head=head.replace("p.add_argument('--steps',type=int,default=1500)","p.add_argument('--model_name',required=True,choices=['2026-07-23_16-23-21','2026-07-30_09-16-27']);p.add_argument('--steps',type=int,default=750)")
    head=head.replace('default=32','default=80').replace('import WheelbipeV14FlatEnvCfg','import WheelbipeV14RoughEnvCfg').replace("prefix=O/'pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03'","prefix=O/'pretrained/26_infantry/rough_rotation_stair'/args.model_name").replace('cfg=WheelbipeV14FlatEnvCfg()','cfg=WheelbipeV14RoughEnvCfg()').replace("prefix/'model_15000.pt'","prefix/'model_1000.pt'")
    body=(D/'scut_wave_probe_body.py').read_text(encoding='utf8');text=head+body;compile(text,'scut_wave50_original_probe.py','exec')
    p=D/'scut_wave50_original_probe.py';assert not p.exists();p.write_text(text,encoding='utf8')
    save('SCUT_PROBE_BUILT.json',dict(epoch=time.time(),probe_path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()),previous_API_adapter_source=str(source),previous_API_adapter_SHA=H(source.read_bytes()),all_previous_math_Proxy_Warp_reset_privileged_API_conversions_reused=True,only_new_frozen_terrain_route_fixture_capture_classifier=True,ordinary_original_dones_not_relaxed=True,no_GPU_launched=True))
    print(json.dumps(dict(built=True,probe=str(p),AST_passed=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_PROBE_BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_GPU=True));raise
