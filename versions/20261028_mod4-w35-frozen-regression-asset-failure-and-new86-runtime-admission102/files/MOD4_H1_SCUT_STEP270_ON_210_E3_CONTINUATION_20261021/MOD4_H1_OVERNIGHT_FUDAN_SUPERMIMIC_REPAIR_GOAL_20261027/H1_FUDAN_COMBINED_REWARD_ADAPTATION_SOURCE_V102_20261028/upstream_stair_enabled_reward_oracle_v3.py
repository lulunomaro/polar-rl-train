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


import torch

class UpstreamStairRewardOracleV3:

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

    def _reward_nominal_state(self):
            # return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            if self.reward_scales["nominal_state"] < 0:
                return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            else:
                ang_diff = torch.square(self.theta0[:, 0] - self.theta0[:, 1])
                return torch.exp(-ang_diff / 0.1)

    def _reward_lin_vel_z(self):
            # Penalize z axis base linear velocity
            return torch.square(self.base_lin_vel[:, 2])

    def _reward_ang_vel_xy(self):
            # Penalize xy axes base angular velocity
            return torch.sum(torch.square(self.base_ang_vel[:, :2]), dim=1)

    def _reward_orientation(self):
            # Penalize non flat base orientation
            return torch.sum(torch.square(self.projected_gravity[:, :2]), dim=1)

    def _reward_dof_vel(self):
            # Penalize dof velocities
            return torch.sum(torch.square(self.dof_vel[:, :2]), dim=1) + torch.sum(
                torch.square(self.dof_vel[:, 3:5]), dim=1
            )

    def _reward_dof_acc(self):
            # Penalize dof accelerations
            return torch.sum(torch.square(self.dof_acc), dim=1)

    def _reward_torques(self):
            # Penalize torques
            return torch.sum(torch.square(self.torques), dim=1)

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
