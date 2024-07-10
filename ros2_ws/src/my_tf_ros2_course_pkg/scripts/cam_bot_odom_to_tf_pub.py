#! /usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, DurabilityPolicy, QoSProfile
import tf2_ros
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry


class CamBotOdomToTF(Node):

    def __init__(self, robot_base_frame="camera_bot_base_link"):
        super().__init__('odom_to_tf_broadcaster_node')

        self._robot_base_frame = robot_base_frame
        
        # Create a new `TransformStamped` object.
        # A `TransformStamped` object is a ROS message that represents a transformation between two frames.
        self.transform_stamped = TransformStamped()
        # This line sets the `header.frame_id` attribute of the `TransformStamped` object.
        # The `header.frame_id` attribute specifies the frame in which the transformation is defined.
        # In this case, the transformation is defined in the `world` frame.
        self.transform_stamped.header.frame_id = "world"
        # This line sets the `child_frame_id` attribute of the `TransformStamped` object.
        # The `child_frame_id` attribute specifies the frame that is being transformed to.
        # In this case, the robot's base frame is being transformed to the `world` frame.
        self.transform_stamped.child_frame_id = self._robot_base_frame

        self.subscriber = self.create_subscription(
            Odometry,
            '/cam_bot_odom',
            self.odom_callback,
            QoSProfile(depth=1, durability=DurabilityPolicy.VOLATILE, reliability=ReliabilityPolicy.BEST_EFFORT))

        # This line creates a new `TransformBroadcaster` object.
        # A `TransformBroadcaster` object is a ROS node that publishes TF messages.
        self.br = tf2_ros.TransformBroadcaster(self)

        self.get_logger().info("odom_to_tf_broadcaster_node ready!")

    def odom_callback(self, msg):
        self.cam_bot_odom = msg
        # print the log info in the terminal
        self.get_logger().debug('Odom VALUE: "%s"' % str(self.cam_bot_odom))
        self.broadcast_new_tf()

    def broadcast_new_tf(self):
        """
        This function broadcasts a new TF message to the TF network.
        """

        # Get the current odometry data.
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # Set the timestamp of the TF message.
        # The timestamp of the TF message is set to the current time.
        self.transform_stamped.header.stamp = self.get_clock().now().to_msg()

        # Set the translation of the TF message.
        # The translation of the TF message is set to the current position of the robot.
        self.transform_stamped.transform.translation.x = position.x
        self.transform_stamped.transform.translation.y = position.y
        self.transform_stamped.transform.translation.z = position.z

        # Set the rotation of the TF message.
        # The rotation of the TF message is set to the current orientation of the robot.
        self.transform_stamped.transform.rotation.x = orientation.x
        self.transform_stamped.transform.rotation.y = orientation.y
        self.transform_stamped.transform.rotation.z = orientation.z
        self.transform_stamped.transform.rotation.w = orientation.w

        # Send (broadcast) the TF message.
        self.br.sendTransform(self.transform_stamped)


def main(args=None):

    rclpy.init()
    odom_to_tf_obj = CamBotOdomToTF()
    rclpy.spin(odom_to_tf_obj)

if __name__ == '__main__':
    main()