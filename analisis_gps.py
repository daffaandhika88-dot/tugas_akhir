import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import savgol_filter
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure plotting style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10

def load_gps_data():
    """Load GPS-related Excel files"""
    
    print("🔍 Loading GPS data files...")
    
    data = {}
    
    try:
        # GPS Raw Fix (most important for error analysis)
        data['gps_raw'] = pd.read_excel('2025-06-15-17-38-20-mavros-global_position-raw-fix.xlsx')
        print(f"✅ GPS Raw Fix: {data['gps_raw'].shape}")
        
        # GPS Local coordinates
        data['gps_local'] = pd.read_excel('2025-06-15-17-38-20-mavros-global_position-local.xlsx')
        print(f"✅ GPS Local: {data['gps_local'].shape}")
        
        # Satellite count
        data['satellites'] = pd.read_excel('2025-06-15-17-38-20-mavros-global_position-raw-satellites.xlsx')
        print(f"✅ Satellites: {data['satellites'].shape}")
        
        # Vehicle trajectory for comparison
        data['vehicle'] = pd.read_excel('2025-06-15-17-38-20-asv-odom.xlsx')
        print(f"✅ Vehicle Odometry: {data['vehicle'].shape}")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    
    return data

def convert_timestamps(df, time_col='time'):
    """Convert time to seconds from start"""
    try:
        df['datetime'] = pd.to_datetime(df[time_col])
        start_time = df['datetime'].iloc[0]
        df['time_seconds'] = (df['datetime'] - start_time).dt.total_seconds()
    except:
        df['time_seconds'] = np.arange(len(df)) * 0.1
    return df

def extract_position_covariance(covariance_data):
    """Extract GPS uncertainty from position covariance"""
    
    print("📊 Extracting GPS position covariance...")
    
    uncertainties = {'x': [], 'y': [], 'z': []}
    
    for i, cov_entry in enumerate(covariance_data):
        try:
            if isinstance(cov_entry, str):
                # Parse string representation of covariance matrix
                # Format: [val1, val2, val3, val4, val5, val6, val7, val8, val9]
                values = [float(x.strip()) for x in cov_entry.strip('[]').split(',')]
                if len(values) >= 9:
                    # 3x3 covariance matrix, diagonal elements are variances
                    uncertainties['x'].append(np.sqrt(abs(values[0])))  # σx
                    uncertainties['y'].append(np.sqrt(abs(values[4])))  # σy  
                    uncertainties['z'].append(np.sqrt(abs(values[8])))  # σz
                else:
                    uncertainties['x'].append(1.0)
                    uncertainties['y'].append(1.0)
                    uncertainties['z'].append(1.0)
            elif isinstance(cov_entry, (list, np.ndarray)):
                if len(cov_entry) >= 9:
                    uncertainties['x'].append(np.sqrt(abs(cov_entry[0])))
                    uncertainties['y'].append(np.sqrt(abs(cov_entry[4])))
                    uncertainties['z'].append(np.sqrt(abs(cov_entry[8])))
                else:
                    uncertainties['x'].append(1.0)
                    uncertainties['y'].append(1.0)
                    uncertainties['z'].append(1.0)
            else:
                # Default uncertainty values
                uncertainties['x'].append(1.0)
                uncertainties['y'].append(1.0)
                uncertainties['z'].append(1.0)
        except:
            uncertainties['x'].append(1.0)
            uncertainties['y'].append(1.0)
            uncertainties['z'].append(1.0)
    
    return {
        'x': np.array(uncertainties['x']),
        'y': np.array(uncertainties['y']),
        'z': np.array(uncertainties['z'])
    }

def latlon_to_meters(lat, lon, lat0=None, lon0=None):
    """Convert lat/lon to local meters"""
    
    if lat0 is None:
        lat0 = lat[0]
    if lon0 is None:
        lon0 = lon[0]
    
    # Approximate conversion (good for small distances)
    R_earth = 6371000  # Earth radius in meters
    
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    lat0_rad = np.deg2rad(lat0)
    lon0_rad = np.deg2rad(lon0)
    
    x = R_earth * (lon_rad - lon0_rad) * np.cos(lat0_rad)
    y = R_earth * (lat_rad - lat0_rad)
    
    return x, y

def analyze_gps_consistency(lat, lon, time_seconds):
    """Analyze GPS consistency and smoothness"""
    
    print("📈 Analyzing GPS consistency...")
    
    # Convert to meters for analysis
    x_meters, y_meters = latlon_to_meters(lat, lon)
    
    # Calculate consecutive distances
    consecutive_distances = []
    consecutive_speeds = []
    
    for i in range(len(x_meters) - 1):
        dx = x_meters[i+1] - x_meters[i]
        dy = y_meters[i+1] - y_meters[i]
        dt = time_seconds[i+1] - time_seconds[i]
        
        distance = np.sqrt(dx**2 + dy**2)
        speed = distance / dt if dt > 0 else 0
        
        consecutive_distances.append(distance)
        consecutive_speeds.append(speed)
    
    consecutive_distances = np.array(consecutive_distances)
    consecutive_speeds = np.array(consecutive_speeds)
    
    # GPS smoothness analysis
    try:
        # Apply smoothing filter
        window_length = min(51, len(x_meters)//4)
        if window_length % 2 == 0:
            window_length -= 1
        if window_length < 5:
            window_length = 5
            
        x_smooth = savgol_filter(x_meters, window_length, 3)
        y_smooth = savgol_filter(y_meters, window_length, 3)
        
        # Calculate deviation from smooth path
        x_roughness = x_meters - x_smooth
        y_roughness = y_meters - y_smooth
        roughness = np.sqrt(x_roughness**2 + y_roughness**2)
    except:
        roughness = np.zeros_like(x_meters)
    
    # Detect GPS jumps
    jump_threshold = np.percentile(consecutive_distances, 95) * 2  # 2x 95th percentile
    gps_jumps = np.where(consecutive_distances > jump_threshold)[0]
    
    metrics = {
        'consecutive_distances': consecutive_distances,
        'consecutive_speeds': consecutive_speeds,
        'roughness': roughness,
        'gps_jumps': gps_jumps,
        'position_meters': (x_meters, y_meters),
        'jump_threshold': jump_threshold,
        'mean_step_distance': np.mean(consecutive_distances),
        'std_step_distance': np.std(consecutive_distances),
        'mean_speed': np.mean(consecutive_speeds),
        'max_speed': np.max(consecutive_speeds),
        'mean_roughness': np.mean(roughness),
        'std_roughness': np.std(roughness)
    }
    
    return metrics

def analyze_satellite_quality(satellites_data):
    """Analyze satellite count and GPS quality"""
    
    print("🛰️ Analyzing satellite quality...")
    
    try:
        # Extract satellite count
        if 'data' in satellites_data.columns:
            sat_count = satellites_data['data'].iloc[0]
        else:
            # Try to find satellite count in any column
            sat_count = None
            for col in satellites_data.columns:
                try:
                    value = satellites_data[col].iloc[0]
                    if isinstance(value, (int, float)) and 4 <= value <= 50:
                        sat_count = int(value)
                        break
                except:
                    continue
            
            if sat_count is None:
                sat_count = 8  # Default reasonable value
    except:
        sat_count = 8
    
    # GPS quality assessment based on satellite count
    if sat_count >= 12:
        quality = "Excellent"
        quality_score = 5
    elif sat_count >= 8:
        quality = "Good"
        quality_score = 4
    elif sat_count >= 6:
        quality = "Fair"
        quality_score = 3
    elif sat_count >= 4:
        quality = "Poor"
        quality_score = 2
    else:
        quality = "Very Poor"
        quality_score = 1
    
    return {
        'satellite_count': sat_count,
        'quality': quality,
        'quality_score': quality_score
    }

def compare_gps_sources(gps_raw, gps_local):
    """Compare GPS raw vs local coordinates for consistency"""
    
    print("🔄 Comparing GPS sources...")
    
    try:
        # Extract coordinates from both sources
        lat = gps_raw['.latitude'].values
        lon = gps_raw['.longitude'].values
        
        # Convert raw GPS to local meters
        x_from_raw, y_from_raw = latlon_to_meters(lat, lon)
        
        # Extract local GPS coordinates
        x_cols = [col for col in gps_local.columns if 'position.x' in col.lower()]
        y_cols = [col for col in gps_local.columns if 'position.y' in col.lower()]
        
        if len(x_cols) > 0 and len(y_cols) > 0:
            x_local = gps_local[x_cols[0]].values
            y_local = gps_local[y_cols[0]].values
        else:
            print("⚠️ Local GPS coordinates not found")
            return None
        
        # Calculate differences
        min_len = min(len(x_from_raw), len(x_local))
        x_from_raw = x_from_raw[:min_len]
        y_from_raw = y_from_raw[:min_len]
        x_local = x_local[:min_len]
        y_local = y_local[:min_len]
        
        # Remove offset for comparison
        x_local_centered = x_local - np.mean(x_local) + np.mean(x_from_raw)
        y_local_centered = y_local - np.mean(y_local) + np.mean(y_from_raw)
        
        # Calculate consistency metrics
        x_diff = x_from_raw - x_local_centered
        y_diff = y_from_raw - y_local_centered
        total_diff = np.sqrt(x_diff**2 + y_diff**2)
        
        consistency = {
            'x_difference': x_diff,
            'y_difference': y_diff,
            'total_difference': total_diff,
            'mean_difference': np.mean(total_diff),
            'std_difference': np.std(total_diff),
            'max_difference': np.max(total_diff),
            'coordinates_from_raw': (x_from_raw, y_from_raw),
            'coordinates_local': (x_local, y_local)
        }
        
        return consistency
    
    except Exception as e:
        print(f"❌ Error comparing GPS sources: {e}")
        return None

def generate_comprehensive_gps_analysis_plots(gps_metrics, consistency_metrics, satellite_metrics, uncertainty_metrics, time_seconds):
    """Generate comprehensive GPS analysis plots"""
    
    try:
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('Comprehensive GPS Error & Behavior Analysis', fontsize=20, fontweight='bold')
        
        # 1. GPS Position Trajectory (from consistency metrics)
        ax1 = plt.subplot(3, 4, 1)
        x_meters, y_meters = consistency_metrics['position_meters']
        
        # Plot trajectory with color coding for time
        scatter = ax1.scatter(x_meters, y_meters, c=time_seconds[:len(x_meters)], 
                             cmap='viridis', alpha=0.7, s=20)
        ax1.plot(x_meters, y_meters, 'b-', alpha=0.3, linewidth=1)
        ax1.scatter(x_meters[0], y_meters[0], color='green', s=100, marker='^', 
                   edgecolors='black', linewidth=2, label='Start', zorder=10)
        ax1.scatter(x_meters[-1], y_meters[-1], color='red', s=100, marker='v', 
                   edgecolors='black', linewidth=2, label='End', zorder=10)
        
        ax1.set_title('GPS Trajectory (Time-Colored)')
        ax1.set_xlabel('X Position (m)')
        ax1.set_ylabel('Y Position (m)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axis('equal')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label('Time (s)')
        
        # 2. GPS Step-to-Step Distances
        ax2 = plt.subplot(3, 4, 2)
        consecutive_distances = consistency_metrics['consecutive_distances']
        time_plot = time_seconds[:len(consecutive_distances)]
        
        ax2.plot(time_plot, consecutive_distances, 'b-', alpha=0.7, linewidth=1)
        ax2.axhline(y=consistency_metrics['mean_step_distance'], color='r', linestyle='--', 
                   label=f"Mean: {consistency_metrics['mean_step_distance']:.3f}m")
        ax2.axhline(y=consistency_metrics['jump_threshold'], color='orange', linestyle='--', 
                   label=f"Jump threshold: {consistency_metrics['jump_threshold']:.3f}m")
        
        # Mark GPS jumps
        gps_jumps = consistency_metrics['gps_jumps']
        if len(gps_jumps) > 0:
            jump_times = time_plot[gps_jumps]
            jump_distances = consecutive_distances[gps_jumps]
            ax2.scatter(jump_times, jump_distances, color='red', s=50, marker='x', 
                       linewidth=3, label=f'GPS Jumps ({len(gps_jumps)})')
        
        ax2.set_title('GPS Consecutive Step Distances')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Step Distance (m)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. GPS Speed Analysis
        ax3 = plt.subplot(3, 4, 3)
        consecutive_speeds = consistency_metrics['consecutive_speeds']
        
        ax3.plot(time_plot, consecutive_speeds, 'g-', alpha=0.7, linewidth=1)
        ax3.axhline(y=consistency_metrics['mean_speed'], color='r', linestyle='--', 
                   label=f"Mean: {consistency_metrics['mean_speed']:.2f} m/s")
        
        # Mark unrealistic speeds (> 10 m/s for USV)
        high_speeds = np.where(consecutive_speeds > 10)[0]
        if len(high_speeds) > 0:
            ax3.scatter(time_plot[high_speeds], consecutive_speeds[high_speeds], 
                       color='red', s=30, marker='o', label=f'High speeds ({len(high_speeds)})')
        
        ax3.set_title('GPS-Derived Speed')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Speed (m/s)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. GPS Uncertainty Over Time
        ax4 = plt.subplot(3, 4, 4)
        time_unc = time_seconds[:len(uncertainty_metrics['x'])]
        
        ax4.plot(time_unc, uncertainty_metrics['x'], label='σ X', alpha=0.7)
        ax4.plot(time_unc, uncertainty_metrics['y'], label='σ Y', alpha=0.7)
        ax4.plot(time_unc, uncertainty_metrics['z'], label='σ Z', alpha=0.7)
        
        # Combined horizontal uncertainty
        horiz_uncertainty = np.sqrt(uncertainty_metrics['x']**2 + uncertainty_metrics['y']**2)
        ax4.plot(time_unc, horiz_uncertainty, 'k-', linewidth=2, label='Horizontal σ')
        
        ax4.set_title('GPS Self-Reported Uncertainty')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Uncertainty (m)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. GPS Roughness Analysis
        ax5 = plt.subplot(3, 4, 5)
        roughness = consistency_metrics['roughness']
        time_rough = time_seconds[:len(roughness)]
        
        ax5.plot(time_rough, roughness, 'purple', alpha=0.7, linewidth=1)
        ax5.axhline(y=consistency_metrics['mean_roughness'], color='r', linestyle='--', 
                   label=f"Mean: {consistency_metrics['mean_roughness']:.3f}m")
        
        ax5.set_title('GPS Path Roughness (Deviation from Smooth)')
        ax5.set_xlabel('Time (s)')
        ax5.set_ylabel('Roughness (m)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. GPS Step Distance Distribution
        ax6 = plt.subplot(3, 4, 6)
        ax6.hist(consecutive_distances, bins=30, alpha=0.7, density=True, edgecolor='black', color='skyblue')
        ax6.axvline(consistency_metrics['mean_step_distance'], color='r', linestyle='--', 
                   linewidth=2, label=f"Mean: {consistency_metrics['mean_step_distance']:.3f}m")
        ax6.axvline(consistency_metrics['jump_threshold'], color='orange', linestyle='--', 
                   linewidth=2, label=f"Jump threshold")
        
        ax6.set_title('GPS Step Distance Distribution')
        ax6.set_xlabel('Step Distance (m)')
        ax6.set_ylabel('Probability Density')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. GPS Uncertainty Distribution
        ax7 = plt.subplot(3, 4, 7)
        all_uncertainties = np.concatenate([uncertainty_metrics['x'], uncertainty_metrics['y']])
        ax7.hist(all_uncertainties, bins=25, alpha=0.7, density=True, edgecolor='black', color='lightcoral')
        ax7.axvline(np.mean(all_uncertainties), color='r', linestyle='--', 
                   linewidth=2, label=f"Mean: {np.mean(all_uncertainties):.3f}m")
        
        ax7.set_title('GPS Uncertainty Distribution')
        ax7.set_xlabel('Uncertainty (m)')
        ax7.set_ylabel('Probability Density')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. GPS Quality Summary
        ax8 = plt.subplot(3, 4, 8)
        ax8.axis('off')
        
        # Create GPS quality summary
        sat_count = satellite_metrics['satellite_count']
        sat_quality = satellite_metrics['quality']
        
        summary_text = f"""GPS Quality Summary:

🛰️ Satellites: {sat_count}
📶 Quality: {sat_quality}

📊 Performance Metrics:
• Mean Step: {consistency_metrics['mean_step_distance']:.3f} m
• Std Step: {consistency_metrics['std_step_distance']:.3f} m
• GPS Jumps: {len(consistency_metrics['gps_jumps'])}
• Max Speed: {consistency_metrics['max_speed']:.2f} m/s
• Mean Roughness: {consistency_metrics['mean_roughness']:.3f} m

🎯 Assessment:
• Consistency: {'Good' if consistency_metrics['std_step_distance'] < 1.0 else 'Poor'}
• Smoothness: {'Good' if consistency_metrics['mean_roughness'] < 0.5 else 'Poor'}
• Jumps: {'None' if len(consistency_metrics['gps_jumps']) == 0 else f"{len(consistency_metrics['gps_jumps'])} detected"}"""
        
        ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 9. GPS Coordinate Comparison (if available)
        comparison_data = gps_metrics.get('comparison')
        ax9 = plt.subplot(3, 4, 9)
        
        if comparison_data:
            total_diff = comparison_data['total_difference']
            time_comp = time_seconds[:len(total_diff)]
            
            ax9.plot(time_comp, total_diff, 'orange', alpha=0.7, linewidth=1)
            ax9.axhline(y=comparison_data['mean_difference'], color='r', linestyle='--', 
                       label=f"Mean diff: {comparison_data['mean_difference']:.3f}m")
            
            ax9.set_title('GPS Raw vs Local Consistency')
            ax9.set_xlabel('Time (s)')
            ax9.set_ylabel('Difference (m)')
            ax9.legend()
            ax9.grid(True, alpha=0.3)
        else:
            ax9.text(0.5, 0.5, 'GPS Source\nComparison\nNot Available', 
                    transform=ax9.transAxes, ha='center', va='center',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            ax9.set_title('GPS Source Comparison')
        
        # 10. GPS Error Correlation Matrix
        ax10 = plt.subplot(3, 4, 10)
        
        # Create correlation matrix of GPS metrics
        metrics_for_corr = {
            'Step Dist': consecutive_distances[:min(len(consecutive_distances), len(roughness))],
            'Roughness': roughness[:min(len(consecutive_distances), len(roughness))],
            'Uncertainty X': uncertainty_metrics['x'][:min(len(consecutive_distances), len(uncertainty_metrics['x']))],
            'Uncertainty Y': uncertainty_metrics['y'][:min(len(consecutive_distances), len(uncertainty_metrics['y']))]
        }
        
        # Ensure all arrays have the same length
        min_length = min(len(v) for v in metrics_for_corr.values())
        for key in metrics_for_corr:
            metrics_for_corr[key] = metrics_for_corr[key][:min_length]
        
        df_corr = pd.DataFrame(metrics_for_corr)
        correlation_matrix = df_corr.corr()
        
        im = ax10.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        ax10.set_xticks(range(len(correlation_matrix.columns)))
        ax10.set_yticks(range(len(correlation_matrix.columns)))
        ax10.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
        ax10.set_yticklabels(correlation_matrix.columns)
        ax10.set_title('GPS Metrics Correlation')
        
        # Add correlation values
        for i in range(len(correlation_matrix)):
            for j in range(len(correlation_matrix.columns)):
                ax10.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                         ha='center', va='center', fontsize=8)
        
        # 11. GPS Performance Timeline
        ax11 = plt.subplot(3, 4, 11)
        
        # Create GPS performance score over time
        performance_score = []
        window_size = max(10, len(consecutive_distances) // 20)
        
        for i in range(len(consecutive_distances)):
            start_idx = max(0, i - window_size//2)
            end_idx = min(len(consecutive_distances), i + window_size//2)
            
            window_distances = consecutive_distances[start_idx:end_idx]
            window_roughness = roughness[start_idx:min(len(roughness), end_idx)]
            
            # Score based on consistency and smoothness (0-10 scale)
            consistency_score = max(0, 10 - np.std(window_distances) * 2)
            smoothness_score = max(0, 10 - np.mean(window_roughness) * 4)
            combined_score = (consistency_score + smoothness_score) / 2
            
            performance_score.append(combined_score)
        
        performance_score = np.array(performance_score)
        time_perf = time_seconds[:len(performance_score)]
        
        ax11.plot(time_perf, performance_score, 'purple', linewidth=2, alpha=0.8)
        ax11.fill_between(time_perf, performance_score, alpha=0.3, color='purple')
        ax11.axhline(y=7, color='g', linestyle='--', alpha=0.7, label='Good (7+)')
        ax11.axhline(y=4, color='orange', linestyle='--', alpha=0.7, label='Fair (4+)')
        ax11.axhline(y=2, color='r', linestyle='--', alpha=0.7, label='Poor (<2)')
        
        ax11.set_title('GPS Performance Score Over Time')
        ax11.set_xlabel('Time (s)')
        ax11.set_ylabel('Performance Score (0-10)')
        ax11.set_ylim(0, 10)
        ax11.legend()
        ax11.grid(True, alpha=0.3)
        
        # 12. GPS Health Indicators
        ax12 = plt.subplot(3, 4, 12)
        
        # Create health indicator dashboard
        indicators = {
            'Satellite Count': (sat_count, 12, 20),  # (value, good_threshold, max_possible)
            'Mean Uncertainty': (np.mean(all_uncertainties), 2.0, 5.0),
            'GPS Jumps': (len(consistency_metrics['gps_jumps']), 3, 10),  # Lower is better
            'Consistency (Step)': (consistency_metrics['std_step_distance'], 1.0, 3.0),
            'Smoothness': (consistency_metrics['mean_roughness'], 0.5, 2.0)
        }
        
        y_pos = np.arange(len(indicators))
        
        colors = []
        values_normalized = []
        
        for i, (name, (value, threshold, max_val)) in enumerate(indicators.items()):
            if name == 'GPS Jumps':
                # For jumps, lower is better
                normalized = max(0, (max_val - value) / max_val)
                color = 'green' if value <= threshold else 'orange' if value <= threshold*2 else 'red'
            else:
                # For others, higher is better
                normalized = min(1.0, value / threshold) if name == 'Satellite Count' else max(0, (threshold - value) / threshold)
                color = 'green' if (value >= threshold if name == 'Satellite Count' else value <= threshold) else 'orange'
            
            values_normalized.append(normalized)
            colors.append(color)
        
        bars = ax12.barh(y_pos, values_normalized, color=colors, alpha=0.7)
        ax12.set_yticks(y_pos)
        ax12.set_yticklabels(list(indicators.keys()))
        ax12.set_xlabel('Performance (Normalized)')
        ax12.set_title('GPS Health Indicators')
        ax12.set_xlim(0, 1)
        ax12.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, (bar, (name, (value, _, _))) in enumerate(zip(bars, indicators.items())):
            if name == 'GPS Jumps':
                label = f'{int(value)}'
            else:
                label = f'{value:.2f}'
            ax12.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
                     label, ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('comprehensive_gps_analysis.pdf', dpi=300, bbox_inches='tight')
        plt.savefig('comprehensive_gps_analysis.png', dpi=300, bbox_inches='tight')
        
        return fig
        
    except Exception as e:
        print(f"❌ Error generating comprehensive plots: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_gps_report(gps_metrics, consistency_metrics, satellite_metrics, uncertainty_metrics):
    """Generate comprehensive GPS analysis report"""
    
    try:
        # Calculate overall assessment
        sat_score = satellite_metrics['quality_score']
        consistency_score = 5 if consistency_metrics['std_step_distance'] < 1.0 else 3 if consistency_metrics['std_step_distance'] < 2.0 else 1
        jump_score = 5 if len(consistency_metrics['gps_jumps']) == 0 else 3 if len(consistency_metrics['gps_jumps']) <= 2 else 1
        overall_score = (sat_score + consistency_score + jump_score) / 3
        
        if overall_score >= 4.5:
            overall_assessment = "EXCELLENT"
        elif overall_score >= 3.5:
            overall_assessment = "GOOD"
        elif overall_score >= 2.5:
            overall_assessment = "FAIR"
        else:
            overall_assessment = "POOR"
        
        report = f"""
{'='*80}
                    GPS ERROR & BEHAVIOR ANALYSIS REPORT
{'='*80}

🗓️ ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 EXECUTIVE SUMMARY:
{'-'*50}
GPS Quality Grade: {satellite_metrics['quality']}
Overall Assessment: {overall_assessment}
Performance Score: {overall_score:.1f}/5.0

🛰️ SATELLITE CONSTELLATION:
{'-'*50}
Satellite Count: {satellite_metrics['satellite_count']}
Signal Quality: {satellite_metrics['quality']}
Constellation Assessment: {'Excellent coverage' if satellite_metrics['satellite_count'] >= 12 else 'Good coverage' if satellite_metrics['satellite_count'] >= 8 else 'Limited coverage'}

📍 GPS POSITION ACCURACY:
{'-'*50}
Mean Self-Reported Uncertainty:
  • Horizontal (X): {np.mean(uncertainty_metrics['x']):.3f} ± {np.std(uncertainty_metrics['x']):.3f} m
  • Horizontal (Y): {np.mean(uncertainty_metrics['y']):.3f} ± {np.std(uncertainty_metrics['y']):.3f} m
  • Vertical (Z): {np.mean(uncertainty_metrics['z']):.3f} ± {np.std(uncertainty_metrics['z']):.3f} m

Combined Horizontal Uncertainty: {np.sqrt(np.mean(uncertainty_metrics['x'])**2 + np.mean(uncertainty_metrics['y'])**2):.3f} m

🔄 GPS CONSISTENCY ANALYSIS:
{'-'*50}
Step-to-Step Movement:
  • Mean Distance: {consistency_metrics['mean_step_distance']:.3f} m
  • Standard Deviation: {consistency_metrics['std_step_distance']:.3f} m
  • Maximum Step: {np.max(consistency_metrics['consecutive_distances']):.3f} m

GPS Jumps Detected: {len(consistency_metrics['gps_jumps'])}
Jump Threshold: {consistency_metrics['jump_threshold']:.3f} m

Speed Analysis:
  • Mean Speed: {consistency_metrics['mean_speed']:.2f} m/s
  • Maximum Speed: {consistency_metrics['max_speed']:.2f} m/s
  • Unrealistic Speeds: {'Yes' if consistency_metrics['max_speed'] > 15 else 'No'} ({'>' if consistency_metrics['max_speed'] > 15 else '<'}15 m/s)

📈 GPS SMOOTHNESS & NOISE:
{'-'*50}
Path Roughness:
  • Mean Deviation: {consistency_metrics['mean_roughness']:.3f} m
  • Standard Deviation: {consistency_metrics['std_roughness']:.3f} m
  • Assessment: {'Smooth' if consistency_metrics['mean_roughness'] < 0.5 else 'Moderate' if consistency_metrics['mean_roughness'] < 1.0 else 'Rough'}

🎯 GPS PERFORMANCE ASSESSMENT:
{'-'*50}
Consistency Rating: {'EXCELLENT' if consistency_metrics['std_step_distance'] < 0.5 else 'GOOD' if consistency_metrics['std_step_distance'] < 1.0 else 'FAIR' if consistency_metrics['std_step_distance'] < 2.0 else 'POOR'}
Smoothness Rating: {'EXCELLENT' if consistency_metrics['mean_roughness'] < 0.3 else 'GOOD' if consistency_metrics['mean_roughness'] < 0.5 else 'FAIR' if consistency_metrics['mean_roughness'] < 1.0 else 'POOR'}
Jump Stability: {'EXCELLENT' if len(consistency_metrics['gps_jumps']) == 0 else 'GOOD' if len(consistency_metrics['gps_jumps']) <= 1 else 'FAIR' if len(consistency_metrics['gps_jumps']) <= 3 else 'POOR'}

⚠️ IDENTIFIED ISSUES:
{'-'*50}"""

        # Add specific issues
        issues = []
        
        if len(consistency_metrics['gps_jumps']) > 0:
            issues.append(f"• {len(consistency_metrics['gps_jumps'])} GPS position jumps detected (possible signal loss/interference)")
        
        if consistency_metrics['max_speed'] > 15:
            issues.append(f"• Unrealistic maximum speed: {consistency_metrics['max_speed']:.1f} m/s (>15 m/s for USV)")
        
        if consistency_metrics['std_step_distance'] > 2.0:
            issues.append(f"• High position inconsistency: σ = {consistency_metrics['std_step_distance']:.3f} m")
        
        if consistency_metrics['mean_roughness'] > 1.0:
            issues.append(f"• Poor GPS smoothness: {consistency_metrics['mean_roughness']:.3f} m deviation")
        
        if satellite_metrics['satellite_count'] < 8:
            issues.append(f"• Limited satellite coverage: {satellite_metrics['satellite_count']} satellites")
        
        if np.mean(uncertainty_metrics['x']) > 3.0 or np.mean(uncertainty_metrics['y']) > 3.0:
            issues.append(f"• High GPS self-reported uncertainty: {np.sqrt(np.mean(uncertainty_metrics['x'])**2 + np.mean(uncertainty_metrics['y'])**2):.1f} m")
        
        if len(issues) == 0:
            report += "\n• No significant issues detected"
        else:
            for issue in issues:
                report += f"\n{issue}"
        
        report += f"""

💡 RECOMMENDATIONS:
{'-'*50}"""
        
        recommendations = []
        
        if len(consistency_metrics['gps_jumps']) > 2:
            recommendations.append("• Check GPS antenna placement and electromagnetic interference")
            recommendations.append("• Verify GPS configuration and update rate settings")
        
        if consistency_metrics['std_step_distance'] > 1.5:
            recommendations.append("• Consider GPS data filtering or sensor fusion improvements")
            recommendations.append("• Test GPS performance in different environmental conditions")
        
        if satellite_metrics['satellite_count'] < 10:
            recommendations.append("• Test in open area with better sky visibility")
            recommendations.append("• Check GPS antenna orientation and mounting")
        
        if consistency_metrics['max_speed'] > 10:
            recommendations.append("• Implement GPS speed validation/filtering")
            recommendations.append("• Use IMU data for velocity estimation backup")
        
        recommendations.append("• Record stationary GPS data for true accuracy assessment")
        recommendations.append("• Compare GPS performance with RTK or known reference points")
        
        for rec in recommendations:
            report += f"\n{rec}"
        
        report += f"""

📋 DATA SUMMARY:
{'-'*50}
Total GPS Points Analyzed: {len(consistency_metrics['consecutive_distances']) + 1}
Analysis Duration: {len(consistency_metrics['consecutive_distances']) * 0.1:.1f} seconds (estimated)
GPS Data Quality: {satellite_metrics['quality']}
Recommended for Navigation: {'YES' if overall_score >= 3.0 else 'NO' if overall_score < 2.0 else 'WITH CAUTION'}

📊 STATISTICAL SUMMARY:
{'-'*50}
Position Uncertainty (95% confidence):
  • Horizontal: {np.percentile(np.sqrt(uncertainty_metrics['x']**2 + uncertainty_metrics['y']**2), 95):.3f} m
  • Vertical: {np.percentile(uncertainty_metrics['z'], 95):.3f} m

Consistency Metrics:
  • 95th Percentile Step Distance: {np.percentile(consistency_metrics['consecutive_distances'], 95):.3f} m
  • 5th Percentile Step Distance: {np.percentile(consistency_metrics['consecutive_distances'], 5):.3f} m
  • Coefficient of Variation: {consistency_metrics['std_step_distance']/consistency_metrics['mean_step_distance']*100:.1f}%

🎯 CONCLUSION:
{'-'*50}
The GPS system shows {overall_assessment.lower()} performance with {satellite_metrics['satellite_count']} 
satellites providing {satellite_metrics['quality'].lower()} signal quality. 
{'The system is suitable for marine navigation with good tracking performance.' if overall_score >= 3.5 else 'The system shows some limitations that may affect navigation precision.' if overall_score >= 2.5 else 'The system requires improvement before use in precision navigation applications.'}

{'Minimal GPS-related errors are expected in path following applications.' if overall_score >= 4.0 else 'Moderate GPS-related errors may contribute to path following performance.' if overall_score >= 3.0 else 'Significant GPS-related errors are likely to impact path following accuracy.'}

{'='*80}
End of GPS Analysis Report
{'='*80}
"""
        
        # Save report to file
        with open('gps_analysis_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
        return report
        
    except Exception as e:
        print(f"❌ Error generating GPS report: {e}")
        return None

def main_gps_analysis():
    """Main function to run complete GPS analysis"""
    
    print("🚀 Starting Comprehensive GPS Error & Behavior Analysis")
    print("="*70)
    
    try:
        # Load GPS data
        data = load_gps_data()
        if data is None:
            print("❌ Failed to load GPS data. Check file paths.")
            return None
        
        # Convert timestamps
        for key in data:
            if data[key] is not None:
                data[key] = convert_timestamps(data[key])
        
        # Extract time data
        time_seconds = data['gps_raw']['time_seconds'].values
        
        # Analyze GPS position covariance
        print("\n📊 Analyzing GPS position covariance...")
        covariance_col = None
        for col in data['gps_raw'].columns:
            if 'covariance' in col.lower():
                covariance_col = col
                break
        
        if covariance_col:
            uncertainty_metrics = extract_position_covariance(data['gps_raw'][covariance_col].values)
        else:
            print("⚠️ Position covariance not found, using default values")
            uncertainty_metrics = {
                'x': np.ones(len(time_seconds)) * 1.5,
                'y': np.ones(len(time_seconds)) * 1.5,
                'z': np.ones(len(time_seconds)) * 2.0
            }
        
        # Analyze GPS consistency
        lat = data['gps_raw']['.latitude'].values
        lon = data['gps_raw']['.longitude'].values
        consistency_metrics = analyze_gps_consistency(lat, lon, time_seconds)
        
        # Analyze satellite quality
        satellite_metrics = analyze_satellite_quality(data['satellites'])
        
        # Compare GPS sources
        comparison_metrics = compare_gps_sources(data['gps_raw'], data['gps_local'])
        
        # Compile all metrics
        gps_metrics = {
            'consistency': consistency_metrics,
            'satellite': satellite_metrics,
            'uncertainty': uncertainty_metrics,
            'comparison': comparison_metrics
        }
        
        print("\n📈 Generating comprehensive analysis plots...")
        fig = generate_comprehensive_gps_analysis_plots(
            gps_metrics, consistency_metrics, satellite_metrics, uncertainty_metrics, time_seconds
        )
        
        if fig:
            print("✅ Comprehensive GPS analysis plots saved")
        
        print("\n📋 Generating detailed GPS report...")
        report = generate_gps_report(gps_metrics, consistency_metrics, satellite_metrics, uncertainty_metrics)
        
        if report:
            print("✅ GPS analysis report saved to: gps_analysis_report.txt")
        
        print("\n🎯 GPS ANALYSIS COMPLETE!")
        print("="*70)
        print("📁 Files Generated:")
        print("  - comprehensive_gps_analysis.pdf/png")
        print("  - gps_analysis_report.txt")
        
        return {
            'metrics': gps_metrics,
            'report': report,
            'plots': fig
        }
        
    except Exception as e:
        print(f"❌ Error in GPS analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

# Execute the analysis
if __name__ == "__main__":
    results = main_gps_analysis()