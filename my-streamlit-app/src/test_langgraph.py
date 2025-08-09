"""
Test LangGraph functionality
"""
from langgraph_agent import mau_agent
from market_updater import market_updater

def test_langgraph_agent():
    """Test LangGraph agent functionality"""
    print("Testing LangGraph Agent...")
    
    try:
        # Test PDF generation task
        result = mau_agent.execute_task("Generate PDF for patient", {
            "patient_data": {
                "patient_name": "Test Patient",
                "age": 30,
                "gender": "Male",
                "prescription": {"Test Medicine": 1},
                "advice": "Test advice",
                "rx_table": {},
                "recommendations": []
            }
        })
        print(f"[OK] PDF generation task: {result}")
        
        # Test market data task
        result = mau_agent.execute_task("Fetch latest market data")
        print(f"[OK] Market data task: {result}")
        
        # Test inventory task
        result = mau_agent.execute_task("Check low stock items")
        print(f"[OK] Inventory task: {result}")
        
        return True
    except Exception as e:
        print(f"[ERROR] LangGraph agent failed: {e}")
        return False

def test_market_updater():
    """Test market updater functionality"""
    print("\nTesting Market Updater...")
    
    try:
        # Test market data update
        result = market_updater.update_inventory_from_market()
        print(f"[OK] Market update: {result}")
        
        # Test low stock check
        low_stock = market_updater.check_low_stock_alerts()
        print(f"[OK] Low stock check: {len(low_stock)} items")
        
        # Test market trends
        trends = market_updater.get_market_trends()
        print(f"[OK] Market trends: {len(trends)} categories")
        
        return True
    except Exception as e:
        print(f"[ERROR] Market updater failed: {e}")
        return False

def main():
    """Run LangGraph tests"""
    print("=" * 50)
    print("MauEyeCare LangGraph Test")
    print("=" * 50)
    
    agent_success = test_langgraph_agent()
    market_success = test_market_updater()
    
    print("\n" + "=" * 50)
    print("LangGraph Test Results:")
    print(f"[{'OK' if agent_success else 'ERROR'}] LangGraph Agent: {'Working' if agent_success else 'Failed'}")
    print(f"[{'OK' if market_success else 'ERROR'}] Market Updater: {'Working' if market_success else 'Failed'}")
    print("=" * 50)
    
    if agent_success and market_success:
        print("SUCCESS: LangGraph functionality is working!")
        print("Ready to run full Streamlit app with AI features")
    else:
        print("WARNING: Some LangGraph features need attention")

if __name__ == "__main__":
    main()