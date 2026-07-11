#!/usr/bin/env python
"""
Comprehensive medicine database for eye care with Indian pricing
"""
import datetime

# Comprehensive medicine database with Indian pricing (INR)
COMPREHENSIVE_MEDICINE_DATABASE = {
    # === EYE DROPS ===
    # Antibiotic Eye Drops
    "Moxifloxacin Eye Drops 0.5% (Vigamox)": {
        "price": 180, "category": "Antibiotic", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Alcon", "prescription_required": True, "dosage": "1-2 drops 3 times daily",
        "indication": "Bacterial conjunctivitis", "side_effects": "Mild burning, stinging",
        "contraindications": "Hypersensitivity to quinolones", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "pharmacy.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Tobramycin Eye Drops 0.3% (Tobrex)": {
        "price": 95, "category": "Antibiotic", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Alcon", "prescription_required": True, "dosage": "1-2 drops every 4 hours",
        "indication": "Bacterial eye infections", "side_effects": "Eye irritation, redness",
        "contraindications": "Viral or fungal infections", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "medplus.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Ciprofloxacin Eye Drops 0.3% (Ciloxan)": {
        "price": 85, "category": "Antibiotic", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Alcon", "prescription_required": True, "dosage": "1-2 drops every 2 hours",
        "indication": "Bacterial conjunctivitis, corneal ulcers", "side_effects": "Burning, white deposits",
        "contraindications": "Viral infections", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "1mg.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # Anti-inflammatory Eye Drops
    "Prednisolone Acetate 1% (Pred Forte)": {
        "price": 220, "category": "Steroid", "type": "Eye Drops", "volume": "10ml",
        "manufacturer": "Allergan", "prescription_required": True, "dosage": "1-2 drops 2-4 times daily",
        "indication": "Inflammatory eye conditions", "side_effects": "Increased eye pressure, cataract",
        "contraindications": "Viral/fungal infections", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "netmeds.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Dexamethasone 0.1% (Maxidex)": {
        "price": 165, "category": "Steroid", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Alcon", "prescription_required": True, "dosage": "1-2 drops every 4-6 hours",
        "indication": "Allergic conjunctivitis, uveitis", "side_effects": "Blurred vision, eye pain",
        "contraindications": "Bacterial infections", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "apollo247.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # Glaucoma Medications
    "Latanoprost 0.005% (Xalatan)": {
        "price": 450, "category": "Glaucoma", "type": "Eye Drops", "volume": "2.5ml",
        "manufacturer": "Pfizer", "prescription_required": True, "dosage": "1 drop once daily at bedtime",
        "indication": "Open-angle glaucoma, ocular hypertension", "side_effects": "Iris color change, eyelash growth",
        "contraindications": "Pregnancy, inflammatory eye conditions", "storage": "Refrigerate",
        "expiry_months": 36, "availability": "In Stock", "source": "pharmeasy.in",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Timolol 0.5% (Timoptic)": {
        "price": 180, "category": "Glaucoma", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "MSD", "prescription_required": True, "dosage": "1 drop twice daily",
        "indication": "Glaucoma, ocular hypertension", "side_effects": "Bradycardia, bronchospasm",
        "contraindications": "Asthma, heart block", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "tata1mg.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Brimonidine 0.2% (Alphagan P)": {
        "price": 320, "category": "Glaucoma", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Allergan", "prescription_required": True, "dosage": "1 drop 2-3 times daily",
        "indication": "Glaucoma, ocular hypertension", "side_effects": "Dry mouth, fatigue",
        "contraindications": "MAO inhibitor use", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "medlife.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # Dry Eye Medications
    "Carboxymethylcellulose 0.5% (Refresh Tears)": {
        "price": 120, "category": "Lubricant", "type": "Eye Drops", "volume": "10ml",
        "manufacturer": "Allergan", "prescription_required": False, "dosage": "1-2 drops as needed",
        "indication": "Dry eyes, eye irritation", "side_effects": "Temporary blurred vision",
        "contraindications": "None known", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "amazon.in",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Hypromellose 0.3% (Tears Naturale)": {
        "price": 95, "category": "Lubricant", "type": "Eye Drops", "volume": "15ml",
        "manufacturer": "Alcon", "prescription_required": False, "dosage": "1-2 drops 3-4 times daily",
        "indication": "Dry eye syndrome", "side_effects": "Mild eye irritation",
        "contraindications": "Hypersensitivity", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "flipkart.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Sodium Hyaluronate 0.1% (Hylo-Forte)": {
        "price": 380, "category": "Lubricant", "type": "Eye Drops", "volume": "10ml",
        "manufacturer": "Ursapharm", "prescription_required": False, "dosage": "1 drop 3 times daily",
        "indication": "Severe dry eyes", "side_effects": "Temporary stinging",
        "contraindications": "None known", "storage": "Room temperature",
        "expiry_months": 12, "availability": "In Stock", "source": "lenskart.com",
        "collected_date": "2024-01-15", "generic_available": False
    },
    
    # Antihistamine Eye Drops
    "Olopatadine 0.1% (Patanol)": {
        "price": 280, "category": "Antihistamine", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Alcon", "prescription_required": True, "dosage": "1 drop twice daily",
        "indication": "Allergic conjunctivitis", "side_effects": "Headache, burning sensation",
        "contraindications": "Hypersensitivity", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "practo.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Ketotifen 0.025% (Zaditor)": {
        "price": 150, "category": "Antihistamine", "type": "Eye Drops", "volume": "5ml",
        "manufacturer": "Novartis", "prescription_required": False, "dosage": "1 drop twice daily",
        "indication": "Allergic conjunctivitis", "side_effects": "Mild eye irritation",
        "contraindications": "Contact lens wear", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "healthkart.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # === ORAL MEDICATIONS ===
    # Pain Relief
    "Ibuprofen 400mg (Brufen)": {
        "price": 45, "category": "NSAID", "type": "Tablet", "volume": "10 tablets",
        "manufacturer": "Abbott", "prescription_required": False, "dosage": "1 tablet 2-3 times daily",
        "indication": "Eye pain, inflammation", "side_effects": "Stomach upset, dizziness",
        "contraindications": "Peptic ulcer, kidney disease", "storage": "Room temperature",
        "expiry_months": 36, "availability": "In Stock", "source": "local_pharmacy",
        "collected_date": "2024-01-15", "generic_available": True
    },
    "Paracetamol 500mg (Crocin)": {
        "price": 25, "category": "Analgesic", "type": "Tablet", "volume": "10 tablets",
        "manufacturer": "GSK", "prescription_required": False, "dosage": "1-2 tablets every 6 hours",
        "indication": "Pain, fever", "side_effects": "Rare at normal doses",
        "contraindications": "Liver disease", "storage": "Room temperature",
        "expiry_months": 36, "availability": "In Stock", "source": "local_pharmacy",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # Antibiotics (Oral)
    "Azithromycin 500mg (Zithromax)": {
        "price": 180, "category": "Antibiotic", "type": "Tablet", "volume": "3 tablets",
        "manufacturer": "Pfizer", "prescription_required": True, "dosage": "1 tablet daily for 3 days",
        "indication": "Bacterial infections", "side_effects": "Nausea, diarrhea",
        "contraindications": "Liver disease", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "apollo_pharmacy",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    # Vitamins and Supplements
    "Vitamin A 25000 IU (Aquasol A)": {
        "price": 120, "category": "Vitamin", "type": "Capsule", "volume": "30 capsules",
        "manufacturer": "Mayne Pharma", "prescription_required": False, "dosage": "1 capsule daily",
        "indication": "Vitamin A deficiency, night blindness", "side_effects": "Nausea, headache",
        "contraindications": "Pregnancy, liver disease", "storage": "Room temperature",
        "expiry_months": 24, "availability": "In Stock", "source": "healthkart.com",
        "collected_date": "2024-01-15", "generic_available": True
    },
    
    "Omega-3 Fish Oil (Maxepa)": {
        "price": 350, "category": "Supplement", "type": "Capsule", "volume": "30 capsules",
        "manufacturer": "Seven Seas", "prescription_required": False, "dosage": "1-2 capsules daily",
        "indication": "Dry eyes, general eye health", "side_effects": "Fishy aftertaste, nausea",
        "contraindications": "Fish allergy", "storage": "Room temperature",
        "expiry_months": 18, "availability": "In Stock", "source": "amazon.in",
        "collected_date": "2024-01-15", "generic_available": True
    }

}


def get_medicines_by_category(category="All"):
    """Get medicines filtered by category"""
    if category == "All":
        return COMPREHENSIVE_MEDICINE_DATABASE
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if v["category"] == category}

def get_medicines_by_price_range(min_price=0, max_price=1000):
    """Get medicines filtered by price range in INR"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if min_price <= v["price"] <= max_price}

def get_prescription_required_medicines():
    """Get medicines that require prescription"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if v["prescription_required"]}

def get_otc_medicines():
    """Get over-the-counter medicines"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if not v["prescription_required"]}

def search_medicines_by_indication(indication):
    """Search medicines by medical indication"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if indication.lower() in v["indication"].lower()}

def get_medicines_by_type(med_type):
    """Get medicines by type (Eye Drops, Tablet, etc.)"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if v["type"] == med_type}

def get_expiring_medicines(months=6):
    """Get medicines expiring within specified months"""
    return {k: v for k, v in COMPREHENSIVE_MEDICINE_DATABASE.items() 
            if v["expiry_months"] <= months}

def get_medicine_recommendations_by_condition(condition, age=30):
    """Get medicine recommendations based on condition and age"""
    
    condition_mapping = {
        "dry_eyes": ["Carboxymethylcellulose 0.5% (Refresh Tears)", 
                    "Hypromellose 0.3% (Tears Naturale)",
                    "Sodium Hyaluronate 0.1% (Hylo-Forte)"],
        "bacterial_infection": ["Moxifloxacin Eye Drops 0.5% (Vigamox)",
                              "Tobramycin Eye Drops 0.3% (Tobrex)",
                              "Ciprofloxacin Eye Drops 0.3% (Ciloxan)"],
        "allergic_conjunctivitis": ["Olopatadine 0.1% (Patanol)",
                                  "Ketotifen 0.025% (Zaditor)",
                                  "Dexamethasone 0.1% (Maxidex)"],
        "glaucoma": ["Latanoprost 0.005% (Xalatan)",
                    "Timolol 0.5% (Timoptic)",
                    "Brimonidine 0.2% (Alphagan P)"],
        "inflammation": ["Prednisolone Acetate 1% (Pred Forte)",
                        "Dexamethasone 0.1% (Maxidex)",
                        "Ibuprofen 400mg (Brufen)"]
    }
    
    recommended_medicines = condition_mapping.get(condition.lower(), [])
    
    # Age-based filtering
    if age > 65:
        # Avoid certain medications for elderly
        recommended_medicines = [med for med in recommended_medicines 
                               if "Timolol" not in med]  # Avoid beta-blockers in elderly
    
    return {med: COMPREHENSIVE_MEDICINE_DATABASE[med] 
            for med in recommended_medicines 
            if med in COMPREHENSIVE_MEDICINE_DATABASE}

def calculate_treatment_cost(medicines_list, duration_days=7):
    """Calculate total treatment cost for given medicines and duration"""
    
    total_cost = 0
    cost_breakdown = {}
    
    for med_name in medicines_list:
        if med_name in COMPREHENSIVE_MEDICINE_DATABASE:
            med_data = COMPREHENSIVE_MEDICINE_DATABASE[med_name]
            med_cost = med_data["price"]
            
            # Estimate quantity needed based on duration
            if med_data["type"] == "Eye Drops":
                # Assume 1 bottle lasts 7-10 days
                bottles_needed = max(1, duration_days // 7)
                total_med_cost = med_cost * bottles_needed
            elif med_data["type"] in ["Tablet", "Capsule"]:
                # Calculate based on dosage
                if "twice daily" in med_data["dosage"]:
                    tablets_needed = duration_days * 2
                elif "3 times daily" in med_data["dosage"]:
                    tablets_needed = duration_days * 3
                else:
                    tablets_needed = duration_days
                
                # Assume 10 tablets per pack
                packs_needed = max(1, tablets_needed // 10)
                total_med_cost = med_cost * packs_needed
            else:
                total_med_cost = med_cost
            
            cost_breakdown[med_name] = total_med_cost
            total_cost += total_med_cost
    
    return {
        "total_cost": total_cost,
        "breakdown": cost_breakdown,
        "duration_days": duration_days
    }