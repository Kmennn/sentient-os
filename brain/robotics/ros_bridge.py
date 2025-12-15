
import logging
import threading
import json
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try importing rclpy
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    Node = object

class RosBridge(Node if ROS_AVAILABLE else object):
    """
    Real ROS2 Bridge.
    Publishes to: /robot/cmd_move, /robot/cmd_grasp
    Subscribes to: /robot/pose
    """
    def __init__(self):
        self.is_mock = not ROS_AVAILABLE
        self.latest_pose = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.connected = False
        self.lock = threading.Lock()
        
        if ROS_AVAILABLE:
            super().__init__('sentient_bridge_v2')
            self._init_ros()
        else:
            logger.info("ROS: rclpy not installed. Using Mock Bridge v2.")
            self.connected = True

    def _init_ros(self):
        try:
            # Publishers
            self.move_pub = self.create_publisher(String, '/robot/cmd_move', 10)
            self.grasp_pub = self.create_publisher(String, '/robot/cmd_grasp', 10)
            
            # Subscribers
            self.pose_sub = self.create_subscription(
                String,
                '/robot/pose',
                self._pose_callback,
                10
            )
            
            # Spin thread
            self.ros_thread = threading.Thread(target=self._spin_ros, daemon=True)
            self.ros_thread.start()
            self.connected = True
            logger.info("ROS: Bridge v2 initialized.")
        except Exception as e:
            logger.error(f"ROS Init Error: {e}")
            self.is_mock = True

    def _spin_ros(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)

    def _pose_callback(self, msg):
        try:
            pose = json.loads(msg.data)
            with self.lock:
                self.latest_pose = pose
        except Exception as e:
            logger.error(f"ROS Pose Parse Error: {e}")

    def get_pose(self) -> Dict[str, float]:
        with self.lock:
            return self.latest_pose.copy()

    def publish_move(self, target: Dict[str, float]) -> bool:
        if self.is_mock:
            logger.info(f"ROS [MOCK]: Move to {target}")
            self.latest_pose = target # Sim instant move
            return True
            
        if not self.connected: return False
        
        msg = String()
        msg.data = json.dumps(target)
        self.move_pub.publish(msg)
        return True

    def publish_grasp(self, release: bool = False) -> bool:
        cmd = "release" if release else "grasp"
        if self.is_mock:
            logger.info(f"ROS [MOCK]: {cmd}")
            return True
            
        if not self.connected: return False
        
        msg = String()
        msg.data = json.dumps({"command": cmd})
        self.grasp_pub.publish(msg)
        return True

    def shutdown(self):
        if ROS_AVAILABLE and self.connected:
            self.destroy_node()
            rclpy.shutdown()

ros_bridge = RosBridge()
