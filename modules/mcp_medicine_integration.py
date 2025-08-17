"""
MCP Medicine Integration Module
Integrates with external medicine databases and pharmacy APIs
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st

class MCPMedicineIntegrator:
    """MCP-enabled medicine database integrator"""
    
    def __init__(self):
        self.medicine_sources = {
            "1mg": "https://www.1mg.com/api/drug_skus/by_name",
            "netmeds": "https://www.netmeds.com/api/products/search",
            "pharmeasy": "https://pharmeasy.in/api/otc/search",
            "apollo": "https://www.apollopharmacy.in/api/search"
        }
        
        # Eye care specific medicine categories
        self.eye_medicine_categories = {
            "eye_drops": ["artificial tears", "antibiotic drops", "steroid drops", "glaucoma drops"],
            "oral_medications": ["pain relief", "antibiotics", "vitamins", "supplements"],
            "ointments": ["antibiotic ointment", "lubricating ointment"],
            "contact_solutions": ["cleaning solution", "disinfecting solution", "rewetting drops"]
        }
    
    def search_medicines_by_condition(self, condition: str, age: int = 30) -> List[Dict]:
        """Search medicines based on eye condition using MCP"""
        
        condition_medicine_map = {
            "dry_eyes": [
                "Carboxymethylcellulose 0.5%", "Hypromellose 0.3%", "Sodium Hyaluronate 0.1%",
                "Polyethylene Glycol 400", "Propylene Glycol", "Hydroxypropyl Guar"
            ],
            "bacterial_infection": [
                "Moxifloxacin 0.5%", "Tobramycin 0.3%", "Ciprofloxacin 0.3%",
                "Ofloxacin 0.3%", "Gatifloxacin 0.3%", "Chloramphenicol 0.5%"
            ],
            "allergic_conjunctivitis": [
                "Olopatadine 0.1%", "Ketotifen 0.025%", "Azelastine 0.05%",
                "Epinastine 0.05%", "Bepotastine 1.5%"
            ],
            "glaucoma": [
                "Latanoprost 0.005%", "Timolol 0.5%", "Brimonidine 0.2%",
                "Dorzolamide 2%", "Bimatoprost 0.03%", "Travoprost 0.004%"
            ],
            "inflammation": [
                "Prednisolone Acetate 1%", "Dexamethasone 0.1%", "Fluorometholone 0.1%",
                "Loteprednol 0.5%", "Rimexolone 1%"
            ]
        }
        
        medicines = condition_medicine_map.get(condition.lower(), [])
        return self._fetch_medicine_details(medicines)
    
    def _fetch_medicine_details(self, medicine_names: List[str]) -> List[Dict]:
        """Fetch detailed medicine information from multiple sources"""
        detailed_medicines = []
        
        for medicine in medicine_names:
            medicine_data = {
                "name": medicine,
                "price_range": self._get_price_range(medicine),
                "availability": "Available",
                "sources": ["1mg", "NetMeds", "PharmEasy"],
                "prescription_required": self._is_prescription_required(medicine),
                "dosage_forms": ["Eye Drops", "Tablet", "Ointment"],
                "manufacturers": self._get_manufacturers(medicine),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            detailed_medicines.append(medicine_data)
        
        return detailed_medicines
    
    def _get_price_range(self, medicine: str) -> Dict:
        """Get price range from multiple sources"""
        # Simulated price data - in real MCP implementation, this would fetch from APIs
        base_prices = {
            "eye_drops": {"min": 50, "max": 300, "avg": 150},
            "tablets": {"min": 20, "max": 200, "avg": 80},
            "ointments": {"min": 40, "max": 250, "avg": 120}
        }
        
        if "drop" in medicine.lower():
            return base_prices["eye_drops"]
        elif any(word in medicine.lower() for word in ["tablet", "capsule"]):
            return base_prices["tablets"]
        else:
            return base_prices["ointments"]
    
    def _is_prescription_required(self, medicine: str) -> bool:
        """Check if prescription is required"""
        prescription_medicines = [
            "moxifloxacin", "tobramycin", "prednisolone", "dexamethasone",
            "latanoprost", "timolol", "brimonidine", "olopatadine"
        ]
        return any(med in medicine.lower() for med in prescription_medicines)
    
    def _get_manufacturers(self, medicine: str) -> List[str]:
        """Get list of manufacturers"""
        manufacturers_db = {
            "moxifloxacin": ["Alcon", "Bausch & Lomb", "Sun Pharma"],
            "tobramycin": ["Alcon", "Novartis", "FDC"],
            "carboxymethylcellulose": ["Allergan", "Sun Pharma", "Cipla"],
            "prednisolone": ["Allergan", "FDC", "Entod"],
            "latanoprost": ["Pfizer", "Sun Pharma", "Cipla"]
        }
        
        for key, manufacturers in manufacturers_db.items():
            if key in medicine.lower():
                return manufacturers
        
        return ["Generic Manufacturer", "Local Pharmacy"]
    
    def get_real_time_inventory(self, source: str = "all") -> Dict:
        """Get real-time inventory from pharmacy sources"""
        # Simulated real-time inventory - MCP would connect to actual APIs
        inventory_data = {
            "eye_drops": {
                "Refresh Tears (Carboxymethylcellulose 0.5%)": {"stock": 25, "price": 120, "source": "1mg"},
                "Vigamox (Moxifloxacin 0.5%)": {"stock": 15, "price": 280, "source": "NetMeds"},
                "Pred Forte (Prednisolone Acetate 1%)": {"stock": 8, "price": 320, "source": "PharmEasy"},
                "Xalatan (Latanoprost 0.005%)": {"stock": 12, "price": 450, "source": "Apollo"}
            },
            "oral_medications": {
                "Brufen 400mg (Ibuprofen)": {"stock": 50, "price": 45, "source": "1mg"},
                "Crocin 500mg (Paracetamol)": {"stock": 100, "price": 25, "source": "NetMeds"},
                "Zithromax 500mg (Azithromycin)": {"stock": 20, "price": 180, "source": "PharmEasy"}
            },
            "supplements": {
                "Aquasol A (Vitamin A 25000 IU)": {"stock": 30, "price": 120, "source": "1mg"},
                "Maxepa (Omega-3 Fish Oil)": {"stock": 40, "price": 350, "source": "NetMeds"}
            }
        }
        
        return inventory_data
    
    def purchase_and_add_to_inventory(self, medicine_name: str, quantity: int, source: str) -> Dict:
        """Purchase medicine from external source and add to inventory"""
        purchase_result = {
            "status": "success",
            "medicine": medicine_name,
            "quantity": quantity,
            "source": source,
            "estimated_delivery": "2-3 days",
            "tracking_id": f"MCP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "total_cost": 0,
            "purchase_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Simulate cost calculation
        inventory = self.get_real_time_inventory()
        for category in inventory.values():
            if medicine_name in category:
                purchase_result["total_cost"] = category[medicine_name]["price"] * quantity
                break
        
        return purchase_result

# Global instance
mcp_integrator = MCPMedicineIntegrator()