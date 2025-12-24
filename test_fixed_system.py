"""
Script test toàn bộ hệ thống sau khi fix
Chạy file này để kiểm tra mọi thứ hoạt động đúng
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from datetime import datetime


def print_separator(title="", char="="):
    print("\n" + char*70)
    if title:
        print(f"  {title}")
        print(char*70)


def test_data_loader():
    """Test 1: Kiểm tra data loader"""
    print_separator("TEST 1: DATA LOADER")
    
    try:
        from src.backend.data_loader import load_dataset
        
        print("\n📊 Loading dataset...")
        df = load_dataset(nrows=10000)
        
        print(f"✅ Dataset loaded successfully")
        print(f"   • Shape: {df.shape}")
        print(f"   • Columns: {len(df.columns)}")
        
        # Kiểm tra các columns cần thiết
        required_cols = [
            'Global_active_power',
            'Global_reactive_power',
            'Voltage',
            'Global_intensity',
            'Sub_metering_1',
            'Sub_metering_2',
            'Sub_metering_3',
            'hour',
            'weekday',
            'month',
            'season',
            'rolling_5',
            'rolling_15',
            'rolling_60',
            'rolling_1440'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False
        else:
            print(f"✅ All required columns present")
        
        # Kiểm tra null values
        nulls = df.isnull().sum().sum()
        if nulls > 0:
            print(f"⚠️ Found {nulls} null values")
        else:
            print(f"✅ No null values")
        
        # Hiển thị sample
        print(f"\n📋 Sample data:")
        print(df[['Global_active_power', 'Voltage', 'Global_intensity']].head())
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_predictor():
    """Test 2: Kiểm tra predictor"""
    print_separator("TEST 2: PREDICTOR")
    
    try:
        from src.backend.predictor_fixed import EnergyPredictor
        from src.backend.data_loader import load_dataset
        
        print("\n🔮 Initializing predictor...")
        predictor = EnergyPredictor()
        
        if predictor.model is None:
            print("⚠️ Model not loaded - Running in mock mode")
        else:
            print("✅ Model loaded successfully")
        
        print("\n📊 Loading history data...")
        history_df = load_dataset(nrows=50000).tail(1440)
        
        print(f"✅ History data loaded: {len(history_df)} rows")
        
        print("\n🔮 Testing 24h prediction...")
        result_24h = predictor.predict_next_period(history_df, hours_ahead=24)
        
        print(f"✅ 24h prediction completed:")
        print(f"   • Total kWh: {result_24h['total_kwh']:.2f}")
        print(f"   • Avg power: {result_24h['avg_power_kw']:.3f} kW")
        print(f"   • Data points: {len(result_24h['predictions_kw'])}")
        
        print("\n🔮 Testing monthly prediction...")
        result_monthly = predictor.predict_monthly_consumption(history_df, days=30)
        
        print(f"✅ Monthly prediction completed:")
        print(f"   • Total kWh: {result_monthly['total_kwh']:.0f}")
        print(f"   • Daily avg: {result_monthly['daily_avg_kwh']:.2f} kWh")
        print(f"   • Peak hours: {result_monthly['peak_hours']}")
        print(f"   • Off-peak hours: {result_monthly['off_peak_hours']}")
        
        # Validate results
        if 100 <= result_monthly['total_kwh'] <= 1000:
            print(f"✅ Monthly kWh in reasonable range")
        else:
            print(f"⚠️ Monthly kWh outside typical range: {result_monthly['total_kwh']:.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_simulation():
    """Test 3: Kiểm tra simulate user pattern"""
    print_separator("TEST 3: USER SIMULATION")
    
    try:
        from src.backend.data_loader import load_dataset
        
        print("\n🏠 Testing user pattern simulation...")
        
        base_df = load_dataset(nrows=10000).tail(1440)
        
        # User params
        user_params = {
            'num_people': 4,
            'area_m2': 80,
            'num_ac': 2,
            'num_fridge': 1,
            'num_tv': 2,
            'num_washer': 1,
            'num_water_heater': 1,
            'house_type': 'Nhà phố'
        }
        
        # Simulate (copy logic từ user_page_fixed.py)
        df = base_df.copy()
        
        people_factor = user_params['num_people'] / 3
        area_factor = user_params['area_m2'] / 60
        
        df['Global_active_power'] *= (people_factor + area_factor) / 2
        df['Global_intensity'] *= (people_factor + area_factor) / 2
        df['Sub_metering_1'] *= people_factor
        df['Sub_metering_2'] *= user_params['num_washer']
        df['Sub_metering_3'] *= user_params['num_ac'] * area_factor
        
        df['Global_active_power'] = df['Global_active_power'].clip(0.1, 10.0)
        
        print(f"✅ User pattern simulated")
        print(f"   • People factor: {people_factor:.2f}")
        print(f"   • Area factor: {area_factor:.2f}")
        print(f"   • Avg power: {df['Global_active_power'].mean():.3f} kW")
        
        # So sánh trước/sau
        print(f"\n📊 Comparison:")
        print(f"   • Original avg: {base_df['Global_active_power'].mean():.3f} kW")
        print(f"   • User avg: {df['Global_active_power'].mean():.3f} kW")
        print(f"   • Ratio: {df['Global_active_power'].mean() / base_df['Global_active_power'].mean():.2f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evn_billing():
    """Test 4: Kiểm tra tính tiền EVN"""
    print_separator("TEST 4: EVN BILLING")
    
    try:
        from src.backend.logic_engine import calculate_evn_bill
        
        print("\n💰 Testing EVN bill calculation...")
        
        test_cases = [
            (100, "Low consumption"),
            (250, "Average consumption"),
            (400, "High consumption"),
            (600, "Very high consumption")
        ]
        
        for kwh, desc in test_cases:
            cost, breakdown = calculate_evn_bill(kwh)
            print(f"\n📊 {desc} ({kwh} kWh):")
            print(f"   • Total cost: {cost:,} đ")
            print(f"   • Per day: {cost/30:,.0f} đ")
            print(f"   • Per kWh: {cost/kwh:,.0f} đ")
        
        print(f"\n✅ EVN billing calculation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test 5: Integration test - toàn bộ workflow"""
    print_separator("TEST 5: INTEGRATION TEST")
    
    try:
        from src.backend.data_loader import load_dataset
        from src.backend.predictor_fixed import EnergyPredictor
        from src.backend.logic_engine import calculate_evn_bill
        
        print("\n🔄 Testing full workflow...")
        
        # 1. Load data
        print("   [1/5] Loading data...")
        base_df = load_dataset(nrows=50000).tail(1440)
        
        # 2. Simulate user
        print("   [2/5] Simulating user pattern...")
        user_params = {
            'num_people': 4,
            'area_m2': 80,
            'num_ac': 2,
            'num_washer': 1,
        }
        
        df = base_df.copy()
        people_factor = user_params['num_people'] / 3
        area_factor = user_params['area_m2'] / 60
        df['Global_active_power'] *= (people_factor + area_factor) / 2
        df['Global_intensity'] *= (people_factor + area_factor) / 2
        
        # 3. Predict
        print("   [3/5] Predicting with model...")
        predictor = EnergyPredictor()
        monthly_result = predictor.predict_monthly_consumption(df, days=30)
        
        # 4. Calculate cost
        print("   [4/5] Calculating EVN bill...")
        total_kwh = monthly_result['total_kwh']
        total_cost, breakdown = calculate_evn_bill(total_kwh)
        
        # 5. Display results
        print("   [5/5] Formatting results...")
        
        print(f"\n" + "="*70)
        print(f"  🎉 INTEGRATION TEST RESULTS")
        print(f"="*70)
        
        print(f"\n📊 Input:")
        print(f"   • {user_params['num_people']} người")
        print(f"   • {user_params['area_m2']} m²")
        print(f"   • {user_params['num_ac']} máy lạnh")
        
        print(f"\n⚡ Prediction:")
        print(f"   • Total: {total_kwh:.0f} kWh/tháng")
        print(f"   • Daily avg: {monthly_result['daily_avg_kwh']:.2f} kWh/ngày")
        print(f"   • Peak hours: {monthly_result['peak_hours']}")
        
        print(f"\n💰 Cost:")
        print(f"   • Monthly: {total_cost:,} đ")
        print(f"   • Daily: {total_cost/30:,.0f} đ")
        print(f"   • Per kWh: {total_cost/total_kwh:,.0f} đ")
        
        print(f"\n✅ Integration test PASSED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    
    print("\n" + "="*70)
    print("  🧪 ENERGY PREDICTION SYSTEM - TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    tests = [
        ("Data Loader", test_data_loader),
        ("Predictor", test_predictor),
        ("User Simulation", test_user_simulation),
        ("EVN Billing", test_evn_billing),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}")
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
        
        if results[test_name]:
            print(f"\n✅ {test_name}: PASSED")
        else:
            print(f"\n❌ {test_name}: FAILED")
        
        input("\nPress Enter to continue...")
    
    # Summary
    print_separator("SUMMARY", "=")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    if passed == total:
        print(f"\n🎉 All tests PASSED! System is ready.")
    else:
        print(f"\n⚠️ Some tests FAILED. Please check the errors above.")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()