import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import lightgbm as lgb

from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tqdm import tqdm
import joblib
from datetime import datetime

#=============================================================================
# 1. DATA LOADING & PREPARATION
#=============================================================================

def load_and_prepare_data(filepath='data/cleaned_dataset.csv'):
    """Load and prepare data - FIXED VERSION"""
    print("📂 Loading data...")
    df = pd.read_csv(filepath)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.set_index('Datetime')
    
    # Encode categorical
    if 'season' in df.columns:
        df['season'] = LabelEncoder().fit_transform(df['season'])
    
    print(f"   ✅ Data shape: {df.shape}")
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    
    # Check sampling rate
    median_interval = df.index.to_series().diff().median()
    print(f"   ⏱️  Median sampling: {median_interval}")
    
    if median_interval == pd.Timedelta('1min'):
        print(f"   ✅ Confirmed: 1-minute sampling")
    else:
        print(f"   ⚠️  Warning: Unexpected sampling rate!")
    
    # Prepare features (REMOVE energy_per_day_kwh to avoid leakage!)
    target_col = 'Global_active_power'
    y = df[target_col].values
    
    # CRITICAL: Remove energy_per_day_kwh from features!
    forbidden_cols = [target_col, 'energy_per_day_kwh']
    feature_cols = [col for col in df.columns if col not in forbidden_cols]
    X = df[feature_cols].values
    
    print(f"   ✅ Features: {len(feature_cols)}, Samples: {len(X)}")
    print(f"   🚫 Excluded from features: {forbidden_cols}")
    
    # Keep datetime index for later conversion
    datetime_index = df.index
    
    return X, y, feature_cols, datetime_index

def time_split_and_scale(X, y, datetime_index, test_size=0.2):
    """Time-based split and scaling - FIXED VERSION"""
    split_idx = int(len(X) * (1 - test_size))
    
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    datetime_train = datetime_index[:split_idx]
    datetime_test = datetime_index[split_idx:]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"   ✅ Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   ✅ Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    
    return (X_train_scaled, X_test_scaled, y_train, y_test, 
            scaler, datetime_train, datetime_test)

#=============================================================================
# 2. EVALUATION METRICS (KW TO KWH CONVERSION)
#=============================================================================

def calculate_metrics(y_true, y_pred, model_name="Model", 
                     datetime_index=None, convert_to_kwh=False):
    """
    Calculate metrics with proper kW → kWh conversion
    
    Args:
        y_true: True power values (kW)
        y_pred: Predicted power values (kW)
        datetime_index: Datetime index for aggregation
        convert_to_kwh: Whether to convert and show monthly kWh
    """
    # Basic metrics on kW predictions
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    print(f"\n{'='*60}")
    print(f"📊 {model_name}")
    print(f"{'='*60}")
    print(f"🔸 kW-level metrics (per minute):")
    print(f"   MAE:  {mae:.4f} kW")
    print(f"   RMSE: {rmse:.4f} kW")
    print(f"   R²:   {r2:.4f}")
    print(f"   MAPE: {mape:.2f}%")
    
    # Convert to kWh if datetime index provided
    monthly_error = None
    if convert_to_kwh and datetime_index is not None:
        dt_hours = 1/60  # 1 minute = 1/60 hour
        
        # Convert kW to kWh
        true_series = pd.Series(y_true, index=datetime_index)
        pred_series = pd.Series(y_pred, index=datetime_index)
        
        true_kwh = true_series * dt_hours
        pred_kwh = pred_series * dt_hours
        
        # Aggregate to monthly
        true_monthly = true_kwh.resample('M').sum()
        pred_monthly = pred_kwh.resample('M').sum()
        
        monthly_mae = mean_absolute_error(true_monthly, pred_monthly)
        monthly_error = monthly_mae
        
        print(f"\n🔸 Monthly kWh metrics:")
        print(f"   Average True:  {true_monthly.mean():.2f} kWh/month")
        print(f"   Average Pred:  {pred_monthly.mean():.2f} kWh/month")
        print(f"   Monthly MAE:   {monthly_mae:.2f} kWh")
        print(f"   Monthly Error: {(monthly_mae/true_monthly.mean())*100:.2f}%")
    
    print(f"{'='*60}")
    
    return {
        'MAE': mae, 
        'RMSE': rmse, 
        'R2': r2, 
        'MAPE': mape,
        'Monthly_Error': monthly_error
    }

#=============================================================================
# 3. BASELINE MODELS
#=============================================================================

def baseline_models(y_train, y_test, datetime_test):
    """Fixed baseline models"""
    results = {}
    
    print("\n" + "="*60)
    print("📈 BASELINE MODELS")
    print("="*60)
    
    # 1. Naive Forecast (last value)
    print("\n1️⃣ Naive Forecast...")
    y_pred_naive = np.full(len(y_test), y_train[-1])
    results['Naive'] = calculate_metrics(
        y_test, y_pred_naive, "Naive Forecast",
        datetime_index=datetime_test, convert_to_kwh=True
    )
    
    # 2. Moving Average (no recursive prediction)
    print("\n2️⃣ Moving Average (24h window)...")
    window = 1440  # 24 hours × 60 minutes
    
    # Use last window from training data as baseline
    baseline_value = np.mean(y_train[-window:])
    y_pred_ma = np.full(len(y_test), baseline_value)
    
    results['Moving Average'] = calculate_metrics(
        y_test, y_pred_ma, "Moving Average",
        datetime_index=datetime_test, convert_to_kwh=True
    )
    
    return results

#=============================================================================
# 4. TRADITIONAL ML MODELS
#=============================================================================

def train_traditional_ml(X_train, y_train, X_test, y_test, datetime_test):
    """Train traditional ML models - FIXED VERSION"""
    results = {}
    models = {}
    
    print("\n" + "="*60)
    print("🤖 TRADITIONAL ML MODELS")
    print("="*60)
    
    # LightGBM (fastest and often best)
    print("\n3️⃣ LightGBM...")
    print("   Training 200 trees...")
    
    lgb_model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1
    )
    
    pbar_lgb = tqdm(total=200, desc="Training LightGBM", 
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]')
    
    def lgb_callback(env):
        pbar_lgb.update(1)
    
    lgb_model.fit(X_train, y_train, callbacks=[lgb_callback])
    pbar_lgb.close()
    
    y_pred_lgb = lgb_model.predict(X_test)
    results['LightGBM'] = calculate_metrics(
        y_test, y_pred_lgb, "LightGBM",
        datetime_index=datetime_test, convert_to_kwh=True
    )
    models['LightGBM'] = lgb_model
    
    # Random Forest
    print("\n4️⃣ Random Forest...")
    print("   Training 100 trees...")
    
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    with tqdm(total=100, desc="Training Random Forest", 
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]') as pbar:
        rf_model.fit(X_train, y_train)
        pbar.update(100)
    
    y_pred_rf = rf_model.predict(X_test)
    results['Random Forest'] = calculate_metrics(
        y_test, y_pred_rf, "Random Forest",
        datetime_index=datetime_test, convert_to_kwh=True
    )
    models['Random Forest'] = rf_model
    
    return results, models

#=============================================================================
# 5. DEEP LEARNING
#=============================================================================

def create_sequences(X, y, seq_length=60):
    """
    Create sequences for LSTM
    
    FIXED: seq_length now represents MINUTES, not hours!
    - seq_length=60 → 1 hour lookback
    - seq_length=1440 → 1 day lookback
    """
    X_seq, y_seq = [], []
    
    print(f"   Creating sequences (length={seq_length} minutes = {seq_length/60:.1f} hours)...")
    for i in tqdm(range(len(X) - seq_length), desc="Creating sequences"):
        X_seq.append(X[i:i+seq_length])
        y_seq.append(y[i+seq_length])
    
    return np.array(X_seq), np.array(y_seq)

def build_lstm_model(input_shape):
    """Build LSTM model"""
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(64, return_sequences=True),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_deep_learning(X_train_scaled, y_train, X_test_scaled, y_test, 
                       datetime_train, datetime_test):
    """Train LSTM - FIXED VERSION"""
    results = {}
    
    print("\n" + "="*60)
    print("🧠 DEEP LEARNING MODEL")
    print("="*60)
    
    # FIXED: Use proper sequence length
    # Option 1: 60 minutes (1 hour) - faster
    # Option 2: 1440 minutes (1 day) - more context but slower
    seq_length = 60  # Start with 1 hour, can increase to 1440
    
    print(f"\n⚙️  Using seq_length={seq_length} minutes ({seq_length/60:.1f} hours)")
    
    # Create sequences
    X_train_seq, y_train_seq = create_sequences(X_train_scaled, y_train, seq_length)
    X_test_seq, y_test_seq = create_sequences(X_test_scaled, y_test, seq_length)
    
    # Adjust datetime indices (skip first seq_length samples)
    datetime_train_seq = datetime_train[seq_length:]
    datetime_test_seq = datetime_test[seq_length:]
    
    # Validation split
    val_size = int(len(X_train_seq) * 0.2)
    X_val = X_train_seq[-val_size:]
    y_val = y_train_seq[-val_size:]
    X_train_seq = X_train_seq[:-val_size]
    y_train_seq = y_train_seq[:-val_size]
    
    print(f"   ✅ Train sequences: {len(X_train_seq)}")
    print(f"   ✅ Val sequences: {len(X_val)}")
    print(f"   ✅ Test sequences: {len(X_test_seq)}")
    
    # Build and train LSTM
    print("\n5️⃣ LSTM...")
    input_shape = (seq_length, X_train_scaled.shape[1])
    lstm_model = build_lstm_model(input_shape)
    
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7)
    
    class ProgressBar(keras.callbacks.Callback):
        def on_train_begin(self, logs=None):
            self.epochs = self.params['epochs']
            self.pbar = tqdm(total=self.epochs, desc="Training LSTM", 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} epochs [{elapsed}<{remaining}]')
        
        def on_epoch_end(self, epoch, logs=None):
            self.pbar.update(1)
            self.pbar.set_postfix({
                'loss': f"{logs.get('loss', 0):.4f}",
                'val_loss': f"{logs.get('val_loss', 0):.4f}"
            })
        
        def on_train_end(self, logs=None):
            self.pbar.close()
    
    history = lstm_model.fit(
        X_train_seq, y_train_seq,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=64,
        callbacks=[early_stop, reduce_lr, ProgressBar()],
        verbose=0
    )
    
    y_pred_lstm = lstm_model.predict(X_test_seq, verbose=0).flatten()
    results['LSTM'] = calculate_metrics(
        y_test_seq, y_pred_lstm, "LSTM",
        datetime_index=datetime_test_seq, convert_to_kwh=True
    )
    
    return results, lstm_model

#=============================================================================
# 6. MODEL COMPARISON & SELECTION
#=============================================================================

def compare_and_select_best(all_results):
    """Compare all models and select best"""
    print("\n" + "="*60)
    print("🏆 MODEL COMPARISON")
    print("="*60)
    
    df = pd.DataFrame(all_results).T
    df = df.sort_values('R2', ascending=False)
    
    print("\n" + df.to_string())
    print("\n" + "="*60)
    
    best_model = df.index[0]
    best_metrics = df.loc[best_model]
    
    print(f"\n🥇 BEST MODEL: {best_model}")
    print(f"   R² Score: {best_metrics['R2']:.4f}")
    print(f"   RMSE: {best_metrics['RMSE']:.4f} kW")
    print(f"   MAE: {best_metrics['MAE']:.4f} kW")
    print(f"   MAPE: {best_metrics['MAPE']:.2f}%")
    if best_metrics.get('Monthly_Error'):
        print(f"   Monthly Error: {best_metrics['Monthly_Error']:.2f} kWh")
    
    # Visualize comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    metrics = ['MAE', 'RMSE', 'R2', 'MAPE']
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx//2, idx%2]
        df[metric].plot(kind='barh', ax=ax, color='skyblue')
        ax.set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        ax.set_xlabel(metric)
        ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\n   ✅ Saved: model_comparison.png")
    
    return best_model, best_metrics, df

#=============================================================================
# 7. FEATURE IMPORTANCE
#=============================================================================

def plot_feature_importance(model, feature_names, model_name):
    """Plot feature importance"""
    if not hasattr(model, 'feature_importances_'):
        print(f"   ⚠️  {model_name} doesn't support feature importance")
        return
    
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    top_k = min(20, len(importance))
    
    plt.figure(figsize=(12, 8))
    plt.barh(range(top_k), importance[indices[:top_k]], color='steelblue')
    plt.yticks(range(top_k), [feature_names[i] for i in indices[:top_k]])
    plt.xlabel('Importance Score')
    plt.title(f'Top {top_k} Feature Importance - {model_name}', 
             fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    filename = f'feature_importance_{model_name.replace(" ", "_").lower()}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {filename}")

#=============================================================================
# 8. SAVE MODEL & REPORT
#=============================================================================

def save_model_package(model, scaler, feature_names, metrics, model_name):
    """Save model package"""
    package = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'metrics': metrics,
        'model_name': model_name,
        'timestamp': datetime.now().isoformat(),
        'sampling_rate': '1 minute',
        'conversion_note': 'Remember to convert kW to kWh: multiply by 1/60'
    }
    
    filename = f'best_model_{model_name.replace(" ", "_").lower()}.pkl'
    joblib.dump(package, filename)
    print(f"\n   ✅ Model saved: {filename}")

def generate_report(model_name, metrics, comparison_df):
    """Generate final report"""
    report = f"""
{'='*70}
POWER CONSUMPTION FORECASTING - FINAL REPORT (FIXED VERSION)
{'='*70}

🏆 BEST MODEL: {model_name}
{'='*70}

📊 PERFORMANCE METRICS (kW-level, per minute):
   • MAE (Mean Absolute Error):     {metrics['MAE']:.4f} kW
   • RMSE (Root Mean Squared Error): {metrics['RMSE']:.4f} kW
   • R² Score:                       {metrics['R2']:.4f}
   • MAPE (Mean Absolute % Error):   {metrics['MAPE']:.2f}%

"""
    
    if metrics.get('Monthly_Error'):
        report += f"""📈 MONTHLY kWh METRICS:
   • Monthly Error (MAE):            {metrics['Monthly_Error']:.2f} kWh
   • This represents the average monthly prediction error

"""
    
    report += f"""💡 INTERPRETATION:
   • R² = {metrics['R2']:.4f} → Model explains {metrics['R2']*100:.1f}% of variance
   • Average prediction error: {metrics['MAE']:.4f} kW per minute
   • MAPE of {metrics['MAPE']:.2f}% indicates forecasting accuracy

⚠️  CRITICAL NOTES:
   • Data sampling: 1 minute per sample
   • Global_active_power unit: kW (kilowatts)
   • To convert to kWh: multiply by Δt = 1/60 hours
   • Monthly aggregation: resample to 'M' and sum
   • Feature 'energy_per_day_kwh' excluded to prevent data leakage

📈 ALL MODELS RANKING:
{comparison_df.to_string()}

{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
"""
    
    with open('model_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print("   ✅ Report saved: model_report.txt")

#=============================================================================
# 9. MAIN PIPELINE
#=============================================================================

def main_pipeline(filepath='data/cleaned_dataset.csv', run_deep_learning=True):
    """
    FIXED Main forecasting pipeline
    
    Key fixes:
    1. Removed energy_per_day_kwh from features
    2. Fixed seq_length to match 1-minute sampling
    3. Added proper kW → kWh conversion
    4. Fixed moving average baseline
    5. Enhanced metrics with monthly aggregation
    """
    
    print("\n" + "="*70)
    print("🚀 POWER CONSUMPTION FORECASTING PIPELINE (FIXED)")
    print("="*70 + "\n")
    
    # 1. Load and prepare data (FIXED)
    X, y, feature_names, datetime_index = load_and_prepare_data(filepath)
    (X_train, X_test, y_train, y_test, scaler, 
     datetime_train, datetime_test) = time_split_and_scale(X, y, datetime_index)
    
    # 2. Baseline models
    baseline_results = baseline_models(y_train, y_test, datetime_test)
    
    # 3. Traditional ML models
    ml_results, ml_models = train_traditional_ml(
        X_train, y_train, X_test, y_test, datetime_test
    )
    
    # 4. Deep Learning
    dl_results = {}
    if run_deep_learning:
        dl_results, lstm_model = train_deep_learning(
            X_train, y_train, X_test, y_test,
            datetime_train, datetime_test
        )
    
    # 5. Combine all results
    all_results = {**baseline_results, **ml_results, **dl_results}
    
    # 6. Compare and select best
    best_model_name, best_metrics, comparison_df = compare_and_select_best(all_results)
    
    # 7. Feature importance for best model
    print("\n" + "="*70)
    print("📊 FEATURE IMPORTANCE")
    print("="*70)
    
    if best_model_name in ml_models:
        best_model = ml_models[best_model_name]
        plot_feature_importance(best_model, feature_names, best_model_name)
        
        # Save best model
        save_model_package(best_model, scaler, feature_names, 
                          best_metrics, best_model_name)
    
    # 8. Generate final report
    generate_report(best_model_name, best_metrics, comparison_df)
    
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETED!")
    print("="*70)
    print("\n📁 Generated Files:")
    print("   • best_model_*.pkl")
    print("   • model_report.txt")
    print("   • model_comparison.png")
    print("   • feature_importance_*.png")
    
    return {
        'best_model_name': best_model_name,
        'best_metrics': best_metrics,
        'all_results': all_results,
        'comparison_df': comparison_df
    }

#=============================================================================
# 10. RUN PIPELINE
#=============================================================================

if __name__ == "__main__":
    # Configuration
    DATA_PATH = 'data/cleaned_dataset.csv'
    
    print("\n" + "="*70)
    print("⚠️  CRITICAL FIXES APPLIED:")
    print("="*70)
    print("✅ 1. Removed 'energy_per_day_kwh' from features (data leakage)")
    print("✅ 2. Fixed LSTM seq_length (60 min = 1 hour, adjustable)")
    print("✅ 3. Added kW → kWh conversion in metrics")
    print("✅ 4. Fixed moving average baseline (no recursive prediction)")
    print("✅ 5. Enhanced evaluation with monthly aggregation")
    print("="*70 + "\n")
    
    # Run pipeline
    print("🎯 Starting forecasting pipeline...")
    print("💡 Tip: LSTM uses seq_length=60 (1 hour). Increase to 1440 for 1-day lookback")
    
    results = main_pipeline(
        filepath=DATA_PATH,
        run_deep_learning=False  # Set False to skip LSTM (faster)
    )
    
    print("\n🎉 All done! Check the output files for detailed results.")
    print(f"🏆 Best Model: {results['best_model_name']}")
    print(f"📊 R² Score: {results['best_metrics']['R2']:.4f}")
    
    if results['best_metrics'].get('Monthly_Error'):
        print(f"📈 Monthly Error: {results['best_metrics']['Monthly_Error']:.2f} kWh")