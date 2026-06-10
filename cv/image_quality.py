import cv2
import numpy as np
import requests
import torch
from PIL import Image
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel


device = "cuda" if torch.cuda.is_available() else "cpu"


model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name).to(device)
processor = CLIPProcessor.from_pretrained(model_name)
print("Model loaded successfully :", device)

def download_image(url: str) -> tuple:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.flipkart.com/"
    }
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: Image block .")
        
    pil_img = Image.open(BytesIO(response.content))
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
        
    open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return pil_img, open_cv_image

def analyze_image_quality(image_url: str, product_title: str = None) -> dict:
    """
    Input: Product Image URL aur optional Product Title
    Output: Quality Metrics + Image-to-Text Consistency (Mismatch Check)
    """
    try:
        pil_img, cv_img = download_image(image_url)
    except Exception as e:
        return {"error": f"Problem loading image: {e}"}

    # 1. PHYSICAL CHECKS 
    height, width, _ = cv_img.shape
    resolution_score = 100
    if width < 500 or height < 500:
        resolution_score = 60
    if width < 300 or height < 300:
        resolution_score = 30

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 2. CLIP AESTHETIC CHECK
    aesthetic_prompts = [
        "a high-quality, sharp, well-lit, professional e-commerce product photograph with clear details",
        "a blurry, dark, low-quality, out-of-focus, or messy amateur smartphone photograph"
    ]
    inputs_aes = processor(text=aesthetic_prompts, images=pil_img, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        outputs_aes = model(**inputs_aes)
    probs_aes = outputs_aes.logits_per_image.softmax(dim=1)
    clip_aesthetic_score = round(probs_aes[0][0].item() * 100, 2)

    # 3.Image to text consistency check (Product Title vs Image)
    consistency_score = 100.0
    consistency_status = "Matched"
    
    if product_title:
        # Product Title ko truncate karein taaki prompt lamba na ho
        short_title = product_title[:60]
        match_prompts = [
            f"a photograph of {short_title}",
            "a photograph of a completely different unrelated object"
        ]
        
        inputs_match = processor(text=match_prompts, images=pil_img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs_match = model(**inputs_match)
        probs_match = outputs_match.logits_per_image.softmax(dim=1)
        consistency_score = round(probs_match[0][0].item() * 100, 2)
        
        if consistency_score < 60:
            consistency_status = " Mismatch Alert!"
        elif consistency_score < 40:
            consistency_status = " Potential Fraud/Wrong Listing!"

    # 4. HYBRID SCORE CALCULATION
    physical_score = resolution_score
    if laplacian_var < 100:
        sharpness_score = max(10, int(laplacian_var))
    elif laplacian_var > 1000:
        sharpness_score = 100
    else:
        sharpness_score = int(50 + (laplacian_var / 1000) * 50)

    overall_score = round((physical_score * 0.2) + (sharpness_score * 0.2) + (clip_aesthetic_score * 0.6))

    status = "Good"
    if overall_score < 75:
        status = "Average"
    if overall_score < 50:
        status = "Poor"

    return {
        "width": width,
        "height": height,
        "blur_metric": round(laplacian_var, 2),
        "physical_score": physical_score,
        "clip_aesthetic_score": clip_aesthetic_score,
        "consistency_score": consistency_score,
        "consistency_status": consistency_status,
        "overall_score": overall_score,
        "status": status
    }

