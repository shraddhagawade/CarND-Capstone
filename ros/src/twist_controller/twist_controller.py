import rospy
from yaw_controller import YawController
from pid import PID
from lowpass import LowPassFilter

GAS_DENSITY = 2.858
ONE_MPH = 0.44704

class Controller(object):
    def __init__(self, vehicle_mass, fuel_capacity, brake_deadband, decel_limit, accel_limit, 
	                                wheel_radius, wheel_base, steer_ratio, max_lat_accel, max_steer_angle):
        # TODO: Implement
		self.yaw_controller = YawController(wheel_base, steer_ratio, 0.1, max_lat_accel, max_steer_angle) # min_speed = 0.1
		kp = 0.3
		ki = 0.1
		kd = 0.
		mn = 0.
		mx = 0.2
		self.throttle_controller = PID(kp, ki, kd, mn, mx)
        
        tau = 0.5
		ts = 0.02
		self.vel_lpf = LowPassFilter(tau, ts)
		
		self.last_velocity = None
		self.last_time = rospy.get_time()
		
    def control(self, current_velocity, dbw_enabled, linear_velocity, angular_velocity):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
		
		if not dbw_enabled:
		    self.throttle_controller.reset()
		    return 0.,0.,0.
			
		current_velocity = self.vel_lpf.filt(current_velocity)
		
		steering = self.yaw_controller.get_steering(linear_velocity, angular_velocity, current_velocity)
		
		velocity_error = linear_velocity - current_velocity
		self.last_velocity = current_velocity
		
		current_time = rospy.get_time()
		elapsed_time = current_time - self.last_time
		self.last_time = current_time
		
		throttle = self.throttle_controller.step(velocity_error, elapsed_time)
		
		brake = 0
		
		if linear_velocity == 0. and current_velocity <0.1:
		    throttle = 0
			brake = 700
			
		elif throttle < 0.1 and vel_error < 0:
		    throttle = 0
			decel = max(vel_error, self.decel_limit)
			brake = abs(decel)*self.vehicle_mass*self.wheel_radius
		
        return throttle, brake, steering
