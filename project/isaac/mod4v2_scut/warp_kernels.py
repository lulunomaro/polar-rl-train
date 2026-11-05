"""Fused sampling kernels; same measured contacts, jump meter and Fudan equations.

Uses the device-resident, preallocated-output pattern in basic_loco_lib's
tasks/velocity/mdp_warp/rewards.py at e4181af587330d0b70ca72e0d36b49be32e12a65.
MOD4 equations and state transitions below come from its existing Torch bridge.
No simulator step, actuator, DR draw or policy action is added here.
"""
import warp as wp

TERMS = ('tracking_lin_vel', 'tracking_lin_vel_enhance', 'tracking_ang_vel',
         'flight', 'encourage_jump', 'base_height_flight', 'leg_tuck',
         'takeoff_extend', 'line_z', 'pen_theta_no0', 'action_rate', 'torques',
         'orientation', 'ang_vel_xy', 'nominal_state', 'collision')
TermValues = wp.types.vector(length=16, dtype=wp.float32)


@wp.func
def rotate(w: float, x: float, y: float, z: float, v: wp.vec3):
    xyz = wp.vec3(x, y, z)
    t = 2.0 * wp.cross(xyz, v)
    return v + w * t + wp.cross(xyz, t)


@wp.kernel
def manifold(force: wp.array(dtype=float), points: wp.array(dtype=wp.vec3),
             normals: wp.array(dtype=wp.vec3), counts: wp.array2d(dtype=wp.int32),
             starts: wp.array2d(dtype=wp.int32), origins: wp.array2d(dtype=float),
             wheel: int, top: wp.array2d(dtype=float), ground: wp.array2d(dtype=float),
             surface: wp.array2d(dtype=float), height: wp.array2d(dtype=float),
             error: wp.array(dtype=wp.int32)):
    i = wp.tid()
    ft, fg, fs = float(0.0), float(0.0), float(0.0)
    peak, peak_z = float(-1.0), float(0.0)
    any_horizontal = bool(False)
    for group in range(counts.shape[1]):
        count, start = wp.int64(counts[i, group]), wp.int64(starts[i, group])
        if count < 0 or count > 64 or start < 0 or start + count > force.shape[0]:
            wp.atomic_or(error, 0, 1)
        else:
            for k in range(int(count)):
                j = start + wp.int64(k)
                if wp.abs(normals[j][2]) > 0.8:
                    f = wp.abs(force[j])
                    p = points[j] - wp.vec3(origins[i, 0], origins[i, 1], origins[i, 2])
                    fs += f
                    if not any_horizontal or f > peak:
                        peak, peak_z = f, points[j][2]
                    any_horizontal = True
                    if wp.abs(p[2] - 0.2) < 0.001 and p[0] >= 0.799 and p[0] <= 3.501 and wp.abs(p[1]) <= 3.501:
                        ft += f
                    if wp.abs(p[2]) < 0.001:
                        fg += f
    top[i, wheel] = ft
    ground[i, wheel] = fg
    surface[i, wheel] = fs
    height[i, wheel] = peak_z


@wp.kernel
def acceptance(body_pos: wp.array3d(dtype=float), body_quat: wp.array3d(dtype=float),
               root_quat: wp.array2d(dtype=float), velocity: wp.array2d(dtype=float),
               origins: wp.array2d(dtype=float), contacts: wp.array3d(dtype=float),
               wheel_ids: wp.array(dtype=int), nonwheel_ids: wp.array(dtype=int),
               axes: wp.array2d(dtype=float), offsets: wp.array2d(dtype=float),
               radii: wp.array(dtype=float), widths: wp.array(dtype=float),
               top: wp.array2d(dtype=float), ground: wp.array2d(dtype=float),
               success: wp.array(dtype=wp.bool), wholeclear: wp.array(dtype=wp.bool),
               leading: wp.array(dtype=wp.bool), ground_seen: wp.array(dtype=wp.bool),
               previous_air: wp.array(dtype=wp.bool), up: wp.array(dtype=wp.bool),
               current_clear: wp.array(dtype=wp.bool), failed_return: wp.array(dtype=wp.bool),
               landed_top: wp.array(dtype=wp.bool), flight_id: wp.array(dtype=wp.int64),
               stable_ticks: wp.array(dtype=wp.int64), stable_peak: wp.array(dtype=wp.int64),
               support_ticks: wp.array(dtype=wp.int64), support_peak: wp.array(dtype=wp.int64),
               initial_yaw: wp.array(dtype=float)):
    i = wp.tid()
    supported_ground, air, high = bool(True), bool(True), bool(True)
    front, rear, inside, returned = bool(True), bool(True), bool(True), bool(False)
    top_supported = bool(True)
    for k in range(nonwheel_ids.shape[0]):
        b = nonwheel_ids[k]
        f = wp.vec3(contacts[i, b, 0], contacts[i, b, 1], contacts[i, b, 2])
        air = air and wp.length(f) <= 1.0
        top_supported = top_supported and wp.length(f) <= 1.0
    for k in range(2):
        b = wheel_ids[k]
        w = float(body_quat[i, b, 0])
        x = float(body_quat[i, b, 1])
        y = float(body_quat[i, b, 2])
        z = float(body_quat[i, b, 3])
        axis = rotate(w, x, y, z, wp.vec3(axes[k, 0], axes[k, 1], axes[k, 2]))
        axis = axis / wp.max(wp.length(axis), 1.0e-6)
        center = wp.vec3(body_pos[i, b, 0], body_pos[i, b, 1], body_pos[i, b, 2])
        center += rotate(w, x, y, z, wp.vec3(offsets[k, 0], offsets[k, 1], offsets[k, 2]))
        center -= wp.vec3(origins[i, 0], origins[i, 1], origins[i, 2])
        extent = wp.vec3(radii[k]*wp.sqrt(axis[1]*axis[1]+axis[2]*axis[2])+widths[k]*wp.abs(axis[0]),
                         radii[k]*wp.sqrt(axis[0]*axis[0]+axis[2]*axis[2])+widths[k]*wp.abs(axis[1]),
                         radii[k]*wp.sqrt(axis[0]*axis[0]+axis[1]*axis[1])+widths[k]*wp.abs(axis[2]))
        low, upper = center - extent, center + extent
        force = wp.vec3(contacts[i, b, 0], contacts[i, b, 1], contacts[i, b, 2])
        supported_ground = supported_ground and ground[i, k] > 1.0
        air = air and wp.length(force) <= 1.0 and low[2] > 0.005
        high = high and low[2] >= 0.2
        front = front and upper[0] >= 0.8
        rear = rear and low[0] >= 0.8
        inside = inside and low[0] >= 0.8 and upper[0] <= 3.5 and low[1] >= -3.5 and upper[1] <= 3.5
        returned = returned or ground[i, k] > 1.0 or low[0] < 0.78
        top_supported = top_supported and top[i, k] > 1.0
    seen = ground_seen[i] or supported_ground
    launch = air and not previous_air[i] and seen
    if launch:
        flight_id[i] += wp.int64(1)
        up[i] = False
        current_clear[i] = False
        failed_return[i] = False
        landed_top[i] = False
        seen = False
    up[i] = up[i] or (air and flight_id[i] > wp.int64(0) and velocity[i, 2] > 0.05)
    leading[i] = leading[i] or (air and up[i] and high and front)
    current_clear[i] = current_clear[i] or (air and up[i] and high and rear)
    wholeclear[i] = wholeclear[i] or current_clear[i]
    failed_return[i] = failed_return[i] or (current_clear[i] and returned)
    supported = current_clear[i] and not failed_return[i] and inside and top_supported
    landed_top[i] = landed_top[i] or supported
    st = wp.int64(0)
    if supported:
        st = support_ticks[i] + wp.int64(1)
    support_ticks[i] = st
    support_peak[i] = wp.max(support_peak[i], st)
    rw, rx, ry, rz = root_quat[i, 0], root_quat[i, 1], root_quat[i, 2], root_quat[i, 3]
    roll = wp.atan2(2.0*(rw*rx+ry*rz), 1.0-2.0*(rx*rx+ry*ry))
    pitch = wp.asin(wp.clamp(2.0*(rw*ry-rz*rx), -1.0, 1.0))
    yaw = wp.atan2(2.0*(rw*rz+rx*ry), 1.0-2.0*(ry*ry+rz*rz))
    if wp.isnan(initial_yaw[i]):
        initial_yaw[i] = yaw
    yaw_delta = yaw - initial_yaw[i]
    shifted = yaw_delta + wp.pi
    wrapped = shifted - wp.floor(shifted/(2.0*wp.pi))*(2.0*wp.pi)
    # Mirror math_ops.wrap_to_pi, including its endpoint convention.
    yaw_delta = wrapped - wp.pi
    if wrapped == 0.0:
        if yaw - initial_yaw[i] > 0.0:
            yaw_delta = wp.pi
    steady = supported and wp.sqrt(velocity[i, 0]**2.0+velocity[i, 1]**2.0) <= 0.03
    steady = steady and wp.abs(velocity[i, 2]) <= 0.03 and wp.abs(roll) <= wp.pi/18.0
    steady = steady and wp.abs(pitch) <= wp.pi/18.0 and wp.abs(yaw_delta) <= 0.2
    ticks = wp.int64(0)
    if steady:
        ticks = stable_ticks[i] + wp.int64(1)
    stable_ticks[i] = ticks
    stable_peak[i] = wp.max(stable_peak[i], ticks)
    success[i] = success[i] or ticks >= wp.int64(200)
    ground_seen[i] = seen
    previous_air[i] = air


@wp.kernel
def fudan(root_pos: wp.array2d(dtype=float), root_quat: wp.array2d(dtype=float),
          world_velocity: wp.array2d(dtype=float), lin_velocity: wp.array2d(dtype=float),
          ang_velocity: wp.array2d(dtype=float), gravity: wp.array2d(dtype=float),
          body_pos: wp.array3d(dtype=float), contacts: wp.array3d(dtype=float),
          wheel_ids: wp.array(dtype=int), collision_ids: wp.array(dtype=int),
          motor_ids: wp.array(dtype=int), anchors: wp.array2d(dtype=float),
          torque: wp.array2d(dtype=float), actions: wp.array2d(dtype=float),
          previous_actions: wp.array2d(dtype=float), command: wp.array2d(dtype=float),
          last_contact: wp.array2d(dtype=wp.bool), filtered_contact: wp.array2d(dtype=wp.bool),
          flight: wp.array(dtype=wp.bool), air_time: wp.array(dtype=float),
          leg_length: wp.array2d(dtype=float), leg_theta: wp.array2d(dtype=float),
          weights: wp.array(dtype=float), raw: wp.array2d(dtype=float),
          weighted: wp.array2d(dtype=float), sums: wp.array2d(dtype=float),
          total: wp.array(dtype=float)):
    i = wp.tid()
    w, x, y, z = root_quat[i, 0], root_quat[i, 1], root_quat[i, 2], root_quat[i, 3]
    airborne, supported = bool(True), bool(False)
    tuck_error, extend_error, theta_cost = float(0.0), float(0.0), float(0.0)
    for k in range(2):
        b = wheel_ids[k]
        contact = contacts[i, b, 2] > 1.0
        filtered = contact or last_contact[i, k]
        last_contact[i, k] = contact
        filtered_contact[i, k] = filtered
        airborne, supported = airborne and not filtered, supported or filtered
        delta = wp.vec3(body_pos[i, b, 0]-root_pos[i, 0], body_pos[i, b, 1]-root_pos[i, 1], body_pos[i, b, 2]-root_pos[i, 2])
        leg = rotate(w, -x, -y, -z, delta) - wp.vec3(anchors[k, 0], anchors[k, 1], anchors[k, 2])
        length, theta = wp.sqrt(leg[0]*leg[0]+leg[2]*leg[2]), wp.atan2(-leg[0], -leg[2])
        leg_length[i, k] = length
        leg_theta[i, k] = theta
        tuck_error += wp.abs(length-0.16)
        extend_error += wp.abs(length-0.31)
        theta_cost += theta*theta
    flight[i] = airborne
    first_contact = air_time[i] > 0.0 and not airborne
    updated_air_time = air_time[i] + 0.02*wp.clamp(root_pos[i, 2], 0.0, 0.5)
    encourage = 0.15*wp.max(world_velocity[i, 2], 0.0)
    if first_contact:
        encourage += (updated_air_time-5.0e-5)*0.15
    air_time[i] = updated_air_time
    if airborne:
        air_time[i] = 0.0
    action_cost, torque_cost, collision_cost = float(0.0), float(0.0), float(0.0)
    for k in range(6):
        delta_action = previous_actions[i, k] - actions[i, k]
        action_cost += delta_action*delta_action
        t = torque[i, motor_ids[k]]
        torque_cost += t*t
    for k in range(collision_ids.shape[0]):
        b = collision_ids[k]
        if wp.length(wp.vec3(contacts[i, b, 0], contacts[i, b, 1], contacts[i, b, 2])) > 0.1:
            collision_cost += 1.0
    v = TermValues(0.0)
    lin_error = (command[i, 0]-lin_velocity[i, 0])**2.0
    v[0] = wp.exp(-lin_error/0.25)*2.0
    v[1] = (wp.exp(-lin_error/0.25/10.0)-1.0)*2.0
    v[2] = wp.exp(-(command[i, 2]-ang_velocity[i, 2])**2.0/0.25)
    if airborne:
        v[3] = 1.0
        v[5] = wp.exp(-wp.abs(root_pos[i, 2]-0.65)*6.0)
        v[6] = wp.exp(-tuck_error*4.0)
        if world_velocity[i, 2] > 0.0:
            v[8] = world_velocity[i, 2]
    v[4] = encourage
    if supported and world_velocity[i, 2] > 0.15:
        v[7] = wp.exp(-extend_error*4.0)
    v[9] = theta_cost
    v[10] = action_cost
    v[11] = torque_cost
    v[12] = gravity[i, 0]*gravity[i, 0]+gravity[i, 1]*gravity[i, 1]
    v[13] = ang_velocity[i, 0]*ang_velocity[i, 0]+ang_velocity[i, 1]*ang_velocity[i, 1]
    v[14] = (leg_theta[i, 0]-leg_theta[i, 1])**2.0 + 10.0*(leg_length[i, 0]-leg_length[i, 1])**2.0
    v[15] = collision_cost
    result = float(0.0)
    for k in range(16):
        raw[i, k] = v[k]
        value = wp.clamp(v[k]*weights[k]*0.02, -0.05, 0.05)
        weighted[i, k] = value
        sums[i, k] += value
        result += value
    total[i] = result
