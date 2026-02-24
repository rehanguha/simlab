"""
Result object.

Contains simulation results and provides methods for accessing and manipulating them.
"""

import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

class Result:
    """Simulation result object."""
    
    def __init__(
        self,
        data: pd.DataFrame,
        summary: Dict[str, Any],
        config: Dict[str, Any],
        output_manager: Optional['OutputManager'] = None
    ):
        """
        Initialize result object.
        
        Args:
            data (pd.DataFrame): Simulation trajectory data
            summary (dict): Summary statistics
            config (dict): Configuration used
            output_manager (OutputManager): Output manager for saving
        """
        self.data = data
        self.summary = summary
        self.config = config
        self.output_manager = output_manager
    
    @property
    def time(self) -> pd.Series:
        """Get time series."""
        return self.data['time']
    
    @property
    def height(self) -> pd.Series:
        """Get height series."""
        return self.data['z']
    
    @property
    def velocity(self) -> pd.Series:
        """Get velocity magnitude series."""
        return self.data['speed']
    
    @property
    def velocity_xyz(self) -> pd.DataFrame:
        """Get velocity components."""
        return self.data[['vx', 'vy', 'vz']]
    
    @property
    def position_xyz(self) -> pd.DataFrame:
        """Get position components."""
        return self.data[['x', 'y', 'z']]
    
    @property
    def flight_time(self) -> float:
        """Get flight time."""
        return self.summary['flight_time']
    
    @property
    def max_height(self) -> float:
        """Get maximum height."""
        return self.summary['max_height']
    
    @property
    def horizontal_range(self) -> float:
        """Get horizontal range."""
        return self.summary['horizontal_range']
    
    @property
    def max_velocity(self) -> float:
        """Get maximum velocity."""
        return self.summary['max_velocity']
    
    @property
    def bounce_count(self) -> int:
        """Get number of ground contacts."""
        return self.summary['ground_contacts']
    
    @property
    def is_stable(self) -> bool:
        """Check if simulation is stable."""
        return self.summary['is_stable']
    
    @property
    def energy_conserved(self) -> bool:
        """Check if energy is conserved."""
        return self.summary['energy_conserved']
    
    def at_time(self, time: float) -> pd.Series:
        """
        Get data at specific time.
        
        Args:
            time (float): Time value
            
        Returns:
            pd.Series: Data at specified time
        """
        idx = (self.data['time'] - time).abs().idxmin()
        return self.data.loc[idx]
    
    def interpolate(self, time: float) -> pd.Series:
        """
        Interpolate data at specific time.
        
        Args:
            time (float): Time value
            
        Returns:
            pd.Series: Interpolated data
        """
        # Simple linear interpolation
        t = self.data['time']
        idx = t.searchsorted(time)
        
        if idx == 0:
            return self.data.iloc[0]
        elif idx >= len(self.data):
            return self.data.iloc[-1]
        
        # Linear interpolation
        t0, t1 = t.iloc[idx-1], t.iloc[idx]
        weight = (time - t0) / (t1 - t0)
        
        row0 = self.data.iloc[idx-1]
        row1 = self.data.iloc[idx]
        
        interpolated = row0 * (1 - weight) + row1 * weight
        interpolated['time'] = time
        
        return interpolated
    
    def save(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Save all outputs.
        
        Args:
            output_dir (str): Output directory
            
        Returns:
            dict: Dictionary of saved file paths
        """
        if self.output_manager is None:
            from .manager import OutputManager
            self.output_manager = OutputManager(output_dir)
        
        self.output_manager.save_all(self)
        return self.output_manager.get_output_files()
    
    def plot_height(self, save: Optional[str] = None, show: bool = True) -> None:
        """
        Plot height vs time.
        
        Args:
            save (str): File path to save plot
            show (bool): Whether to display plot
        """
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.data['time'], self.data['z'], 'b-', linewidth=2)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Height (m)')
        ax.set_title('Height vs Time')
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        
        plt.close()
    
    def plot_velocity(self, save: Optional[str] = None, show: bool = True) -> None:
        """
        Plot velocity components vs time.
        
        Args:
            save (str): File path to save plot
            show (bool): Whether to display plot
        """
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.data['time'], self.data['vx'], 'r-', label='Vx', linewidth=2)
        ax.plot(self.data['time'], self.data['vy'], 'g-', label='Vy', linewidth=2)
        ax.plot(self.data['time'], self.data['vz'], 'b-', label='Vz', linewidth=2)
        ax.plot(self.data['time'], self.data['speed'], 'k-', label='Speed', linewidth=2)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Velocity Components vs Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        
        plt.close()
    
    def plot_trajectory_2d(self, save: Optional[str] = None, show: bool = True) -> None:
        """
        Plot 2D trajectory.
        
        Args:
            save (str): File path to save plot
            show (bool): Whether to display plot
        """
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.data['x'], self.data['z'], 'b-', linewidth=2)
        ax.set_xlabel('Horizontal Distance (m)')
        ax.set_ylabel('Height (m)')
        ax.set_title('2D Trajectory')
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        
        plt.close()
    
    def plot_trajectory_3d(self, save: Optional[str] = None, show: bool = True) -> None:
        """
        Plot 3D trajectory.
        
        Args:
            save (str): File path to save plot
            show (bool): Whether to display plot
        """
        import matplotlib.pyplot as plt
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(self.data['x'], self.data['y'], self.data['z'], 'b-', linewidth=2)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('3D Trajectory')
        
        if save:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        
        plt.close()
    
    def save_plots(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Save all plots.
        
        Args:
            output_dir (str): Output directory
            
        Returns:
            dict: Dictionary of saved plot file paths
        """
        if output_dir is None:
            output_dir = self.output_manager.output_dir / "plots" if self.output_manager else Path("plots")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Save height plot
        height_file = output_dir / "height_vs_time.png"
        self.plot_height(save=str(height_file), show=False)
        files['height'] = str(height_file)
        
        # Save velocity plot
        velocity_file = output_dir / "velocity_vs_time.png"
        self.plot_velocity(save=str(velocity_file), show=False)
        files['velocity'] = str(velocity_file)
        
        # Save 2D trajectory
        trajectory_2d_file = output_dir / "2d_trajectory.png"
        self.plot_trajectory_2d(save=str(trajectory_2d_file), show=False)
        files['trajectory_2d'] = str(trajectory_2d_file)
        
        # Save 3D trajectory
        trajectory_3d_file = output_dir / "3d_trajectory.png"
        self.plot_trajectory_3d(save=str(trajectory_3d_file), show=False)
        files['trajectory_3d'] = str(trajectory_3d_file)
        
        return files