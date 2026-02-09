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
import math
import numpy as np
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


# ============================================================================
# PHASE 2.6: RHYTHMIC PRESETS + ATTRACTOR VISUALIZATION
# ============================================================================
# Normalized parameter space for aesthetic dynamics integration.
# Maps magazine×photography aesthetics to a 6D morphospace [0.0, 1.0].
# ============================================================================



MAGPHOTO_PARAMETER_NAMES = [
    "color_saturation",          # 0.0 = muted/desaturated, 1.0 = vivid/saturated
    "detail_sharpness",          # 0.0 = soft/dreamy, 1.0 = razor crisp
    "mood_intensity",            # 0.0 = understated/quiet, 1.0 = dramatic/powerful
    "contrast_level",            # 0.0 = flat/even, 1.0 = extreme chiaroscuro
    "temporal_warmth",           # 0.0 = cool/modern/clinical, 1.0 = warm/vintage/analog
    "compositional_formality",   # 0.0 = candid/loose/spontaneous, 1.0 = rigid/staged/formal
]

# ----------------------------------------------------------------------------
# Canonical aesthetic states (archetypes)
# Each represents a recognizable magazine×photography configuration
# ----------------------------------------------------------------------------

MAGPHOTO_COORDS = {
    "editorial_glamour": {
        # Vogue / Harper's Bazaar × Fashion Photography
        "color_saturation": 0.85,
        "detail_sharpness": 0.80,
        "mood_intensity": 0.70,
        "contrast_level": 0.65,
        "temporal_warmth": 0.40,
        "compositional_formality": 0.90,
    },
    "documentary_grit": {
        # Life / Magnum × Documentary Photography
        "color_saturation": 0.45,
        "detail_sharpness": 0.60,
        "mood_intensity": 0.80,
        "contrast_level": 0.85,
        "temporal_warmth": 0.55,
        "compositional_formality": 0.15,
    },
    "minimalist_modern": {
        # Kinfolk / Cereal × Minimalist Photography
        "color_saturation": 0.25,
        "detail_sharpness": 0.75,
        "mood_intensity": 0.20,
        "contrast_level": 0.30,
        "temporal_warmth": 0.25,
        "compositional_formality": 0.60,
    },
    "avant_garde_experimental": {
        # i-D / Dazed × Experimental Photography
        "color_saturation": 0.65,
        "detail_sharpness": 0.40,
        "mood_intensity": 0.95,
        "contrast_level": 0.75,
        "temporal_warmth": 0.35,
        "compositional_formality": 0.10,
    },
    "golden_age_portrait": {
        # Classic Vanity Fair / Esquire × Portrait Photography
        "color_saturation": 0.60,
        "detail_sharpness": 0.70,
        "mood_intensity": 0.55,
        "contrast_level": 0.50,
        "temporal_warmth": 0.85,
        "compositional_formality": 0.80,
    },
    "street_candid": {
        # Vice / early Rolling Stone × Street Photography
        "color_saturation": 0.50,
        "detail_sharpness": 0.45,
        "mood_intensity": 0.60,
        "contrast_level": 0.70,
        "temporal_warmth": 0.50,
        "compositional_formality": 0.05,
    },
    "nature_sublime": {
        # National Geographic × Landscape Photography
        "color_saturation": 0.90,
        "detail_sharpness": 0.85,
        "mood_intensity": 0.75,
        "contrast_level": 0.55,
        "temporal_warmth": 0.60,
        "compositional_formality": 0.50,
    },
}

# ----------------------------------------------------------------------------
# Phase 2.6 Rhythmic Presets
# Oscillations between canonical states creating temporal aesthetics
# Periods: [12, 16, 20, 24, 30]
# ----------------------------------------------------------------------------

MAGPHOTO_RHYTHMIC_PRESETS = {
    "editorial_sweep": {
        "state_a": "editorial_glamour",
        "state_b": "minimalist_modern",
        "pattern": "sinusoidal",
        "num_cycles": 3,
        "steps_per_cycle": 20,
        "description": "Fashion editorial cycling between glamour saturation and minimalist restraint",
    },
    "era_drift": {
        "state_a": "golden_age_portrait",
        "state_b": "minimalist_modern",
        "pattern": "sinusoidal",
        "num_cycles": 3,
        "steps_per_cycle": 24,
        "description": "Temporal drift between warm vintage portraiture and cool modern minimalism",
    },
    "tension_pulse": {
        "state_a": "documentary_grit",
        "state_b": "avant_garde_experimental",
        "pattern": "sinusoidal",
        "num_cycles": 4,
        "steps_per_cycle": 16,
        "description": "Rhythmic pulse between raw documentary honesty and experimental abstraction",
    },
    "mood_arc": {
        "state_a": "minimalist_modern",
        "state_b": "nature_sublime",
        "pattern": "triangular",
        "num_cycles": 2,
        "steps_per_cycle": 30,
        "description": "Gradual arc from quiet minimalism to sublime natural drama and back",
    },
    "formality_toggle": {
        "state_a": "street_candid",
        "state_b": "editorial_glamour",
        "pattern": "square",
        "num_cycles": 5,
        "steps_per_cycle": 12,
        "description": "Sharp toggle between raw street spontaneity and controlled editorial staging",
    },
}

# ----------------------------------------------------------------------------
# Phase 2.7 Visual Vocabulary Types
# Nearest-neighbor matching maps parameter coordinates → prompt keywords
# ----------------------------------------------------------------------------

MAGPHOTO_VISUAL_TYPES = {
    "editorial_polished": {
        "coords": {
            "color_saturation": 0.85,
            "detail_sharpness": 0.80,
            "mood_intensity": 0.65,
            "contrast_level": 0.60,
            "temporal_warmth": 0.40,
            "compositional_formality": 0.90,
        },
        "keywords": [
            "editorial fashion photography",
            "studio-lit with precise shadows",
            "retouched skin and fabric textures",
            "saturated color palette with designer precision",
            "geometric composition with deliberate negative space",
            "glossy magazine-spread finish",
            "high-end commercial aesthetic",
        ],
        "optical_properties": {
            "finish": "glossy",
            "lighting": "controlled multi-source studio",
            "grain": "none",
            "depth_of_field": "selective razor focus",
        },
    },
    "raw_documentary": {
        "coords": {
            "color_saturation": 0.45,
            "detail_sharpness": 0.55,
            "mood_intensity": 0.80,
            "contrast_level": 0.85,
            "temporal_warmth": 0.55,
            "compositional_formality": 0.15,
        },
        "keywords": [
            "raw photojournalistic documentary",
            "available light with deep shadows",
            "visible film grain and optical imperfections",
            "high-contrast tonal range",
            "unposed decisive-moment composition",
            "gritty street-level authenticity",
            "analog warmth with honest texture",
        ],
        "optical_properties": {
            "finish": "matte",
            "lighting": "available/natural with hard shadows",
            "grain": "pronounced film grain",
            "depth_of_field": "deep environmental focus",
        },
    },
    "ethereal_minimal": {
        "coords": {
            "color_saturation": 0.25,
            "detail_sharpness": 0.70,
            "mood_intensity": 0.20,
            "contrast_level": 0.25,
            "temporal_warmth": 0.25,
            "compositional_formality": 0.60,
        },
        "keywords": [
            "airy minimalist photography",
            "soft diffused even lighting",
            "desaturated muted pastel tones",
            "expansive negative space with clean geometry",
            "understated quiet presence",
            "fine-art gallery aesthetic",
            "crisp detail within restrained palette",
        ],
        "optical_properties": {
            "finish": "matte with slight luminosity",
            "lighting": "diffused overcast softbox",
            "grain": "none, clean sensor",
            "depth_of_field": "moderate, subject isolation",
        },
    },
    "dramatic_cinematic": {
        "coords": {
            "color_saturation": 0.70,
            "detail_sharpness": 0.50,
            "mood_intensity": 0.90,
            "contrast_level": 0.80,
            "temporal_warmth": 0.50,
            "compositional_formality": 0.35,
        },
        "keywords": [
            "cinematic narrative photography",
            "chiaroscuro lighting with motivated sources",
            "rich color grading with teal-orange or complementary split",
            "atmospheric haze and volumetric light",
            "widescreen compositional framing",
            "emotionally charged with filmic tension",
            "shallow depth isolating subject from environment",
        ],
        "optical_properties": {
            "finish": "filmic with subtle halation",
            "lighting": "motivated practical sources with controlled spill",
            "grain": "subtle filmic texture",
            "depth_of_field": "shallow cinematic bokeh",
        },
    },
    "vintage_analog": {
        "coords": {
            "color_saturation": 0.55,
            "detail_sharpness": 0.45,
            "mood_intensity": 0.55,
            "contrast_level": 0.50,
            "temporal_warmth": 0.90,
            "compositional_formality": 0.70,
        },
        "keywords": [
            "vintage analog film photography",
            "warm color cast with lifted blacks",
            "soft optical rendering with gentle vignette",
            "Kodachrome or Ektachrome color science",
            "period-correct styling and staging",
            "nostalgic golden-hour warmth",
            "hand-printed darkroom finish",
        ],
        "optical_properties": {
            "finish": "semi-matte with warm cast",
            "lighting": "golden-hour natural or tungsten",
            "grain": "organic film grain, medium format",
            "depth_of_field": "vintage lens rendering with swirl bokeh",
        },
    },
}


# ============================================================================
# Phase 2.6 Oscillation Engine (deterministic, 0 LLM tokens)
# ============================================================================

def _generate_oscillation(num_steps: int, num_cycles: float, pattern: str) -> list:
    """Generate oscillation alpha values [0, 1] for trajectory interpolation."""
    t = [2.0 * math.pi * num_cycles * i / num_steps for i in range(num_steps)]

    if pattern == "sinusoidal":
        return [0.5 * (1.0 + math.sin(v)) for v in t]
    elif pattern == "triangular":
        result = []
        for v in t:
            t_norm = (v / (2.0 * math.pi)) % 1.0
            result.append(2.0 * t_norm if t_norm < 0.5 else 2.0 * (1.0 - t_norm))
        return result
    elif pattern == "square":
        return [0.0 if (v / (2.0 * math.pi)) % 1.0 < 0.5 else 1.0 for v in t]
    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def _interpolate_states(state_a: dict, state_b: dict, alpha: float) -> dict:
    """Linearly interpolate between two parameter states."""
    return {
        p: state_a[p] * (1.0 - alpha) + state_b[p] * alpha
        for p in MAGPHOTO_PARAMETER_NAMES
    }


def _generate_preset_trajectory(preset_name: str) -> list:
    """Generate full trajectory for a Phase 2.6 preset. Returns list of state dicts."""
    preset = MAGPHOTO_RHYTHMIC_PRESETS[preset_name]
    state_a = MAGPHOTO_COORDS[preset["state_a"]]
    state_b = MAGPHOTO_COORDS[preset["state_b"]]
    total_steps = preset["num_cycles"] * preset["steps_per_cycle"]
    alphas = _generate_oscillation(total_steps, preset["num_cycles"], preset["pattern"])
    return [_interpolate_states(state_a, state_b, a) for a in alphas]


def _euclidean_distance(a: dict, b: dict) -> float:
    """Euclidean distance between two parameter states."""
    return math.sqrt(sum((a[p] - b[p]) ** 2 for p in MAGPHOTO_PARAMETER_NAMES))


def _find_nearest_visual_type(state: dict) -> tuple:
    """Find nearest visual vocabulary type via Euclidean distance. Returns (type_name, distance, type_data)."""
    best_name = None
    best_dist = float("inf")
    best_data = None
    for type_name, type_data in MAGPHOTO_VISUAL_TYPES.items():
        d = _euclidean_distance(state, type_data["coords"])
        if d < best_dist:
            best_dist = d
            best_name = type_name
            best_data = type_data
    return best_name, best_dist, best_data


# ============================================================================
# Phase 2.6 MCP Tools
# ============================================================================

@mcp.tool()
def list_rhythmic_presets() -> Dict:
    """
    List all Phase 2.6 rhythmic presets for magazine×photography aesthetics.

    Returns available temporal oscillation patterns between canonical aesthetic
    states.  Each preset defines a periodic trajectory through the 6D
    magazine-photography morphospace that can be used for:
    - Temporal aesthetic transitions in image sequences
    - Multi-domain composition with other Lushy aesthetic domains
    - Attractor-based limit cycle discovery

    Cost: 0 tokens (deterministic lookup)
    """
    result = {}
    for name, preset in MAGPHOTO_RHYTHMIC_PRESETS.items():
        total_steps = preset["num_cycles"] * preset["steps_per_cycle"]
        result[name] = {
            "description": preset["description"],
            "state_a": preset["state_a"],
            "state_b": preset["state_b"],
            "pattern": preset["pattern"],
            "period": preset["steps_per_cycle"],
            "total_steps": total_steps,
            "num_cycles": preset["num_cycles"],
        }
    return {
        "domain": "magazine_photography",
        "parameter_names": MAGPHOTO_PARAMETER_NAMES,
        "presets": result,
        "periods": sorted(set(p["steps_per_cycle"] for p in MAGPHOTO_RHYTHMIC_PRESETS.values())),
    }


@mcp.tool()
def get_aesthetic_state_coordinates(state_name: str) -> Dict:
    """
    Get normalized parameter coordinates for a canonical aesthetic state.

    Args:
        state_name: One of the canonical states — "editorial_glamour",
            "documentary_grit", "minimalist_modern", "avant_garde_experimental",
            "golden_age_portrait", "street_candid", "nature_sublime"

    Returns parameter coordinates in the 6D magazine-photography morphospace
    with values in [0.0, 1.0].

    Cost: 0 tokens (deterministic lookup)
    """
    if state_name not in MAGPHOTO_COORDS:
        return {
            "error": f"Unknown state '{state_name}'",
            "available_states": list(MAGPHOTO_COORDS.keys()),
        }
    return {
        "state_name": state_name,
        "domain": "magazine_photography",
        "parameter_names": MAGPHOTO_PARAMETER_NAMES,
        "coordinates": MAGPHOTO_COORDS[state_name],
    }


@mcp.tool()
def generate_rhythmic_sequence(
    preset_name: str,
    num_steps: Optional[int] = None,
) -> Dict:
    """
    Generate a Phase 2.6 rhythmic oscillation sequence from a preset.

    Produces a temporal trajectory oscillating between two canonical
    aesthetic states.  Each step is a complete parameter state in the 6D
    magazine-photography morphospace.

    Args:
        preset_name: Preset name from list_rhythmic_presets()
        num_steps: Override total steps (default uses preset's num_cycles × steps_per_cycle)

    Returns full trajectory with per-step parameter states and metadata.

    Cost: 0 tokens (deterministic computation)
    """
    if preset_name not in MAGPHOTO_RHYTHMIC_PRESETS:
        return {
            "error": f"Unknown preset '{preset_name}'",
            "available_presets": list(MAGPHOTO_RHYTHMIC_PRESETS.keys()),
        }

    preset = MAGPHOTO_RHYTHMIC_PRESETS[preset_name]
    state_a = MAGPHOTO_COORDS[preset["state_a"]]
    state_b = MAGPHOTO_COORDS[preset["state_b"]]

    total = num_steps or (preset["num_cycles"] * preset["steps_per_cycle"])
    num_cycles = preset["num_cycles"] if num_steps is None else num_steps / preset["steps_per_cycle"]
    alphas = _generate_oscillation(total, num_cycles, preset["pattern"])

    trajectory = [_interpolate_states(state_a, state_b, a) for a in alphas]

    return {
        "domain": "magazine_photography",
        "preset": preset_name,
        "description": preset["description"],
        "period": preset["steps_per_cycle"],
        "total_steps": total,
        "pattern": preset["pattern"],
        "state_a": preset["state_a"],
        "state_b": preset["state_b"],
        "parameter_names": MAGPHOTO_PARAMETER_NAMES,
        "trajectory": trajectory,
    }


@mcp.tool()
def map_magazine_photography_parameters(
    state_name: str,
    intensity: str = "moderate",
    emphasis: str = "color",
) -> Dict:
    """
    Map an aesthetic state to full visual synthesis parameters.

    Like catastrophe-morph's map_catastrophe_parameters — returns a
    complete parameter set adjusted by intensity and emphasis, ready for
    visual synthesis or cross-domain composition.

    Args:
        state_name: Canonical state (e.g. "editorial_glamour", "documentary_grit")
        intensity: "subtle", "moderate", or "dramatic"
        emphasis: "color", "detail", "mood", "contrast", "warmth", or "composition"

    Cost: 0 tokens (deterministic)
    """
    if state_name not in MAGPHOTO_COORDS:
        return {
            "error": f"Unknown state '{state_name}'",
            "available_states": list(MAGPHOTO_COORDS.keys()),
        }

    base = dict(MAGPHOTO_COORDS[state_name])

    # Intensity scaling
    scale = {"subtle": 0.6, "moderate": 1.0, "dramatic": 1.4}.get(intensity, 1.0)
    emphasis_param = {
        "color": "color_saturation",
        "detail": "detail_sharpness",
        "mood": "mood_intensity",
        "contrast": "contrast_level",
        "warmth": "temporal_warmth",
        "composition": "compositional_formality",
    }.get(emphasis)

    params = {}
    for p in MAGPHOTO_PARAMETER_NAMES:
        v = base[p]
        if p == emphasis_param:
            v = min(1.0, max(0.0, v * scale * 1.2))
        else:
            v = min(1.0, max(0.0, v * scale))
        params[p] = round(v, 4)

    return {
        "domain": "magazine_photography",
        "state": state_name,
        "intensity": intensity,
        "emphasis": emphasis,
        "parameters": params,
        "parameter_names": MAGPHOTO_PARAMETER_NAMES,
    }


# ============================================================================
# Phase 2.7 Attractor Visualization — Prompt Generation
# ============================================================================

@mcp.tool()
def extract_visual_vocabulary(
    state: Dict,
    strength: float = 1.0,
) -> Dict:
    """
    Extract visual prompt vocabulary from parameter coordinates.

    Maps a 6D parameter state to the nearest canonical visual type and
    returns image-generation-ready keywords.  Uses nearest-neighbour
    matching against 5 visual types derived from the magazine×photography
    morphospace.

    Args:
        state: Parameter dict with keys matching MAGPHOTO_PARAMETER_NAMES
               (values in [0.0, 1.0])
        strength: Keyword weight multiplier [0.0, 1.0] (default 1.0)

    Returns nearest visual type, distance, keywords, and optical properties.

    Cost: 0 tokens (deterministic nearest-neighbour computation)
    """
    # Validate keys
    missing = [p for p in MAGPHOTO_PARAMETER_NAMES if p not in state]
    if missing:
        return {"error": f"Missing parameters: {missing}", "expected": MAGPHOTO_PARAMETER_NAMES}

    type_name, dist, type_data = _find_nearest_visual_type(state)

    keywords = type_data["keywords"]
    if strength < 1.0:
        # Reduce keyword count proportionally
        n = max(2, int(len(keywords) * strength))
        keywords = keywords[:n]

    return {
        "domain": "magazine_photography",
        "nearest_type": type_name,
        "distance": round(dist, 4),
        "keywords": keywords,
        "optical_properties": type_data["optical_properties"],
        "input_state": state,
        "strength": strength,
    }


@mcp.tool()
def generate_attractor_prompt(
    preset_name: Optional[str] = None,
    custom_state: Optional[Dict] = None,
    mode: str = "composite",
    style_modifier: str = "",
    keyframe_count: int = 4,
) -> Dict:
    """
    Generate image-generation prompts from attractor state or preset.

    Translates mathematical attractor coordinates into visual prompts
    suitable for Flux, Stable Diffusion, DALL-E, ComfyUI, Midjourney, etc.

    Modes:
        composite:  Single blended prompt from current state
        split_view: Separate prompt sections (color, lighting, texture, mood)
        sequence:   Multiple keyframe prompts from a rhythmic preset trajectory

    Args:
        preset_name: Phase 2.6 preset name (for sequence mode or default state)
        custom_state: Optional custom parameter dict (overrides preset if given)
        mode: "composite" | "split_view" | "sequence"
        style_modifier: Optional prefix like "35mm film", "digital medium format"
        keyframe_count: Number of keyframes for sequence mode (default 4)

    Cost: 0 tokens (deterministic)
    """
    # --- Resolve the working state(s) ----
    if mode == "sequence":
        if not preset_name:
            return {"error": "preset_name required for sequence mode"}
        if preset_name not in MAGPHOTO_RHYTHMIC_PRESETS:
            return {"error": f"Unknown preset '{preset_name}'",
                    "available": list(MAGPHOTO_RHYTHMIC_PRESETS.keys())}

        trajectory = _generate_preset_trajectory(preset_name)
        total = len(trajectory)
        step_size = max(1, total // keyframe_count)
        keyframes = []
        for k in range(keyframe_count):
            idx = min(k * step_size, total - 1)
            st = trajectory[idx]
            type_name, dist, type_data = _find_nearest_visual_type(st)
            kw = type_data["keywords"]
            prompt = f"{style_modifier + ', ' if style_modifier else ''}{', '.join(kw)}"
            keyframes.append({
                "step": idx,
                "state": {p: round(st[p], 4) for p in MAGPHOTO_PARAMETER_NAMES},
                "nearest_type": type_name,
                "distance": round(dist, 4),
                "prompt": prompt,
            })
        return {
            "domain": "magazine_photography",
            "mode": "sequence",
            "preset": preset_name,
            "description": MAGPHOTO_RHYTHMIC_PRESETS[preset_name]["description"],
            "keyframe_count": keyframe_count,
            "keyframes": keyframes,
        }

    # Single state for composite / split_view
    if custom_state:
        missing = [p for p in MAGPHOTO_PARAMETER_NAMES if p not in custom_state]
        if missing:
            return {"error": f"Missing parameters in custom_state: {missing}"}
        state = custom_state
        state_source = "custom"
    elif preset_name:
        if preset_name not in MAGPHOTO_RHYTHMIC_PRESETS:
            return {"error": f"Unknown preset '{preset_name}'"}
        # Use midpoint of first cycle as representative state
        trajectory = _generate_preset_trajectory(preset_name)
        mid = len(trajectory) // 4  # quarter-cycle = peak of sinusoidal
        state = trajectory[mid]
        state_source = f"preset:{preset_name}:step_{mid}"
    else:
        return {"error": "Provide preset_name or custom_state"}

    type_name, dist, type_data = _find_nearest_visual_type(state)

    if mode == "composite":
        prompt = f"{style_modifier + ', ' if style_modifier else ''}{', '.join(type_data['keywords'])}"
        return {
            "domain": "magazine_photography",
            "mode": "composite",
            "source": state_source,
            "nearest_type": type_name,
            "distance": round(dist, 4),
            "prompt": prompt,
            "vocabulary": {
                "keywords": type_data["keywords"],
                "optical": type_data["optical_properties"],
            },
            "state": {p: round(state[p], 4) for p in MAGPHOTO_PARAMETER_NAMES},
        }

    elif mode == "split_view":
        kw = type_data["keywords"]
        optical = type_data["optical_properties"]
        prefix = f"{style_modifier}, " if style_modifier else ""
        sections = {
            "color_and_tone": f"{prefix}{kw[3] if len(kw) > 3 else ''}, {optical.get('finish', '')}",
            "lighting": f"{prefix}{kw[1] if len(kw) > 1 else ''}, {optical.get('lighting', '')}",
            "texture_and_detail": f"{prefix}{kw[2] if len(kw) > 2 else ''}, {optical.get('grain', '')}",
            "mood_and_composition": f"{prefix}{kw[4] if len(kw) > 4 else ''}, {kw[5] if len(kw) > 5 else ''}",
        }
        return {
            "domain": "magazine_photography",
            "mode": "split_view",
            "source": state_source,
            "nearest_type": type_name,
            "distance": round(dist, 4),
            "sections": sections,
            "state": {p: round(state[p], 4) for p in MAGPHOTO_PARAMETER_NAMES},
        }

    return {"error": f"Unknown mode '{mode}'. Use composite, split_view, or sequence."}


@mcp.tool()
def compute_aesthetic_distance(state_a_name: str, state_b_name: str) -> Dict:
    """
    Compute Euclidean distance between two canonical aesthetic states.

    Useful for understanding how far apart two magazine×photography
    aesthetics are in morphospace, which affects transition smoothness
    and rhythmic preset behavior.

    Args:
        state_a_name: First canonical state name
        state_b_name: Second canonical state name

    Cost: 0 tokens (pure computation)
    """
    if state_a_name not in MAGPHOTO_COORDS:
        return {"error": f"Unknown state '{state_a_name}'", "available": list(MAGPHOTO_COORDS.keys())}
    if state_b_name not in MAGPHOTO_COORDS:
        return {"error": f"Unknown state '{state_b_name}'", "available": list(MAGPHOTO_COORDS.keys())}

    a = MAGPHOTO_COORDS[state_a_name]
    b = MAGPHOTO_COORDS[state_b_name]
    dist = _euclidean_distance(a, b)

    per_param = {p: round(abs(a[p] - b[p]), 4) for p in MAGPHOTO_PARAMETER_NAMES}
    max_param = max(per_param, key=per_param.get)

    return {
        "state_a": state_a_name,
        "state_b": state_b_name,
        "euclidean_distance": round(dist, 4),
        "per_parameter_difference": per_param,
        "largest_difference": {"parameter": max_param, "value": per_param[max_param]},
        "transition_characterization": (
            "smooth" if dist < 0.4 else "moderate" if dist < 0.7 else "dramatic"
        ),
    }


@mcp.tool()
def get_server_info() -> Dict:
    """
    Get comprehensive information about the Magazine×Photography MCP server.

    Returns server metadata, capabilities, library stats, and Phase 2.6/2.7
    enhancement details.
    """
    return {
        "server": "magazine-photography",
        "version": "2.7.0",
        "description": "Magazine × Photography aesthetic domain with rhythmic presets and attractor visualization",
        "library": {
            "magazines": len(MAGAZINES),
            "photography_styles": len(PHOTOGRAPHY),
            "combinations": len(COMBINATIONS),
        },
        "phase_2_6_enhancements": {
            "rhythmic_presets": True,
            "preset_count": len(MAGPHOTO_RHYTHMIC_PRESETS),
            "presets": list(MAGPHOTO_RHYTHMIC_PRESETS.keys()),
            "periods": sorted(set(p["steps_per_cycle"] for p in MAGPHOTO_RHYTHMIC_PRESETS.values())),
            "canonical_states": list(MAGPHOTO_COORDS.keys()),
            "parameter_count": len(MAGPHOTO_PARAMETER_NAMES),
            "parameter_names": MAGPHOTO_PARAMETER_NAMES,
        },
        "phase_2_7_enhancements": {
            "attractor_visualization": True,
            "visual_types": list(MAGPHOTO_VISUAL_TYPES.keys()),
            "prompt_modes": ["composite", "split_view", "sequence"],
            "supported_generators": [
                "Flux", "Stable Diffusion", "DALL-E",
                "Midjourney", "ComfyUI",
            ],
        },
        "multi_domain_composition": {
            "compatible_with": [
                "microscopy-aesthetics",
                "nuclear-aesthetic",
                "catastrophe-morph-mcp",
                "diatom-morphology-mcp",
                "heraldic-blazonry-mcp",
            ],
            "domain_id": "magazine_photography",
            "integration_ready": True,
        },
        "cost_profile": {
            "phase_2_6_tools": "0 tokens (deterministic)",
            "phase_2_7_tools": "0 tokens (deterministic)",
            "llm_required_for": "creative synthesis only (Layer 3)",
        },
    }


if __name__ == "__main__":
    mcp.run()
