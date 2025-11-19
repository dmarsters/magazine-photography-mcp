"""
MCP Server for Magazine × Photography Style Combinations
Provides tools for browsing and generating image prompts from style combinations

Usage:
    python magazine_photography_mcp.py
    
    Or add to Claude Desktop config:
    {
      "mcpServers": {
        "magazine-photography": {
          "command": "python",
          "args": ["/absolute/path/to/magazine_photography_mcp.py"],
          "env": {
            "MAGAZINE_CACHE_DIR": "/path/to/cache"  # Optional, defaults to ./cache
          }
        }
      }
    }
"""

from fastmcp import FastMCP
from pathlib import Path
import json
import os
import sys
from typing import List, Dict, Optional

# Initialize MCP server
mcp = FastMCP("Magazine Photography Styles")

# Configurable cache directory with fallback
DEFAULT_CACHE = Path(__file__).parent / "cache"
CACHE_DIR = Path(os.environ.get("MAGAZINE_CACHE_DIR", DEFAULT_CACHE))

def validate_cache():
    """Validate that cache directory exists and contains required files"""
    if not CACHE_DIR.exists():
        print(f"❌ Cache directory not found: {CACHE_DIR}", file=sys.stderr)
        print(f"   Expected location: {DEFAULT_CACHE}", file=sys.stderr)
        print(f"   Or set MAGAZINE_CACHE_DIR environment variable", file=sys.stderr)
        return False
    
    required_files = ["magazines.json", "photography.json", "combinations.json"]
    missing = []
    
    for filename in required_files:
        if not (CACHE_DIR / filename).exists():
            missing.append(filename)
    
    if missing:
        print(f"❌ Cache incomplete. Missing files:", file=sys.stderr)
        for filename in missing:
            print(f"   - {filename}", file=sys.stderr)
        print(f"   Cache directory: {CACHE_DIR}", file=sys.stderr)
        return False
    
    return True

def load_json(filepath: Path):
    """Load JSON file safely with error handling"""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️  Warning: {filepath.name} not found", file=sys.stderr)
            return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {filepath.name}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error loading {filepath.name}: {e}", file=sys.stderr)
        return None

# Validate cache before loading
if not validate_cache():
    print(f"\n💡 To fix this:", file=sys.stderr)
    print(f"   1. Ensure cache files exist in {CACHE_DIR}", file=sys.stderr)
    print(f"   2. Or set MAGAZINE_CACHE_DIR environment variable to correct location", file=sys.stderr)
    print(f"   3. Run generate_cache.py if cache doesn't exist yet\n", file=sys.stderr)
    sys.exit(1)

# Load cache at startup
print(f"📂 Loading cache from {CACHE_DIR}...", file=sys.stderr)
MAGAZINES = load_json(CACHE_DIR / "magazines.json") or []
PHOTOGRAPHY = load_json(CACHE_DIR / "photography.json") or []
COMBINATIONS = load_json(CACHE_DIR / "combinations.json") or []

# Final validation
if not MAGAZINES or not PHOTOGRAPHY or not COMBINATIONS:
    print(f"❌ Cache loaded but appears empty", file=sys.stderr)
    print(f"   Magazines: {len(MAGAZINES)}", file=sys.stderr)
    print(f"   Photography: {len(PHOTOGRAPHY)}", file=sys.stderr)
    print(f"   Combinations: {len(COMBINATIONS)}", file=sys.stderr)
    sys.exit(1)

# Create lookup dictionaries for fast access
MAG_LOOKUP = {m["name"]: m for m in MAGAZINES}
PHOTO_LOOKUP = {p["name"]: p for p in PHOTOGRAPHY}
COMBO_LOOKUP = {c["id"]: c for c in COMBINATIONS}

print(f"✓ Loaded {len(MAGAZINES)} magazines, {len(PHOTOGRAPHY)} photography styles, {len(COMBINATIONS)} combinations", file=sys.stderr)
print(f"✓ MCP server ready\n", file=sys.stderr)


@mcp.tool()
def list_magazines() -> List[Dict]:
    """
    Get all available magazine styles with their era and characteristics.
    
    Returns a list of magazine profiles including name, era, visual treatment,
    and cultural context. Use this to explore available magazine aesthetics.
    
    Example usage:
    - Browse all available magazines
    - Find magazines from specific eras
    - Discover magazine aesthetic characteristics
    """
    return [{
        "name": m["name"],
        "display_name": m.get("display_name", m["name"]),
        "era": m["era"]["label"],
        "color_palette": m["visual_treatment"]["color_palette"],
        "lighting": m["visual_treatment"]["lighting"],
        "values": m["cultural_context"]["values"]
    } for m in MAGAZINES]


@mcp.tool()
def list_photography_styles() -> List[Dict]:
    """
    Get all available photography styles with their technical characteristics.
    
    Returns a list of photography style profiles including name, typical uses,
    key characteristics, and technical approach. Use this to explore photography
    approaches available in the system.
    
    Example usage:
    - Browse all photography styles
    - Find styles for specific use cases
    - Understand technical characteristics
    """
    return [{
        "name": p["name"],
        "typical_uses": p["context"]["typical_uses"],
        "key_characteristics": p["context"]["key_characteristics"],
        "focal_length": p["technical"]["focal_length"],
        "composition": p["aesthetic"]["composition"]
    } for p in PHOTOGRAPHY]


@mcp.tool()
def get_combination(magazine_name: str, photography_style: str) -> Dict:
    """
    Get detailed analysis of a specific magazine × photography combination.
    
    Args:
        magazine_name: Full name of magazine including era, e.g., "Life (1960s)", "Vogue (1990s)"
        photography_style: Full name of photography style, e.g., "Portrait Photography", "Documentary Photography"
    
    Returns detailed combination including:
    - Evocative name and tagline
    - Full description of the aesthetic
    - Compatibility scores (harmony, technical, aesthetic, creative tension)
    - Visual expectations
    - Suggested subjects
    - Use cases
    - Prompt keywords
    
    Example:
        get_combination("Life (1960s)", "Documentary Photography")
    """
    # Find magazine and photography profiles
    mag = MAG_LOOKUP.get(magazine_name)
    photo = PHOTO_LOOKUP.get(photography_style)
    
    if not mag:
        available_mags = [m["name"] for m in MAGAZINES]
        return {
            "error": f"Magazine '{magazine_name}' not found",
            "available_magazines": available_mags[:10],
            "hint": "Use list_magazines() to see all available magazines"
        }
    
    if not photo:
        available_photos = [p["name"] for p in PHOTOGRAPHY]
        return {
            "error": f"Photography style '{photography_style}' not found",
            "available_styles": available_photos[:10],
            "hint": "Use list_photography_styles() to see all available styles"
        }
    
    # Create slug for combination lookup
    def slugify(text):
        return text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("*", "")
    
    mag_slug = slugify(magazine_name)
    photo_slug = slugify(photography_style)
    combo_id = f"{mag_slug}__{photo_slug}"
    
    combo = COMBO_LOOKUP.get(combo_id)
    if not combo:
        return {
            "error": f"Combination not found for {magazine_name} × {photography_style}",
            "combination_id": combo_id
        }
    
    return {
        "combination_id": combo["id"],
        "name": combo["description"]["name"],
        "tagline": combo["description"]["tagline"],
        "description": combo["description"]["full_description"],
        "visual_expectations": combo["description"]["visual_expectations"],
        "use_cases": combo["description"]["use_cases"],
        "compatibility": {
            "overall_harmony": combo["compatibility"]["overall_harmony"],
            "technical_score": combo["compatibility"]["technical_score"],
            "aesthetic_score": combo["compatibility"]["aesthetic_score"],
            "creative_tension": combo["compatibility"]["creative_tension"],
            "temporal_alignment": combo["compatibility"]["temporal_alignment"],
            "reasoning": combo["compatibility"]["reasoning"]
        },
        "suggested_subjects": combo["suggested_subjects"],
        "prompt_keywords": combo["prompt_keywords"],
        "temporal_notes": combo.get("temporal_notes", "")
    }


@mcp.tool()
def search_combinations(
    query: Optional[str] = None,
    min_harmony: Optional[int] = None,
    max_harmony: Optional[int] = None,
    min_tension: Optional[int] = None,
    magazine_filter: Optional[str] = None,
    photography_filter: Optional[str] = None,
    temporal_alignment: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """
    Search and filter style combinations with various criteria.
    
    Args:
        query: Search text (searches names, descriptions, use cases)
        min_harmony: Minimum harmony score 0-10 (8+ = very harmonious)
        max_harmony: Maximum harmony score 0-10 (use low values to find experimental combos)
        min_tension: Minimum creative tension score 0-10 (7+ = high tension/interesting contrasts)
        magazine_filter: Filter by magazine name (partial match OK)
        photography_filter: Filter by photography style (partial match OK)
        temporal_alignment: Filter by temporal relationship - "era_matched", "creative_anachronism", or "temporal_clash"
        limit: Maximum results to return (default 20)
    
    Returns matching combinations with name, tagline, scores, and IDs.
    
    Examples:
        search_combinations(query="vintage") 
          → Find combinations with vintage aesthetics
        
        search_combinations(min_harmony=8) 
          → Find highly harmonious, naturally compatible pairs
        
        search_combinations(min_tension=7) 
          → Find combinations with interesting creative tension
        
        search_combinations(magazine_filter="Life", temporal_alignment="era_matched")
          → Find Life magazine combinations that are temporally aligned
        
        search_combinations(max_harmony=5, min_tension=7)
          → Find experimental combinations with high creative tension
    """
    results = COMBINATIONS.copy()
    
    # Text search
    if query:
        query_lower = query.lower()
        results = [c for c in results if (
            query_lower in c["description"]["name"].lower() or
            query_lower in c["description"]["tagline"].lower() or
            query_lower in c["description"]["full_description"].lower() or
            any(query_lower in use_case.lower() for use_case in c["description"]["use_cases"]) or
            any(query_lower in subj.lower() for subj in c["suggested_subjects"])
        )]
    
    # Harmony filters
    if min_harmony is not None:
        results = [c for c in results if c["compatibility"]["overall_harmony"] >= min_harmony]
    
    if max_harmony is not None:
        results = [c for c in results if c["compatibility"]["overall_harmony"] <= max_harmony]
    
    # Tension filter
    if min_tension is not None:
        results = [c for c in results if c["compatibility"]["creative_tension"] >= min_tension]
    
    # Magazine filter (partial match)
    if magazine_filter:
        mag_filter_lower = magazine_filter.lower()
        results = [c for c in results if mag_filter_lower in c["magazine_id"]]
    
    # Photography filter (partial match)
    if photography_filter:
        photo_filter_lower = photography_filter.lower()
        results = [c for c in results if photo_filter_lower in c["photography_id"]]
    
    # Temporal alignment filter
    if temporal_alignment:
        results = [c for c in results if c["compatibility"]["temporal_alignment"] == temporal_alignment]
    
    # Sort by harmony score descending
    results.sort(key=lambda c: c["compatibility"]["overall_harmony"], reverse=True)
    
    # Limit and format results
    results = results[:limit]
    
    def format_id(id_str):
        """Convert slug back to readable format"""
        return id_str.replace("_", " ").title()
    
    return [{
        "combination_id": c["id"],
        "name": c["description"]["name"],
        "tagline": c["description"]["tagline"],
        "magazine": format_id(c["magazine_id"]),
        "photography": format_id(c["photography_id"]),
        "harmony": c["compatibility"]["overall_harmony"],
        "technical": c["compatibility"]["technical_score"],
        "aesthetic": c["compatibility"]["aesthetic_score"],
        "tension": c["compatibility"]["creative_tension"],
        "temporal_alignment": c["compatibility"]["temporal_alignment"],
        "use_cases": c["description"]["use_cases"][:2]  # First 2 use cases for preview
    } for c in results]


@mcp.tool()
def generate_image_prompt(
    combination_id: str,
    distance: str,
    angle: str,
    subject: Optional[str] = None,
    color_intensity: float = 0.5,
    detail_sharpness: float = 0.5,
    mood_intensity: float = 0.5
) -> str:
    """
    Generate a detailed image generation prompt from a style combination.
    
    Args:
        combination_id: ID from search_combinations or get_combination (e.g., "life_1960s__documentary_photography")
        distance: Shot distance - "Extreme Close-up", "Close-up", "Medium", "Full", or "Wide"
        angle: Camera angle - "Overhead", "Eye-level", "Low Angle", "Dutch Tilt", or "Profile"
        subject: Subject description (uses suggested subject if not provided)
        color_intensity: Color saturation 0.0 (very muted) to 1.0 (very saturated), default 0.5 (balanced)
        detail_sharpness: Detail level 0.0 (soft/dreamy) to 1.0 (razor sharp), default 0.5 (balanced)
        mood_intensity: Mood drama 0.0 (subtle/understated) to 1.0 (highly dramatic), default 0.5 (balanced)
    
    Returns a detailed image generation prompt ready for Flux, Midjourney, Stable Diffusion, etc.
    
    Example:
        generate_image_prompt(
            combination_id="life_1960s__documentary_photography",
            distance="Close-up",
            angle="Eye-level",
            subject="elderly woman holding protest sign",
            color_intensity=0.8
        )
    """
    combo = COMBO_LOOKUP.get(combination_id)
    if not combo:
        return f"Error: Combination ID '{combination_id}' not found. Use search_combinations() to find valid IDs."
    
    # Get magazine and photography profiles
    def unslugify(slug):
        """Convert slug to readable name"""
        parts = slug.split("_")
        result = []
        i = 0
        while i < len(parts):
            part = parts[i]
            # Check if next part is a year range
            if i + 1 < len(parts) and parts[i + 1].isdigit():
                result.append(f"{part.title()} ({parts[i + 1]})")
                i += 2
            else:
                result.append(part.title())
                i += 1
        return " ".join(result)
    
    mag_name = unslugify(combo["magazine_id"])
    photo_name = unslugify(combo["photography_id"])
    
    # Try to find exact matches first
    mag = MAG_LOOKUP.get(mag_name)
    photo = PHOTO_LOOKUP.get(photo_name)
    
    # If not found, try without spaces
    if not mag:
        for m in MAGAZINES:
            if slugify_helper(m["name"]) == combo["magazine_id"]:
                mag = m
                break
    
    if not photo:
        for p in PHOTOGRAPHY:
            if slugify_helper(p["name"]) == combo["photography_id"]:
                photo = p
                break
    
    def slugify_helper(text):
        return text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("*", "")
    
    if not mag or not photo:
        # Fallback: use combination's own keywords
        parts = [combo["description"]["name"]]
        if subject:
            parts.append(f"of {subject}")
        parts.extend(combo["prompt_keywords"][:5])
        return ", ".join(parts)
    
    # Build prompt components
    parts = []
    
    # Base style description
    parts.append(f"{mag['name']} style")
    parts.append(photo['name'].lower())
    
    # Subject
    if subject:
        parts.append(f"of {subject}")
    elif combo["suggested_subjects"]:
        parts.append(f"featuring {combo['suggested_subjects'][0]}")
    
    # Framing
    parts.append(f"{distance.lower()} framing")
    parts.append(f"{angle.lower()} perspective")
    
    # Lighting
    parts.append(mag["visual_treatment"]["lighting"])
    
    # Color adjustment based on intensity
    base_color = mag["visual_treatment"]["color_palette"]
    if color_intensity < 0.3:
        parts.append("desaturated, muted color palette, subtle tones")
    elif color_intensity < 0.4:
        parts.append(f"slightly desaturated {base_color}")
    elif color_intensity > 0.7:
        parts.append(f"highly saturated, vivid {base_color}, bold color emphasis")
    elif color_intensity > 0.6:
        parts.append(f"enhanced saturation, vibrant {base_color}")
    else:
        parts.append(base_color)
    
    # Detail/sharpness
    if detail_sharpness < 0.3:
        parts.append("soft focus, gentle detail, dreamlike quality")
    elif detail_sharpness > 0.7:
        parts.append("razor sharp, crisp detail, pronounced texture")
    else:
        parts.append(mag["visual_treatment"]["texture"])
    
    # Mood intensity
    if mood_intensity < 0.3:
        parts.append("understated mood, subtle atmosphere, quiet presence")
    elif mood_intensity > 0.7:
        parts.append("dramatic atmosphere, intense mood, powerful emotional impact")
    
    # Add top keywords from combination
    keywords = combo.get("prompt_keywords", [])[:3]
    if keywords:
        parts.extend(keywords)
    
    # Join into final prompt
    return ", ".join(parts)


@mcp.tool()
def get_stats() -> Dict:
    """
    Get statistics about the style combination library.
    
    Returns comprehensive statistics including:
    - Total counts of magazines, styles, combinations
    - Average compatibility scores
    - Distribution of high-quality combinations
    - Temporal alignment breakdown
    
    Useful for understanding the scope and characteristics of the library.
    """
    harmony_scores = [c["compatibility"]["overall_harmony"] for c in COMBINATIONS]
    tension_scores = [c["compatibility"]["creative_tension"] for c in COMBINATIONS]
    technical_scores = [c["compatibility"]["technical_score"] for c in COMBINATIONS]
    aesthetic_scores = [c["compatibility"]["aesthetic_score"] for c in COMBINATIONS]
    
    temporal_counts = {}
    for c in COMBINATIONS:
        t = c["compatibility"]["temporal_alignment"]
        temporal_counts[t] = temporal_counts.get(t, 0) + 1
    
    return {
        "library_size": {
            "total_magazines": len(MAGAZINES),
            "total_photography_styles": len(PHOTOGRAPHY),
            "total_combinations": len(COMBINATIONS)
        },
        "average_scores": {
            "harmony": round(sum(harmony_scores) / len(harmony_scores), 2),
            "technical": round(sum(technical_scores) / len(technical_scores), 2),
            "aesthetic": round(sum(aesthetic_scores) / len(aesthetic_scores), 2),
            "creative_tension": round(sum(tension_scores) / len(tension_scores), 2)
        },
        "high_quality_combinations": {
            "harmony_8_plus": len([s for s in harmony_scores if s >= 8]),
            "harmony_9_plus": len([s for s in harmony_scores if s >= 9]),
            "tension_7_plus": len([s for s in tension_scores if s >= 7]),
            "tension_8_plus": len([s for s in tension_scores if s >= 8])
        },
        "temporal_distribution": temporal_counts,
        "magazines_by_era": {
            "1940s": len([m for m in MAGAZINES if "1940" in m["name"]]),
            "1950s": len([m for m in MAGAZINES if "1950" in m["name"]]),
            "1960s": len([m for m in MAGAZINES if "1960" in m["name"]]),
            "1970s": len([m for m in MAGAZINES if "1970" in m["name"]]),
            "1980s": len([m for m in MAGAZINES if "1980" in m["name"]]),
            "1990s": len([m for m in MAGAZINES if "1990" in m["name"]]),
            "2000s": len([m for m in MAGAZINES if "2000" in m["name"]]),
            "contemporary": len([m for m in MAGAZINES if "contemporary" in m["name"]])
        },
        "cache_location": str(CACHE_DIR)
    }


@mcp.tool()
def get_random_combinations(count: int = 5, min_harmony: int = 7) -> List[Dict]:
    """
    Get random high-quality combinations for inspiration.
    
    Args:
        count: Number of random combinations to return (default 5)
        min_harmony: Minimum harmony score to include (default 7)
    
    Returns random selection of combinations meeting the quality threshold.
    Useful for discovering unexpected pairings or getting inspiration.
    """
    import random
    
    # Filter by minimum harmony
    filtered = [c for c in COMBINATIONS if c["compatibility"]["overall_harmony"] >= min_harmony]
    
    # Random sample
    sample_size = min(count, len(filtered))
    sampled = random.sample(filtered, sample_size)
    
    def format_id(id_str):
        return id_str.replace("_", " ").title()
    
    return [{
        "combination_id": c["id"],
        "name": c["description"]["name"],
        "tagline": c["description"]["tagline"],
        "magazine": format_id(c["magazine_id"]),
        "photography": format_id(c["photography_id"]),
        "harmony": c["compatibility"]["overall_harmony"],
        "tension": c["compatibility"]["creative_tension"],
        "temporal_alignment": c["compatibility"]["temporal_alignment"]
    } for c in sampled]

if __name__ == "__main__":
    mcp.run()
