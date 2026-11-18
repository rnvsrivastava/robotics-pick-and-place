import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('pick_place_demo')
    ros_gz_share = get_package_share_directory('ros_gz_sim')

    urdf_file = os.path.join(package_share, 'urdf', 'arm.urdf')
    world_file = os.path.join(package_share, 'worlds', 'pick_place_world.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'{world_file} -r'}.items(),
    )

    robot_description = Command([
        FindExecutable(name='xacro'),
        ' ',
        urdf_file,
    ])

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        output='screen',
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'pick_place_world',
            '-topic', '/robot_description',
            '-name', 'learning_arm',
        ],
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        state_publisher,
        spawn_robot,
    ])