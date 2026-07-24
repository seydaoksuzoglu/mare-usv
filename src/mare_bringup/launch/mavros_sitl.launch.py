"""
Bu dosya, MAVROS'u (Ardupilot/apm plugin listesiyle) başlatır ve `/mavros/local_position/odom` çıktısını
launch-time remap ile `/odometry/filtered` adına bağlar. Ayrı bir relay/republish node'u YOK — MAVROS'un 
kendisi doğrudan `/odometry/filtered` üzerine yayın yapıyor gibi davranır.

Faz 2: MAVROS(Ardupilot/apm) + /odometry/filtered remap.

Karar: robot_localization eklenmiyor, ArduPilot EKF3 ciktisi
(/mavros/local_position/odom) launch-time remap ile /odometry/filtered
adini aliyor. Ileride gercek bir ekf_node eklenirse bu remap kaldirilip
yerine EKF'in yayini konur; downstream node'lar degismez.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    fcu_url_arg = DeclareLaunchArgument(
        'fcu_url',
        default_value='udp://127.0.0.1:14550@',
        description=(
            'MAVROS FCU baglanti adresi. Sprint 0da SITL icin kullanilan '
            'degerle AYNI tutulmali (ros2 launch mavros apm.launch fcu_url:=... '
            'ile elle baslattiginiz deger).'
        ),
    )

    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        namespace='mavros',
        output='screen',
        parameters=[
            PathJoinSubstitution(
                [FindPackageShare('mavros'), 'launch', 'apm_pluginlists.yaml']
            ),
            PathJoinSubstitution(
                [FindPackageShare('mavros'), 'launch', 'apm_config.yaml']
            ),
            {
                'fcu_url': LaunchConfiguration('fcu_url'),
                'gcs_url': '',
                'tgt_system': 1,
                'tgt_component': 1,
                'fcu_protocol': 'v2.0',
            },
        ],
        remappings=[
            ('/mavros/local_position/odom', '/odometry/filtered'),
        ],
    )

    return LaunchDescription([
        fcu_url_arg,
        mavros_node,
    ])

