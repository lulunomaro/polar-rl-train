# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin


from __future__ import annotations
import torch

class OriginalStairs3Methods:
    def compute_reward(self):
        """Compute rewards
        Calls each reward function which had a non-zero scale (processed in self._prepare_reward_function())
        adds each terms to the episode sums and to the total reward
        """
        self.rew_buf[:] = 0.0
        for i in range(len(self.reward_functions)):
            name = self.reward_names[i]
            rew = self.reward_functions[i]() * self.reward_scales[name]
            rew = torch.clip(
                rew,
                -self.cfg.rewards.clip_single_reward * self.dt,
                self.cfg.rewards.clip_single_reward * self.dt,
            )
            self.rew_buf += rew
            self.episode_sums[name] += rew
        if self.cfg.rewards.only_positive_rewards:
            self.rew_buf[:] = torch.clip(self.rew_buf[:], min=0.0)
        # add termination reward after clipping
        if "termination" in self.reward_scales:
            rew = self._reward_termination() * self.reward_scales["termination"]
            self.rew_buf += rew
            self.episode_sums["termination"] += rew

    def _update_terrain_curriculum(self, env_ids):
        """Implements the game-inspired curriculum.

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # Implement Terrain curriculum
        if not self.init_done:
            # don't change on initial reset
            return
        distance = torch.norm(
            self.root_states[env_ids, :2] - self.env_origins[env_ids, :2], dim=1
        )
        # robots that walked far enough progress to harder terains
        move_up = distance > self.terrain.env_length / 2  #原本是/2
        # robots that walked less than half of their required distance go to simpler terrains
        move_down = (
            self.episode_sums["tracking_lin_vel"][env_ids] / self.max_episode_length_s
            < (self.reward_scales["tracking_lin_vel"] / self.dt) * 0.4
        ) * ~move_up
        self.terrain_levels[env_ids] += 1 * move_up - 1 * move_down
        mask = self.terrain_levels[env_ids] >= self.max_terrain_level
        self.success_ids = env_ids[mask]
        mask = self.terrain_levels[env_ids] < 0
        self.fail_ids = env_ids[mask]
        # Robots that solve the last level are sent to a random one
        self.terrain_levels[env_ids] = torch.where(
            self.terrain_levels[env_ids] >= self.max_terrain_level,
            torch.randint_like(self.terrain_levels[env_ids], self.max_terrain_level),
            torch.clip(self.terrain_levels[env_ids], 0),
        )  # (the minumum level is zero)
        self.env_origins[env_ids] = self.terrain_origins[
            self.terrain_levels[env_ids], self.terrain_types[env_ids]
        ]
        if self.cfg.commands.curriculum:
            self.command_ranges["lin_vel_x"][self.fail_ids, 0] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 0] + 0.25,
                -self.cfg.commands.basic_max_curriculum,
                -1,
            )
            self.command_ranges["lin_vel_x"][self.fail_ids, 1] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 1] - 0.25,
                1,
                self.cfg.commands.basic_max_curriculum,
            )

    def _prepare_reward_function(self):
        """Prepares a list of reward functions, whcih will be called to compute the total reward.
        Looks for self._reward_<REWARD_NAME>, where <REWARD_NAME> are names of all non zero reward scales in the cfg.
        """
        # remove zero scales + multiply non-zero ones by dt
        for key in list(self.reward_scales.keys()):
            scale = self.reward_scales[key]
            if scale == 0:
                self.reward_scales.pop(key)
            else:
                self.reward_scales[key] *= self.dt
        # prepare list of functions
        self.reward_functions = []
        self.reward_names = []
        for name, scale in self.reward_scales.items():
            if name == "termination":
                continue
            self.reward_names.append(name)
            name = "_reward_" + name
            self.reward_functions.append(getattr(self, name))

        # reward episode sums
        self.episode_sums = {
            name: torch.zeros(
                self.num_envs,
                dtype=torch.float,
                device=self.device,
                requires_grad=False,
            )
            for name in self.reward_scales.keys()
        }

    def _get_heights(self, env_ids=None):
        """Samples heights of the terrain at required points around each robot.
            The points are offset by the base's position and rotated by the base's yaw

        Args:
            env_ids (List[int], optional): Subset of environments for which to return the heights. Defaults to None.

        Raises:
            NameError: [description]

        Returns:
            [type]: [description]
        """
        if self.cfg.terrain.mesh_type == "plane":
            return torch.zeros(
                self.num_envs,
                self.num_height_points,
                device=self.device,
                requires_grad=False,
            )
        elif self.cfg.terrain.mesh_type == "none":
            raise NameError("Can't measure height with terrain mesh type 'none'")

        if env_ids:
            points = quat_apply_yaw(
                self.base_quat[env_ids].repeat(1, self.num_height_points),
                self.height_points[env_ids],
            ) + (self.root_states[env_ids, :3]).unsqueeze(1)
        else:
            points = quat_apply_yaw(
                self.base_quat.repeat(1, self.num_height_points), self.height_points
            ) + (self.root_states[:, :3]).unsqueeze(1)

        points += self.terrain.cfg.border_size
        points = (points / self.terrain.cfg.horizontal_scale).long()
        px = points[:, :, 0].view(-1)
        py = points[:, :, 1].view(-1)
        px = torch.clip(px, 0, self.height_samples.shape[0] - 2)
        py = torch.clip(py, 0, self.height_samples.shape[1] - 2)

        heights1 = self.height_samples[px, py]
        heights2 = self.height_samples[px + 1, py]
        heights3 = self.height_samples[px, py + 1]
        heights = torch.min(heights1, heights2)
        heights = torch.min(heights, heights3)

        return heights.view(self.num_envs, -1) * self.terrain.cfg.vertical_scale

    def _reward_lin_vel_z(self):
        # Penalize z axis base linear velocity
        return torch.square(self.base_lin_vel[:, 2])

    def _reward_ang_vel_xy(self):
        # Penalize xy axes base angular velocity
        return torch.sum(torch.square(self.base_ang_vel[:, :2]), dim=1)

    def _reward_orientation(self):
        # Penalize non flat base orientation
        return torch.sum(torch.square(self.projected_gravity[:, :2]), dim=1)

    def _reward_base_height(self):
        # Penalize base height away from target
        # print(self.commands[0, 2], self.base_height[0])
        if self.reward_scales["base_height"] < 0:
            return torch.abs(self.base_height - self.commands[:, 2])
        else:
            base_height_error = torch.square(self.base_height - self.commands[:, 2])
            return torch.exp(-base_height_error * 1000) * 1.5

    def _reward_base_height_enhance(self):
        base_height_error = torch.square(self.base_height - self.commands[:, 2])
        return torch.exp(-base_height_error / 0.001 / 10) - 1

    def _reward_torques(self):
        # Penalize torques
        return torch.sum(torch.square(self.torques), dim=1)

    def _reward_power(self):
        # Penalize torques
        return torch.sum(torch.abs(self.torques * self.dof_vel), dim=1)

    def _reward_dof_vel(self):
        # Penalize dof velocities
        return torch.sum(torch.square(self.dof_vel[:, :2]), dim=1) + torch.sum(
            torch.square(self.dof_vel[:, 3:5]), dim=1
        )

    def _reward_dof_acc(self):
        # Penalize dof accelerations
        return torch.sum(torch.square(self.dof_acc), dim=1)

    def _reward_action_rate(self):
        # Penalize changes in actions
        return torch.sum(torch.square(self.last_actions[:, :, 0] - self.actions), dim=1)

    def _reward_action_smooth(self):
        # Penalize changes in actions
        return torch.sum(
            torch.square(
                self.actions[:, :2]
                - 2 * self.last_actions[:, :2, 0]
                + self.last_actions[:, :2, 1]
            ),
            dim=1,
        ) + torch.sum(
            torch.square(
                self.actions[:, 3:5]
                - 2 * self.last_actions[:, 3:5, 0]
                + self.last_actions[:, 3:5, 1]
            ),
            dim=1,
        )

    def _reward_collision(self):
        # Penalize collisions on selected bodies
        return torch.sum(
            1.0
            * (
                torch.norm(
                    self.contact_forces[:, self.penalised_contact_indices, :], dim=-1
                )
                > 0.1
            ),
            dim=1,
        )

    def _reward_termination(self):
        # Terminal reward / penalty
        return self.reset_buf * ~self.time_out_buf

    def _reward_dof_pos_limits(self):
        # Penalize dof positions too close to the limit
        out_of_limits = -(self.dof_pos[:, :2] - self.dof_pos_limits[:2, 0]).clip(
            max=0.0
        )  # lower limit
        out_of_limits += (self.dof_pos[:, :2] - self.dof_pos_limits[:2, 1]).clip(
            min=0.0
        )
        out_of_limits += -(self.dof_pos[:, 3:5] - self.dof_pos_limits[3:5, 0]).clip(
            max=0.0
        )  # lower limit
        out_of_limits += (self.dof_pos[:, 3:5] - self.dof_pos_limits[3:5, 1]).clip(
            min=0.0
        )
        return torch.sum(out_of_limits, dim=1)

    def _reward_dof_vel_limits(self):
        # Penalize dof velocities too close to the limit
        # clip to max error = 1 rad/s per joint to avoid huge penalties
        return torch.sum(
            (
                torch.abs(self.dof_vel)
                - self.dof_vel_limits * self.cfg.rewards.soft_dof_vel_limit
            ).clip(min=0.0, max=1.0),
            dim=1,
        )

    def _reward_torque_limits(self):
        # penalize torques too close to the limit
        return torch.sum(
            (
                torch.abs(self.torques)
                - self.torque_limits * self.cfg.rewards.soft_torque_limit
            ).clip(min=0.0),
            dim=1,
        )

    def _reward_tracking_lin_vel(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma)

    def _reward_tracking_lin_vel_enhance(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1

    def _reward_tracking_ang_vel(self):
        # Tracking of angular velocity commands (yaw)
        ang_vel_error = torch.square(self.commands[:, 1] - self.base_ang_vel[:, 2])
        return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma)

    def _reward_tracking_ang_vel_enhance(self):
        # Tracking of angular velocity commands (x axes)
        ang_vel_error = torch.square(self.commands[:, 1] - self.base_ang_vel[:, 2])
        return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1

    def _reward_theta0_equ_0(self):    
        left_theta0_error = torch.square(self.theta0[:, 0])
        right_theta0_error = torch.square(self.theta0[:, 1])

        return torch.exp(-(left_theta0_error + right_theta0_error) / self.cfg.rewards.tracking_sigma)

    def _reward_tracking_lin_vel_pbrs(self):
        delta_phi = ~self.reset_buf * (
            self._reward_tracking_lin_vel() - self.rwd_linVelTrackPrev
        )
        # return lin_vel_error
        return delta_phi

    def _reward_tracking_ang_vel_pbrs(self):
        delta_phi = ~self.reset_buf * (
            self._reward_tracking_ang_vel() - self.rwd_angVelTrackPrev
        )
        # return ang_vel_error
        return delta_phi

    def _reward_stumble(self):
        # Penalize feet hitting vertical surfaces
        return torch.any(
            torch.norm(self.contact_forces[:, self.feet_indices, :2], dim=2)
            > 5 * torch.abs(self.contact_forces[:, self.feet_indices, 2]),
            dim=1,
        )

    def _reward_stand_still(self):
        # Penalize motion at zero commands
        return torch.sum(torch.abs(self.dof_pos - self.default_dof_pos), dim=1) * (
            torch.norm(self.commands[:, :2], dim=1) < 0.1
        )

    def _reward_nominal_state(self):
        # return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        if self.reward_scales["nominal_state"] < 0:
            return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        else:
            ang_diff = torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            return torch.exp(-ang_diff / 0.1)

    def _reward_feet_contact_forces(self):
        # penalize high contact forces
        return torch.sum(
            (
                torch.norm(self.contact_forces[:, self.feet_indices, :], dim=-1)
                - self.cfg.rewards.max_contact_force
            ).clip(min=0.0),
            dim=1,
        )
