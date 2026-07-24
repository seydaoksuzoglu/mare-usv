"""
Parkur-1 waypoint yukleyici: mavros_msgs/srv/WaypointPush servisini (/mavros/mission/push) cagirarak config/*.yaml icindeki waypoint dizisini araca basar.

Tek sorumluluk: yukleme. Mode AUTO'ya gecis ve arm etme bu node'un sorumlulugu DEGILDIR (Sprint 0'daki sitl_cmd_vel_bridge_node'da benimsenen
ayni ilke) -- elle ros2 service call ile yapilir. Bir kere calisip sonucu loglayan, spin etmeyen tek-seferlik bir script'tir.
"""

import os

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from mavros_msgs.msg import Waypoint
from mavros_msgs.srv import WaypointPush
from rclpy.node import Node


class WaypointLoaderNode(Node):

    def __init__(self):
        super().__init__('waypoint_loader_node')

        default_path = os.path.join(
            get_package_share_directory('mare_mission'),
            'config', 'parkur1_waypoints.yaml',
        )
        self.declare_parameter('waypoint_file', default_path)
        waypoint_file = self.get_parameter('waypoint_file').value

        waypoints = self._load_waypoints(waypoint_file)

        self._client = self.create_client(WaypointPush, '/mavros/mission/push')
        if not self._client.wait_for_service(timeout_sec=10.0):
            self.get_logger().error(
                '/mavros/mission/push servisi bulunamadi (MAVROS calisiyor mu?)')
            return

        request = WaypointPush.Request()
        request.start_index = 0
        request.waypoints = waypoints

        future = self._client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=15.0)

        if future.result() is None:
            self.get_logger().error('WaypointPush servis cagrisi zaman asimina ugradi.')
            return

        response = future.result()
        self.get_logger().info(
            f'WaypointPush sonucu: success={response.success}, '
            f'wp_transfered={response.wp_transfered} '
            f'(yuklenen dosya: {waypoint_file})'
        )

    @staticmethod
    def _load_waypoints(path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        waypoints = []
        for wp in data['waypoints']:
            waypoints.append(Waypoint(
                frame=wp['frame'],
                command=wp['command'],
                is_current=wp['is_current'],
                autocontinue=wp['autocontinue'],
                param1=float(wp['param1']),
                param2=float(wp['param2']),
                param3=float(wp['param3']),
                param4=float(wp['param4']),
                x_lat=float(wp['lat']),
                y_long=float(wp['lon']),
                z_alt=float(wp['alt']),
            ))
        return waypoints


def main(args=None):
    rclpy.init(args=args)
    node = WaypointLoaderNode()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()