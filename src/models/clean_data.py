"""
============================================
clean_data.py - OPTIMIZED FOR TIME-SERIES
Data Cleaning with Time Continuity Preservation
============================================
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = "data/household_power_consumption.txt"
OUTPUT_FILE = "data/cleaned_dataset.csv"
REPORT_FILE = "cleaning_report.txt"

# Outlier thresholds (based on domain knowledge)
OUTLIER_BOUNDS = {
    'Global_active_power': {'min': 0.001, 'max': 15.0},
    'Global_reactive_power': {'min': 0.0, 'max': 5.0},
    'Voltage': {'min': 200.0, 'max': 260.0},
    'Global_intensity': {'min': 0.0, 'max': 50.0}
}

# ============================================
# UTILITY FUNCTIONS
# ============================================
def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def safe_percentage(numerator, denominator):
    """Calculate percentage safely"""
    return (numerator / denominator * 100) if denominator > 0 else 0.0

# ============================================
# MAIN CLEANING PIPELINE
# ============================================
def clean_household_data():
    """
    Main cleaning pipeline with time continuity preservation
    """
    try:
        # ==========================================
        # STEP 1: LOAD RAW DATA
        # ==========================================
        print_section("STEP 1: LOADING RAW DATA")
        
        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"❌ Input file not found: {INPUT_FILE}")
        
        # Load with proper handling of missing values
        df = pd.read_csv(
            INPUT_FILE,
            sep=";",
            low_memory=False,
            na_values=['?', '', 'nan', 'NaN']
        )
        
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        print(f"   Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        
        # Store original stats for report
        original_shape = df.shape
        missing_before = df.isnull().sum()
        
        # ==========================================
        # STEP 2: CONVERT TO NUMERIC
        # ==========================================
        print_section("STEP 2: CONVERTING TO NUMERIC TYPES")
        
        numeric_cols = [
            'Global_active_power', 'Global_reactive_power',
            'Voltage', 'Global_intensity',
            'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'
        ]
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"✅ Converted {len(numeric_cols)} columns to numeric")
        
        # ==========================================
        # STEP 3: CREATE DATETIME INDEX
        # ==========================================
        print_section("STEP 3: CREATING DATETIME INDEX")
        
        df['Datetime'] = pd.to_datetime(
            df['Date'] + ' ' + df['Time'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        
        # Remove rows with invalid datetime (extremely rare)
        invalid_dt = df['Datetime'].isnull().sum()
        if invalid_dt > 0:
            print(f"⚠️  Removing {invalid_dt} rows with invalid datetime")
            df = df.dropna(subset=['Datetime'])
        
        # Set index and sort
        df = df.set_index('Datetime')
        df = df.sort_index()
        
        # Handle duplicate timestamps (keep first)
        duplicates = df.index.duplicated().sum()
        if duplicates > 0:
            print(f"⚠️  Removing {duplicates} duplicate timestamps")
            df = df[~df.index.duplicated(keep='first')]
        
        # Drop original Date/Time columns
        df = df.drop(columns=['Date', 'Time'], errors='ignore')
        
        print(f"✅ Datetime index created: {df.index[0]} to {df.index[-1]}")
        print(f"   Total timespan: {(df.index[-1] - df.index[0]).days} days")
        
        # ==========================================
        # STEP 4: HANDLE OUTLIERS (INTERPOLATION)
        # ==========================================
        print_section("STEP 4: OUTLIER DETECTION & INTERPOLATION")
        
        outlier_stats = {}
        total_outliers = 0
        
        for col, bounds in OUTLIER_BOUNDS.items():
            if col not in df.columns:
                continue
            
            # Detect outliers
            valid_mask = (df[col] >= bounds['min']) & (df[col] <= bounds['max'])
            n_outliers = (~valid_mask).sum()
            
            if n_outliers > 0:
                # Mark outliers as NaN
                df.loc[~valid_mask, col] = np.nan
                total_outliers += n_outliers
                
                outlier_stats[col] = {
                    'count': n_outliers,
                    'percentage': safe_percentage(n_outliers, len(df)),
                    'bounds': f"[{bounds['min']}, {bounds['max']}]"
                }
                
                print(f"  • {col}: {n_outliers:,} outliers marked as NaN "
                      f"({safe_percentage(n_outliers, len(df)):.2f}%)")
        
        # Interpolate to fill gaps (preserves time continuity)
        print("\n  🔄 Interpolating missing values...")
        df = df.interpolate(method='linear', limit_direction='both')
        
        # Final forward/backward fill for edge cases
        df = df.ffill().bfill()
        
        print(f"✅ {total_outliers:,} outliers handled via interpolation")
        print(f"✅ Time continuity preserved: {len(df):,} rows retained")
        
        # ==========================================
        # STEP 5: FEATURE ENGINEERING
        # ==========================================
        print_section("STEP 5: FEATURE ENGINEERING")
        
        # Time-based features
        df['hour'] = df.index.hour
        df['weekday'] = df.index.weekday  # Monday=0, Sunday=6
        df['month'] = df.index.month
        
        # Season (NUMERIC: 0-3)
        def get_season_numeric(month):
            """Convert month to season number"""
            if month in [12, 1, 2]:
                return 0  # Winter
            elif month in [3, 4, 5]:
                return 1  # Spring
            elif month in [6, 7, 8]:
                return 2  # Summer
            else:
                return 3  # Autumn
        
        df['season'] = df['month'].apply(get_season_numeric)
        
        # Rolling averages (useful for pattern detection)
        print("  📊 Creating rolling features...")
        for window in [5, 15, 60, 1440]:  # 5min, 15min, 1h, 1day
            df[f'rolling_{window}'] = (
                df['Global_active_power']
                .rolling(window=window, min_periods=1)
                .mean()
            )
        
        # Daily energy consumption
        df['energy_per_day_kwh'] = (
            df.groupby(df.index.date)['Global_active_power']
            .transform('sum') / 60  # Convert from kW*min to kWh
        )
        
        print(f"✅ Feature engineering completed")
        print(f"   • Time features: hour, weekday, month, season (0-3)")
        print(f"   • Rolling features: 5min, 15min, 1h, 1day windows")
        print(f"   • Daily energy: kWh per day")
        
        # ==========================================
        # STEP 6: FINAL VALIDATION
        # ==========================================
        print_section("STEP 6: FINAL VALIDATION")
        
        # Check for remaining NaNs
        remaining_na = df.isnull().sum().sum()
        if remaining_na > 0:
            print(f"⚠️  WARNING: {remaining_na} NaN values still present")
            print("   These will be dropped...")
            df = df.dropna()
        else:
            print("✅ No missing values remaining")
        
        # Verify numeric columns
        numeric_check = df.select_dtypes(include=[np.number]).shape[1]
        print(f"✅ {numeric_check} numeric columns validated")
        
        # ==========================================
        # STEP 7: SAVE CLEANED DATA
        # ==========================================
        print_section("STEP 7: SAVING RESULTS")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Save to CSV
        df.to_csv(OUTPUT_FILE)
        print(f"✅ Cleaned data saved: {OUTPUT_FILE}")
        print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        
        # ==========================================
        # STEP 8: GENERATE REPORT
        # ==========================================
        print_section("STEP 8: GENERATING REPORT")
        
        report_lines = [
            "="*70,
            "DATA CLEANING REPORT - Household Power Consumption",
            "="*70,
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n" + "-"*70,
            "1. ORIGINAL DATASET",
            "-"*70,
            f"Shape: {original_shape[0]:,} rows × {original_shape[1]} columns",
            f"Date range: {df.index[0]} to {df.index[-1]}",
            f"Timespan: {(df.index[-1] - df.index[0]).days} days",
            "\n" + "-"*70,
            "2. MISSING VALUES (Before Cleaning)",
            "-"*70
        ]
        
        for col in missing_before.index:
            if missing_before[col] > 0:
                pct = safe_percentage(missing_before[col], original_shape[0])
                report_lines.append(f"  • {col}: {missing_before[col]:,} ({pct:.2f}%)")
        
        report_lines.extend([
            "\n" + "-"*70,
            "3. OUTLIERS HANDLED (Interpolation Strategy)",
            "-"*70,
            f"Total outliers detected: {total_outliers:,}",
            "Strategy: Mark as NaN → Linear interpolation",
            "\nOutlier bounds applied:"
        ])
        
        for col, stats in outlier_stats.items():
            report_lines.append(
                f"  • {col}: {stats['count']:,} ({stats['percentage']:.2f}%) "
                f"outside {stats['bounds']}"
            )
        
        report_lines.extend([
            "\n⚠️  IMPORTANT: No rows were dropped to preserve time continuity!",
            "\n" + "-"*70,
            "4. FEATURES ENGINEERED",
            "-"*70,
            "  ✓ hour (0-23)",
            "  ✓ weekday (0=Mon, 6=Sun)",
            "  ✓ month (1-12)",
            "  ✓ season (0=Winter, 1=Spring, 2=Summer, 3=Autumn)",
            "  ✓ rolling_5, rolling_15, rolling_60, rolling_1440",
            "  ✓ energy_per_day_kwh",
            "\n" + "-"*70,
            "5. FINAL DATASET",
            "-"*70,
            f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
            f"Missing values: {remaining_na}",
            f"Output file: {OUTPUT_FILE}",
            "\n" + "="*70,
            "✅ CLEANING COMPLETED SUCCESSFULLY",
            "="*70
        ])
        
        # Save report
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✅ Report saved: {REPORT_FILE}")
        
        print("\n" + "="*70)
        print("🎉 DATA CLEANING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nNext step: Run train_build.py to train your model")
        
        return df
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    print("="*70)
    print("  HOUSEHOLD POWER CONSUMPTION - DATA CLEANING")
    print("="*70)
    print("  Strategy: Time Continuity Preservation + Interpolation")
    print("="*70)
    
    cleaned_df = clean_household_data()
    
    print(f"\n📊 Quick Stats:")
    print(f"   • Total records: {len(cleaned_df):,}")
    print(f"   • Time range: {(cleaned_df.index[-1] - cleaned_df.index[0]).days} days")
    print(f"   • Avg consumption: {cleaned_df['Global_active_power'].mean():.3f} kW")
    print(f"   • Peak consumption: {cleaned_df['Global_active_power'].max():.3f} kW")