# mare_bringup icine sitl_cmd_vel_bridge_node eklenmesi
"""
Faz 0 duman testi koprusu: /cmd_vel (geometry_msgs/Twist) dinler ve MAVROS'un
GUIDED hiz setpoint topic'ine (/mavros/setpoint_velocity/cmd_vel_unstamped,
tip: geometry_msgs/Twist) oldugu gibi republish eder.

Neden gecici: Faz 2'de gercek
control_bridge_node gelince silinecek. ARM etme ve GUIDED moduna gecis bu node'un
sorumlulugu DEGILDIR (tek sorumluluk kurali) -- Sprint 0'da elle ros2 service call
ile yapilir.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SitlCmdVelBridgeNode(Node):
    """Faz 0: /cmd_vel -> MAVROS setpoint_velocity kopru node'u."""

    def __init__(self):
        super().__init__('sitl_cmd_vel_bridge_node')

        self.declare_parameter('input_topic', '/cmd_vel')
        self.declare_parameter(
            'output_topic', '/mavros/setpoint_velocity/cmd_vel_unstamped')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self._publisher = self.create_publisher(Twist, output_topic, 10)
        self._subscription = self.create_subscription(
            Twist, input_topic, self._on_cmd_vel, 10)

        self.get_logger().info(
            f'sitl_cmd_vel_bridge_node basladi: {input_topic} -> {output_topic}'
        )

    def _on_cmd_vel(self, msg: Twist):
        self._publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SitlCmdVelBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
