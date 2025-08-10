"""
LangGraph Agent for MauEyeCare with tools for PDF generation, market data, and inventory management
"""
import json
import requests
from typing import Dict, List, Any
# LangGraph imports with fallback
try:
    from langgraph.graph import StateGraph, END
    from langchain_core.tools import BaseTool
    from langchain_core.messages import HumanMessage, AIMessage
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create dummy classes for fallback
    class BaseTool:
        def __init__(self):
            self.name = ""
            self.description = ""
        def _run(self, *args, **kwargs):
            return "LangGraph not available"
    
    class StateGraph:
        def __init__(self, *args): pass
        def add_node(self, *args): pass
        def add_edge(self, *args): pass
        def add_conditional_edges(self, *args): pass
        def set_entry_point(self, *args): pass
        def compile(self): return self
        def invoke(self, state): return state
    
    END = "end"
    def add_messages(x): return x
import db
from modules.pdf_utils import generate_pdf

class PDFGeneratorTool(BaseTool):
    name: str = "pdf_generator"
    description: str = "Generate prescription PDF for patients"
    
    def _run(self, patient_data: Dict) -> str:
        try:
            pdf_bytes = generate_pdf(
                patient_data.get('prescription', {}),
                patient_data.get('dosage', ''),
                patient_data.get('eye_test', ''),
                patient_data.get('doctor_name', 'Dr Danish'),
                patient_data.get('patient_name', ''),
                patient_data.get('age', 0),
                patient_data.get('gender', ''),
                patient_data.get('advice', ''),
                patient_data.get('rx_table', {}),
                patient_data.get('recommendations', [])
            )
            return f"PDF generated successfully for {patient_data.get('patient_name', 'patient')}"
        except Exception as e:
            return f"Error generating PDF: {str(e)}"

class MarketDataTool(BaseTool):
    name: str = "market_data_fetcher"
    description: str = "Fetch latest spectacles and medicines data from market"
    
    def _run(self, query: str) -> str:
        # Simulated market data - in real implementation, connect to actual APIs
        market_data = {
            "spectacles": [
                {"name": "Ray-Ban Aviator", "price": 150, "stock": 25},
                {"name": "Oakley Holbrook", "price": 120, "stock": 30},
                {"name": "Progressive Lens", "price": 200, "stock": 15},
                {"name": "Blue Light Filter", "price": 80, "stock": 40},
                {"name": "Photochromic Lens", "price": 180, "stock": 20}
            ],
            "medicines": [
                {"name": "Latanoprost Eye Drops", "price": 25, "stock": 50},
                {"name": "Timolol Eye Drops", "price": 15, "stock": 35},
                {"name": "Artificial Tears", "price": 10, "stock": 100},
                {"name": "Antibiotic Eye Drops", "price": 20, "stock": 60}
            ]
        }
        
        if "spectacles" in query.lower():
            return json.dumps(market_data["spectacles"])
        elif "medicines" in query.lower():
            return json.dumps(market_data["medicines"])
        else:
            return json.dumps(market_data)

class InventoryManagerTool(BaseTool):
    name: str = "inventory_manager"
    description: str = "Update inventory with latest market data"
    
    def _run(self, action_data: Dict) -> str:
        try:
            action = action_data.get('action', 'update')
            items = action_data.get('items', [])
            
            if action == 'update':
                for item in items:
                    db.update_inventory(item['name'], item['stock'])
                return f"Updated {len(items)} items in inventory"
            
            elif action == 'check_low_stock':
                inventory = db.get_inventory()
                low_stock = [item for item in inventory if item[1] < 10]
                return f"Low stock items: {low_stock}"
            
            return "Inventory action completed"
        except Exception as e:
            return f"Error managing inventory: {str(e)}"

class PatientDataTool(BaseTool):
    name: str = "patient_data_reader"
    description: str = "Read latest patient data and history"
    
    def _run(self, patient_id: int) -> str:
        try:
            # Get patient info
            patients = db.get_patients()
            patient = next((p for p in patients if p[0] == patient_id), None)
            
            if not patient:
                return "Patient not found"
            
            # Get prescription history
            prescriptions = db.get_prescriptions(patient_id)
            
            # Get medical tests
            try:
                medical_tests = db.get_medical_tests(patient_id)
            except:
                medical_tests = []
            
            data = {
                "patient_info": {
                    "name": patient[1],
                    "age": patient[2],
                    "gender": patient[3],
                    "contact": patient[4]
                },
                "recent_prescriptions": len(prescriptions),
                "recent_tests": len(medical_tests)
            }
            
            return json.dumps(data)
        except Exception as e:
            return f"Error reading patient data: {str(e)}"

# Agent State
from typing import TypedDict

if LANGGRAPH_AVAILABLE:
    from typing import Annotated
    class AgentState(TypedDict):
        messages: Annotated[list, add_messages]
        current_task: str
        results: dict
else:
    class AgentState(TypedDict):
        messages: list
        current_task: str
        results: dict

# Create tools
tools = [
    PDFGeneratorTool(),
    MarketDataTool(),
    InventoryManagerTool(),
    PatientDataTool()
]

# Simple tool executor
class SimpleToolExecutor:
    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}
    
    def invoke(self, tool_call):
        tool_name = tool_call.get('tool') if isinstance(tool_call, dict) else tool_call.tool
        tool_input = tool_call.get('tool_input') if isinstance(tool_call, dict) else tool_call.tool_input
        
        if tool_name in self.tools:
            return self.tools[tool_name]._run(tool_input)
        return f"Tool {tool_name} not found"

tool_executor = SimpleToolExecutor(tools)

def should_continue(state: AgentState) -> str:
    """Decide whether to continue or end"""
    if len(state["messages"]) > 10:  # Prevent infinite loops
        return "end"
    
    last_message = state["messages"][-1] if state["messages"] else None
    if last_message and "completed" in str(last_message).lower():
        return "end"
    
    return "continue"

def call_model(state: AgentState) -> AgentState:
    """Main agent logic"""
    if not state.get("current_task"):
        return state
    
    task = state["current_task"]
    
    # Route to appropriate tool based on task
    if "pdf" in task.lower():
        tool_call = {
            "tool": "pdf_generator",
            "tool_input": state.get("results", {}).get('patient_data', {})
        }
    elif "market" in task.lower() or "latest" in task.lower():
        tool_call = {
            "tool": "market_data_fetcher",
            "tool_input": task
        }
    elif "inventory" in task.lower():
        tool_call = {
            "tool": "inventory_manager",
            "tool_input": {"action": "check_low_stock", "items": []}
        }
    elif "patient" in task.lower():
        tool_call = {
            "tool": "patient_data_reader",
            "tool_input": state.get("results", {}).get('patient_id', 1)
        }
    else:
        state["messages"].append(AIMessage(content="Task not recognized"))
        return state
    
    # Execute tool
    result = tool_executor.invoke(tool_call)
    if "results" not in state:
        state["results"] = {}
    state["results"][tool_call["tool"]] = result
    state["messages"].append(AIMessage(content=f"Tool {tool_call['tool']} executed: {result}"))
    
    return state

def call_tool(state: AgentState) -> AgentState:
    """Execute tools based on agent decisions"""
    return state

# Create the graph with fallback
if LANGGRAPH_AVAILABLE:
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tool)
    workflow.add_edge("agent", "action")
    workflow.add_conditional_edges(
        "action",
        should_continue,
        {
            "continue": "agent",
            "end": END
        }
    )
    workflow.set_entry_point("agent")
    app = workflow.compile()
else:
    app = StateGraph()

class MauEyeCareAgent:
    def __init__(self):
        self.app = app
    
    def execute_task(self, task: str, context: Dict = None) -> str:
        """Execute a task using the LangGraph agent"""
        state = {
            "messages": [],
            "current_task": task,
            "results": context or {}
        }
        
        try:
            final_state = self.app.invoke(state)
            return final_state.get("results", {})
        except Exception as e:
            return f"Agent execution error: {str(e)}"
    
    def update_inventory_from_market(self) -> str:
        """Update inventory with latest market data"""
        # Get market data
        market_result = self.execute_task("fetch latest spectacles and medicines market data")
        
        # Update inventory
        inventory_result = self.execute_task("update inventory", {"market_data": market_result})
        
        return f"Inventory updated: {inventory_result}"
    
    def generate_patient_pdf(self, patient_data: Dict) -> str:
        """Generate PDF for patient"""
        return self.execute_task("generate pdf", {"patient_data": patient_data})
    
    def check_low_stock(self) -> str:
        """Check for low stock items"""
        return self.execute_task("check inventory low stock")
    
    def get_patient_summary(self, patient_id: int) -> str:
        """Get patient data summary"""
        return self.execute_task("read patient data", {"patient_id": patient_id})

# Global agent instance
mau_agent = MauEyeCareAgent()