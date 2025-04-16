"""
Script to generate synthetic product and FAQ data for the VerdeMuse knowledge base.
This data will be embedded and stored in the vector database for retrieval.
"""

import os
import json
import sys
from typing import List, Dict, Any
import random

# Add the project root to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.vector_store.vector_store import VectorStore

def generate_product_data() -> List[Dict[str, Any]]:
    """Generate synthetic product data for VerdeMuse."""
    products = [
        {
            "id": "vm-plant-001",
            "name": "VerdeMuse Harmony Palm",
            "category": "Indoor Plants",
            "description": """The VerdeMuse Harmony Palm is a lush, air-purifying plant that thrives in indirect 
            sunlight. Perfect for improving indoor air quality while adding a touch of natural beauty to any space. 
            Its elegant fronds create a peaceful atmosphere and it's known for being low-maintenance.""",
            "care_instructions": """Water once a week, allowing soil to dry slightly between waterings. 
            Place in bright, indirect sunlight. Keep away from cold drafts and avoid temperature below 55°F (13°C).
            Mist occasionally to maintain humidity. Fertilize monthly during growing season with organic plant food.""",
            "benefits": ["Air purifying", "Low maintenance", "Pet friendly", "Stress reducing"],
            "price": 49.99,
            "sustainability": "Grown in our carbon-neutral greenhouse using rainwater collection systems."
        },
        {
            "id": "vm-plant-002",
            "name": "VerdeMuse Serenity Succulent Collection",
            "category": "Succulents",
            "description": """The VerdeMuse Serenity Succulent Collection features a curated selection of drought-resistant 
            succulents in biodegradable pots. These charming plants add a modern touch to any space while requiring 
            minimal care. Each collection contains 3 unique varieties chosen for their complementary aesthetics.""",
            "care_instructions": """Water sparingly, only when soil is completely dry (approximately every 2-3 weeks). 
            Place in bright light with some direct sun. Use well-draining soil specifically formulated for cacti and succulents. 
            Protect from frost. Fertilize lightly during spring and summer months.""",
            "benefits": ["Drought resistant", "Very low maintenance", "Air purifying", "Improves focus"],
            "price": 34.99,
            "sustainability": "Packaged in compostable materials with seeds embedded in the packaging."
        },
        {
            "id": "vm-plant-003",
            "name": "VerdeMuse Tranquility Fern",
            "category": "Indoor Plants",
            "description": """The VerdeMuse Tranquility Fern brings the lushness of a forest into your home. 
            With its delicate, feathery fronds and rich green color, this fern creates a sense of calm and natural abundance. 
            It thrives in humid environments, making it perfect for bathrooms and kitchens.""",
            "care_instructions": """Keep soil consistently moist but not soggy. Place in medium to bright indirect light, 
            avoiding direct sunlight which can scorch the leaves. Maintain high humidity by misting regularly or using a pebble tray. 
            Feed with diluted organic fertilizer monthly during growing season. Trim any brown fronds at the base.""",
            "benefits": ["Air humidifying", "Air purifying", "Stress reducing", "Improves bathroom air quality"],
            "price": 39.99,
            "sustainability": "Grown using sustainable farming practices that conserve water and protect local ecosystems."
        },
        {
            "id": "vm-soil-001",
            "name": "VerdeMuse Vital Soil Mix",
            "category": "Plant Care",
            "description": """VerdeMuse Vital Soil Mix is a premium, organic potting soil designed to provide optimal 
            nutrition and drainage for all your houseplants. This proprietary blend contains coconut coir, perlite, 
            worm castings, and slow-release organic nutrients to support healthy root development and plant growth.""",
            "usage_instructions": """For repotting: Remove plant from current pot, gently loosen root ball, and place in new pot 
            with fresh Vital Soil Mix. For existing plants: Replace the top 2 inches of soil with fresh mix every 6 months 
            to replenish nutrients. Water thoroughly after applying.""",
            "benefits": ["Improves drainage", "Promotes healthy roots", "Contains natural nutrients", "Sustainable ingredients"],
            "price": 19.99,
            "sustainability": "Made from 100% sustainable and renewable resources. Packaged in compostable bags."
        },
        {
            "id": "vm-fert-001",
            "name": "VerdeMuse Plant Vitality Drops",
            "category": "Plant Care",
            "description": """VerdeMuse Plant Vitality Drops is a concentrated liquid fertilizer that provides essential 
            nutrients for flourishing houseplants. Our balanced formula supports healthy foliage, vibrant flowers, and 
            strong roots. Made with natural ingredients and beneficial microorganisms.""",
            "usage_instructions": """Add 5 drops per cup of water when watering your plants. For small plants, use once a month. 
            For larger plants and fast-growing varieties, use every two weeks. Avoid application to very dry soil; 
            water plants first, then apply diluted product.""",
            "benefits": ["Promotes growth", "Enhances leaf color", "Supports root health", "Long-lasting"],
            "price": 24.99,
            "sustainability": "Produced using solar energy. Bottles made from 100% post-consumer recycled materials."
        }
    ]
    return products

def generate_faq_data() -> List[Dict[str, Any]]:
    """Generate synthetic FAQ data for VerdeMuse."""
    faqs = [
        {
            "question": "How often should I water my VerdeMuse plant?",
            "answer": """Watering frequency depends on the specific plant variety, but most VerdeMuse plants should be 
            watered when the top 1-2 inches of soil feel dry to the touch. The Harmony Palm typically needs watering 
            once a week, while the Serenity Succulents only need water every 2-3 weeks. The Tranquility Fern prefers 
            consistently moist soil. Always check the specific care instructions included with your plant or refer to 
            the product description on our website."""
        },
        {
            "question": "Are VerdeMuse plants pet-friendly?",
            "answer": """Many of our plants are pet-friendly, but not all. The VerdeMuse Harmony Palm is safe for pets, 
            as are most of our succulent collections. However, some plants may be toxic if ingested by cats, dogs, or other pets. 
            Each product description clearly indicates whether the plant is pet-friendly. If you have pets, we recommend 
            checking this information before purchasing or keeping plants out of your pets' reach."""
        },
        {
            "question": "How do I use the VerdeMuse Plant Vitality Drops?",
            "answer": """To use the VerdeMuse Plant Vitality Drops, add 5 drops per cup of water when watering your plants. 
            For small plants, apply once a month. For larger plants and fast-growing varieties, apply every two weeks. 
            It's best to avoid applying the fertilizer to very dry soil, so water your plants first, then apply the 
            diluted product. The concentrated formula provides essential nutrients that support healthy foliage, 
            vibrant flowers, and strong roots."""
        },
        {
            "question": "What is your return policy?",
            "answer": """VerdeMuse offers a 30-day satisfaction guarantee on all our plants. If your plant arrives damaged 
            or dies within 30 days despite following the care instructions, we'll replace it or issue a refund. To initiate 
            a return, contact our customer service team with your order number and photos of the plant. Please note that 
            plants showing signs of neglect or improper care are not eligible for returns. For plant care products, 
            we accept unused, sealed returns within 30 days of purchase."""
        },
        {
            "question": "How do I repot my VerdeMuse plant?",
            "answer": """To repot your VerdeMuse plant: 1) Choose a pot 1-2 inches larger in diameter than the current one, 
            with drainage holes. 2) Add a layer of VerdeMuse Vital Soil Mix at the bottom. 3) Carefully remove the plant 
            from its current pot, gently loosening the roots. 4) Place in the new pot and fill around the sides with fresh soil. 
            5) Water thoroughly and place in an appropriate light environment. Most plants benefit from repotting every 
            1-2 years in spring or early summer."""
        },
        {
            "question": "Where do you ship VerdeMuse products?",
            "answer": """VerdeMuse currently ships to all 50 U.S. states and select Canadian provinces. We use specialized 
            plant-safe packaging to ensure your plants arrive in perfect condition. Shipping times typically range from 
            3-7 business days, depending on your location. During extreme weather conditions, we may temporarily hold 
            shipments to certain regions to protect the plants. International shipping outside North America is not 
            available at this time, but we're working on expanding our shipping capabilities."""
        },
        {
            "question": "How sustainable are VerdeMuse products?",
            "answer": """Sustainability is at the core of VerdeMuse's mission. Our plants are grown in carbon-neutral 
            greenhouses using rainwater collection systems and renewable energy. We use biodegradable or recyclable 
            packaging materials, many with embedded seeds that can be planted. Our soil products are made from renewable 
            resources and packaged in compostable bags. The Plant Vitality Drops are produced using solar energy, and 
            the bottles are made from 100% post-consumer recycled materials. We also partner with reforestation projects, 
            planting a tree for every 10 products sold."""
        },
        {
            "question": "Why are the leaves on my plant turning yellow?",
            "answer": """Yellow leaves can be caused by several factors: 1) Overwatering: This is the most common cause. 
            Ensure proper drainage and allow soil to dry appropriately between waterings. 2) Underwatering: Consistently 
            dry soil can stress the plant. 3) Lighting issues: Too much or too little light can cause yellowing. 
            4) Nutrient deficiencies: Consider applying VerdeMuse Plant Vitality Drops. 5) Normal aging: Some yellowing 
            of older leaves is natural. If yellowing persists, check the specific care requirements for your plant variety 
            or contact our plant care specialists for personalized advice."""
        },
        {
            "question": "Do you offer plant care consultations?",
            "answer": """Yes, VerdeMuse offers complimentary 15-minute virtual plant care consultations for customers. 
            During these sessions, our plant specialists can help diagnose issues, provide care recommendations, and 
            answer specific questions about your VerdeMuse plants. To schedule a consultation, log into your account 
            on our website and select "Book Plant Care Consultation" from the customer service menu. Premium customers 
            also have access to extended consultation sessions and quarterly plant health check-ups."""
        }
    ]
    return faqs

def create_documents_from_data():
    """Create documents from product and FAQ data."""
    products = generate_product_data()
    faqs = generate_faq_data()
    
    documents = []
    
    # Create documents from product data
    for product in products:
        # General product document
        documents.append({
            "content": f"Product Name: {product['name']}\nCategory: {product['category']}\nDescription: {product['description']}\nPrice: ${product['price']}",
            "metadata": {"type": "product", "id": product["id"], "category": product["category"]}
        })
        
        # Care instructions document
        if "care_instructions" in product:
            documents.append({
                "content": f"Care Instructions for {product['name']}:\n{product['care_instructions']}",
                "metadata": {"type": "care_instructions", "product_id": product["id"]}
            })
        
        # Usage instructions document
        if "usage_instructions" in product:
            documents.append({
                "content": f"Usage Instructions for {product['name']}:\n{product['usage_instructions']}",
                "metadata": {"type": "usage_instructions", "product_id": product["id"]}
            })
        
        # Benefits document
        if "benefits" in product:
            benefits_text = ", ".join(product["benefits"])
            documents.append({
                "content": f"Benefits of {product['name']}:\n{benefits_text}",
                "metadata": {"type": "benefits", "product_id": product["id"]}
            })
        
        # Sustainability document
        if "sustainability" in product:
            documents.append({
                "content": f"Sustainability information for {product['name']}:\n{product['sustainability']}",
                "metadata": {"type": "sustainability", "product_id": product["id"]}
            })
    
    # Create documents from FAQ data
    for faq in faqs:
        documents.append({
            "content": f"Q: {faq['question']}\nA: {faq['answer']}",
            "metadata": {"type": "faq"}
        })
    
    return documents

def save_data_to_file():
    """Save the generated data to JSON files."""
    products = generate_product_data()
    faqs = generate_faq_data()
    
    # Ensure directories exist
    os.makedirs(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/synthetic_data')), exist_ok=True)
    
    # Save products data
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/synthetic_data/products.json')), 'w') as f:
        json.dump(products, f, indent=2)
    
    # Save FAQs data
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/synthetic_data/faqs.json')), 'w') as f:
        json.dump(faqs, f, indent=2)
    
    print("Data saved to files in data/synthetic_data/")

def load_data_to_vectorstore():
    """Load the generated data into the vector store."""
    documents = create_documents_from_data()
    
    # Extract text content and metadata
    texts = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Initialize vector store
    vector_store = VectorStore()
    vector_store.initialize_from_texts(texts=texts, metadatas=metadatas)
    
    print(f"Successfully loaded {len(texts)} documents into the vector store.")

if __name__ == "__main__":
    # Save data to JSON files
    save_data_to_file()
    
    # Load data to vector store
    load_data_to_vectorstore()