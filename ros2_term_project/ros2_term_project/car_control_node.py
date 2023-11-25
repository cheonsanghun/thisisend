
import rclpy
from std_msgs.msg import String
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
import time


class CarStartNode:

    def __init__(self):
        self.node = rclpy.create_node('car_start_node')

        # "start_car" 토픽을 구독할 콜백 함수 등록
        self.subscriber = self.node.create_subscription(
            String,
            '/start_car',
            self.start_car_callback,
            10
        )

        # Gazebo 모델 상태 설정 서비스 클라이언트 생성
        self.set_model_state_client = self.node.create_client(SetModelState, '/gazebo/set_model_state')

        self.node.get_logger().info("Car Start Node가 준비되었습니다.")

    def start_car_callback(self, msg):
        # 수신된 메시지의 데이터 확인
        car_name = msg.data

        # "PR001" 또는 "PR002"가 아니면 경고를 기록하고 함수 종료
        if car_name not in ["PR001", "PR002"]:
            self.node.get_logger().warn(f"잘못된 차량 이름: {car_name}")
            return

        # 모델 상태를 설정하여 차량 이동 시작
        self.set_model_state(car_name, start=True)

        # 추가적인 이동 속도, 차선 이탈, 정지선 감지 등의 로직
        # (여기에 구현)

    def set_model_state(self, car_name, start=True):
        # 모델 상태를 설정하기 위한 서비스 요청 객체 생성
        req = SetModelState.Request()
        req.model_state.model_name = car_name
        req.model_state.reference_frame = 'world'
        req.model_state.pose.position.z = 0.2  # 필요시 높이 조절

        if start:
            # 시작 위치로 초기화
            req.model_state.pose.position.x = 0
            req.model_state.pose.position.y = 0
        else:
            # 정지 위치로 설정 (상황에 따라 조절)
            req.model_state.pose.position.x = 10
            req.model_state.pose.position.y = 10

        try:
            # Gazebo 내의 모델 상태를 설정하는 서비스 호출
            future = self.set_model_state_client.call_async(req)
            rclpy.spin_until_future_complete(self.node, future)
            response = future.result()
            if response.success:
                self.node.get_logger().info(f"{car_name} 이동 시작 성공.")
            else:
                self.node.get_logger().error(f"{car_name} 이동 시작 실패.")
        except Exception as e:
            self.node.get_logger().error(f"서비스 호출 실패: {str(e)}")


def main():
    rclpy.init()
    car_start_node = CarStartNode()
    rclpy.spin(car_start_node.node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
