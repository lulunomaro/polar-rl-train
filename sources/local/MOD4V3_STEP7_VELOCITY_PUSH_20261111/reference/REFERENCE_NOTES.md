# Native source used by D10

`push_by_setting_velocity_target.py` is the function read from the installed IsaacLab path on 10.24.3.125. Its body reads current world root velocity, adds independently sampled XY delta, and calls write_root_velocity_to_sim_index. Other velocity ranges default to zero increments. D10 imports this installed function directly.

`native_event_manager_methods.txt` records the existing reference apply/reset timer logic. The DirectRLEnv post-step calls EventManager.apply(mode="interval",dt=step_dt). DirectRLEnv._reset_idx does not itself call EventManager.reset, so the D10 subclass adds that call after the inherited episode reset, matching the SCUT ManagerBasedRLEnv timer resampling behavior. No existing force/torque timer is replaced.

Original README wording that claimed velocity replacement is superseded by this source and corrected task plan. Actual write/read and partial reset behavior must pass the D10 native interval probe before training. This file does not claim the runtime probe has already run.
