from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mare_bringup',
            executable='walking_skeleton_node',
            name='walking_skeleton_node',
            output='screen',
            parameters=[{
                'linear_x': 0.3,
                'angular_z': 0.0,
                'publish_rate_hz': 10.0,
            }],
        ),
    ])