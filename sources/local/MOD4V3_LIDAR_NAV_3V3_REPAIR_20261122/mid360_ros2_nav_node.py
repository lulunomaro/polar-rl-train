"""ROS 2 Real-Robot Livox Mid-360 + FAST-LIO2 Navigation & Stair/Jump Point-Cloud Bridge Node.

Connects directly to standard Livox Mid-360 + FAST-LIO2 / Point-LIO topics on the real robot:
- Subscribes:
  * `/livox/lidar` (`sensor_msgs/msg/PointCloud2` OR `livox_ros_driver2/msg/CustomMsg`)
  * `/Odometry` (`nav_msgs/msg/Odometry` in `map` / `camera_init` frame from FAST-LIO2 / relocalization)
  * `/goal_pose` (`geometry_msgs/msg/PoseStamped` from RViz2 2D Goal Pose or Sentry Decision Tree)
  * `/cmd_vel_manual` (`geometry_msgs/msg/Twist` optional manual RC/keyboard override)
  * `/jump_trigger` (`std_msgs/msg/Bool` manual jump button rising edge)
- Publishes (50 Hz):
  * `/nav4d/cmd_vel` (`geometry_msgs/msg/Twist` -> `[vx_cmd, wz_cmd]` for locomotion controller)
  * `/nav4d/g_step` (`std_msgs/msg/Float32MultiArray` -> `[d1, h1, d2, h2]` 4D stair vector)
  * `/nav4d/g_jump` (`std_msgs/msg/Float32MultiArray` -> `[d_front, d_back, z_top_rel, z_land_rel]` 4D jump vector)
  * `/nav4d/ceiling` (`std_msgs/msg/Float32` -> overhead clearance in meters)
  * `/nav4d/planned_path` (`nav_msgs/msg/Path` -> smoothed normal-aligned stair + obstacle-avoiding A* path)

Can also be imported directly in pure Python (without `rclpy`) via `Mid360RealRobotBridge`!
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import numpy as np

from lidar_nav_planner import ElevationMap, WaypointFollower
from mid360_sensor import DEFAULT_EXTRINSIC_PATH, Mid360Config, quat_wxyz_to_rotmat
from mid360_stair_nav_detector import Mid360PointCloudNavDetector
from terrain_sensor_4d import EMPTY_JUMP_NP, EMPTY_NP


def pointcloud2_to_xyz(msg) -> np.ndarray:
    """Zero-dependency fast NumPy unpacker for `sensor_msgs/msg/PointCloud2` (`x, y, z` float32)."""
    width = int(msg.width)
    height = int(msg.height)
    n_pts = width * height
    if n_pts == 0:
        return np.zeros((0, 3), dtype=np.float32)
    point_step = int(msg.point_step)
    offsets = {f.name: int(f.offset) for f in msg.fields}
    if not ("x" in offsets and "y" in offsets and "z" in offsets):
        return np.zeros((0, 3), dtype=np.float32)
    buf = np.frombuffer(msg.data, dtype=np.uint8)
    avail = len(buf) // max(1, point_step)
    n = min(n_pts, avail)
    raw2d = buf[: n * point_step].reshape(n, point_step)
    x = raw2d[:, offsets["x"] : offsets["x"] + 4].copy().view("<f4").reshape(-1)
    y = raw2d[:, offsets["y"] : offsets["y"] + 4].copy().view("<f4").reshape(-1)
    z = raw2d[:, offsets["z"] : offsets["z"] + 4].copy().view("<f4").reshape(-1)
    xyz = np.stack((x, y, z), axis=1)
    return xyz[np.isfinite(xyz).all(axis=1)]


def livox_custom_msg_to_xyz(msg) -> np.ndarray:
    """Unpack `livox_ros_driver2/msg/CustomMsg` (`points[i].x, .y, .z` in meters)."""
    pts = msg.points
    n = len(pts)
    if n == 0:
        return np.zeros((0, 3), dtype=np.float32)
    xyz = np.array([[p.x, p.y, p.z] for p in pts], dtype=np.float32)
    return xyz[np.isfinite(xyz).all(axis=1)]


class Mid360RealRobotBridge:
    """Framework-agnostic real-robot Mid-360 navigation + stair/jump perception core (`50 Hz`)."""

    def __init__(
        self,
        prior_map_npz: str | Path | None = "mid360:suite_rmul2027",
        extrinsic_json: str | Path = DEFAULT_EXTRINSIC_PATH,
        mode: str = "fusion",
        default_nav_speed: float = 1.10,
    ):
        self.cfg = Mid360Config.from_json(extrinsic_json)
        self.prior_map = ElevationMap(prior_map_npz) if prior_map_npz else None
        self.detector = Mid360PointCloudNavDetector(
            prior_map=self.prior_map,
            config=self.cfg,
            mode=mode if self.prior_map is not None else "online_pc",
        )
        self.nav_speed = float(default_nav_speed)
        self.goal_xy: tuple[float, float] | None = None
        self.planned_path: list[tuple[float, float]] = []
        self.follower: WaypointFollower | None = None
        self.pos_w = np.zeros(3, dtype=np.float64)
        self.quat_wxyz = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        self.yaw = 0.0
        self.pose_valid = False
        self.jump_z_ref: float | None = None
        self._tick = 0

    def update_odometry(self, pos_xyz: np.ndarray, quat_wxyz: np.ndarray) -> None:
        self.pos_w = np.asarray(pos_xyz, dtype=np.float64).reshape(3)
        self.quat_wxyz = np.asarray(quat_wxyz, dtype=np.float64).reshape(4)
        R = quat_wxyz_to_rotmat(self.quat_wxyz)
        self.yaw = math.atan2(float(R[1, 0]), float(R[0, 0]))
        self.pose_valid = True

    def ingest_mid360_cloud(self, points_lidar_xyz: np.ndarray, z_foot: float | None = None) -> None:
        if not self.pose_valid:
            return
        self.detector.ingest_lidar_scan(points_lidar_xyz, self.pos_w, self.quat_wxyz, z_foot=z_foot)

    def set_goal(self, goal_x: float, goal_y: float, speed: float | None = None) -> list[tuple[float, float]]:
        if self.prior_map is None:
            raise RuntimeError("Global A* goal planning requires a loaded prior map (--prior-map).")
        if speed is not None:
            self.nav_speed = float(speed)
        self.goal_xy = (float(goal_x), float(goal_y))
        dyn = self.detector.dyn_blocked if self.detector.last_dyn_cells_count > 0 else None
        self.planned_path = self.prior_map.plan((float(self.pos_w[0]), float(self.pos_w[1])), self.goal_xy, dynamic_blocked=dyn)
        self.follower = WaypointFollower(self.planned_path, self.nav_speed)
        return self.planned_path

    def step_50hz(self, z_foot: float | None = None, jump_active: bool = False) -> dict:
        self._tick += 1
        if not self.pose_valid:
            return dict(
                vx_cmd=0.0,
                wz_cmd=0.0,
                g_step=EMPTY_NP.copy(),
                g_jump=EMPTY_JUMP_NP.copy(),
                ceiling=float("inf"),
                planned_path=[],
            )
        x, y, yaw = float(self.pos_w[0]), float(self.pos_w[1]), self.yaw
        zf = float(z_foot) if z_foot is not None else (
            float(self.prior_map.sample(x, y)) if self.prior_map is not None else float(self.pos_w[2] - 0.28)
        )
        if not np.isfinite(zf):
            zf = float(self.pos_w[2] - 0.28)

        if not jump_active:
            self.jump_z_ref = None
        elif self.jump_z_ref is None:
            self.jump_z_ref = zf

        # Periodic dynamic-obstacle path check & automatic A* detour
        if (
            self.prior_map is not None
            and self.follower is not None
            and not self.follower.done
            and self.goal_xy is not None
            and self._tick % 8 == 0
        ):
            if self.detector.is_path_blocked(self.planned_path, x, y):
                try:
                    self.planned_path = self.prior_map.plan((x, y), self.goal_xy, dynamic_blocked=self.detector.dyn_blocked)
                    self.follower = WaypointFollower(self.planned_path, self.nav_speed)
                except ValueError:
                    pass

        vx_cmd, wz_cmd = (0.0, 0.0)
        if self.follower is not None and not self.follower.done:
            vx_cmd, wz_cmd = self.follower.command(x, y, yaw)

        g_step, ceiling, _ = self.detector.sample(x, y, yaw, z_foot=zf)
        g_jump = self.detector.sample_jump(x, y, yaw, z_ref=self.jump_z_ref, z_foot=zf)
        return dict(
            vx_cmd=float(vx_cmd),
            wz_cmd=float(wz_cmd),
            g_step=g_step,
            g_jump=g_jump,
            ceiling=float(ceiling),
            planned_path=self.planned_path,
            stair_pts=int(self.detector.last_stair_pts_count),
            dyn_cells=int(self.detector.last_dyn_cells_count),
        )


def run_ros2_node(args) -> None:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped, Twist
    from nav_msgs.msg import Odometry, Path as RosPath
    from sensor_msgs.msg import PointCloud2
    from std_msgs.msg import Bool, Float32, Float32MultiArray

    try:
        from livox_ros_driver2.msg import CustomMsg as LivoxCustomMsg
    except ImportError:
        LivoxCustomMsg = None

    class Mid360Nav4DRosNode(Node):
        def __init__(self):
            super().__init__("mid360_nav4d_node")
            prior = None if args.PriorMap == "none" else args.PriorMap
            self.bridge = Mid360RealRobotBridge(
                prior_map_npz=prior,
                extrinsic_json=args.extrinsic,
                mode="online_pc" if prior is None else "fusion",
                default_nav_speed=args.speed,
            )
            self.jump_active = False
            self.create_subscription(Odometry, args.odom_topic, self.cb_odom, 10)
            if args.custom_msg and LivoxCustomMsg is not None:
                self.create_subscription(LivoxCustomMsg, args.lidar_topic, self.cb_livox_custom, 5)
            else:
                self.create_subscription(PointCloud2, args.lidar_topic, self.cb_pc2, 5)
            self.create_subscription(PoseStamped, "/goal_pose", self.cb_goal, 5)
            self.create_subscription(Bool, "/jump_trigger", self.cb_jump, 5)

            self.pub_cmd = self.create_publisher(Twist, "/nav4d/cmd_vel", 10)
            self.pub_gstep = self.create_publisher(Float32MultiArray, "/nav4d/g_step", 10)
            self.pub_gjump = self.create_publisher(Float32MultiArray, "/nav4d/g_jump", 10)
            self.pub_ceil = self.create_publisher(Float32, "/nav4d/ceiling", 10)
            self.pub_path = self.create_publisher(RosPath, "/nav4d/planned_path", 2)
            self.create_timer(0.02, self.on_timer_50hz)
            self.get_logger().info(f"Mid-360 Nav4D ROS2 Node started (prior={prior}, lidar={args.lidar_topic})")

        def cb_odom(self, msg: Odometry):
            p = msg.pose.pose.position
            q = msg.pose.pose.orientation
            self.bridge.update_odometry(np.array([p.x, p.y, p.z]), np.array([q.w, q.x, q.y, q.z]))

        def cb_pc2(self, msg: PointCloud2):
            self.bridge.ingest_mid360_cloud(pointcloud2_to_xyz(msg))

        def cb_livox_custom(self, msg):
            self.bridge.ingest_mid360_cloud(livox_custom_msg_to_xyz(msg))

        def cb_goal(self, msg: PoseStamped):
            gx, gy = float(msg.pose.position.x), float(msg.pose.position.y)
            path = self.bridge.set_goal(gx, gy)
            ros_path = RosPath()
            ros_path.header = msg.header
            for px, py in path:
                ps = PoseStamped()
                ps.header = msg.header
                ps.pose.position.x = px
                ps.pose.position.y = py
                ros_path.poses.append(ps)
            self.pub_path.publish(ros_path)

        def cb_jump(self, msg: Bool):
            self.jump_active = bool(msg.data)

        def on_timer_50hz(self):
            out = self.bridge.step_50hz(jump_active=self.jump_active)
            tw = Twist()
            tw.linear.x = out["vx_cmd"]
            tw.angular.z = out["wz_cmd"]
            self.pub_cmd.publish(tw)
            ms = Float32MultiArray(data=[float(v) for v in out["g_step"]])
            mj_msg = Float32MultiArray(data=[float(v) for v in out["g_jump"]])
            self.pub_gstep.publish(ms)
            self.pub_gjump.publish(mj_msg)
            self.pub_ceil.publish(Float32(data=float(out["ceiling"])))

    rclpy.init()
    node = Mid360Nav4DRosNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ROS 2 Livox Mid-360 + FAST-LIO2 Nav4D Stair/Jump Perception Node")
    p.add_argument("--prior-map", dest="PriorMap", default="mid360:suite_rmul2027", help="Prior map key/path or 'none'")
    p.add_argument("--extrinsic", default=str(DEFAULT_EXTRINSIC_PATH), help="Path to mid360_extrinsic.json")
    p.add_argument("--lidar-topic", default="/livox/lidar", help="Mid-360 point cloud topic")
    p.add_argument("--odom-topic", default="/Odometry", help="FAST-LIO2 / Point-LIO 6-DoF odometry topic")
    p.add_argument("--custom-msg", action="store_true", help="Subscribe to livox_ros_driver2/msg/CustomMsg")
    p.add_argument("--speed", type=float, default=1.10, help="Default autonomous navigation speed (m/s)")
    run_ros2_node(p.parse_args())
