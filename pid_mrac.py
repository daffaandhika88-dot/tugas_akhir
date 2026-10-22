import numpy as np

class PIDMRAC:
    '''
    PID Model Reference Adaptive Controller (MRAC) class
    Modified for ROS path following application
    '''
    def __init__(self):
        # Initial PID parameters (adaptive)
        self.p = [1.0, 1.0]  # Compatible with existing structure [kp_min, kp_max]
        self.i = [0.1, 0.1]  # Compatible with existing structure [ki_min, ki_max]  
        self.d = [0.01, 0.01]  # Compatible with existing structure [kd_min, kd_max]
        
        # Current adaptive parameters
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.01
        
        # Error tracking
        self.error_bef = 0
        self.error_accum = 0
        
        # MRAC specific variables
        self.tracking_error = 0
        self.tracking_error_bef = 0
        self.tracking_error_accum = 0
        self.reference_output = 0
        self.plant_output = 0
        
        # Adaptation gains (gamma values)
        self.gamma_p = 0.1  # Proportional adaptation gain
        self.gamma_i = 0.01  # Integral adaptation gain
        self.gamma_d = 0.001  # Derivative adaptation gain
        
        # Reference model parameters (first order for simplicity in path following)
        self.tau_ref = 1.0  # Reference model time constant
        self.ref_state = 0  # Reference model state
        
        # Bounds for control output
        self.lower_bound = -np.pi/2
        self.upper_bound = np.pi/2
        
        # Bounds for error accumulation
        self.accum_lower_bound = -10.0
        self.accum_upper_bound = 10.0
        
        # Bounds for adaptive gains
        self.kp_min, self.kp_max = 0.01, 5.0
        self.ki_min, self.ki_max = 0.001, 1.0
        self.kd_min, self.kd_max = 0.0001, 0.5
        
        # Clamping functions
        self.clamp = lambda x: max(min(x, self.upper_bound), self.lower_bound)
        self.clamp_accum = lambda x: max(min(x, self.accum_upper_bound), self.accum_lower_bound)
        self.clamp_kp = lambda x: max(min(x, self.kp_max), self.kp_min)
        self.clamp_ki = lambda x: max(min(x, self.ki_max), self.ki_min)
        self.clamp_kd = lambda x: max(min(x, self.kd_max), self.kd_min)
        
        # Sampling time
        self.dt = 0.1  # Default sampling time for marine applications
        
        # Performance tracking
        self.adaptation_active = True
        self.performance_history = []
        
    def set_reference_model_params(self, tau_ref: float):
        '''
        param
        tau_ref: float - Reference model time constant
        description
        Set reference model parameters (first order system)
        '''
        self.tau_ref = tau_ref
        
    def set_adaptation_gains(self, gamma_p: float, gamma_i: float, gamma_d: float):
        '''
        param
        gamma_p: float - Proportional adaptation gain
        gamma_i: float - Integral adaptation gain  
        gamma_d: float - Derivative adaptation gain
        description
        Set MRAC adaptation gains
        '''
        self.gamma_p = gamma_p
        self.gamma_i = gamma_i
        self.gamma_d = gamma_d
        
    def set_sampling_time(self, dt: float):
        '''
        param
        dt: float - Sampling time
        description
        Set sampling time for discrete implementation
        '''
        self.dt = dt
        
    def reset(self):
        '''
        description
        Reset PID MRAC controller states
        '''
        self.error_bef = 0
        self.error_accum = 0
        self.tracking_error = 0
        self.tracking_error_bef = 0
        self.tracking_error_accum = 0
        self.ref_state = 0
        
        # Reset adaptive gains to initial values
        self.kp = self.p[0] if isinstance(self.p, list) else self.p
        self.ki = self.i[0] if isinstance(self.i, list) else self.i
        self.kd = self.d[0] if isinstance(self.d, list) else self.d
        
    def reference_model(self, reference_input: float) -> float:
        '''
        param
        reference_input: float - Desired reference input
        return
        float - Reference model output
        description
        First-order reference model: G_m(s) = 1 / (tau_ref*s + 1)
        '''
        # First-order system: tau*x_dot + x = u
        # x_dot = (-x + u) / tau
        x_dot = (-self.ref_state + reference_input) / self.tau_ref
        
        # Euler integration
        self.ref_state += x_dot * self.dt
        
        self.reference_output = self.ref_state
        return self.reference_output
        
    def adapt_parameters(self, current_error: float):
        '''
        param
        current_error: float - Current control error
        description
        MIT rule for parameter adaptation based on tracking error
        '''
        if not self.adaptation_active:
            return
            
        # Calculate sensitivity derivatives (simplified for path following)
        sensitivity_p = current_error  # ∂e/∂kp ≈ current error
        sensitivity_i = self.error_accum  # ∂e/∂ki ≈ accumulated error
        sensitivity_d = (current_error - self.error_bef) / self.dt if self.dt > 0 else 0  # ∂e/∂kd
        
        # MIT adaptation rule: θ_dot = -γ * e_t * (∂e/∂θ)
        # Use tracking error for adaptation
        kp_dot = -self.gamma_p * self.tracking_error * sensitivity_p
        ki_dot = -self.gamma_i * self.tracking_error * sensitivity_i
        kd_dot = -self.gamma_d * self.tracking_error * sensitivity_d
        
        # Update parameters with smaller step size for stability
        adaptation_rate = 0.1  # Reduce adaptation speed for marine applications
        self.kp += kp_dot * self.dt * adaptation_rate
        self.ki += ki_dot * self.dt * adaptation_rate
        self.kd += kd_dot * self.dt * adaptation_rate
        
        # Apply bounds
        self.kp = self.clamp_kp(self.kp)
        self.ki = self.clamp_ki(self.ki)
        self.kd = self.clamp_kd(self.kd)
        
        # Update p, i, d arrays for compatibility
        if isinstance(self.p, list):
            self.p = [self.kp, self.kp]
        else:
            self.p = self.kp
            
        if isinstance(self.i, list):
            self.i = [self.ki, self.ki]
        else:
            self.i = self.ki
            
        if isinstance(self.d, list):
            self.d = [self.kd, self.kd]
        else:
            self.d = self.kd
        
    def update(self, err: float) -> float:
        '''
        param
        err: float - Control error (setpoint - current_value)
        return
        float - Control signal
        description
        Update PID MRAC controller - compatible with existing interface
        '''
        # Generate reference model output (assume setpoint is 0 for regulation)
        reference_output = self.reference_model(0.0)  # Reference model tracks zero error
        
        # Estimate plant output (simplified - use filtered error)
        alpha = 0.1  # Low-pass filter coefficient
        self.plant_output = alpha * err + (1 - alpha) * self.plant_output
        
        # Calculate tracking error (difference between reference model and estimated plant)
        self.tracking_error = reference_output - self.plant_output
        
        # Accumulate error with clamping
        self.error_accum += err
        self.error_accum = self.clamp_accum(self.error_accum)
        
        # Adapt PID parameters based on tracking error
        self.adapt_parameters(err)
        
        # Calculate PID control signal with adapted parameters
        derivative_term = (err - self.error_bef) / self.dt if self.dt > 0 else 0
        pid_output = (self.kp * err + 
                     self.ki * self.error_accum + 
                     self.kd * derivative_term)
        
        # Apply output bounds
        control_signal = self.clamp(pid_output)
        
        # Update previous values
        self.error_bef = err
        self.tracking_error_bef = self.tracking_error
        
        # Store performance metrics
        performance = abs(self.tracking_error) + abs(err)
        self.performance_history.append(performance)
        if len(self.performance_history) > 100:  # Keep last 100 samples
            self.performance_history.pop(0)
        
        return control_signal
        
    def get_parameters(self) -> dict:
        '''
        return
        dict - Current PID parameters and states
        description
        Get current controller parameters and states for monitoring
        '''
        avg_performance = np.mean(self.performance_history) if self.performance_history else 0
        return {
            'kp': self.kp,
            'ki': self.ki,
            'kd': self.kd,
            'tracking_error': self.tracking_error,
            'reference_output': self.reference_output,
            'plant_output': self.plant_output,
            'control_error': self.error_bef,
            'avg_performance': avg_performance,
            'adaptation_active': self.adaptation_active
        }
        
    def set_bounds(self, lower: float, upper: float):
        '''
        param
        lower: float - Lower bound for control output
        upper: float - Upper bound for control output
        description
        Set output bounds for control signal
        '''
        self.lower_bound = lower
        self.upper_bound = upper
        self.clamp = lambda x: max(min(x, self.upper_bound), self.lower_bound)
        
    def enable_adaptation(self, enable: bool = True):
        '''
        param
        enable: bool - Enable/disable parameter adaptation
        description
        Enable or disable adaptive behavior
        '''
        self.adaptation_active = enable
        
    def set_pid_bounds(self, kp_bounds: list, ki_bounds: list, kd_bounds: list):
        '''
        param
        kp_bounds: list - [min, max] bounds for Kp
        ki_bounds: list - [min, max] bounds for Ki  
        kd_bounds: list - [min, max] bounds for Kd
        description
        Set bounds for adaptive PID parameters
        '''
        self.kp_min, self.kp_max = kp_bounds
        self.ki_min, self.ki_max = ki_bounds
        self.kd_min, self.kd_max = kd_bounds
        
        # Update clamping functions
        self.clamp_kp = lambda x: max(min(x, self.kp_max), self.kp_min)
        self.clamp_ki = lambda x: max(min(x, self.ki_max), self.ki_min)
        self.clamp_kd = lambda x: max(min(x, self.kd_max), self.kd_min)