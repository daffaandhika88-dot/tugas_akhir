import sys
import os

# Menambahkan folder utils ke sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

import numpy as np
import rospy
from marker_publisher import MarkerPublisher
from basic_pid import BasicPID
from fuzzy_pid import FuzzyPID
from boat_tf import BoatTF
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Point
from nav_msgs.msg  import Path
from utility import get_angle, rad_to_deg, distance_line_to_point
from pid_mrac import PIDMRAC  # Import our new MRAC controller

class PathFollower:
    def __init__(self) -> None:

        self.objects = []
        
        # Replace FuzzyPID with PIDMRAC
        self.pid_angle = PIDMRAC()
        # Configure angle controller
        self.pid_angle.set_bounds(-np.pi/6, np.pi/6)  # Angle control bounds
        self.pid_angle.set_pid_bounds([0.01, 0.1], [0.001, 0.05], [0.0001, 0.02])  # PID parameter bounds
        self.pid_angle.set_adaptation_gains(0.2, 0.05, 0.01)  # Adaptation gains
        self.pid_angle.set_reference_model_params(0.8)  # Reference model time constant
        self.pid_angle.set_sampling_time(0.1)  # Sampling time
        
        self.pid_distance = PIDMRAC()
        # Configure distance controller  
        self.pid_distance.set_bounds(-1.0, 1.0)  # Distance control bounds
        self.pid_distance.set_pid_bounds([0.2, 1.0], [0.01, 0.2], [0.001, 0.1])  # PID parameter bounds
        self.pid_distance.set_adaptation_gains(0.3, 0.1, 0.02)  # Adaptation gains
        self.pid_distance.set_reference_model_params(1.2)  # Reference model time constant
        self.pid_distance.set_sampling_time(0.1)  # Sampling time

        self.error_angle = 0.0
        self.error_distance = 0.0
        self.path_angle_limit = 60
        self.path_keep_distance = 2.0

        self.main_path = Path()
        self.current_position = NavSatFix()

        self.path_idx = 1
        self.path_idx_before = 0
        self.marker_publisher = MarkerPublisher()
        self.boat_tf = BoatTF()
        
        # MRAC monitoring variables
        self.mrac_log_counter = 0
        self.mrac_log_interval = 50  # Log every 50 updates
        
        # Performance monitoring
        self.performance_window = []
        self.performance_window_size = 20

    def update(self):
        self.boat_tf.listen_TF()
        if not self.boat_tf.is_tf_available:
            return 0
        
        if self.is_arrived_last_WP():
            print("ARRIVED TO LAST WP")
            return 0
        
        if(len(self.main_path.poses) < self.path_idx + 1):
            print("NO WAYPOINT LEFT")
            return 0

        if self.is_arrived_path():
            print("ARRIVED ",self.path_idx)
            self.path_idx += 1
            # Reset controllers when reaching new waypoint
            self.reset_controllers()
        
        self.marker_publisher.set_marker_color()
        self.marker_publisher.publish_marker(self.boat_tf.pos, 
                                             self.main_path.poses[self.path_idx].pose.position, 
                                             self.main_path.poses[self.path_idx - 1].pose.position)
        
        # Calculate path angle and error
        angle_path = get_angle(self.main_path.poses[self.path_idx - 1].pose.position,
                                self.main_path.poses[self.path_idx].pose.position)
        path_error_angle = rad_to_deg(angle_path - self.boat_tf.yaw)

        # Normalize angle error to [-180, 180]
        if ( path_error_angle < -180 ):
            path_error_angle += 360
        elif (path_error_angle > 180):
            path_error_angle -= 360

        # Calculate distance error
        path_error_dist = distance_line_to_point(self.main_path.poses[self.path_idx -1].pose.position, 
                                                 self.main_path.poses[self.path_idx].pose.position, self.boat_tf.pos)
        
        # Handle large distance errors - redirect to previous waypoint
        if path_error_dist > 4:
            path_error_dist = 0
            angle_to_first_wp = get_angle(self.boat_tf.pos,self.main_path.poses[self.path_idx-1].pose.position)
            path_error_angle = rad_to_deg(angle_to_first_wp - self.boat_tf.yaw)
            if ( path_error_angle < -180 ):
                path_error_angle += 360
            elif (path_error_angle > 180):
                path_error_angle -= 360
        
        # Store current errors for monitoring
        self.error_angle = path_error_angle
        self.error_distance = path_error_dist
        
        # Update MRAC controllers
        path_control_angle_out = self.pid_angle.update(path_error_angle)
        path_control_distance_out = self.pid_distance.update(path_error_dist)
        
        # Combine control signals
        result = path_control_angle_out + path_control_distance_out
        
        # Monitor performance and log MRAC parameters
        self.monitor_performance(path_error_angle, path_error_dist)
        
        # Optional: Adaptive tuning based on performance
        self.adaptive_tuning()
        
        # if len(self.objects) > 0:
        #     result2 = self.obstacle_avoidance()
        # if result2 < 0 and result < 0:
        #     result = np.min([result,result2])
        # elif result2 > 0 and result > 0:
        #     result = np.max([result,result2])
        
        return result
    
    def reset_controllers(self):
        '''
        Reset MRAC controllers when reaching new waypoint
        '''
        self.pid_angle.reset()
        self.pid_distance.reset()
        print(f"Controllers reset for waypoint {self.path_idx}")
    
    def monitor_performance(self, angle_error: float, distance_error: float):
        '''
        Monitor MRAC performance and log parameters
        '''
        # Calculate combined error metric
        combined_error = abs(angle_error) + abs(distance_error)
        self.performance_window.append(combined_error)
        
        # Keep window size limited
        if len(self.performance_window) > self.performance_window_size:
            self.performance_window.pop(0)
        
        # Log MRAC parameters periodically
        self.mrac_log_counter += 1
        if self.mrac_log_counter >= self.mrac_log_interval:
            self.log_mrac_status()
            self.mrac_log_counter = 0
    
    def log_mrac_status(self):
        '''
        Log current MRAC parameters and performance
        '''
        angle_params = self.pid_angle.get_parameters()
        distance_params = self.pid_distance.get_parameters()
        
        avg_performance = np.mean(self.performance_window) if self.performance_window else 0
        
        print(f"=== MRAC Status ===")
        print(f"Waypoint: {self.path_idx}/{len(self.main_path.poses)-1}")
        print(f"Angle Controller - Kp: {angle_params['kp']:.4f}, Ki: {angle_params['ki']:.4f}, Kd: {angle_params['kd']:.4f}")
        print(f"Distance Controller - Kp: {distance_params['kp']:.4f}, Ki: {distance_params['ki']:.4f}, Kd: {distance_params['kd']:.4f}")
        print(f"Current Errors - Angle: {self.error_angle:.2f}°, Distance: {self.error_distance:.2f}m")
        print(f"Avg Performance: {avg_performance:.3f}")
        print(f"Tracking Errors - Angle: {angle_params['tracking_error']:.4f}, Distance: {distance_params['tracking_error']:.4f}")
        print("==================")
    
    def adaptive_tuning(self):
        '''
        Adaptive tuning of MRAC parameters based on performance
        '''
        if len(self.performance_window) < self.performance_window_size:
            return
        
        avg_performance = np.mean(self.performance_window)
        performance_trend = np.mean(self.performance_window[-5:]) - np.mean(self.performance_window[:5])
        
        # If performance is degrading, increase adaptation gains
        if performance_trend > 0.1:  # Performance getting worse
            current_gamma_p_angle = self.pid_angle.gamma_p
            current_gamma_p_dist = self.pid_distance.gamma_p
            
            # Increase adaptation gains (but with limits)
            new_gamma_p_angle = min(current_gamma_p_angle * 1.1, 0.5)
            new_gamma_p_dist = min(current_gamma_p_dist * 1.1, 0.5)
            
            self.pid_angle.set_adaptation_gains(new_gamma_p_angle, 
                                               self.pid_angle.gamma_i * 1.05, 
                                               self.pid_angle.gamma_d * 1.05)
            self.pid_distance.set_adaptation_gains(new_gamma_p_dist, 
                                                  self.pid_distance.gamma_i * 1.05, 
                                                  self.pid_distance.gamma_d * 1.05)
        
        # If performance is very good and stable, reduce adaptation gains
        elif avg_performance < 0.5 and abs(performance_trend) < 0.05:
            current_gamma_p_angle = self.pid_angle.gamma_p
            current_gamma_p_dist = self.pid_distance.gamma_p
            
            # Reduce adaptation gains for stability
            new_gamma_p_angle = max(current_gamma_p_angle * 0.95, 0.01)
            new_gamma_p_dist = max(current_gamma_p_dist * 0.95, 0.01)
            
            self.pid_angle.set_adaptation_gains(new_gamma_p_angle, 
                                               self.pid_angle.gamma_i * 0.98, 
                                               self.pid_angle.gamma_d * 0.98)
            self.pid_distance.set_adaptation_gains(new_gamma_p_dist, 
                                                  self.pid_distance.gamma_i * 0.98, 
                                                  self.pid_distance.gamma_d * 0.98)
    
    def is_arrived_path(self):
        if len(self.main_path.poses)-1 < self.path_idx:
            return True
        controlled_path_point = self.main_path.poses[self.path_idx].pose.position
        controlled_path_point_before = self.main_path.poses[self.path_idx - 1].pose.position
        
        angle = rad_to_deg(get_angle(self.boat_tf.pos, controlled_path_point) - get_angle(controlled_path_point_before, controlled_path_point))
        
        delta_x = self.boat_tf.pos.x - controlled_path_point.x
        delta_y = self.boat_tf.pos.y - controlled_path_point.y

        if np.abs(angle) >= 180:
            angle = 360 - np.abs(angle)
        return not(abs(angle) < self.path_angle_limit and pow(delta_x, 2) + pow(delta_y, 2) > pow(self.path_keep_distance,2))
    
    def is_arrived_last_WP(self):
        if self.path_idx >= len(self.main_path.poses)-1:
            if self.is_arrived_path():
                return True
        return False
    
    def get_path_angle(self):
        if len(self.main_path.poses) <= 1:
            print("WARNING NOT ENOUGH WAYPOINTS")
            return

        angle_path = get_angle(self.main_path.poses[self.path_idx - 1].pose.position,
                                        self.main_path.poses[self.path_idx].pose.position)
        return angle_path
    
    def set_path(self, path : Path):
        self.main_path = path
        self.path_idx = 1
        self.path_idx_before = 0
        # Reset controllers for new path
        self.reset_controllers()
        print(f"New path set with {len(path.poses)} waypoints")
    
    def get_mrac_status(self) -> dict:
        '''
        Get comprehensive MRAC status for external monitoring
        '''
        angle_params = self.pid_angle.get_parameters()
        distance_params = self.pid_distance.get_parameters()
        
        return {
            'current_waypoint': self.path_idx,
            'total_waypoints': len(self.main_path.poses),
            'angle_controller': angle_params,
            'distance_controller': distance_params,
            'current_errors': {
                'angle': self.error_angle,
                'distance': self.error_distance
            },
            'avg_performance': np.mean(self.performance_window) if self.performance_window else 0
        }
    
    def enable_mrac_adaptation(self, enable_angle: bool = True, enable_distance: bool = True):
        '''
        Enable/disable MRAC adaptation for angle and distance controllers
        '''
        self.pid_angle.enable_adaptation(enable_angle)
        self.pid_distance.enable_adaptation(enable_distance)
        print(f"MRAC Adaptation - Angle: {'Enabled' if enable_angle else 'Disabled'}, Distance: {'Enabled' if enable_distance else 'Disabled'}")
    
    def tune_mrac_parameters(self, 
                           angle_adaptation_gains: tuple = None,
                           distance_adaptation_gains: tuple = None,
                           angle_pid_bounds: tuple = None,
                           distance_pid_bounds: tuple = None):
        '''
        Fine-tune MRAC parameters during runtime
        '''
        if angle_adaptation_gains:
            self.pid_angle.set_adaptation_gains(*angle_adaptation_gains)
            
        if distance_adaptation_gains:
            self.pid_distance.set_adaptation_gains(*distance_adaptation_gains)
            
        if angle_pid_bounds:
            kp_bounds, ki_bounds, kd_bounds = angle_pid_bounds
            self.pid_angle.set_pid_bounds(kp_bounds, ki_bounds, kd_bounds)
            
        if distance_pid_bounds:
            kp_bounds, ki_bounds, kd_bounds = distance_pid_bounds
            self.pid_distance.set_pid_bounds(kp_bounds, ki_bounds, kd_bounds)
        
        print("MRAC parameters updated")


# Example usage and testing
if __name__ == "__main__":
    # This would typically be run within a ROS node
    path_follower = PathFollower()
    
    # Example configuration
    path_follower.enable_mrac_adaptation(True, True)
    
    # Fine-tuning example
    path_follower.tune_mrac_parameters(
        angle_adaptation_gains=(0.3, 0.1, 0.02),
        distance_adaptation_gains=(0.4, 0.15, 0.03),
        angle_pid_bounds=([0.01, 0.2], [0.001, 0.08], [0.0001, 0.03]),
        distance_pid_bounds=([0.1, 1.5], [0.005, 0.3], [0.001, 0.15])
    )
    
    print("PathFollowerMRAC initialized and configured")