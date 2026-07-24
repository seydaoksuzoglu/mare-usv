# mare_bringup içine walking_skeketon_node eklenmesi
"""
Faz 0 çıkış kriteri: "sim'de sabit /cmd_vel ile tekne hareket eder" Bu node geçici bir duman testidir. Faz 1+'de gerçek path_planner_node/control_bridge_node gelince
silinecek/launch'tan çıkarılacak. Kural gereği sabit değerler (hız, frekans) hardcode değil, 
ROS 2 parametre olarak tanımlı.
"""
# Neden parametre olarak: İleride hızı değiştirmek  için kod değişikliği/rebuild gerekmesin diye 
#(ros2 run mare_bringup walking_skeleton_node --ros-args -p linear_x:=0.5 ile test edilebilir).

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class WalkingSkeletonNode(Node):
    """Faz 0 duman testi: sabit hizda /cmd_vel yayinlar, sim + SITL zincirini dogrular."""

    def __init__(self):
        super().__init__('walking_skeleton_node')

        self.declare_parameter('linear_x', 0.3)
        self.declare_parameter('angular_z', 0.0)
        self.declare_parameter('publish_rate_hz', 10.0)

        self._linear_x = self.get_parameter('linear_x').value
        self._angular_z = self.get_parameter('angular_z').value
        rate_hz = self.get_parameter('publish_rate_hz').value

        self._publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self._timer = self.create_timer(1.0 / rate_hz, self._publish_cmd)

        self.get_logger().info(
            f'walking_skeleton_node basladi: linear_x={self._linear_x}, '
            f'angular_z={self._angular_z}, rate={rate_hz} Hz'
        )
    
    def _publish_cmd(self):
        msg = Twist()
        msg.linear.x = self._linear_x
        msg.angular.z = self._angular_z
        self._publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WalkingSkeletonNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


