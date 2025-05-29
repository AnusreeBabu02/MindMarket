import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_and_rank_idea(title, description, category):
    """
    Analyze an idea and return rating, tags, and cluster information
    """
    try:
        prompt = f"""
        Analyze this creative idea submission and provide a comprehensive evaluation:
        
        Title: {title}
        Description: {description}
        Category: {category}
        
        Please evaluate and respond with JSON in this exact format:
        {{
            "rating": <number between 1-10 based on creativity, marketability, and uniqueness>,
            "tags": <array of 3-5 relevant tags describing the idea>,
            "cluster": <industry/style cluster like "Tech", "Marketing", "Entertainment", "Business", "Lifestyle", etc.>,
            "marketability": <number between 1-10>,
            "creativity": <number between 1-10>,
            "uniqueness": <number between 1-10>,
            "reasoning": <brief explanation of the rating>
        }}
        
        Consider factors like:
        - Commercial viability
        - Originality and creativity
        - Market demand
        - Implementation feasibility
        - Target audience appeal
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert idea evaluator with deep knowledge of market trends, creativity assessment, and commercial viability. Provide honest, constructive analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure required fields and validate ranges
        rating = max(1, min(10, float(result.get("rating", 5))))
        tags = result.get("tags", [])
        cluster = result.get("cluster", "General")
        
        return {
            "rating": rating,
            "tags": tags,
            "cluster": cluster,
            "marketability": result.get("marketability", 5),
            "creativity": result.get("creativity", 5),
            "uniqueness": result.get("uniqueness", 5),
            "reasoning": result.get("reasoning", "Analysis completed")
        }
        
    except Exception as e:
        print(f"AI analysis failed: {e}")
        # Return default values on failure
        return {
            "rating": 5.0,
            "tags": ["creative", "innovative"],
            "cluster": "General",
            "marketability": 5,
            "creativity": 5,
            "uniqueness": 5,
            "reasoning": "AI analysis unavailable"
        }

def generate_idea_suggestions(category, keywords=""):
    """
    Generate idea suggestions based on category and keywords
    """
    try:
        prompt = f"""
        Generate 5 creative idea suggestions for the category: {category}
        {f"Related to keywords: {keywords}" if keywords else ""}
        
        Respond with JSON in this format:
        {{
            "suggestions": [
                {{
                    "title": "<idea title>",
                    "description": "<brief description>",
                    "estimated_value": <number representing potential price range>
                }}
            ]
        }}
        
        Make the ideas:
        - Original and creative
        - Commercially viable
        - Appropriate for the category
        - Varied in approach and style
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative idea generator specializing in marketable concepts for different industries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=600
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("suggestions", [])
        
    except Exception as e:
        print(f"Idea generation failed: {e}")
        return []

def cluster_similar_ideas(ideas_data):
    """
    Cluster similar ideas together based on style and industry
    """
    try:
        ideas_text = "\n".join([f"ID: {idea['id']}, Title: {idea['title']}, Category: {idea['category']}, Tags: {idea['tags']}" for idea in ideas_data])
        
        prompt = f"""
        Analyze these ideas and group them into clusters based on similarity in style, industry, or theme:
        
        {ideas_text}
        
        Respond with JSON in this format:
        {{
            "clusters": [
                {{
                    "name": "<cluster name>",
                    "description": "<brief description of what unites this cluster>",
                    "idea_ids": [<array of idea IDs belonging to this cluster>]
                }}
            ]
        }}
        
        Create meaningful clusters that help buyers find related ideas.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at identifying patterns and grouping similar creative concepts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("clusters", [])
        
    except Exception as e:
        print(f"Clustering failed: {e}")
        return []
