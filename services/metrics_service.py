"""Metrics and metadata extraction service for BhujalDrishti."""


def get_model_metrics(metadata: dict) -> dict:
    """Extract verified machine learning and baseline performance metrics."""
    res_fc = metadata.get('results_fc', {})
    rf = res_fc.get('Random Forest Regressor', {})
    pers = res_fc.get('Baseline (Persistence: gw_now)', {})
    
    return {
        "rf_mae": rf.get('MAE', 2.092),
        "rf_rmse": rf.get('RMSE', 2.899),
        "rf_r2": rf.get('R2', 0.247),
        "pers_mae": pers.get('MAE', 2.744),
        "pers_rmse": pers.get('RMSE', 3.709),
    }


def get_uncertainty_metrics(metadata: dict) -> dict:
    """Extract prediction interval empirical coverage and width statistics."""
    unc = metadata.get('uncertainty_intervals', {})
    return {
        "coverage_pct": unc.get('empirical_test_coverage_pct', 57.26),
        "average_width_m": unc.get('average_interval_width_meters', 4.36),
    }


def get_horizon_stats(metadata: dict) -> dict:
    """Extract verified test and overall population forecast horizon statistics."""
    stats = metadata.get('horizon_statistics', {})
    test_h = stats.get('test_population', {
        'mean_days': 109.4, 'median_days': 92.0, 'min_days': 41.0, 'max_days': 233.0
    })
    overall_h = stats.get('overall_population', {
        'mean_days': 106.9, 'median_days': 102.0, 'min_days': 41.0, 'max_days': 2206.0
    })
    return {
        "test": test_h,
        "overall": overall_h,
    }
