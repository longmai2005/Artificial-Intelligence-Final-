# ============================================
# clean_data.py - OPTIMIZED VERSION
# Data Cleaning – Household Power Consumption
# ============================================

import pandas as pd
import numpy as np
import os

def print_section(title):
    """Print section header for better readability"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def generate_cleaning_report(df_original, df_cleaned, missing_info, outlier_info):
    """Generate comprehensive cleaning report"""
    report = []
    report.append("="*70)
    report.append("DATA CLEANING REPORT - Household Power Consumption")
    report.append("="*70)
    
    # Original dataset info
    report.append(f"\n1. ORIGINAL DATASET")
    report.append(f"   - Shape: {df_original.shape}")
    report.append(f"   - Date range: {df_original.index[0]} to {df_original.index[-1]}")
    report.append(f"   - Total records: {len(df_original):,}")
    
    # Missing values
    report.append(f"\n2. MISSING VALUES")
    for col, info in missing_info.items():
        pct = (info['count'] / len(df_original)) * 100
        report.append(f"   - {col}: {info['count']:,} ({pct:.2f}%)")
    
    # Outliers
    report.append(f"\n3. OUTLIERS REMOVED")
    report.append(f"   - Records removed: {outlier_info['removed']:,}")
    report.append(f"   - Percentage: {outlier_info['percentage']:.2f}%")
    report.append(f"   - Criteria:")
    for criterion in outlier_info['criteria']:
        report.append(f"     • {criterion}")
    
    # Cleaned dataset
    report.append(f"\n4. CLEANED DATASET")
    report.append(f"   - Final shape: {df_cleaned.shape}")
    report.append(f"   - Remaining records: {len(df_cleaned):,}")
    report.append(f"   - Missing values after cleaning: {df_cleaned.isnull().sum().sum()}")
    
    # Features added
    report.append(f"\n5. FEATURES ENGINEERED")
    new_features = ['hour', 'weekday', 'month', 'season', 
                   'rolling_5', 'rolling_15', 'rolling_60', 'rolling_1440',
                   'energy_per_day_kwh']
    for feat in new_features:
        if feat in df_cleaned.columns:
            report.append(f"   ✓ {feat}")
    
    report.append("\n" + "="*70)
    
    return "\n".join(report)

def main():
    # --- 1. LOAD DATASET ---
    print_section("STEP 1: LOADING DATASET")
    
    # Sử dụng raw string hoặc forward slash
    filepath = "data/household_power_consumption.txt"
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found at '{filepath}'")
        return
    
    df = pd.read_csv(
        filepath,
        sep=";",
        low_memory=False,
        na_values=['?', '']  # Trực tiếp xử lý '?' thành NaN
    )
    print(f"✓ Dataset loaded successfully")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    # --- 2. DATA QUALITY CHECK ---
    print_section("STEP 2: DATA QUALITY CHECK")
    
    # Store original info for report
    original_shape = df.shape
    
    # Check missing values BEFORE processing
    missing_before = df.isnull().sum()
    missing_info = {}
    print("Missing values:")
    for col in missing_before.index:
        if missing_before[col] > 0:
            pct = (missing_before[col] / len(df)) * 100
            print(f"  - {col}: {missing_before[col]} ({pct:.2f}%)")
            missing_info[col] = {'count': missing_before[col], 'percentage': pct}
    
    # Check data types
    print(f"\nData types:\n{df.dtypes}")

    # --- 3. CONVERT COLUMNS TO NUMERIC ---
    print_section("STEP 3: CONVERTING TO NUMERIC")
    
    numeric_cols = [
        'Global_active_power', 'Global_reactive_power',
        'Voltage', 'Global_intensity',
        'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'
    ]
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"✓ Converted {len(numeric_cols)} columns to numeric")

    # --- 4. CREATE DATETIME INDEX ---
    print_section("STEP 4: CREATING DATETIME INDEX")
    
    df['Datetime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format='%d/%m/%Y %H:%M:%S',
        errors='coerce'
    )
    
    # Remove rows with invalid datetime
    df = df.dropna(subset=['Datetime'])
    df = df.set_index('Datetime')
    df = df.drop(columns=['Date', 'Time'])
    df = df.sort_index()  # Đảm bảo sắp xếp theo thời gian
    
    print(f"✓ Datetime index created")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")

    # --- 5. HANDLE OUTLIERS & INVALID VALUES ---
    print_section("STEP 5: REMOVING OUTLIERS & INVALID VALUES")
    
    len_before_outliers = len(df)
    
    # Xác định ngưỡng hợp lý dựa trên phân tích thực tế
    # Global_active_power: min=0.076, max≈11, nên giới hạn [0.01, 15] là hợp lý
    outlier_criteria = []
    
    # Loại bỏ giá trị <= 0 hoặc quá lớn
    df = df[
        (df['Global_active_power'] > 0) & (df['Global_active_power'] < 15) &
        (df['Global_reactive_power'] >= 0) & (df['Global_reactive_power'] < 5) &
        (df['Voltage'] > 200) & (df['Voltage'] < 260) &  # Điện áp châu Âu ~230V
        (df['Global_intensity'] >= 0) & (df['Global_intensity'] < 50)
    ]
    
    outlier_criteria = [
        "Global_active_power: 0 < x < 15 kW",
        "Global_reactive_power: 0 ≤ x < 5 kW",
        "Voltage: 200V < x < 260V",
        "Global_intensity: 0 ≤ x < 50A"
    ]
    
    outliers_removed = len_before_outliers - len(df)
    outlier_pct = (outliers_removed / len_before_outliers) * 100
    
    print(f"✓ Removed {outliers_removed:,} outlier records ({outlier_pct:.2f}%)")
    
    outlier_info = {
        'removed': outliers_removed,
        'percentage': outlier_pct,
        'criteria': outlier_criteria
    }

    # --- 6. HANDLE MISSING VALUES ---
    print_section("STEP 6: HANDLING MISSING VALUES")
    
    # Interpolate chỉ khi khoảng trống <= 6 điểm (6 phút)
    # Với khoảng trống lớn hơn, sử dụng forward fill
    df = df.interpolate(method='linear', limit=6, limit_direction='forward')
    
    # Forward fill cho các missing còn lại (giới hạn 30 phút)
    df = df.fillna(method='ffill', limit=30)
    
    # Nếu vẫn còn missing (đầu dataset), dùng backward fill
    df = df.fillna(method='bfill', limit=30)
    
    # Drop các hàng vẫn còn missing (nếu có)
    final_missing = df.isnull().sum().sum()
    if final_missing > 0:
        print(f"⚠ Dropping {final_missing} remaining missing values")
        df = df.dropna()
    
    print(f"✓ Missing values handled")
    print(f"  Remaining missing: {df.isnull().sum().sum()}")

    # --- 7. FEATURE ENGINEERING ---
    print_section("STEP 7: FEATURE ENGINEERING")
    
    # Time-based features
    df['hour'] = df.index.hour
    df['weekday'] = df.index.weekday  # 0=Monday, 6=Sunday
    df['month'] = df.index.month
    
    # Season (Bắc bán cầu: châu Âu)
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'
    
    df['season'] = df['month'].apply(get_season)
    
    # Rolling means (cửa sổ theo phút)
    print("  Creating rolling averages...")
    df['rolling_5'] = df['Global_active_power'].rolling(window=5, min_periods=1).mean()
    df['rolling_15'] = df['Global_active_power'].rolling(window=15, min_periods=1).mean()
    df['rolling_60'] = df['Global_active_power'].rolling(window=60, min_periods=1).mean()
    df['rolling_1440'] = df['Global_active_power'].rolling(window=1440, min_periods=1).mean()  # 1 ngày
    
    # Energy per day (kWh) - tính tổng năng lượng mỗi ngày
    # Global_active_power đơn vị: kilowatt, mỗi phút -> cần nhân 1/60 để ra kWh
    df['energy_per_day_kwh'] = (
        df.groupby(df.index.date)['Global_active_power']
        .transform('sum') / 60  # Chia 60 vì mỗi điểm là 1 phút
    )
    
    print(f"✓ Added {9} engineered features")

    # --- 8. SAVE CLEANED DATASET ---
    print_section("STEP 8: SAVING RESULTS")
    
    output_file = "cleaned_dataset.csv"
    df.to_csv(output_file)
    print(f"✓ Cleaned dataset saved: '{output_file}'")
    print(f"  Final shape: {df.shape}")
    
    # --- 9. GENERATE & SAVE REPORT ---
    report = generate_cleaning_report(
        df_original=pd.DataFrame({'shape': [original_shape]}, 
                                index=pd.date_range(df.index[0], df.index[-1], freq='min')[:original_shape[0]]),
        df_cleaned=df,
        missing_info=missing_info,
        outlier_info=outlier_info
    )
    
    report_file = "cleaning_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Cleaning report saved: '{report_file}'")
    
    # Print report to console
    print("\n" + report)
    
    print("\n" + "="*60)
    print("✓ DATA CLEANING COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    main()