#!/usr/bin/env python
"""
Real spectacle inventory data from popular brands and websites
"""

# Real spectacle data from popular brands
REAL_SPECTACLE_INVENTORY = {
    # Ray-Ban Collection
    "Ray-Ban Aviator Classic RB3025": {"price": 150, "category": "Sunglasses", "material": "Metal", "shape": "Aviator"},
    "Ray-Ban Wayfarer RB2140": {"price": 120, "category": "Sunglasses", "material": "Acetate", "shape": "Square"},
    "Ray-Ban Round Metal RB3447": {"price": 140, "category": "Sunglasses", "material": "Metal", "shape": "Round"},
    "Ray-Ban Clubmaster RB3016": {"price": 130, "category": "Sunglasses", "material": "Metal/Acetate", "shape": "Browline"},
    
    # Oakley Collection
    "Oakley Holbrook OO9102": {"price": 110, "category": "Sunglasses", "material": "O-Matter", "shape": "Square"},
    "Oakley Frogskins OO9013": {"price": 100, "category": "Sunglasses", "material": "O-Matter", "shape": "Square"},
    "Oakley Radar EV Path OO9208": {"price": 180, "category": "Sports", "material": "O-Matter", "shape": "Shield"},
    
    # Prescription Frames - Popular Brands
    "Warby Parker Haskell": {"price": 95, "category": "Prescription", "material": "Acetate", "shape": "Round"},
    "Warby Parker Percey": {"price": 95, "category": "Prescription", "material": "Acetate", "shape": "Square"},
    "Warby Parker Chamberlain": {"price": 95, "category": "Prescription", "material": "Metal", "shape": "Aviator"},
    
    # Luxury Brands
    "Gucci GG0061S": {"price": 320, "category": "Luxury", "material": "Acetate", "shape": "Cat-Eye"},
    "Prada PR 17WS": {"price": 280, "category": "Luxury", "material": "Acetate", "shape": "Square"},
    "Tom Ford FT5401": {"price": 350, "category": "Luxury", "material": "Acetate", "shape": "Square"},
    "Versace VE3284": {"price": 250, "category": "Luxury", "material": "Metal", "shape": "Cat-Eye"},
    
    # Budget-Friendly Options
    "Zenni Optical Rectangle 2020": {"price": 25, "category": "Budget", "material": "Plastic", "shape": "Rectangle"},
    "Zenni Optical Round 4420": {"price": 20, "category": "Budget", "material": "Metal", "shape": "Round"},
    "EyeBuyDirect Nevada": {"price": 35, "category": "Budget", "material": "Acetate", "shape": "Square"},
    "Coastal Glasses Maya": {"price": 40, "category": "Budget", "material": "Metal", "shape": "Cat-Eye"},
    
    # Progressive & Bifocal Lenses
    "Varilux Comfort Progressive": {"price": 200, "category": "Progressive", "material": "Lens", "shape": "Any"},
    "Varilux Physio Progressive": {"price": 250, "category": "Progressive", "material": "Lens", "shape": "Any"},
    "Essilor Bifocal FT28": {"price": 120, "category": "Bifocal", "material": "Lens", "shape": "Any"},
    
    # Lens Coatings & Treatments
    "Crizal Sapphire Anti-Reflective": {"price": 80, "category": "Coating", "material": "Coating", "shape": "Any"},
    "Blue Light Filter Coating": {"price": 50, "category": "Coating", "material": "Coating", "shape": "Any"},
    "Photochromic Transitions": {"price": 100, "category": "Coating", "material": "Coating", "shape": "Any"},
    "Polarized Lens Treatment": {"price": 75, "category": "Coating", "material": "Coating", "shape": "Any"},
    
    # Specialized Frames
    "Silhouette Titan Minimal Art": {"price": 400, "category": "Rimless", "material": "Titanium", "shape": "Rimless"},
    "Lindberg Air Titanium": {"price": 500, "category": "Rimless", "material": "Titanium", "shape": "Rimless"},
    "Flexon Autoflex": {"price": 150, "category": "Flexible", "material": "Memory Metal", "shape": "Rectangle"},
    
    # Kids Collection
    "Ray-Ban Junior RJ9506S": {"price": 80, "category": "Kids", "material": "Plastic", "shape": "Aviator"},
    "Oakley Youth Holbrook": {"price": 90, "category": "Kids", "material": "O-Matter", "shape": "Square"},
    "Disney Princess Frames": {"price": 45, "category": "Kids", "material": "Plastic", "shape": "Round"},
    
    # Safety & Work Glasses
    "3M Safety Glasses SecureFit": {"price": 25, "category": "Safety", "material": "Polycarbonate", "shape": "Wrap"},
    "Uvex Genesis Safety Glasses": {"price": 30, "category": "Safety", "material": "Polycarbonate", "shape": "Wrap"},
    
    # Reading Glasses
    "Foster Grant Reading +1.00": {"price": 15, "category": "Reading", "material": "Plastic", "shape": "Rectangle"},
    "Foster Grant Reading +1.50": {"price": 15, "category": "Reading", "material": "Plastic", "shape": "Rectangle"},
    "Foster Grant Reading +2.00": {"price": 15, "category": "Reading", "material": "Plastic", "shape": "Rectangle"},
    "Foster Grant Reading +2.50": {"price": 15, "category": "Reading", "material": "Plastic", "shape": "Rectangle"},
    
    # Computer Glasses
    "Gunnar Optiks Gaming Glasses": {"price": 60, "category": "Computer", "material": "Plastic", "shape": "Rectangle"},
    "Felix Gray Blue Light Glasses": {"price": 95, "category": "Computer", "material": "Acetate", "shape": "Round"},
}

def get_recommendations_by_face_shape(face_shape, age, gender, prescription_strength=""):
    """Get specific frame recommendations based on face shape"""
    
    recommendations = {
        "Wide/Round": {
            "best_frames": ["Ray-Ban Wayfarer RB2140", "Warby Parker Percey", "Tom Ford FT5401", "Zenni Optical Rectangle 2020"],
            "avoid_frames": ["Ray-Ban Round Metal RB3447", "Warby Parker Haskell"],
            "reasoning": "Angular frames add definition and length to round faces"
        },
        "Long/Oval": {
            "best_frames": ["Ray-Ban Aviator Classic RB3025", "Oakley Holbrook OO9102", "Warby Parker Chamberlain", "EyeBuyDirect Nevada"],
            "avoid_frames": ["Zenni Optical Rectangle 2020", "Tom Ford FT5401"],
            "reasoning": "Wide frames balance the length of oval faces"
        },
        "Balanced/Square": {
            "best_frames": ["Ray-Ban Round Metal RB3447", "Warby Parker Haskell", "Gucci GG0061S", "Felix Gray Blue Light Glasses"],
            "avoid_frames": ["Ray-Ban Wayfarer RB2140", "Tom Ford FT5401"],
            "reasoning": "Round frames soften angular features of square faces"
        }
    }
    
    # Age-based adjustments
    age_recommendations = []
    if age < 25:
        age_recommendations = ["Trendy styles", "Bold colors", "Fashion-forward designs"]
    elif age < 40:
        age_recommendations = ["Professional styles", "Classic designs", "Versatile colors"]
    elif age < 60:
        age_recommendations = ["Sophisticated styles", "Quality materials", "Comfortable fit"]
    else:
        age_recommendations = ["Comfortable reading glasses", "Progressive lenses", "Easy-to-clean materials"]
    
    # Gender-based suggestions
    gender_suggestions = []
    if gender.lower() == "female":
        gender_suggestions = ["Cat-eye frames", "Decorative temples", "Elegant colors"]
    else:
        gender_suggestions = ["Classic rectangular", "Aviator styles", "Professional colors"]
    
    # Prescription-based recommendations
    prescription_notes = []
    if "strong" in prescription_strength.lower():
        prescription_notes = ["High-index lenses recommended", "Smaller frames to reduce thickness", "Anti-reflective coating essential"]
    elif "moderate" in prescription_strength.lower():
        prescription_notes = ["Standard lenses suitable", "Most frame sizes work", "Consider anti-glare coating"]
    else:
        prescription_notes = ["Any lens type suitable", "Focus on style preferences", "Optional coatings available"]
    
    return {
        "face_shape_recs": recommendations.get(face_shape, recommendations["Balanced/Square"]),
        "age_considerations": age_recommendations,
        "gender_preferences": gender_suggestions,
        "prescription_notes": prescription_notes
    }

def get_inventory_by_category(category="All"):
    """Get inventory filtered by category"""
    if category == "All":
        return REAL_SPECTACLE_INVENTORY
    
    return {k: v for k, v in REAL_SPECTACLE_INVENTORY.items() if v["category"] == category}

def get_price_range_inventory(min_price=0, max_price=1000):
    """Get inventory filtered by price range"""
    return {k: v for k, v in REAL_SPECTACLE_INVENTORY.items() 
            if min_price <= v["price"] <= max_price}

def search_frames_by_criteria(face_shape="", material="", price_range="", category=""):
    """Search frames by multiple criteria"""
    results = REAL_SPECTACLE_INVENTORY.copy()
    
    # Filter by material
    if material:
        results = {k: v for k, v in results.items() if material.lower() in v["material"].lower()}
    
    # Filter by category
    if category:
        results = {k: v for k, v in results.items() if v["category"] == category}
    
    # Filter by price range
    if price_range:
        if price_range == "Budget":
            results = {k: v for k, v in results.items() if v["price"] <= 50}
        elif price_range == "Mid-range":
            results = {k: v for k, v in results.items() if 50 < v["price"] <= 200}
        elif price_range == "Premium":
            results = {k: v for k, v in results.items() if v["price"] > 200}
    
    return results