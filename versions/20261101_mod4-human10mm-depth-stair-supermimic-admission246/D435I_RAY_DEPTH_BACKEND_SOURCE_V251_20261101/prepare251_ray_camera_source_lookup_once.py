from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
base=(T/'D435I_FRONT_FIXED_SDK_SOURCE_V248_20261101/read248_current_camera_SDK_metadata_once.py').read_text('utf8').replace('248','251')
old="files=['sensors/camera/camera_cfg.py','sensors/camera/tiled_camera.py','sensors/camera/camera.py','app/app_launcher.py']"
new="files=['sensors/ray_caster/ray_caster_camera_cfg.py','sensors/ray_caster/ray_caster_camera.py','sensors/ray_caster/patterns/patterns_cfg.py','sensors/ray_caster/ray_caster_cfg.py']"
assert base.count(old)==1;base=base.replace(old,new)
base=base.replace("pattern='read251_|","pattern='read251_|run_ROOT250_|")
base=base.replace("before creating sensor-only0PT caller. No camera construction or data claimed.","after original250 RTX Vulkan failure, before independent ray-camera depth caller. No install/driver changes or actual sensor data.")
p=N/'read251_current_ray_camera_SDK_metadata_once.py';p.write_text(base,encoding='utf8');ast.parse(base)
with(R/'FROZEN251_ORIGINAL250_RTX_FALSE_AND_DISTINCT_RAY_SOURCE_PURPOSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original250='Consumed; no valid depth frame. First graphics errors VkResultERROR_INCOMPATIBLE_DRIVER/vkCreateInstance/GPUfoundation before CUDA700. GPUordinal mismatch is not proved as unique cause.',next='Read actual supported geometric ray-camera API; generates forward depth image from own scene rays, never substitute ground-truth heightmap or claim real D435i stereo rendering.',source_files_each_once=4,model_assets_or_GPU_App_calls=0,host_driver_install_or_global_config_changes=False),f,indent=2)
print(json.dumps(dict(passed=True,path=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest())))
