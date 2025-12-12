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
    """Load and prepare data - single call"""
    print("📂 Loading data...")
    df = pd.read_csv(filepath)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.set_index('Datetime')
    
    # Encode categorical
    if 'season' in df.columns:
        df['season'] = LabelEncoder().fit_transform(df['season'])
    
    print(f"   ✅ Data shape: {df.shape}")
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    
    # Prepare features immediately
    target_col = 'Global_active_power'
    y = df[target_col].values
    feature_cols = [col for col in df.columns 
                   if col not in [target_col, 'energy_per_day_kwh']]
    X = df[feature_cols].values
    
    print(f"   ✅ Features: {len(feature_cols)}, Samples: {len(X)}")
    
    return X, y, feature_cols

def time_split_and_scale(X, y, test_size=0.2):
    """Time-based split and scaling"""
    split_idx = int(len(X) * (1 - test_size))
    
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"   ✅ Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   ✅ Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

#=============================================================================
# 2. EVALUATION METRICS
#=============================================================================

def calculate_metrics(y_true, y_pred, model_name="Model"):
    """Calculate and print metrics"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    print(f"\n{'='*60}")
    print(f"📊 {model_name}")
    print(f"{'='*60}")
    print(f"MAE:  {mae:.4f} kW")
    print(f"RMSE: {rmse:.4f} kW")
    print(f"R²:   {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"{'='*60}")
    
    return {'MAE': mae, 'RMSE': rmse, 'R2': r2, 'MAPE': mape}

#=============================================================================
# 3. BASELINE MODELS
#=============================================================================

def baseline_models(y_train, y_test):
    """Quick baseline models"""
    results = {}
    
    print("\n" + "="*60)
    print("📈 BASELINE MODELS")
    print("="*60)
    
    # 1. Naive Forecast
    print("\n1️⃣ Naive Forecast...")
    y_pred_naive = np.full(len(y_test), y_train[-1])
    results['Naive'] = calculate_metrics(y_test, y_pred_naive, "Naive Forecast")
    
    # 2. Moving Average
    print("\n2️⃣ Moving Average (24h)...")
    window = 24
    y_pred_ma = []
    history = list(y_train[-window:])
    
    for _ in range(len(y_test)):
        pred = np.mean(history[-window:])
        y_pred_ma.append(pred)
        history.append(pred)
    
    results['Moving Average'] = calculate_metrics(y_test, np.array(y_pred_ma), "Moving Average")
    
    return results

#=============================================================================
# 4. TRADITIONAL ML MODELS WITH PROGRESS
#=============================================================================

def train_traditional_ml(X_train, y_train, X_test, y_test):
    """Train traditional ML models with progress tracking"""
    results = {}
    models = {}
    
    print("\n" + "="*60)
    print("🤖 TRADITIONAL ML MODELS")
    print("="*60)
    
    # # 1. Random Forest
    # print("\n3️⃣ Random Forest...")
    # print("   Training 100 trees...")
    # rf_model = RandomForestRegressor(
    #     n_estimators=100,
    #     max_depth=20,
    #     min_samples_split=5,
    #     random_state=42,
    #     n_jobs=-1,
    #     verbose=0
    # )
    
    # with tqdm(total=100, desc="Training Random Forest", 
    #           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]') as pbar:
    #     # Train in chunks to show progress
    #     rf_model.fit(X_train, y_train)
    #     pbar.update(100)
    
    # y_pred_rf = rf_model.predict(X_test)
    # results['Random Forest'] = calculate_metrics(y_test, y_pred_rf, "Random Forest")
    # models['Random Forest'] = rf_model
    
    # # 2. Gradient Boosting
    # print("\n4️⃣ Gradient Boosting...")
    # print("   Training 100 trees...")
    # gb_model = GradientBoostingRegressor(
    #     n_estimators=100,
    #     learning_rate=0.1,
    #     max_depth=5,
    #     random_state=42,
    #     verbose=0
    # )
    
    # with tqdm(total=100, desc="Training Gradient Boosting", 
    #           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]') as pbar:
    #     gb_model.fit(X_train, y_train)
    #     pbar.update(100)
    
    # y_pred_gb = gb_model.predict(X_test)
    # results['Gradient Boosting'] = calculate_metrics(y_test, y_pred_gb, "Gradient Boosting")
    # models['Gradient Boosting'] = gb_model
    
    # # 3. XGBoost with proper progress tracking
    # print("\n5️⃣ XGBoost...")
    # print("   Training 100 trees...")
    
    # # Create progress bar
    # pbar = tqdm(total=100, desc="Training XGBoost", 
    #             bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]')
    
    # # Custom callback for XGBoost
    # class XGBProgressCallback(xgb.callback.TrainingCallback):
    #     def __init__(self, pbar):
    #         self.pbar = pbar
            
    #     def after_iteration(self, model, epoch, evals_log):
    #         self.pbar.update(1)
    #         return False
        
    #     def after_training(self, model):
    #         self.pbar.close()
    #         return model
    
    # xgb_model = xgb.XGBRegressor(
    #     n_estimators=100,
    #     learning_rate=0.1,
    #     max_depth=5,
    #     random_state=42,
    #     tree_method='hist'
    # )
    
    # xgb_model.fit(
    #     X_train, y_train,
    #     verbose=False,
    #     callbacks=[XGBProgressCallback(pbar)]
    # )
    
    # y_pred_xgb = xgb_model.predict(X_test)
    # results['XGBoost'] = calculate_metrics(y_test, y_pred_xgb, "XGBoost")
    # models['XGBoost'] = xgb_model
    
    # 4. LightGBM with callback
    print("\n6️⃣ LightGBM...")
    print("   Training 100 trees...")
    
    lgb_model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbose=-1
    )
    
    # Progress tracking for LightGBM
    pbar_lgb = tqdm(total=100, desc="Training LightGBM", 
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} trees [{elapsed}<{remaining}]')
    
    def lgb_callback(env):
        pbar_lgb.update(1)
    
    lgb_model.fit(
        X_train, y_train,
        callbacks=[lgb_callback]
    )
    pbar_lgb.close()
    
    y_pred_lgb = lgb_model.predict(X_test)
    results['LightGBM'] = calculate_metrics(y_test, y_pred_lgb, "LightGBM")
    models['LightGBM'] = lgb_model
    
    return results, models

#=============================================================================
# 5. DEEP LEARNING WITH PROGRESS
#=============================================================================

def create_sequences(X, y, seq_length=24):
    """Create sequences for LSTM"""
    X_seq, y_seq = [], []
    
    print(f"   Creating sequences (length={seq_length})...")
    for i in tqdm(range(len(X) - seq_length), desc="Creating sequences"):
        X_seq.append(X[i:i+seq_length])
        y_seq.append(y[i+seq_length])
    
    return np.array(X_seq), np.array(y_seq)

def build_lstm_model(input_shape):
    """Build compact LSTM model"""
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_deep_learning(X_train_scaled, y_train, X_test_scaled, y_test):
    """Train LSTM with progress tracking"""
    results = {}
    
    print("\n" + "="*60)
    print("🧠 DEEP LEARNING MODEL")
    print("="*60)
    
    # Create sequences
    seq_length = 24
    X_train_seq, y_train_seq = create_sequences(X_train_scaled, y_train, seq_length)
    X_test_seq, y_test_seq = create_sequences(X_test_scaled, y_test, seq_length)
    
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
    print("\n7️⃣ LSTM...")
    input_shape = (seq_length, X_train_scaled.shape[1])
    lstm_model = build_lstm_model(input_shape)
    
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
    
    # Custom callback for epoch progress
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
        epochs=50,
        batch_size=32,
        callbacks=[early_stop, reduce_lr, ProgressBar()],
        verbose=0
    )
    
    y_pred_lstm = lstm_model.predict(X_test_seq, verbose=0).flatten()
    results['LSTM'] = calculate_metrics(y_test_seq, y_pred_lstm, "LSTM")
    
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
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]

    top_k = min(15, len(importance))

    plt.figure(figsize=(10, 6))
    plt.bar(range(top_k), importance[indices[:top_k]])
    plt.xticks(range(top_k), [feature_names[i] for i in indices[:top_k]], rotation=45)
    plt.title(f"Feature Importance - {model_name}")
    plt.tight_layout()
    plt.show()


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
        'timestamp': datetime.now().isoformat()
    }
    
    filename = f'best_model_{model_name.replace(" ", "_").lower()}.pkl'
    joblib.dump(package, filename)
    print(f"\n   ✅ Model saved: {filename}")

def generate_report(model_name, metrics, comparison_df):
    """Generate final report"""
    report = f"""
{'='*70}
POWER CONSUMPTION FORECASTING - FINAL REPORT
{'='*70}

🏆 BEST MODEL: {model_name}
{'='*70}

📊 PERFORMANCE METRICS:
   • MAE (Mean Absolute Error):     {metrics['MAE']:.4f} kW
   • RMSE (Root Mean Squared Error): {metrics['RMSE']:.4f} kW
   • R² Score:                       {metrics['R2']:.4f}
   • MAPE (Mean Absolute % Error):   {metrics['MAPE']:.2f}%

💡 INTERPRETATION:
   • R² = {metrics['R2']:.4f} → Model explains {metrics['R2']*100:.1f}% of variance
   • Average prediction error: {metrics['MAE']:.4f} kW
   • MAPE of {metrics['MAPE']:.2f}% indicates good forecasting accuracy

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

def main_pipeline(filepath='data/cleaned_dataset.csv', run_deep_learning=False):
    """
    Main forecasting pipeline
    
    Args:
        filepath: Path to cleaned CSV
        run_deep_learning: Whether to train LSTM (slower)
    """
    
    print("\n" + "="*70)
    print("🚀 POWER CONSUMPTION FORECASTING PIPELINE")
    print("="*70 + "\n")
    
    # 1. Load and prepare data (single call)
    X, y, feature_names = load_and_prepare_data(filepath)
    X_train, X_test, y_train, y_test, scaler = time_split_and_scale(X, y)
    
    # 2. Baseline models
    baseline_results = baseline_models(y_train, y_test)
    
    # 3. Traditional ML models
    ml_results, ml_models = train_traditional_ml(X_train, y_train, X_test, y_test)
    
    # 4. Deep Learning (optional)
    dl_results = {}
    if run_deep_learning:
        dl_results, lstm_model = train_deep_learning(X_train, y_train, X_test, y_test)
    
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
    
    # Run pipeline
    print("\n🎯 Starting forecasting pipeline...")
    print("💡 Tip: Set run_deep_learning=True for LSTM (slower but might be better)")
    
    results = main_pipeline(
        filepath=DATA_PATH,
        run_deep_learning=True  # Set True to include LSTM
    )
    
    print("\n🎉 All done! Check the output files for detailed results.")
    print(f"🏆 Best Model: {results['best_model_name']}")
    print(f"📊 R² Score: {results['best_metrics']['R2']:.4f}")