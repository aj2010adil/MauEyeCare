#!/usr/bin/env python
"""
Comprehensive spectacle database with Indian brands and pricing in INR
"""
import datetime

# Comprehensive spectacle database with Indian pricing (INR)
COMPREHENSIVE_SPECTACLE_DATABASE = {
    # === LUXURY BRANDS ===
    # Ray-Ban Collection
    "Ray-Ban Aviator Classic RB3025": {
        "price": 12500, "lens_price": 4000, "category": "Luxury", "material": "Metal", "shape": "Aviator",
        "source": "ray-ban.com", "collected_date": "2024-01-15", "delivery_days": 3, "brand": "Ray-Ban",
        "model": "RB3025", "availability": "In Stock", "description": "Classic aviator sunglasses with metal frame",
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8056597177238_shad_qt.png"
    },
    "Ray-Ban Wayfarer RB2140": {
        "price": 10000, "lens_price": 3500, "category": "Luxury", "material": "Acetate", "shape": "Square",
        "source": "ray-ban.com", "collected_date": "2024-01-15", "delivery_days": 3, "brand": "Ray-Ban",
        "model": "RB2140", "availability": "In Stock", "description": "Iconic wayfarer style with acetate frame",
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8056597177245_shad_qt.png"
    },
    "Ray-Ban Round Metal RB3447": {
        "price": 11500, "lens_price": 4000, "category": "Luxury", "material": "Metal", "shape": "Round",
        "source": "ray-ban.com", "collected_date": "2024-01-15", "delivery_days": 3, "brand": "Ray-Ban",
        "model": "RB3447", "availability": "In Stock", "description": "Round metal frame with vintage appeal",
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/8056597177252_shad_qt.png"
    },
    
    # Oakley Collection
    "Oakley Holbrook OO9102": {
        "price": 9000, "lens_price": 3200, "category": "Luxury", "material": "O-Matter", "shape": "Square",
        "source": "oakley.com", "collected_date": "2024-01-16", "delivery_days": 4, "brand": "Oakley",
        "model": "OO9102", "availability": "In Stock", "description": "Durable O-Matter frame with square design",
        "image_url": "https://assets.oakley.com/is/image/Oakley/888392550583_1.png"
    },
    "Oakley Frogskins OO9013": {
        "price": 8500, "lens_price": 3000, "category": "Luxury", "material": "O-Matter", "shape": "Square",
        "source": "oakley.com", "collected_date": "2024-01-16", "delivery_days": 4, "brand": "Oakley",
        "model": "OO9013", "availability": "In Stock", "description": "Retro-inspired square frame",
        "image_url": "https://assets.oakley.com/is/image/Oakley/888392550590_1.png"
    },
    
    # Gucci Collection
    "Gucci GG0061S": {
        "price": 26000, "lens_price": 12000, "category": "Luxury", "material": "Acetate", "shape": "Cat-Eye",
        "source": "gucci.com", "collected_date": "2024-01-18", "delivery_days": 10, "brand": "Gucci",
        "model": "GG0061S", "availability": "Limited Stock", "description": "Luxury cat-eye frame with Gucci branding",
        "image_url": "https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1479139843/GG0061S_001_1.jpg"
    },
    "Gucci GG0034S": {
        "price": 28000, "lens_price": 12000, "category": "Luxury", "material": "Metal", "shape": "Round",
        "source": "gucci.com", "collected_date": "2024-01-18", "delivery_days": 10, "brand": "Gucci",
        "model": "GG0034S", "availability": "Limited Stock", "description": "Premium round metal frame",
        "image_url": "https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1479139844/GG0034S_001_1.jpg"
    },
    
    # Prada Collection
    "Prada PR 17WS": {
        "price": 23000, "lens_price": 10000, "category": "Luxury", "material": "Acetate", "shape": "Square",
        "source": "prada.com", "collected_date": "2024-01-19", "delivery_days": 12, "brand": "Prada",
        "model": "PR 17WS", "availability": "In Stock", "description": "Sophisticated square acetate frame",
        "image_url": "https://assets.prada.com/is/image/Prada/PR17WS_1AB5S0_F0002_C_000.jpg"
    },
    
    # === MID-RANGE BRANDS ===
    # Warby Parker Collection
    "Warby Parker Haskell": {
        "price": 7800, "lens_price": 8000, "category": "Mid-Range", "material": "Acetate", "shape": "Round",
        "source": "warbyparker.com", "collected_date": "2024-01-17", "delivery_days": 7, "brand": "Warby Parker",
        "model": "Haskell", "availability": "In Stock", "description": "Classic round acetate prescription frame",
        "image_url": "https://cdn.warbyparker.com/img/products/eyeglasses/haskell/haskell-whiskey-tortoise-front.jpg"
    },
    "Warby Parker Percey": {
        "price": 7800, "lens_price": 8000, "category": "Mid-Range", "material": "Acetate", "shape": "Square",
        "source": "warbyparker.com", "collected_date": "2024-01-17", "delivery_days": 7, "brand": "Warby Parker",
        "model": "Percey", "availability": "In Stock", "description": "Modern square acetate prescription frame",
        "image_url": "https://cdn.warbyparker.com/img/products/eyeglasses/percey/percey-black-front.jpg"
    },
    
    # Fossil Collection
    "Fossil FOS 2103/G/S": {
        "price": 4500, "lens_price": 2500, "category": "Mid-Range", "material": "Metal", "shape": "Aviator",
        "source": "fossil.com", "collected_date": "2024-01-20", "delivery_days": 5, "brand": "Fossil",
        "model": "FOS 2103/G/S", "availability": "In Stock", "description": "Stylish aviator with modern twist",
        "image_url": "https://fossil.scene7.com/is/image/FossilPartners/FOS2103GS_main.jpg"
    },
    "Fossil FOS 3102/S": {
        "price": 4200, "lens_price": 2500, "category": "Mid-Range", "material": "Plastic", "shape": "Square",
        "source": "fossil.com", "collected_date": "2024-01-20", "delivery_days": 5, "brand": "Fossil",
        "model": "FOS 3102/S", "availability": "In Stock", "description": "Contemporary square plastic frame",
        "image_url": "https://fossil.scene7.com/is/image/FossilPartners/FOS3102S_main.jpg"
    },
    
    # === INDIAN BRANDS ===
    # Titan Eye Plus Collection
    "Titan Eye Plus Classic Rectangle": {
        "price": 3500, "lens_price": 2000, "category": "Indian", "material": "Metal", "shape": "Rectangle",
        "source": "titaneyeplus.com", "collected_date": "2024-01-21", "delivery_days": 2, "brand": "Titan Eye Plus",
        "model": "Classic Rectangle", "availability": "In Stock", "description": "Premium Indian brand rectangular frame",
        "image_url": "https://www.titaneyeplus.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/t/e/tep_classic_rect.jpg"
    },
    "Titan Eye Plus Aviator Gold": {
        "price": 4200, "lens_price": 2500, "category": "Indian", "material": "Metal", "shape": "Aviator",
        "source": "titaneyeplus.com", "collected_date": "2024-01-21", "delivery_days": 2, "brand": "Titan Eye Plus",
        "model": "Aviator Gold", "availability": "In Stock", "description": "Gold-plated aviator frame",
        "image_url": "https://www.titaneyeplus.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/t/e/tep_aviator_gold.jpg"
    },
    "Titan Eye Plus Cat-Eye Fashion": {
        "price": 3800, "lens_price": 2200, "category": "Indian", "material": "Acetate", "shape": "Cat-Eye",
        "source": "titaneyeplus.com", "collected_date": "2024-01-21", "delivery_days": 2, "brand": "Titan Eye Plus",
        "model": "Cat-Eye Fashion", "availability": "In Stock", "description": "Trendy cat-eye frame for women",
        "image_url": "https://www.titaneyeplus.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/t/e/tep_cateye.jpg"
    },
    
    # Lenskart Collection
    "Lenskart Air Classic Black": {
        "price": 2500, "lens_price": 1500, "category": "Indian", "material": "TR90", "shape": "Rectangle",
        "source": "lenskart.com", "collected_date": "2024-01-22", "delivery_days": 1, "brand": "Lenskart",
        "model": "Air Classic Black", "availability": "In Stock", "description": "Ultra-light TR90 frame",
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-classic-black.jpg"
    },
    "Lenskart Air Round Blue": {
        "price": 2300, "lens_price": 1500, "category": "Indian", "material": "TR90", "shape": "Round",
        "source": "lenskart.com", "collected_date": "2024-01-22", "delivery_days": 1, "brand": "Lenskart",
        "model": "Air Round Blue", "availability": "In Stock", "description": "Lightweight round frame in blue",
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-round-blue.jpg"
    },
    "Lenskart Air Cat-Eye Pink": {
        "price": 2400, "lens_price": 1500, "category": "Indian", "material": "TR90", "shape": "Cat-Eye",
        "source": "lenskart.com", "collected_date": "2024-01-22", "delivery_days": 1, "brand": "Lenskart",
        "model": "Air Cat-Eye Pink", "availability": "In Stock", "description": "Stylish cat-eye in pink color",
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/s/lenskart-air-cateye-pink.jpg"
    },
    
    # Coolwinks Collection
    "Coolwinks Classic Wayfarer": {
        "price": 1800, "lens_price": 1200, "category": "Indian", "material": "Acetate", "shape": "Square",
        "source": "coolwinks.com", "collected_date": "2024-01-23", "delivery_days": 3, "brand": "Coolwinks",
        "model": "Classic Wayfarer", "availability": "In Stock", "description": "Affordable wayfarer style frame",
        "image_url": "https://d2py0n4pzah0xy.cloudfront.net/image/coolwinks-classic-wayfarer.jpg"
    },
    "Coolwinks Aviator Silver": {
        "price": 1900, "lens_price": 1200, "category": "Indian", "material": "Metal", "shape": "Aviator",
        "source": "coolwinks.com", "collected_date": "2024-01-23", "delivery_days": 3, "brand": "Coolwinks",
        "model": "Aviator Silver", "availability": "In Stock", "description": "Silver aviator frame",
        "image_url": "https://d2py0n4pzah0xy.cloudfront.net/image/coolwinks-aviator-silver.jpg"
    },
    
    # === BUDGET/LOCAL BRANDS ===
    # Local Indian Brands
    "Specsmakers Rectangle Black": {
        "price": 1200, "lens_price": 800, "category": "Budget", "material": "Plastic", "shape": "Rectangle",
        "source": "specsmakers.com", "collected_date": "2024-01-24", "delivery_days": 2, "brand": "Specsmakers",
        "model": "Rectangle Black", "availability": "In Stock", "description": "Basic rectangular plastic frame",
        "image_url": "https://specsmakers.com/images/rectangle-black.jpg"
    },
    "Specsmakers Round Metal": {
        "price": 1400, "lens_price": 800, "category": "Budget", "material": "Metal", "shape": "Round",
        "source": "specsmakers.com", "collected_date": "2024-01-24", "delivery_days": 2, "brand": "Specsmakers",
        "model": "Round Metal", "availability": "In Stock", "description": "Simple round metal frame",
        "image_url": "https://specsmakers.com/images/round-metal.jpg"
    },
    
    # Zenni Optical (Budget International)
    "Zenni Optical Rectangle 2020": {
        "price": 2000, "lens_price": 1600, "category": "Budget", "material": "Plastic", "shape": "Rectangle",
        "source": "zennioptical.com", "collected_date": "2024-01-19", "delivery_days": 14, "brand": "Zenni Optical",
        "model": "2020", "availability": "In Stock", "description": "Affordable rectangular plastic frame",
        "image_url": "https://static.zennioptical.com/production/products/general/2020/2020-black-front.jpg"
    },
    "Zenni Optical Round 4420": {
        "price": 1600, "lens_price": 1600, "category": "Budget", "material": "Metal", "shape": "Round",
        "source": "zennioptical.com", "collected_date": "2024-01-19", "delivery_days": 14, "brand": "Zenni Optical",
        "model": "4420", "availability": "In Stock", "description": "Budget-friendly round metal frame",
        "image_url": "https://static.zennioptical.com/production/products/general/4420/4420-silver-front.jpg"
    },
    
    # EyeBuyDirect Collection
    "EyeBuyDirect Nevada": {
        "price": 2800, "lens_price": 2000, "category": "Budget", "material": "Acetate", "shape": "Square",
        "source": "eyebuydirect.com", "collected_date": "2024-01-25", "delivery_days": 10, "brand": "EyeBuyDirect",
        "model": "Nevada", "availability": "In Stock", "description": "Stylish square acetate frame",
        "image_url": "https://d3oo5u0hgxvqxz.cloudfront.net/images/nevada-square-acetate.jpg"
    },
    "EyeBuyDirect Maya": {
        "price": 3200, "lens_price": 2000, "category": "Budget", "material": "Metal", "shape": "Cat-Eye",
        "source": "eyebuydirect.com", "collected_date": "2024-01-25", "delivery_days": 10, "brand": "EyeBuyDirect",
        "model": "Maya", "availability": "In Stock", "description": "Elegant cat-eye metal frame",
        "image_url": "https://d3oo5u0hgxvqxz.cloudfront.net/images/maya-cateye-metal.jpg"
    },
    
    # === PROGRESSIVE & SPECIALTY LENSES ===
    "Varilux Comfort Progressive": {
        "price": 16000, "lens_price": 0, "category": "Progressive", "material": "Lens", "shape": "Any",
        "source": "essilor.com", "collected_date": "2024-01-20", "delivery_days": 5, "brand": "Varilux",
        "model": "Comfort", "availability": "In Stock", "description": "Premium progressive lens technology",
        "image_url": "https://www.essilor.com/content/dam/essilor/images/products/varilux-comfort.jpg"
    },
    "Varilux Physio Progressive": {
        "price": 20000, "lens_price": 0, "category": "Progressive", "material": "Lens", "shape": "Any",
        "source": "essilor.com", "collected_date": "2024-01-20", "delivery_days": 5, "brand": "Varilux",
        "model": "Physio", "availability": "In Stock", "description": "Advanced progressive lens with enhanced clarity",
        "image_url": "https://www.essilor.com/content/dam/essilor/images/products/varilux-physio.jpg"
    },
    "Essilor Bifocal FT28": {
        "price": 9600, "lens_price": 0, "category": "Bifocal", "material": "Lens", "shape": "Any",
        "source": "essilor.com", "collected_date": "2024-01-20", "delivery_days": 5, "brand": "Essilor",
        "model": "FT28", "availability": "In Stock", "description": "Traditional bifocal lens",
        "image_url": "https://www.essilor.com/content/dam/essilor/images/products/bifocal-ft28.jpg"
    },
    
    # === COATINGS & TREATMENTS ===
    "Crizal Sapphire Anti-Reflective": {
        "price": 6400, "lens_price": 0, "category": "Coating", "material": "Coating", "shape": "Any",
        "source": "essilor.com", "collected_date": "2024-01-21", "delivery_days": 1, "brand": "Crizal",
        "model": "Sapphire", "availability": "In Stock", "description": "Premium anti-reflective coating",
        "image_url": "https://www.essilor.com/content/dam/essilor/images/products/crizal-sapphire.jpg"
    },
    "Blue Light Filter Coating": {
        "price": 4000, "lens_price": 0, "category": "Coating", "material": "Coating", "shape": "Any",
        "source": "multiple-sources.com", "collected_date": "2024-01-21", "delivery_days": 1, "brand": "Various",
        "model": "Blue Light", "availability": "In Stock", "description": "Protective blue light filtering coating",
        "image_url": "https://example.com/blue-light-coating.jpg"
    },
    "Photochromic Transitions": {
        "price": 8000, "lens_price": 0, "category": "Coating", "material": "Coating", "shape": "Any",
        "source": "transitions.com", "collected_date": "2024-01-21", "delivery_days": 3, "brand": "Transitions",
        "model": "Signature", "availability": "In Stock", "description": "Adaptive photochromic lenses",
        "image_url": "https://www.transitions.com/content/dam/transitions/images/products/signature.jpg"
    },
    "Polarized Lens Treatment": {
        "price": 6000, "lens_price": 0, "category": "Coating", "material": "Coating", "shape": "Any",
        "source": "multiple-sources.com", "collected_date": "2024-01-21", "delivery_days": 2, "brand": "Various",
        "model": "Polarized", "availability": "In Stock", "description": "Polarized lens treatment for sunglasses",
        "image_url": "https://example.com/polarized-coating.jpg"
    },
    
    # === KIDS COLLECTION ===
    "Ray-Ban Junior RJ9506S": {
        "price": 6400, "lens_price": 2000, "category": "Kids", "material": "Plastic", "shape": "Aviator",
        "source": "ray-ban.com", "collected_date": "2024-01-22", "delivery_days": 5, "brand": "Ray-Ban Junior",
        "model": "RJ9506S", "availability": "In Stock", "description": "Kids aviator sunglasses",
        "image_url": "https://assets.ray-ban.com/is/image/RayBan/RJ9506S_kids.png"
    },
    "Lenskart Kids Rectangle": {
        "price": 1800, "lens_price": 1200, "category": "Kids", "material": "TR90", "shape": "Rectangle",
        "source": "lenskart.com", "collected_date": "2024-01-22", "delivery_days": 2, "brand": "Lenskart Kids",
        "model": "Rectangle", "availability": "In Stock", "description": "Durable kids rectangular frame",
        "image_url": "https://static1.lenskart.com/media/catalog/product/cache/1/image/628x628/9df78eab33525d08d6e5fb8d27136e95/l/k/lenskart-kids-rectangle.jpg"
    },
    
    # === SAFETY GLASSES ===
    "3M Safety Glasses SecureFit": {
        "price": 2000, "lens_price": 1000, "category": "Safety", "material": "Polycarbonate", "shape": "Wrap",
        "source": "3m.com", "collected_date": "2024-01-23", "delivery_days": 7, "brand": "3M",
        "model": "SecureFit", "availability": "In Stock", "description": "Industrial safety glasses",
        "image_url": "https://multimedia.3m.com/mws/media/safety-glasses-securefit.jpg"
    },
    
    # === READING GLASSES ===
    "Foster Grant Reading +1.00": {
        "price": 1200, "lens_price": 0, "category": "Reading", "material": "Plastic", "shape": "Rectangle",
        "source": "fostergrant.com", "collected_date": "2024-01-24", "delivery_days": 5, "brand": "Foster Grant",
        "model": "+1.00", "availability": "In Stock", "description": "Basic reading glasses +1.00",
        "image_url": "https://www.fostergrant.com/images/reading-glasses-1.jpg"
    },
    "Foster Grant Reading +1.50": {
        "price": 1200, "lens_price": 0, "category": "Reading", "material": "Plastic", "shape": "Rectangle",
        "source": "fostergrant.com", "collected_date": "2024-01-24", "delivery_days": 5, "brand": "Foster Grant",
        "model": "+1.50", "availability": "In Stock", "description": "Basic reading glasses +1.50",
        "image_url": "https://www.fostergrant.com/images/reading-glasses-1-5.jpg"
    },
    "Foster Grant Reading +2.00": {
        "price": 1200, "lens_price": 0, "category": "Reading", "material": "Plastic", "shape": "Rectangle",
        "source": "fostergrant.com", "collected_date": "2024-01-24", "delivery_days": 5, "brand": "Foster Grant",
        "model": "+2.00", "availability": "In Stock", "description": "Basic reading glasses +2.00",
        "image_url": "https://www.fostergrant.com/images/reading-glasses-2.jpg"
    },
    
    # === COMPUTER GLASSES ===
    "Gunnar Optiks Gaming Glasses": {
        "price": 4800, "lens_price": 2000, "category": "Computer", "material": "Plastic", "shape": "Rectangle",
        "source": "gunnar.com", "collected_date": "2024-01-25", "delivery_days": 8, "brand": "Gunnar Optiks",
        "model": "Gaming", "availability": "In Stock", "description": "Gaming glasses with blue light protection",
        "image_url": "https://gunnar.com/images/gaming-glasses.jpg"
    },
    "Felix Gray Blue Light Glasses": {
        "price": 7600, "lens_price": 3000, "category": "Computer", "material": "Acetate", "shape": "Round",
        "source": "felixgray.com", "collected_date": "2024-01-25", "delivery_days": 10, "brand": "Felix Gray",
        "model": "Blue Light", "availability": "In Stock", "description": "Premium blue light filtering glasses",
        "image_url": "https://felixgray.com/images/blue-light-glasses.jpg"
    }
}

def get_spectacles_by_price_range(min_price=0, max_price=50000):
    """Get spectacles filtered by price range in INR"""
    return {k: v for k, v in COMPREHENSIVE_SPECTACLE_DATABASE.items() 
            if min_price <= v["price"] <= max_price}

def get_spectacles_by_category(category="All"):
    """Get spectacles filtered by category"""
    if category == "All":
        return COMPREHENSIVE_SPECTACLE_DATABASE
    return {k: v for k, v in COMPREHENSIVE_SPECTACLE_DATABASE.items() 
            if v["category"] == category}

def get_spectacles_sorted_by_price(ascending=True):
    """Get all spectacles sorted by price"""
    sorted_items = sorted(COMPREHENSIVE_SPECTACLE_DATABASE.items(), 
                         key=lambda x: x[1]["price"], 
                         reverse=not ascending)
    return dict(sorted_items)

def get_indian_brands_only():
    """Get only Indian brand spectacles"""
    indian_categories = ["Indian", "Budget"]
    indian_brands = ["Titan Eye Plus", "Lenskart", "Coolwinks", "Specsmakers"]
    
    return {k: v for k, v in COMPREHENSIVE_SPECTACLE_DATABASE.items() 
            if v["category"] in indian_categories or v["brand"] in indian_brands}

def get_luxury_brands_only():
    """Get only luxury brand spectacles"""
    luxury_brands = ["Ray-Ban", "Oakley", "Gucci", "Prada", "Tom Ford"]
    
    return {k: v for k, v in COMPREHENSIVE_SPECTACLE_DATABASE.items() 
            if v["brand"] in luxury_brands or v["category"] == "Luxury"}

def search_spectacles_by_criteria(face_shape="", material="", price_range="", category="", brand=""):
    """Advanced search with multiple criteria"""
    results = COMPREHENSIVE_SPECTACLE_DATABASE.copy()
    
    # Filter by face shape compatibility
    if face_shape:
        shape_mapping = {
            "Wide/Round": ["Rectangle", "Square", "Cat-Eye", "Aviator"],
            "Long/Oval": ["Round", "Aviator", "Square"],
            "Balanced/Square": ["Round", "Oval", "Cat-Eye"]
        }
        compatible_shapes = shape_mapping.get(face_shape, [])
        results = {k: v for k, v in results.items() 
                  if v["shape"] in compatible_shapes or v["shape"] == "Any"}
    
    # Filter by material
    if material:
        results = {k: v for k, v in results.items() 
                  if material.lower() in v["material"].lower()}
    
    # Filter by category
    if category:
        results = {k: v for k, v in results.items() if v["category"] == category}
    
    # Filter by brand
    if brand:
        results = {k: v for k, v in results.items() if v["brand"] == brand}
    
    # Filter by price range
    if price_range:
        if price_range == "Budget":
            results = {k: v for k, v in results.items() if v["price"] <= 5000}
        elif price_range == "Mid-Range":
            results = {k: v for k, v in results.items() if 5000 < v["price"] <= 15000}
        elif price_range == "Luxury":
            results = {k: v for k, v in results.items() if v["price"] > 15000}
    
    return results

def get_recommendations_by_face_shape_inr(face_shape, age, gender, prescription_strength=""):
    """Get recommendations with Indian pricing"""
    
    # Get compatible spectacles
    compatible_specs = search_spectacles_by_criteria(face_shape=face_shape)
    
    # Age-based filtering
    if age < 25:
        preferred_categories = ["Budget", "Indian", "Mid-Range"]
    elif age < 40:
        preferred_categories = ["Mid-Range", "Indian", "Luxury"]
    elif age < 60:
        preferred_categories = ["Luxury", "Progressive", "Mid-Range"]
    else:
        preferred_categories = ["Progressive", "Reading", "Mid-Range"]
    
    # Filter by age preferences
    age_filtered = {k: v for k, v in compatible_specs.items() 
                   if v["category"] in preferred_categories}
    
    # Sort by price (budget-friendly for younger, premium for older)
    if age < 30:
        sorted_specs = sorted(age_filtered.items(), key=lambda x: x[1]["price"])
    else:
        sorted_specs = sorted(age_filtered.items(), key=lambda x: -x[1]["price"])
    
    return dict(sorted_specs)