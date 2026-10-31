"""Narrow V2: preserve original theta's atan2-minus-pi/2 branch convention.

V1's atan2(-forward,down) is equivalent on the downward branch, but wraps
some upside poses by 2pi; squared original pen_theta_no0 then differs.
V1 source/CPU PASS are retained as a limited downward-domain fixture.
"""
import math
import torch
from mod4_literal_math184 import *

GEOMETRY_DEFINITION = (
    "own MOD4 authored hip local_pos0 on chassis -> actual main-wheel BODY ORIGIN/axis; "
    "v_b=R_chassis^T*(p_wheel-p_chassis)-hip_anchor_b; "
    "L0=sqrt(v_b.x^2+v_b.z^2) metres; "
    "theta0=atan2(down=-v_b.z,forward=v_b.x)-pi/2 radians, "
    "zero downward, positive wheel rearward on downward branch; "
    "retain original unwrapped atan2-minus-pi/2 convention even upside; "
    "sagittal projection ignores lateral offset; no Fudan rods or retargeted constants"
)


def own_virtual_legs(body_position, chassis_R, body_names, hip_anchors):
    chassis = body_position[:, named_indices(body_names, ("chassis",))[0]]
    wheel = body_position[:, named_indices(body_names, WHEEL_BODIES)]
    delta = torch.einsum("nji,nkj->nki", chassis_R, wheel-chassis[:, None])
    v = delta-hip_anchors.to(delta)[None]
    length = torch.sqrt(v[..., 0].square()+v[..., 2].square())
    theta = torch.atan2(-v[..., 2], v[..., 0])-math.pi/2
    return length, theta
