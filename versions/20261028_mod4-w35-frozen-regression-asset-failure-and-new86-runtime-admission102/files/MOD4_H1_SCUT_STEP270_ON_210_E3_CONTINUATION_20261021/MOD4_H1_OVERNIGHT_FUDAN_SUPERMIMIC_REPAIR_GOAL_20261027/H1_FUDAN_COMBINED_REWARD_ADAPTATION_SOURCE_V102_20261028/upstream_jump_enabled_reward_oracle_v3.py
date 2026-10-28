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

class UpstreamJumpRewardOracleV3:

    def _reward_tracking_lin_vel(self):
            # Tracking of linear velocity commands (x axes)
            lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
            return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma) * 2

    def _reward_tracking_lin_vel_enhance(self):
            # Tracking of linear velocity commands (x axes)
            lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
            return (torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1) * 2

    def _reward_tracking_ang_vel(self):
            # Tracking of angular velocity commands (yaw)
            ang_vel_error = torch.square(self.commands[:, 1] - self.base_ang_vel[:, 2])
            return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma)

    def _reward_flight(self):
            # Penalize dof velocities
            return self.was_in_flight

    def _reward_encourage_jump(self):
    
            first_contact = (self.base_air_time > 0.0) * ~self.was_in_flight
            self.base_air_time += self.dt * torch.clip(
                self.root_states[:, 2],
                torch.tensor(0.0, device=self.device),
                0.50,
            )
    
            rew_airTime = (self.base_air_time - 5e-5) * first_contact * 0.15
    
            rew_airTime += (
                torch.maximum(
                    torch.tensor(0.0, device=self.device), self.root_states[:, 9]
                )
    
            )  * 0.15
    
            self.base_air_time *= ~self.was_in_flight
            return rew_airTime

    def _reward_base_height_flight(self):
            #跳跃的高度奖励
            base_height_flight = (self.root_states[:, 2] - 0.65)
            rew= torch.exp(-torch.abs(base_height_flight)*6.0)*(self.was_in_flight)
            return rew

    def _reward_leg_tuck(self):
            # Reward tucking legs in air (shorter virtual leg length) during flight.
            leg_tuck_err = torch.sum(torch.abs(self.L0 - 0.16), dim=1)
            rew = torch.exp(-leg_tuck_err * 4.0) * (self.was_in_flight) 
            return rew

    def _reward_takeoff_extend(self):
            # Reward extending the virtual leg during the push-off phase.
            takeoff_mask = torch.any(self.contact_filt, dim=1) & (self.root_states[:, 9] > 0.15)
            target_l0 = 0.31
            l0_err = torch.sum(torch.abs(self.L0 - target_l0), dim=1)
            rew = torch.exp(-l0_err * 4.0) * takeoff_mask
            return rew

    def _reward_line_z(self):
            #在初始化后和落地之前z轴线速度越大越好
            rew=(self.root_states[:, 9]>0)*self.root_states[:, 9] * (self.was_in_flight)
            return rew

    def _reward_pen_theta_no0(self):
            # Penalize non-zero theta0 to encourage legs to be under the body
            return torch.sum(torch.square(self.theta0), dim=1)

    def _reward_action_rate(self):
            # Penalize changes in actions
            return torch.sum(torch.square(self.last_actions[:, :, 0] - self.actions), dim=1)

    def _reward_torques(self):
            # Penalize torques
            return torch.sum(torch.square(self.torques), dim=1)

    def _reward_orientation(self):
            # Penalize non flat base orientation
            return torch.sum(torch.square(self.projected_gravity[:, :2]), dim=1)

    def _reward_ang_vel_xy(self):
            # Penalize xy axes base angular velocity
            return torch.sum(torch.square(self.base_ang_vel[:, :2]), dim=1)

    def _reward_nominal_state(self):
            # return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            a = torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            b = 10 * torch.square(self.L0[:, 0] - self.L0[:, 1]) 
            return a + b

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
