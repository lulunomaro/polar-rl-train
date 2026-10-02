import io
p=r"D:/claude2/fangzhen/sim2sim/wsl/monitor_rm.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("""import rclpy
from geometry_msgs.msg import Twist""","""import rclpy
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist""")
t=t.replace("""rclpy.init()
n = rclpy.create_node("rm_vehicle_monitor")""","""rclpy.init()
n = rclpy.create_node("rm_vehicle_monitor")
BEST = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT,
                  history=HistoryPolicy.KEEP_LAST)""")
t=t.replace('cb("base"), 10)','cb("base"), BEST)')
t=t.replace('cb("contact"), 10)','cb("contact"), BEST)')
t=t.replace('cb("imu"), 10)','cb("imu"), BEST)')
t=t.replace('n.create_subscription(JointState, "/joint_states", cb("joints"), 10)',
            'n.create_subscription(JointState, PREFIX + "/joint_states", cb("joints"), BEST)')
t=t.replace('PREFIX + "/template_ros2_controller/rl_network_input", cb("obs"), 10)',
            'PREFIX + "/template_ros2_controller/rl_network_input", cb("obs"), 10)')
io.open(p,"w",encoding="utf-8",newline="\n").write(t)
print("monitor QoS fixed")
