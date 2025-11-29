"""
Magazine × Photography MCP Server (Refactored)
Three-layer architecture: Olog + Aesthetic profiles + FastMCP interface

This version separates:
1. Categorical taxonomy (ologs.py) - pure logic, deterministic
2. Aesthetic definitions (JSON) - pre-generated magazine/photography profiles
3. MCP interface (this file) - Claude interaction layer

Cost optimization: Claude only called for creative synthesis, all taxonomy mapping
is deterministic via ologs.
"""

from fastmcp import FastMCP
from pathlib import Path
import json
import os
import sys
import random
from typing import List, Dict, Optional

# Import olog system (Layer 1: Categorical Taxonomy)
from ologs import OlogMorphisms, TemporalAlignment, ColorPaletteCategory

# Initialize MCP server
mcp = FastMCP("magazine-photography")

# Configurable cache directory
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


# Validate and load cache
if not validate_cache():
    print(f"\n💡 To fix this:", file=sys.stderr)
    print(f"   1. Ensure cache files exist in {CACHE_DIR}", file=sys.stderr)
    print(f"   2. Or set MAGAZINE_CACHE_DIR environment variable", file=sys.stderr)
    sys.exit(1)

print(f"📂 Loading cache from {CACHE_DIR}...", file=sys.stderr)
MAGAZINES = load_json(CACHE_DIR / "magazines.json") or []
PHOTOGRAPHY = load_json(CACHE_DIR / "photography.json") or []
COMBINATIONS = load_json(CACHE_DIR / "combinations.json") or []

if not MAGAZINES or not PHOTOGRAPHY or not COMBINATIONS:
    print(f"❌ Cache loaded but appears empty", file=sys.stderr)
    sys.exit(1)

# Create lookup dictionaries
MAG_LOOKUP = {m["name"]: m for m in MAGAZINES}
PHOTO_LOOKUP = {p["name"]: p for p in PHOTOGRAPHY}
COMBO_LOOKUP = {c["id"]: c for c in COMBINATIONS}

print(f"✓ Loaded {len(MAGAZINES)} magazines, {len(PHOTOGRAPHY)} styles, {len(COMBINATIONS)} combinations", file=sys.stderr)
print(f"✓ MCP server ready\n", file=sys.stderr)


# ============================================================================
# DETERMINISTIC UTILITY FUNCTIONS (Using ologs)
# ============================================================================

def extract_magazine_olog(magazine: Dict) -> Dict:
    """Extract olog representation from magazine definition"""
    profile = OlogMorphisms.magazine_to_visual_treatment(magazine)
    return {
        "color_category": profile.color_category.value,
        "lighting_approach": profile.lighting_approach.value,
        "contrast_profile": profile.contrast_profile.value,
        "texture_emphasis": profile.texture_emphasis.value
    }


def extract_photography_olog(photography: Dict) -> Dict:
    """Extract olog representation from photography style definition"""
    profile = OlogMorphisms.photography_to_technical_profile(photography)
    return {
        "composition_strategy": profile.composition_strategy.value,
        "focal_length_category": profile.focal_length_category.value,
        "subject_context": profile.subject_context.value,
        "depth_of_field": profile.depth_of_field
    }


def calculate_compatibility_deterministic(magazine: Dict, photography: Dict) -> Dict:
    """
    Deterministic compatibility calculation via olog morphisms.
    Pure category theory - no LLM needed.
    """
    mag_profile = OlogMorphisms.magazine_to_visual_treatment(magazine)
    photo_profile = OlogMorphisms.photography_to_technical_profile(photography)
    
    scores = OlogMorphisms.compatibility_mapping(
        mag_profile,
        photo_profile,
        magazine.get("era", {}).get("label", ""),
        photography.get("name", "")
    )
    
    return {
        "overall_harmony": scores.overall_harmony,
        "technical_score": scores.technical_score,
        "aesthetic_score": scores.aesthetic_score,
        "creative_tension": scores.creative_tension,
        "temporal_alignment": scores.temporal_alignment.value,
        "rationale": scores.rationale
    }


def slugify(text):
    """Convert text to URL-safe slug"""
    return text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("*", "")


# ============================================================================
# MCP TOOLS
# ============================================================================

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
    
    # Create combo ID using deterministic slugification
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
            "rationale": combo["compatibility"].get("rationale", "")
        },
        "suggested_subjects": combo.get("suggested_subjects", []),
        "prompt_keywords": combo.get("prompt_keywords", [])
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
    results = COMBINATIONS
    
    # Text search
    if query:
        query_lower = query.lower()
        results = [
            c for c in results
            if query_lower in c["description"]["name"].lower()
            or query_lower in c["description"]["full_description"].lower()
            or query_lower in " ".join(c.get("prompt_keywords", [])).lower()
            or query_lower in " ".join(c.get("suggested_subjects", [])).lower()
        ]
    
    # Harmony filtering
    if min_harmony is not None:
        results = [c for c in results if c["compatibility"]["overall_harmony"] >= min_harmony]
    if max_harmony is not None:
        results = [c for c in results if c["compatibility"]["overall_harmony"] <= max_harmony]
    
    # Tension filtering
    if min_tension is not None:
        results = [c for c in results if c["compatibility"]["creative_tension"] >= min_tension]
    
    # Magazine filtering
    if magazine_filter:
        magazine_filter_lower = magazine_filter.lower()
        results = [c for c in results if magazine_filter_lower in c["magazine_id"].lower()]
    
    # Photography filtering
    if photography_filter:
        photography_filter_lower = photography_filter.lower()
        results = [c for c in results if photography_filter_lower in c["photography_id"].lower()]
    
    # Temporal alignment filtering
    if temporal_alignment:
        results = [c for c in results if c["compatibility"]["temporal_alignment"] == temporal_alignment]
    
    # Format results
    def format_id(id_str):
        return id_str.replace("_", " ").title()
    
    formatted = [{
        "combination_id": c["id"],
        "name": c["description"]["name"],
        "tagline": c["description"]["tagline"],
        "magazine": format_id(c["magazine_id"]),
        "photography": format_id(c["photography_id"]),
        "harmony": c["compatibility"]["overall_harmony"],
        "tension": c["compatibility"]["creative_tension"],
        "temporal_alignment": c["compatibility"]["temporal_alignment"]
    } for c in results]
    
    return formatted[:limit]


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
    
    # Build deterministic prompt components using combination data
    parts = []
    
    # Base style description
    parts.append(f"{combo['description']['name']} aesthetic")
    
    # Subject
    if subject:
        parts.append(f"of {subject}")
    elif combo.get("suggested_subjects"):
        parts.append(f"featuring {combo['suggested_subjects'][0]}")
    
    # Framing
    parts.append(f"{distance.lower()} framing")
    parts.append(f"{angle.lower()} perspective")
    
    # Color adjustment based on intensity
    base_color = combo.get("magazine_color_palette", "balanced color palette")
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
        parts.append("balanced detail and clarity")
    
    # Mood intensity
    if mood_intensity < 0.3:
        parts.append("understated mood, subtle atmosphere, quiet presence")
    elif mood_intensity > 0.7:
        parts.append("dramatic atmosphere, intense mood, powerful emotional impact")
    
    # Add keywords from combination
    keywords = combo.get("prompt_keywords", [])[:3]
    if keywords:
        parts.extend(keywords)
    
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
    filtered = [c for c in COMBINATIONS if c["compatibility"]["overall_harmony"] >= min_harmony]
    
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
