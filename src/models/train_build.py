"""
============================================
train_build.py - HOURLY RESAMPLING + BATTLE MODE
Random Forest vs LightGBM for Pattern Learning
============================================
"""

import pandas as pd
import numpy as np
import joblib
import os
import warnings
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = 'data/cleaned_dataset.csv'
CHECKPOINT_DIR = 'checkpoints'
FINAL_MODEL_NAME = 'best_model_final.pkl'
TRAIN_SPLIT = 0.8  # 80% train, 20% test

# Ensure checkpoint directory exists
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ============================================
# UTILITY FUNCTIONS
# ============================================
def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def safe_mape(y_true, y_pred, threshold=0.1):
    """Calculate MAPE safely (avoid division by zero)"""
    mask = y_true > threshold
    if np.sum(mask) > 0:
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    return 0.0

# ============================================
# DATA LOADING & PREPARATION
# ============================================
def load_and_prepare_hourly_data(filepath=INPUT_FILE):
    """
    Load cleaned data and resample to hourly intervals
    
    Returns:
        X: Feature matrix
        y: Target values
        feature_names: List of feature column names
        timestamps: Datetime index (for visualization later)
    """
    print_section("STEP 1: LOADING & RESAMPLING DATA")
    
    # Load cleaned data
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Cleaned data not found: {filepath}")
    
    df = pd.read_csv(filepath)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.set_index('Datetime')
    
    print(f"✅ Loaded {len(df):,} minute-level records")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    
    # ==========================================
    # KEY STEP: RESAMPLE TO HOURLY
    # ==========================================
    print("\n🔄 Resampling to HOURLY intervals...")
    
    # Select numeric columns for resampling
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_hourly = df[numeric_cols].resample('H').mean()
    
    print(f"✅ Resampled to {len(df_hourly):,} hourly records")
    print(f"   Reduction: {len(df) / len(df_hourly):.1f}x (noise reduced)")
    
    # ==========================================
    # FEATURE ENGINEERING
    # ==========================================
    print_section("STEP 2: FEATURE ENGINEERING")
    
    # Time-based features (recalculate after resampling)
    df_hourly['hour'] = df_hourly.index.hour
    df_hourly['weekday'] = df_hourly.index.weekday
    df_hourly['month'] = df_hourly.index.month
    
    # Season (recalculate)
    def get_season(month):
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Autumn
    
    df_hourly['season'] = df_hourly['month'].apply(get_season)
    
    # ==========================================
    # LAG FEATURES (Critical for Time-Series)
    # ==========================================
    print("\n📊 Creating lag features...")
    
    # Lag 24h: Same hour yesterday
    df_hourly['lag_24h'] = df_hourly['Global_active_power'].shift(24)
    print("  ✓ lag_24h: Yesterday's value at same hour")
    
    # Lag 7d: Same hour last week
    df_hourly['lag_7d'] = df_hourly['Global_active_power'].shift(24 * 7)
    print("  ✓ lag_7d: Last week's value at same hour")
    
    # Drop NaN created by shifting
    df_hourly = df_hourly.dropna()
    
    print(f"\n✅ Final dataset: {len(df_hourly):,} rows (after lag creation)")
    
    # ==========================================
    # PREPARE FEATURES & TARGET
    # ==========================================
    feature_cols = ['hour', 'weekday', 'month', 'season', 'lag_24h', 'lag_7d']
    target_col = 'Global_active_power'
    
    # Verify all features exist
    missing_features = [col for col in feature_cols if col not in df_hourly.columns]
    if missing_features:
        raise ValueError(f"❌ Missing features: {missing_features}")
    
    X = df_hourly[feature_cols].values
    y = df_hourly[target_col].values
    timestamps = df_hourly.index
    
    print(f"\n📋 Feature Summary:")
    print(f"   • Features: {feature_cols}")
    print(f"   • Target: {target_col}")
    print(f"   • Data shape: X={X.shape}, y={y.shape}")
    
    return X, y, feature_cols, timestamps

# ============================================
# MODEL EVALUATION
# ============================================
def evaluate_model(y_true, y_pred, model_name):
    """
    Evaluate model performance with multiple metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = safe_mape(y_true, y_pred)
    
    print(f"\n📊 {model_name} Performance:")
    print(f"   • R² Score:  {r2:.4f}")
    print(f"   • MAE:       {mae:.4f} kW")
    print(f"   • RMSE:      {rmse:.4f} kW")
    print(f"   • MAPE:      {mape:.2f}%")
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'mape': mape
    }

# ============================================
# TRAINING BATTLE
# ============================================
def train_battle_mode(X, y):
    """
    Train both RF and LGBM models, compare performance
    
    Returns:
        results: Dict with model and metrics for each
        scaler: Fitted StandardScaler
    """
    print_section("STEP 3: TRAINING BATTLE - RF vs LGBM")
    
    # ==========================================
    # SPLIT DATA
    # ==========================================
    split_idx = int(len(X) * TRAIN_SPLIT)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\n✂️  Data Split:")
    print(f"   • Train: {len(X_train):,} samples ({TRAIN_SPLIT*100:.0f}%)")
    print(f"   • Test:  {len(X_test):,} samples ({(1-TRAIN_SPLIT)*100:.0f}%)")
    
    # ==========================================
    # SCALING
    # ==========================================
    print(f"\n🔧 Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(f"   ✓ StandardScaler fitted")
    
    results = {}
    
    # ==========================================
    # MODEL 1: LightGBM
    # ==========================================
    print_section("🥊 ROUND 1: LightGBM")
    
    lgb_model = lgb.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=20,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    print("⚡ Training LightGBM...")
    lgb_model.fit(X_train_scaled, y_train)
    y_pred_lgb = lgb_model.predict(X_test_scaled)
    
    lgb_metrics = evaluate_model(y_test, y_pred_lgb, "LightGBM")
    results['LightGBM'] = {
        'model': lgb_model,
        'metrics': lgb_metrics,
        'predictions': y_pred_lgb
    }
    
    # ==========================================
    # MODEL 2: Random Forest
    # ==========================================
    print_section("🥊 ROUND 2: Random Forest")
    
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=4,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    print("🌲 Training Random Forest...")
    rf_model.fit(X_train_scaled, y_train)
    y_pred_rf = rf_model.predict(X_test_scaled)
    
    rf_metrics = evaluate_model(y_test, y_pred_rf, "Random Forest")
    results['Random Forest'] = {
        'model': rf_model,
        'metrics': rf_metrics,
        'predictions': y_pred_rf
    }
    
    return results, scaler

# ============================================
# MODEL SELECTION & SAVING
# ============================================
def save_winning_model(results, scaler, feature_names):
    """
    Compare models, select winner, and save complete package
    """
    print_section("🏆 FINAL VERDICT")
    
    lgb_r2 = results['LightGBM']['metrics']['r2']
    rf_r2 = results['Random Forest']['metrics']['r2']
    
    # Determine winner
    if rf_r2 > lgb_r2:
        winner_name = "Random Forest"
        winner_data = results['Random Forest']
        margin = rf_r2 - lgb_r2
        print(f"🥇 Random Forest WINS!")
        print(f"   Advantage: +{margin:.4f} R²")
    else:
        winner_name = "LightGBM"
        winner_data = results['LightGBM']
        margin = lgb_r2 - rf_r2
        print(f"🥇 LightGBM WINS!")
        print(f"   Advantage: +{margin:.4f} R²")
    
    # Display winner's metrics
    print(f"\n📊 Champion's Stats:")
    for metric, value in winner_data['metrics'].items():
        print(f"   • {metric.upper()}: {value:.4f}")
    
    # ==========================================
    # PACKAGE & SAVE
    # ==========================================
    print_section("💾 SAVING CHAMPION MODEL")
    
    model_package = {
        'model': winner_data['model'],
        'scaler': scaler,
        'feature_names': feature_names,
        'metrics': winner_data['metrics'],
        'model_name': winner_name,
        'timestamp': datetime.now().isoformat(),
        'training_info': {
            'resampling': 'hourly',
            'train_split': TRAIN_SPLIT,
            'features': feature_names
        }
    }
    
    save_path = os.path.join(CHECKPOINT_DIR, FINAL_MODEL_NAME)
    joblib.dump(model_package, save_path)
    
    print(f"✅ Model saved to: {save_path}")
    print(f"\n📦 Package contents:")
    print(f"   • model: {winner_name}")
    print(f"   • scaler: StandardScaler (fitted)")
    print(f"   • feature_names: {feature_names}")
    print(f"   • metrics: R², MAE, RMSE, MAPE")
    print(f"   • timestamp: {model_package['timestamp']}")
    
    print(f"\n💡 Usage in predictor.py:")
    print(f"   package = joblib.load('{save_path}')")
    print(f"   model = package['model']")
    print(f"   scaler = package['scaler']")
    
    return model_package

# ============================================
# MAIN EXECUTION
# ============================================
def main():
    """
    Main training pipeline
    """
    print("="*70)
    print("  HOUSEHOLD ENERGY FORECASTING - MODEL TRAINING")
    print("="*70)
    print("  Strategy: Hourly Resampling + Tree-based Models")
    print("  Battle: Random Forest vs LightGBM")
    print("="*70)
    
    try:
        # Step 1: Load & Prepare
        X, y, feature_names, timestamps = load_and_prepare_hourly_data()
        
        # Step 2: Train Battle
        results, scaler = train_battle_mode(X, y)
        
        # Step 3: Save Winner
        model_package = save_winning_model(results, scaler, feature_names)
        
        # Final Summary
        print_section("✅ TRAINING COMPLETED")
        print(f"🎯 Champion: {model_package['model_name']}")
        print(f"📈 R² Score: {model_package['metrics']['r2']:.4f}")
        print(f"📁 Model saved: {os.path.join(CHECKPOINT_DIR, FINAL_MODEL_NAME)}")
        print("\n🚀 Ready for prediction! Run your predictor.py script.")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()