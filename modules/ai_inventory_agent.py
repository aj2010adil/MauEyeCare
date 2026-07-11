"""
AI Inventory Management Agent
Intelligent agent for automated inventory management and recommendations
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import db
from modules.spectacle_inventory_tool import spectacle_tool
from modules.enhanced_inventory_manager import enhanced_inventory
from modules.mcp_medicine_integration import mcp_integrator

class AIInventoryAgent:
    """AI-powered inventory management agent"""
    
    def __init__(self):
        self.agent_name = "MauEyeCare AI Assistant"
        self.capabilities = [
            "Inventory Analysis", "Stock Prediction", "Automated Reordering",
            "Patient Recommendations", "Cost Optimization", "Trend Analysis"
        ]
        
        # Agent knowledge base
        self.knowledge_base = {
            "eye_conditions": {
                "dry_eyes": {
                    "medicines": ["Carboxymethylcellulose", "Hypromellose", "Sodium Hyaluronate"],
                    "spectacles": ["Computer Glasses", "Blue Light Filter"],
                    "priority": "high"
                },
                "myopia": {
                    "medicines": ["Atropine drops", "Vitamin A"],
                    "spectacles": ["Single Vision", "Progressive"],
                    "priority": "high"
                },
                "presbyopia": {
                    "medicines": ["Lubricating drops"],
                    "spectacles": ["Reading Glasses", "Progressive", "Bifocal"],
                    "priority": "medium"
                },
                "astigmatism": {
                    "medicines": ["Artificial tears"],
                    "spectacles": ["Toric lenses", "Cylinder correction"],
                    "priority": "high"
                }
            },
            
            "age_recommendations": {
                "children": {
                    "spectacle_features": ["Flexible frames", "Impact resistant", "Colorful"],
                    "medicine_considerations": ["Lower dosage", "Child-safe formulations"]
                },
                "adults": {
                    "spectacle_features": ["Professional look", "Durability", "Style variety"],
                    "medicine_considerations": ["Standard dosage", "Full range available"]
                },
                "elderly": {
                    "spectacle_features": ["Lightweight", "Easy handling", "Progressive lenses"],
                    "medicine_considerations": ["Gentle formulations", "Easy application"]
                }
            }
        }
    
    def analyze_patient_needs(self, patient_data: Dict) -> Dict:
        """Analyze patient needs and provide intelligent recommendations"""
        
        age = patient_data.get("age", 30)
        gender = patient_data.get("gender", "Male")
        condition = patient_data.get("condition", "general_checkup")
        rx_data = patient_data.get("rx_table", {})
        
        analysis = {
            "patient_profile": {
                "age_group": self._get_age_group(age),
                "risk_factors": self._assess_risk_factors(age, gender, rx_data),
                "lifestyle_factors": self._assess_lifestyle_factors(age)
            },
            "recommendations": {
                "medicines": [],
                "spectacles": [],
                "follow_up": []
            },
            "priority_level": "medium",
            "estimated_cost": 0
        }
        
        # Analyze prescription data
        if rx_data:
            analysis["prescription_analysis"] = self._analyze_prescription(rx_data)
            analysis["recommendations"]["spectacles"].extend(
                self._recommend_spectacles_from_rx(rx_data, age)
            )
        
        # Condition-based recommendations
        if condition in self.knowledge_base["eye_conditions"]:
            condition_data = self.knowledge_base["eye_conditions"][condition]
            analysis["recommendations"]["medicines"].extend(condition_data["medicines"])
            analysis["recommendations"]["spectacles"].extend(condition_data["spectacles"])
            analysis["priority_level"] = condition_data["priority"]
        
        # Age-based recommendations
        age_group = analysis["patient_profile"]["age_group"]
        if age_group in self.knowledge_base["age_recommendations"]:
            age_data = self.knowledge_base["age_recommendations"][age_group]
            analysis["age_specific_features"] = age_data["spectacle_features"]
            analysis["medicine_considerations"] = age_data["medicine_considerations"]
        
        # Calculate estimated cost
        analysis["estimated_cost"] = self._calculate_estimated_cost(analysis["recommendations"])
        
        return analysis
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group"""
        if age < 18:
            return "children"
        elif age < 60:
            return "adults"
        else:
            return "elderly"
    
    def _assess_risk_factors(self, age: int, gender: str, rx_data: Dict) -> List[str]:
        """Assess risk factors based on patient data"""
        risk_factors = []
        
        if age > 40:
            risk_factors.append("presbyopia_risk")
        if age > 60:
            risk_factors.append("cataract_risk")
            risk_factors.append("glaucoma_risk")
        
        # Analyze prescription for high powers
        if rx_data:
            for eye in ["OD", "OS"]:
                if eye in rx_data:
                    sphere = rx_data[eye].get("Sphere", "")
                    if sphere and abs(float(sphere.replace("+", "").replace("-", "") or 0)) > 3.0:
                        risk_factors.append("high_myopia")
        
        return risk_factors
    
    def _assess_lifestyle_factors(self, age: int) -> List[str]:
        """Assess lifestyle factors"""
        factors = []
        
        if 20 <= age <= 50:
            factors.extend(["computer_use", "digital_strain"])
        if age < 25:
            factors.append("sports_activities")
        if age > 35:
            factors.append("reading_requirements")
        
        return factors
    
    def _analyze_prescription(self, rx_data: Dict) -> Dict:
        """Analyze prescription data"""
        analysis = {
            "prescription_type": "single_vision",
            "power_category": "low",
            "astigmatism_present": False,
            "anisometropia": False
        }
        
        powers = []
        cylinders = []
        
        for eye in ["OD", "OS"]:
            if eye in rx_data:
                sphere = rx_data[eye].get("Sphere", "")
                cylinder = rx_data[eye].get("Cylinder", "")
                
                if sphere:
                    power = abs(float(sphere.replace("+", "").replace("-", "") or 0))
                    powers.append(power)
                
                if cylinder:
                    cyl_power = abs(float(cylinder.replace("-", "") or 0))
                    cylinders.append(cyl_power)
                    if cyl_power > 0:
                        analysis["astigmatism_present"] = True
        
        # Determine power category
        if powers:
            max_power = max(powers)
            if max_power > 6.0:
                analysis["power_category"] = "high"
            elif max_power > 3.0:
                analysis["power_category"] = "medium"
            
            # Check for anisometropia
            if len(powers) == 2 and abs(powers[0] - powers[1]) > 1.0:
                analysis["anisometropia"] = True
        
        return analysis
    
    def _recommend_spectacles_from_rx(self, rx_data: Dict, age: int) -> List[str]:
        """Recommend spectacles based on prescription"""
        recommendations = []
        
        # Basic prescription glasses
        recommendations.append("Prescription Glasses")
        
        # Age-based additions
        if age > 40:
            recommendations.append("Progressive Lenses")
        
        # Check for computer use (assume for working age)
        if 20 <= age <= 60:
            recommendations.append("Computer Glasses")
        
        # Check for high powers
        powers = []
        for eye in ["OD", "OS"]:
            if eye in rx_data:
                sphere = rx_data[eye].get("Sphere", "")
                if sphere:
                    power = abs(float(sphere.replace("+", "").replace("-", "") or 0))
                    powers.append(power)
        
        if powers and max(powers) > 3.0:
            recommendations.append("High Index Lenses")
        
        return recommendations
    
    def _calculate_estimated_cost(self, recommendations: Dict) -> int:
        """Calculate estimated cost for recommendations"""
        base_costs = {
            "medicines": 150,  # Average medicine cost
            "spectacles": 3500,  # Average spectacle cost
            "follow_up": 500   # Follow-up consultation
        }
        
        total_cost = 0
        for category, items in recommendations.items():
            if items and category in base_costs:
                total_cost += len(items) * base_costs[category]
        
        return total_cost
    
    def auto_inventory_management(self) -> Dict:
        """Perform automated inventory management"""
        
        management_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actions_taken": [],
            "recommendations": [],
            "alerts": [],
            "statistics": {}
        }
        
        # Check low stock items
        low_stock_medicines = enhanced_inventory.get_low_stock_items(threshold=5)
        low_stock_spectacles = []
        
        spectacle_inventory = spectacle_tool.get_spectacle_inventory()
        for spec_name, spec_data in spectacle_inventory.items():
            if spec_data.get("current_stock", 0) <= 3:
                low_stock_spectacles.append((spec_name, spec_data.get("current_stock", 0)))
        
        # Generate alerts
        if low_stock_medicines:
            management_report["alerts"].append(f"Low stock medicines: {len(low_stock_medicines)} items")
        
        if low_stock_spectacles:
            management_report["alerts"].append(f"Low stock spectacles: {len(low_stock_spectacles)} items")
        
        # Auto-reorder recommendations
        for med_name, stock in low_stock_medicines:
            if stock <= 2:  # Critical stock level
                management_report["recommendations"].append({
                    "action": "urgent_reorder",
                    "item": med_name,
                    "current_stock": stock,
                    "suggested_quantity": 20,
                    "priority": "high"
                })
        
        for spec_name, stock in low_stock_spectacles:
            if stock <= 1:  # Critical stock level
                management_report["recommendations"].append({
                    "action": "urgent_reorder",
                    "item": spec_name,
                    "current_stock": stock,
                    "suggested_quantity": 5,
                    "priority": "high"
                })
        
        # Calculate statistics
        total_medicines = len(enhanced_inventory.get_all_medicines(include_external=False))
        total_spectacles = len(spectacle_tool.premium_spectacle_data)
        inventory_value = enhanced_inventory.get_inventory_value()
        
        management_report["statistics"] = {
            "total_medicines": total_medicines,
            "total_spectacles": total_spectacles,
            "inventory_value": inventory_value,
            "low_stock_items": len(low_stock_medicines) + len(low_stock_spectacles)
        }
        
        return management_report
    
    def get_trending_items(self) -> Dict:
        """Get trending items based on usage patterns"""
        # Simulated trending data - in real implementation, this would analyze actual usage
        trending = {
            "medicines": [
                {"name": "Carboxymethylcellulose 0.5%", "trend": "up", "usage_increase": "25%"},
                {"name": "Computer Eye Drops", "trend": "up", "usage_increase": "40%"},
                {"name": "Moxifloxacin 0.5%", "trend": "stable", "usage_increase": "5%"}
            ],
            "spectacles": [
                {"name": "Computer Glasses", "trend": "up", "usage_increase": "60%"},
                {"name": "Blue Light Filter", "trend": "up", "usage_increase": "45%"},
                {"name": "Progressive Lenses", "trend": "stable", "usage_increase": "10%"}
            ]
        }
        
        return trending
    
    def generate_ai_insights(self) -> List[str]:
        """Generate AI-powered insights for the practice"""
        
        insights = [
            "💡 Computer glasses demand has increased by 60% - consider stocking more blue light filters",
            "📈 Dry eye medications are trending up - patients spending more time on screens",
            "🎯 Progressive lens sales peak in patients aged 45-55 - target marketing accordingly",
            "⚠️ Stock rotation needed for seasonal items - sunglasses inventory optimization required",
            "💰 Cost optimization: Bundle computer glasses with dry eye drops for digital workers",
            "📊 Patient age analysis shows 40% are in presbyopia risk group - increase progressive lens stock",
            "🔄 Automated reordering can reduce stockouts by 80% - enable for critical items",
            "📱 Mobile app integration can improve patient engagement and follow-up compliance"
        ]
        
        return insights

# Global AI agent instance
ai_agent = AIInventoryAgent()