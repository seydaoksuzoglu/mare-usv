# ros2 pkg create'in ürettiği placeholder maintainer/description alanları güncellendi.
# config/*.yaml glob'u şu an boş dizine karşılık geldiği için boş liste döner — bu normal, hata vermez; ileride config dosyası eklendiğinde otomatik kurulacak.

import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'mare_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'sim_overlay'), glob('sim_overlay/*.xacro')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='',
    maintainer_email='',
    description='Launch, config ve veri kayit: sistem genel entegrasyon paketi.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'walking_skeleton_node = mare_bringup.walking_skeleton_node:main',
	    'sitl_cmd_vel_bridge_node = mare_bringup.sitl_cmd_vel_bridge_node:main'
        ],
    },
)
