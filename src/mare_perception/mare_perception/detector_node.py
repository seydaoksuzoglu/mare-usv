# mare_perception icine detector_node (STUB) eklenmesi
"""
Faz 1 STUB: gercek YOLO11s modeli gelene kadar sahte 2D tespit yayinlar.
Kameraya (/camera/image_raw) bagli degildir -- VRX/ZED2 entegrasyonu Faz 1
kapsaminda degil. Cikis arayuzu (Detection2DArray / /detections/obb)
gercek modelle degismeyecek sekilde tasarlandi (CLAUDE.md: "arayuz ayni kalacak").
"""

import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


class DetectorNode(Node):
    """Faz 1: sahte OBB tespiti uretip /detections/obb'a yayinlayan STUB node."""

    def __init__(self):
        super().__init__('detector_node')

        self.declare_parameter('publish_rate_hz', 2.0)
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('class_id', 'buoy_orange')
        self.declare_parameter('score', 0.9)
        self.declare_parameter('center_x', 320.0)
        self.declare_parameter('center_y', 240.0)
        self.declare_parameter('size_x', 60.0)
        self.declare_parameter('size_y', 60.0)

        rate_hz = self.get_parameter('publish_rate_hz').value

        self._publisher = self.create_publisher(Detection2DArray, '/detections/obb', 10)
        self._timer = self.create_timer(1.0 / rate_hz, self._publish_detection)

        self.get_logger().info(
            f"detector_node (STUB) basladi: rate={rate_hz} Hz, "
            f"class_id={self.get_parameter('class_id').value}"
        )

    def _publish_detection(self):
        array_msg = Detection2DArray()
        array_msg.header.stamp = self.get_clock().now().to_msg()
        array_msg.header.frame_id = self.get_parameter('frame_id').value

        detection = Detection2D()
        detection.header = array_msg.header

        hypothesis = ObjectHypothesisWithPose()
        hypothesis.hypothesis.class_id = self.get_parameter('class_id').value
        hypothesis.hypothesis.score = self.get_parameter('score').value
        detection.results.append(hypothesis)

        detection.bbox.center.position.x = self.get_parameter('center_x').value
        detection.bbox.center.position.y = self.get_parameter('center_y').value
        detection.bbox.center.theta = 0.0
        detection.bbox.size_x = self.get_parameter('size_x').value
        detection.bbox.size_y = self.get_parameter('size_y').value

        array_msg.detections.append(detection)
        self._publisher.publish(array_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
