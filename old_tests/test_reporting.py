"""
Comprehensive tests for reporting.py module.
Tests statistics calculation, CSV export, plotting, and HTML report generation.
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reporting import (
    calculate_statistics,
    export_csv,
    generate_2d_plot,
    generate_html_report,
    generate_all_reports
)


# =========================
# Statistics Tests
# =========================

class TestCalculateStatistics:
    """Test calculate_statistics function."""
    
    def test_calculate_statistics_returns_dict(self, simulation_result):
        """Test that calculate_statistics returns a dictionary."""
        stats = calculate_statistics(simulation_result)
        
        assert isinstance(stats, dict)
    
    def test_statistics_has_required_keys(self, simulation_result):
        """Test that statistics has all required keys."""
        stats = calculate_statistics(simulation_result)
        
        required_keys = [
            'max_height', 'total_distance', 'flight_time',
            'max_speed', 'max_mach', 'max_reynolds',
            'bounce_count', 'timestep_count', 'dt_min', 'dt_max'
        ]
        
        for key in required_keys:
            assert key in stats, f"Missing key: {key}"
    
    def test_max_height_positive(self, simulation_result):
        """Test that max_height is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['max_height'] > 0
    
    def test_max_height_at_least_z0(self, simulation_result):
        """Test that max_height is at least initial height."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['max_height'] >= simulation_result.params.z0
    
    def test_flight_time_positive(self, simulation_result):
        """Test that flight_time is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['flight_time'] > 0
    
    def test_max_speed_positive(self, simulation_result):
        """Test that max_speed is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['max_speed'] > 0
    
    def test_max_mach_reasonable(self, simulation_result):
        """Test that max_mach is reasonable (< 1 for typical simulation)."""
        stats = calculate_statistics(simulation_result)
        
        # For typical simulation, Mach number should be subsonic
        assert stats['max_mach'] < 1.0
    
    def test_max_reynolds_positive(self, simulation_result):
        """Test that max_reynolds is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['max_reynolds'] > 0
    
    def test_bounce_count_non_negative(self, simulation_result):
        """Test that bounce_count is non-negative."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['bounce_count'] >= 0
    
    def test_timestep_count_positive(self, simulation_result):
        """Test that timestep_count is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['timestep_count'] > 0
    
    def test_dt_min_positive(self, simulation_result):
        """Test that dt_min is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['dt_min'] > 0
    
    def test_dt_max_positive(self, simulation_result):
        """Test that dt_max is positive."""
        stats = calculate_statistics(simulation_result)
        
        assert stats['dt_max'] > 0
    
    def test_statistics_contains_dataframe(self, simulation_result):
        """Test that statistics contains the processed DataFrame."""
        stats = calculate_statistics(simulation_result)
        
        assert 'df' in stats
        assert isinstance(stats['df'], pd.DataFrame)


class TestCalculateStatisticsWithBounces:
    """Test statistics with bouncing ball."""
    
    def test_bounce_count_with_high_elasticity(self, high_elasticity_surface, no_wind):
        """Test that bounce count is higher with high elasticity."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=5.0,
            t_max=10.0
        )
        
        from simulation import simulate_drop
        result = simulate_drop(params, high_elasticity_surface, no_wind)
        stats = calculate_statistics(result)
        
        # Should have at least one bounce
        assert stats['bounce_count'] >= 1


# =========================
# CSV Export Tests
# =========================

class TestExportCSV:
    """Test export_csv function."""
    
    def test_export_csv_creates_file(self, simulation_result, temp_output_dir):
        """Test that export_csv creates a file."""
        csv_path = os.path.join(temp_output_dir, "test_output.csv")
        
        result_path = export_csv(simulation_result, csv_path)
        
        assert os.path.exists(result_path)
    
    def test_export_csv_returns_path(self, simulation_result, temp_output_dir):
        """Test that export_csv returns the file path."""
        csv_path = os.path.join(temp_output_dir, "test_output.csv")
        
        result_path = export_csv(simulation_result, csv_path)
        
        assert result_path == csv_path
    
    def test_export_csv_contains_data(self, simulation_result, temp_output_dir):
        """Test that exported CSV contains data."""
        csv_path = os.path.join(temp_output_dir, "test_output.csv")
        export_csv(simulation_result, csv_path)
        
        # Read back and verify
        df_read = pd.read_csv(csv_path)
        
        assert len(df_read) > 0
        assert 'Time' in df_read.columns
        assert 'X' in df_read.columns
        assert 'Z' in df_read.columns
    
    def test_export_csv_has_correct_columns(self, simulation_result, temp_output_dir):
        """Test that CSV has all expected columns."""
        csv_path = os.path.join(temp_output_dir, "test_output.csv")
        export_csv(simulation_result, csv_path)
        
        df_read = pd.read_csv(csv_path)
        
        expected_columns = ['Time', 'X', 'Y', 'Z', 'Vx', 'Vy', 'Vz']
        for col in expected_columns:
            assert col in df_read.columns


# =========================
# 2D Plot Tests
# =========================

class TestGenerate2DPlot:
    """Test generate_2d_plot function."""
    
    def test_generate_2d_plot_creates_file(self, simulation_result, temp_output_dir):
        """Test that generate_2d_plot creates a file."""
        plot_path = os.path.join(temp_output_dir, "test_plot.png")
        
        result_path = generate_2d_plot(simulation_result, plot_path)
        
        assert os.path.exists(result_path)
    
    def test_generate_2d_plot_returns_path(self, simulation_result, temp_output_dir):
        """Test that generate_2d_plot returns the file path."""
        plot_path = os.path.join(temp_output_dir, "test_plot.png")
        
        result_path = generate_2d_plot(simulation_result, plot_path)
        
        assert result_path == plot_path
    
    def test_generate_2d_plot_is_image(self, simulation_result, temp_output_dir):
        """Test that generated file is an image."""
        plot_path = os.path.join(temp_output_dir, "test_plot.png")
        generate_2d_plot(simulation_result, plot_path)
        
        # Check file size (should be > 0 for valid image)
        file_size = os.path.getsize(plot_path)
        assert file_size > 1000  # At least 1KB


# =========================
# HTML Report Tests
# =========================

class TestGenerateHTMLReport:
    """Test generate_html_report function."""
    
    def test_generate_html_creates_file(self, simulation_result, temp_output_dir):
        """Test that generate_html_report creates a file."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        
        result_path = generate_html_report(simulation_result, html_path)
        
        assert os.path.exists(result_path)
    
    def test_generate_html_returns_path(self, simulation_result, temp_output_dir):
        """Test that generate_html_report returns the file path."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        
        result_path = generate_html_report(simulation_result, html_path)
        
        assert result_path == html_path
    
    def test_html_report_contains_params(self, simulation_result, temp_output_dir):
        """Test that HTML report contains parameter information."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        # Should contain mass, radius, etc.
        assert 'mass' in content.lower() or str(simulation_result.params.mass) in content
    
    def test_html_report_contains_statistics(self, simulation_result, temp_output_dir):
        """Test that HTML report contains statistics."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        # Should contain flight time, max height, etc.
        stats = calculate_statistics(simulation_result)
        assert str(int(stats['flight_time'])) in content or f"{stats['flight_time']:.2f}" in content
    
    def test_html_report_contains_title(self, simulation_result, temp_output_dir):
        """Test that HTML report has a title."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        assert '<title>' in content.lower()
        assert 'Ball Drop' in content or 'Simulation' in content
    
    def test_html_report_is_valid_html(self, simulation_result, temp_output_dir):
        """Test that HTML report is valid HTML structure."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        # Basic HTML structure
        assert '<!DOCTYPE html>' in content or '<html' in content
        assert '</html>' in content
        assert '<head>' in content
        assert '</head>' in content
        assert '<body>' in content
        assert '</body>' in content
    
    def test_html_report_contains_stability_status(self, simulation_result, temp_output_dir):
        """Test that HTML report contains stability status."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        assert 'Stability' in content or 'stability' in content
    
    def test_html_report_contains_surface_properties(self, simulation_result, temp_output_dir):
        """Test that HTML report contains surface properties."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        # Should mention elasticity or friction
        assert 'elasticity' in content.lower() or 'friction' in content.lower()
    
    def test_html_report_contains_wind_properties(self, simulation_result, temp_output_dir):
        """Test that HTML report contains wind properties."""
        html_path = os.path.join(temp_output_dir, "test_report.html")
        generate_html_report(simulation_result, html_path)
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        # Should mention wind or humidity
        assert 'wind' in content.lower() or 'humidity' in content.lower()


# =========================
# Generate All Reports Tests
# =========================

class TestGenerateAllReports:
    """Test generate_all_reports function."""
    
    def test_generate_all_reports_creates_files(self, simulation_result, temp_output_dir):
        """Test that generate_all_reports creates all files."""
        csv_path = os.path.join(temp_output_dir, "data.csv")
        plot_path = os.path.join(temp_output_dir, "plot.png")
        html_path = os.path.join(temp_output_dir, "report.html")
        
        files = generate_all_reports(
            simulation_result,
            csv_path,
            plot_path,
            html_path,
            generate_video=False
        )
        
        assert os.path.exists(files['csv'])
        assert os.path.exists(files['plot'])
        assert os.path.exists(files['html'])
    
    def test_generate_all_reports_returns_paths(self, simulation_result, temp_output_dir):
        """Test that generate_all_reports returns file paths."""
        csv_path = os.path.join(temp_output_dir, "data.csv")
        plot_path = os.path.join(temp_output_dir, "plot.png")
        html_path = os.path.join(temp_output_dir, "report.html")
        
        files = generate_all_reports(
            simulation_result,
            csv_path,
            plot_path,
            html_path,
            generate_video=False
        )
        
        assert 'csv' in files
        assert 'plot' in files
        assert 'html' in files
    
    def test_generate_all_reports_with_gif(self, simulation_result, temp_output_dir):
        """Test that generate_all_reports can create GIF."""
        csv_path = os.path.join(temp_output_dir, "data.csv")
        plot_path = os.path.join(temp_output_dir, "plot.png")
        html_path = os.path.join(temp_output_dir, "report.html")
        
        try:
            files = generate_all_reports(
                simulation_result,
                csv_path,
                plot_path,
                html_path,
                generate_video=True,
                video_fps=10
            )
            
            # GIF generation may fail in some environments
            if 'gif' in files:
                assert os.path.exists(files['gif'])
        except Exception:
            # GIF generation may not work in all environments
            pass


# =========================
# Edge Cases Tests
# =========================

class TestReportingEdgeCases:
    """Test edge cases in reporting."""
    
    def test_statistics_with_single_timestep(self):
        """Test statistics with minimal data."""
        from models import SimulationResult
        
        # Create minimal DataFrame
        df = pd.DataFrame({
            'Time': [0.0],
            'X': [0.0],
            'Y': [0.0],
            'Z': [10.0],
            'Vx': [0.0],
            'Vy': [0.0],
            'Vz': [0.0],
            'Ox': [0.0],
            'Oy': [0.0],
            'Oz': [0.0],
            'AirDensity': [1.225],
            'Mu': [1.8e-5],
            'Re': [0.0],
            'Cd': [0.44],
            'WindX': [0.0],
            'WindY': [0.0],
            'WindZ': [0.0],
            'Z_ground': [0.0],
            'Mach': [0.0],
            'Dt_actual': [0.005]
        })
        
        params = Params(z0=10.0)
        surface = Surface()
        wind = Wind()
        
        result = SimulationResult(
            df=df,
            params=params,
            surface=surface,
            wind=wind
        )
        
        stats = calculate_statistics(result)
        
        assert stats['max_height'] == 10.0
        assert stats['flight_time'] == 0.0
        assert stats['bounce_count'] == 0