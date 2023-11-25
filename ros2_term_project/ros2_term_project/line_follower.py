import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import String  # 추가된 라인
from .line_traker import LineTracker
import cv_bridge


class LineFollower(Node):
    def __init__(self, line_tracker: LineTracker):
        super().__init__('line_follower')
        self.line_tracker = line_tracker
        self.bridge = cv_bridge.CvBridge()
        self._subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self._start_car_subscription = self.create_subscription(String, '/start_car', self.start_car_callback, 10)  
        
        self._publisher = self.create_publisher(Twist, 'cmd_vel', 1)
        self.twist = Twist()
        self.twist.linear.x = 6.0
        self.img = None
        self.active_car = None 

    def image_callback(self, msg: Image):
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.line_tracker.process(img)
        self.twist.angular.z = (-1) * self.line_tracker.delta / 450
        self.get_logger().info('angular.z = %f' % self.twist.angular.z)
        self._publisher.publish(self.twist)

    def start_car_callback(self, msg: String):  # 추가된 함수
        if msg.data in ["PR001", "PR002"]:
            self.active_car = msg.data
            self.get_logger().info('Starting car: %s' % self.active_car)

        else:
            self.get_logger().info('Invalid car name: %s' % msg.data)

    def stop(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        self._publisher.publish(self.twist)

    @property
    def publishers(self):
        return self._publisher


def main():
    rclpy.init()
    tracker = LineTracker()
    follower = LineFollower(tracker)
    try:
        rclpy.spin(follower)
    except KeyboardInterrupt:
        follower.stop()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
