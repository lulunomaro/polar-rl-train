"""Reuse own observed support across an episode when camera loses the edge."""
from dataclasses import replace
import torch
from future_safe_wm_warm273 import FutureSafeWarmWM273
from native_depth_world_model50_v255 import normalize_context40

class TrackingWM300(FutureSafeWarmWM273):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.observed_cache={};self.cache_episodes=None
        self.protocol.update(kind='OWN_TRACKING_WM300_OBSERVED_EPISODE_ANCHOR',anchor_memory='last actual observed support within same episode, worldfixed; no GT fallback')

    def _anchor_values(self,packet,fields,start_tick):
        values,scope=super()._anchor_values(packet,fields,start_tick)
        ids=torch.tensor(packet.producer.episode_ids,device=self.device)
        if self.cache_episodes is None:self.cache_episodes=torch.full_like(ids,-1)
        same=ids==self.cache_episodes;current=values['valid_anchor'];reuse=~current&same
        keys=('corners_world','floor_world_z','step_height','confidence','initial_age','sensor_time_s')
        if not self.observed_cache:reuse&=False
        for key in keys:
            if key not in self.observed_cache:self.observed_cache[key]=values[key].detach().clone()
            values[key][reuse]=self.observed_cache[key][reuse]
            self.observed_cache[key][current]=values[key][current]
        values['valid_anchor']|=reuse
        values['initial_age'][reuse]=packet.control_time_s[reuse]-values['sensor_time_s'][reuse]
        self.cache_episodes[current]=ids[current]
        return values,scope
