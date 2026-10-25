"""Pure CPU synthetic tensor check, no SDK/environment/GPU/policy use."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,json,platform,sys,time,traceback
from pathlib import Path
import torch
from e3_fixed_recipe_geometry_unused_v1 import original_geometry,build_table,lookup_table

B=Path(__file__).resolve().parent
P=B/'reports'/'E3_FIXED_RECIPE_SYNTHETIC_CPU_V1_ACTUAL.json'


def main():
    assert not P.exists(),'Once-only report already exists'
    report=dict(trial_id='MOD4_SAMPLING_CPU_E3_GEOMETRY_V1_20261025',epoch=time.time(),status='running',
                Python=sys.version,torch=torch.__version__,platform=platform.platform(),device='cpu',
                no_GPU_API_SDK_policy_physics_or_environment=True,actual_bank_not_read=True,
                source_point_count_25200_from_existing_bank_metadata=True,
                helper_SHA=hashlib.sha256((B/'e3_fixed_recipe_geometry_unused_v1.py').read_bytes()).hexdigest(),
                script_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),samples=[])
    def put():P.write_text(json.dumps(report,indent=2),encoding='utf8')
    put()
    try:
        torch.set_num_threads(1)
        rng=torch.Generator(device='cpu').manual_seed(20261025)
        before=torch.random.get_rng_state().clone()
        points=torch.randn((25200,3),generator=rng,device='cpu',dtype=torch.float32)*.25
        recipe=torch.arange(520,device='cpu')%13
        start=time.perf_counter();table=build_table(torch,points);report['one_time_build_table_s']=time.perf_counter()-start
        assert all(value.device.type=='cpu' for value in table.values())
        for repeat in range(3):
            start=time.perf_counter();original=original_geometry(torch,points,recipe);old_s=time.perf_counter()-start
            start=time.perf_counter();cached=lookup_table(torch,table,recipe);new_s=time.perf_counter()-start
            assert all(torch.equal(original[key],cached[key]) for key in original)
            report['samples'].append(dict(repeat=repeat,selected_reset_count=len(recipe),points_per_pose=len(points),original_s=old_s,lookup_s=new_s,
                                          exact_cpu_float32_quat_minimum_initial=True,max_abs_error={key:float((original[key]-cached[key]).abs().max()) for key in original}))
            put()
        assert torch.equal(before,torch.random.get_rng_state())
        report.update(status='CPU_synthetic_equality_passed_not_production_device_validation',
                      global_torch_RNG_untouched=True,private_cpu_generator_seed=20261025,
                      old_per_reset_complexity='O(selected_count *25200)',new_per_reset_complexity='O(selected_count), table once O(13*25200)',
                      no_claim_actual_same_source_bank_or_CUDA_bitwise_equality=True,completed_epoch=time.time())
        put();print(json.dumps(report),flush=True)
    except BaseException:
        report.update(status='original_error_retained',original_error=traceback.format_exc());put();raise


if __name__=='__main__':main()
