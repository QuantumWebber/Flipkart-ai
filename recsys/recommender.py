from difflib import SequenceMatcher

def clean_price_val(price_str: str) -> float:
    """
    Price string se numeric value nikalna (e.g., ₹43,842 -> 43842.0)
    """
    if not price_str or price_str == "N/A":
        return 0.0
    clean = price_str.replace('₹', '').replace(',', '').strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Dono product names ke beech syntactic similarity index (0 to 1) nikalna
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def get_recommendations(current_product: dict, products_list: list, top_n: int = 5) -> list:
    """
    Input:
        - current_product: Dict jo user abhi dekh raha hai
        - products_list: Search list ke saare scanned products
    Output:
        - Top 3 Recommended Alternatives sorted by match score and price advantage
    """
    if not products_list or len(products_list) <= 1:
        return []

    current_name = current_product.get("name", "")
    current_price = clean_price_val(current_product.get("price", ""))
    current_url = current_product.get("url", "")

    recommendations = []

    for prod in products_list:
        prod_url = prod.get("url", "")
        
        
        if prod_url == current_url:
            continue

        prod_name = prod.get("name", "")
        prod_price = clean_price_val(prod.get("price", ""))

        # 1. Similarity Score
        similarity = calculate_similarity(current_name, prod_name)

        
        if similarity < 0.25:
            continue

        # 2. cheaper is better 
        price_advantage = 0.0
        if current_price > 0 and prod_price > 0:
            price_advantage = (current_price - prod_price) / current_price

        
        combined_score = (similarity * 0.7) + (price_advantage * 0.3)

        # Recommendations metadata assemble 
        recommendations.append({
            "name": prod_name,
            "price": prod.get("price", "N/A"),
            "image": prod.get("image"),
            "url": prod_url,
            "similarity": round(similarity * 100, 1),
            "price_diff_pct": round(price_advantage * 100, 1),
            "score": combined_score
        })

    recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)

    return recommendations[:top_n]