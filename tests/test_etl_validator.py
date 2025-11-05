"""
Tests for ETL Validator.

Validates ETL validation framework functionality.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.etl_validator import ETLValidator

class TestETLValidator:
    """Test ETL validation functionality."""
    
    def setup_method(self):
        """Initialize validator for each test."""
        self.validator = ETLValidator()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame."""
        return pd.DataFrame({
            'nombre_asesor': ['Juan Pérez', 'Maria Garcia', 'Pedro Lopez'],
            'telefono': ['3001234567', '6012345678', '3109876543'],
            'tipo_venta': ['TU MASCOTA', 'TU HOGAR', 'TU VEHICULO'],
            'fecha_venta': pd.to_datetime(['2025-11-01', '2025-11-02', '2025-11-03'])
        })
    
    def test_validate_load_success(self, sample_df):
        """Test successful load validation."""
        result = self.validator.validate_load(
            df=sample_df,
            file_name='test_file',
            expected_columns=['nombre_asesor', 'telefono'],
            min_records=2
        )
        
        assert result.passed is True
        assert result.stage == 'LOAD'
        assert result.details['records_loaded'] == 3
    
    def test_validate_load_empty_df(self):
        """Test load validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result = self.validator.validate_load(
            df=empty_df,
            file_name='empty_file',
            min_records=1
        )
        
        assert result.passed is False
        assert result.severity == 'CRITICAL'
    
    def test_validate_load_missing_columns(self, sample_df):
        """Test load validation with missing columns."""
        result = self.validator.validate_load(
            df=sample_df,
            file_name='test_file',
            expected_columns=['nombre_asesor', 'columna_inexistente'],
            min_records=1
        )
        
        # Should have recorded missing column
        assert 'columna_inexistente' in result.details.get('missing_columns', [])
    
    def test_validate_transform_success(self, sample_df):
        """Test successful transformation validation."""
        # Simulate transformation (remove 1 record)
        df_after = sample_df.iloc[:-1].copy()
        
        result = self.validator.validate_transform(
            df_before=sample_df,
            df_after=df_after,
            transform_name='test_transform',
            min_retention=60.0,
            max_retention=100.0
        )
        
        assert result.passed is True
        assert result.details['delta'] == -1
        assert '66.7%' in result.details['retention_rate']  # 2/3 = 66.7%
    
    def test_validate_transform_low_retention(self, sample_df):
        """Test transformation with too low retention."""
        # Remove 2 records (only 33% retention)
        df_after = sample_df.iloc[:1].copy()
        
        result = self.validator.validate_transform(
            df_before=sample_df,
            df_after=df_after,
            transform_name='test_transform',
            min_retention=50.0,  # Expect 50%+
            max_retention=100.0
        )
        
        # Should fail due to low retention
        assert result.passed is False
        assert result.severity == 'WARNING'
    
    def test_validate_data_quality_success(self, sample_df):
        """Test data quality validation success."""
        result = self.validator.validate_data_quality(
            df=sample_df,
            stage_name='test_quality',
            max_null_rate=0.50,
            max_duplicate_rate=0.50
        )
        
        assert result.passed is True
        assert result.stage == 'QUALITY'
    
    def test_validate_data_quality_high_nulls(self):
        """Test data quality with high null rate."""
        df_nulls = pd.DataFrame({
            'col1': [1, None, None, None, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        result = self.validator.validate_data_quality(
            df=df_nulls,
            stage_name='test_nulls',
            max_null_rate=0.30  # Max 30%
        )
        
        # col1 has 60% nulls, should fail
        assert result.passed is False
    
    def test_business_rules_all_pass(self, sample_df):
        """Test business rules validation - all pass."""
        rules = [
            {
                'name': 'has_nombre_asesor',
                'condition': lambda df: 'nombre_asesor' in df.columns,
                'severity': 'CRITICAL'
            },
            {
                'name': 'has_telefono',
                'condition': lambda df: 'telefono' in df.columns,
                'severity': 'CRITICAL'
            }
        ]
        
        result = self.validator.validate_business_rules(
            df=sample_df,
            rules=rules,
            stage_name='test_rules'
        )
        
        assert result.passed is True
        assert result.details['has_nombre_asesor'] == 'passed'
        assert result.details['has_telefono'] == 'passed'
    
    def test_business_rules_some_fail(self, sample_df):
        """Test business rules validation - some fail."""
        rules = [
            {
                'name': 'all_phones_start_with_3',
                'condition': lambda df: (df['telefono'].str[0] == '3').all(),
                'severity': 'ERROR'
            }
        ]
        
        result = self.validator.validate_business_rules(
            df=sample_df,
            rules=rules
        )
        
        # Should fail (has 601... phone)
        assert result.passed is False
        assert result.severity == 'ERROR'
    
    def test_reconciliation(self, sample_df):
        """Test reconciliation."""
        df_output = sample_df.iloc[:-1].copy()  # 2 out of 3
        
        result = self.validator.reconcile(
            df_input=sample_df,
            df_output=df_output,
            expected_retention=66.7
        )
        
        assert result.passed is True
        assert result.details['records_in'] == 3
        assert result.details['records_out'] == 2
    
    def test_generate_report(self, sample_df):
        """Test report generation."""
        # Run some validations
        self.validator.validate_load(sample_df, 'test', min_records=1)
        self.validator.validate_data_quality(sample_df, 'test')
        
        # Generate report
        df_report = self.validator.generate_etl_report()
        
        assert len(df_report) == 2
        assert 'stage' in df_report.columns
        assert 'passed' in df_report.columns
    
    def test_export_report(self, sample_df, tmp_path):
        """Test exporting report to Excel."""
        # Run validations
        self.validator.validate_load(sample_df, 'test', min_records=1)
        
        # Export
        report_path = tmp_path / 'test_report.xlsx'
        self.validator.export_report(report_path)
        
        assert report_path.exists()
        
        # Verify content
        df = pd.read_excel(report_path, sheet_name='Validation Results')
        assert len(df) == 1
    
    def test_has_critical_issues(self, sample_df):
        """Test critical issue detection."""
        # Add a critical issue
        from src.etl_validator import ValidationResult
        
        self.validator.validation_results.append(
            ValidationResult(
                stage='TEST',
                check_name='critical_test',
                passed=False,
                message='Critical failure',
                severity='CRITICAL'
            )
        )
        
        assert self.validator.has_critical_issues() is True
    
    def test_get_failed_checks(self, sample_df):
        """Test getting failed checks."""
        # Add mix of passed/failed
        from src.etl_validator import ValidationResult
        
        self.validator.validation_results.append(
            ValidationResult('TEST', 'check1', True, 'Passed')
        )
        self.validator.validation_results.append(
            ValidationResult('TEST', 'check2', False, 'Failed')
        )
        
        failed = self.validator.get_failed_checks()
        
        assert len(failed) == 1
        assert failed[0].check_name == 'check2'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
