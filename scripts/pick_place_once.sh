#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/lyrical/setup.bash
cd ~/robotics-pick-and-place
source install/setup.bash

controllers="$(ros2 control list_controllers)"
printf '%s\n' "$controllers"

for controller in joint_state_broadcaster arm_controller gripper_controller; do
  if ! grep -Eq "^${controller}[[:space:]].*[[:space:]]active$" <<< "$controllers"; then
    echo "Controller $controller is not active. Start it, then run this script again."
    exit 1
  fi
done

move_arm() {
  ros2 action send_goal /arm_controller/follow_joint_trajectory \
    control_msgs/action/FollowJointTrajectory \
    "{trajectory: {joint_names: ['shoulder_joint', 'elbow_joint'], points: [{positions: [$1, $2], time_from_start: {sec: $3, nanosec: 0}}]}}"
}

move_gripper() {
  ros2 action send_goal /gripper_controller/follow_joint_trajectory \
    control_msgs/action/FollowJointTrajectory \
    "{trajectory: {joint_names: ['left_finger_joint', 'right_finger_joint'], points: [{positions: [$1, $2], time_from_start: {sec: $3, nanosec: 0}}]}}"
}

echo "Opening gripper"
move_gripper 0.0 0.0 2

echo "Moving above block"
move_arm -0.860261 1.585747 3

echo "Moving to grasp pose"
move_arm -0.7818 1.5751 3

echo "Closing gripper"
move_gripper 0.03 0.03 2

echo "Lifting block"
move_arm -0.860261 1.585747 3

echo "Lifting higher"
move_arm -0.8503 1.2900 3

echo "Moving above tray"
move_arm -0.2336 0.2814 4

echo "Lowering to release pose"
move_arm -0.265 0.456 3

echo "Releasing block"
move_gripper 0.0 0.0 2

echo "Retracting above tray"
move_arm -0.2336 0.2814 3

echo "Sequence finished"
EOF