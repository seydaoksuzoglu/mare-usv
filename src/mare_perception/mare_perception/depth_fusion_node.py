# mare_perception icine depth_fusion_node (STUB) eklenmesi
"""
Faz 1 STUB: /detections/obb (gercek, detector_node'dan) + sahte derinlik ->
/detections/3d. Gercek ZED2 derinlik verisi gelene kadar fake_depth_m
parametresiyle sabit derinlik kullanilir. Cikis arayuzu (Detection3DArray)
gercek derinlik entegre edildiginde degismeyecek.
"""

import rclpy
from rclpy.node import Node
from vision_msgs.msg import (
    Detection2DArray,
    Detection3D,
    Detection3DArray,
    ObjectHypothesisWithPose,
)


class DepthFusionNode(Node):
    """Faz 1: 2D tespit + sahte derinlik -> 3B konum (Detection3DArray)."""

    def __init__(self):
        super().__init__('depth_fusion_node')

        self.declare_parameter('fake_depth_m', 5.0)
        self.declare_parameter('frame_id', 'camera_link')

        self._subscription = self.create_subscription(
            Detection2DArray, '/detections/obb', self._on_detections, 10)
        self._publisher = self.create_publisher(Detection3DArray, '/detections/position_3d', 10)

        self.get_logger().info(
            f"depth_fusion_node (STUB) basladi: fake_depth_m="
            f"{self.get_parameter('fake_depth_m').value}"
        )

    def _on_detections(self, msg: Detection2DArray):
        fake_depth = self.get_parameter('fake_depth_m').value

        array_msg = Detection3DArray()
        array_msg.header = msg.header
        array_msg.header.frame_id = self.get_parameter('frame_id').value

        for detection_2d in msg.detections:
            detection_3d = Detection3D()
            detection_3d.header = array_msg.header

            hypothesis = ObjectHypothesisWithPose()
            if detection_2d.results:
                hypothesis.hypothesis.class_id = detection_2d.results[0].hypothesis.class_id
                hypothesis.hypothesis.score = detection_2d.results[0].hypothesis.score
            detection_3d.results.append(hypothesis)

            detection_3d.bbox.center.position.x = detection_2d.bbox.center.position.x
            detection_3d.bbox.center.position.y = detection_2d.bbox.center.position.y
            detection_3d.bbox.center.position.z = fake_depth
            detection_3d.bbox.size.x = detection_2d.bbox.size_x
            detection_3d.bbox.size.y = detection_2d.bbox.size_y
            detection_3d.bbox.size.z = 0.0

            array_msg.detections.append(detection_3d)

        self._publisher.publish(array_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DepthFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
