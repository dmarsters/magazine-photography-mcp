"""
Magazine × Photography Olog System
Three-layer architecture: Categorical taxonomy → Aesthetic profiles → MCP interface

This olog formalizes the semantic relationships between:
- Magazine eras (temporal positioning)
- Visual treatment parameters (color, lighting, contrast, texture)
- Photography styles (composition, technical approach)
- Combination compatibility (harmony, tension, alignment)

Using category theory principles to create deterministic enhancement mappings.
"""

from enum import Enum
from typing import List, Dict, Literal
from dataclasses import dataclass


# ============================================================================
# LAYER 1: CATEGORICAL TAXONOMY (OLOG STRUCTURE)
# ============================================================================

class TemporalAlignment(str, Enum):
    """Era-matched combinations have natural aesthetic resonance"""
    ERA_MATCHED = "era_matched"  # Magazine era matches photography style era
    CREATIVE_ANACHRONISM = "creative_anachronism"  # Intentional temporal mismatch
    TEMPORAL_CLASH = "temporal_clash"  # High-tension historical juxtaposition


class ColorPaletteCategory(str, Enum):
    """High-level color approach"""
    VIBRANT = "vibrant"  # High saturation, bold primaries
    MUTED = "muted"  # Desaturated, earth tones, pastels
    MONOCHROMATIC = "monochromatic"  # B&W, single color dominant
    COOL = "cool"  # Blues, cyans, cool tones
    WARM = "warm"  # Oranges, yellows, earth warmth
    MIXED = "mixed"  # Complex multi-tone


class LightingApproach(str, Enum):
    """Fundamental lighting philosophy"""
    HARD_DIRECTIONAL = "hard_directional"  # Strong shadows, high contrast
    SOFT_DIFFUSED = "soft_diffused"  # Gentle, even illumination
    NATURAL_AMBIENT = "natural_ambient"  # Golden hour, window light
    CLINICAL = "clinical"  # Neutral, even studio light
    DRAMATIC = "dramatic"  # Staged, theatrical lighting


class ContrastProfile(str, Enum):
    """Tonal separation strategy"""
    HIGH = "high"  # Blown highlights, crushed blacks
    MEDIUM = "medium"  # Balanced, good separation
    LOW = "low"  # Lifted shadows, compressed range
    EXTREME = "extreme"  # Maximum separation and posterization


class TextureEmphasis(str, Enum):
    """Surface and detail rendering"""
    SHARP = "sharp"  # Crisp, clinical, grain emphasized
    SMOOTH = "smooth"  # Glossy, polished surfaces
    ORGANIC = "organic"  # Natural textures, tactile quality
    SYNTHETIC = "synthetic"  # Manufactured, materials emphasized
    ETHEREAL = "ethereal"  # Soft, dreamlike, minimal detail


class CompositionStrategy(str, Enum):
    """Spatial organization approach"""
    GEOMETRIC = "geometric"  # Grid, symmetry, mathematical precision
    ASYMMETRICAL = "asymmetrical"  # Balanced but not symmetric
    TIGHT_CROP = "tight_crop"  # Close, intimate framing
    ENVIRONMENTAL = "environmental"  # Subject in context
    MINIMALIST = "minimalist"  # Negative space, sparse elements


class FocalLengthCategory(str, Enum):
    """Lens choice implications"""
    ULTRA_WIDE = "ultra_wide"  # 14-24mm, environmental, distortion
    WIDE = "wide"  # 24-35mm, environmental with form
    STANDARD = "standard"  # 35-50mm, natural perspective
    MEDIUM_TELEPHOTO = "medium_telephoto"  # 50-85mm, intimate portraits
    TELEPHOTO = "telephoto"  # 85-200mm, compressed, isolated


class SubjectContext(str, Enum):
    """What subjects are typically photographed"""
    PEOPLE = "people"  # Portraits, groups, fashion, lifestyle
    OBJECTS = "objects"  # Products, still life, artifacts
    PLACES = "places"  # Architecture, landscape, environment
    MOMENTS = "moments"  # Candid, decisive, temporal
    ABSTRACT = "abstract"  # Concepts, texture, form


# ============================================================================
# LAYER 2: COMPATIBILITY MEASUREMENT
# ============================================================================

@dataclass
class CompatibilityScore:
    """Deterministic compatibility measurement between magazine × photography"""
    
    # Harmony: How naturally do these aesthetics align? (0-10)
    overall_harmony: int
    
    # Technical: Do technical approaches complement? (0-10)
    technical_score: int
    
    # Aesthetic: Do visual treatments align? (0-10)
    aesthetic_score: int
    
    # Tension: How interesting is the creative mismatch? (0-10)
    creative_tension: int
    
    # Temporal: How do eras align? (TemporalAlignment)
    temporal_alignment: TemporalAlignment
    
    # Rationale: Why these scores?
    rationale: str


# ============================================================================
# LAYER 3: ENHANCEMENT PARAMETER MAPPING
# ============================================================================

@dataclass
class ImagePromptModifiers:
    """Deterministic modifiers derived from combination"""
    
    # Distance: how close is the camera?
    distance_options: List[Literal["Extreme Close-up", "Close-up", "Medium", "Full", "Wide"]]
    
    # Angle: what's the camera angle?
    angle_options: List[Literal["Overhead", "Eye-level", "Low Angle", "Dutch Tilt", "Profile"]]
    
    # Intensity controls (0.0-1.0)
    color_intensity_default: float  # 0=muted, 1=vibrant
    detail_sharpness_default: float  # 0=soft, 1=sharp
    mood_intensity_default: float  # 0=subtle, 1=dramatic
    
    # Recommended keyword tags
    prompt_keywords: List[str]


@dataclass
class VisualTreatmentProfile:
    """Deterministic visual treatment extraction"""
    
    color_palette: str
    color_category: ColorPaletteCategory
    
    lighting: str
    lighting_approach: LightingApproach
    
    contrast: str
    contrast_profile: ContrastProfile
    
    texture: str
    texture_emphasis: TextureEmphasis


@dataclass
class PhotographyTechnicalProfile:
    """Deterministic technical approach extraction"""
    
    composition_strategy: CompositionStrategy
    focal_length_category: FocalLengthCategory
    subject_context: SubjectContext
    
    framing_description: str
    depth_of_field: Literal["shallow", "moderate", "deep"]
    typical_aperture_range: str


# ============================================================================
# LAYER 4: OLOG MORPHISMS (MAPPINGS)
# ============================================================================

class OlogMorphisms:
    """Deterministic mappings between categories - implements pure category theory"""
    
    @staticmethod
    def magazine_to_visual_treatment(magazine: Dict) -> VisualTreatmentProfile:
        """
        Extract visual treatment profile from magazine definition.
        Morphism: Magazine → VisualTreatmentProfile
        """
        visual = magazine.get("visual_treatment", {})
        
        # Deterministic color categorization
        color_text = visual.get("color_palette", "").lower()
        if "muted" in color_text or "desaturated" in color_text or "pastel" in color_text:
            color_cat = ColorPaletteCategory.MUTED
        elif "vibrant" in color_text or "saturated" in color_text or "vivid" in color_text:
            color_cat = ColorPaletteCategory.VIBRANT
        elif "cool" in color_text or "blue" in color_text or "cyan" in color_text:
            color_cat = ColorPaletteCategory.COOL
        elif "warm" in color_text or "orange" in color_text or "yellow" in color_text:
            color_cat = ColorPaletteCategory.WARM
        elif "black and white" in color_text or "b&w" in color_text or "monochrome" in color_text:
            color_cat = ColorPaletteCategory.MONOCHROMATIC
        else:
            color_cat = ColorPaletteCategory.MIXED
        
        # Deterministic lighting categorization
        lighting_text = visual.get("lighting", "").lower()
        if "soft" in lighting_text or "diffused" in lighting_text:
            lighting_cat = LightingApproach.SOFT_DIFFUSED
        elif "hard" in lighting_text or "dramatic" in lighting_text or "sharp" in lighting_text:
            lighting_cat = LightingApproach.HARD_DIRECTIONAL
        elif "natural" in lighting_text or "golden hour" in lighting_text or "window" in lighting_text:
            lighting_cat = LightingApproach.NATURAL_AMBIENT
        elif "clinical" in lighting_text or "neutral" in lighting_text or "even" in lighting_text:
            lighting_cat = LightingApproach.CLINICAL
        else:
            lighting_cat = LightingApproach.DRAMATIC
        
        # Deterministic contrast categorization
        contrast_text = visual.get("contrast", "").lower()
        if "extreme" in contrast_text or "crushed" in contrast_text or "blown" in contrast_text:
            contrast_cat = ContrastProfile.EXTREME
        elif "high" in contrast_text:
            contrast_cat = ContrastProfile.HIGH
        elif "low" in contrast_text or "lifted" in contrast_text or "compressed" in contrast_text:
            contrast_cat = ContrastProfile.LOW
        else:
            contrast_cat = ContrastProfile.MEDIUM
        
        # Deterministic texture categorization
        texture_text = visual.get("texture", "").lower()
        if "sharp" in texture_text or "crisp" in texture_text or "clinical" in texture_text:
            texture_cat = TextureEmphasis.SHARP
        elif "soft" in texture_text or "dreamy" in texture_text or "ethereal" in texture_text:
            texture_cat = TextureEmphasis.ETHEREAL
        elif "smooth" in texture_text or "glossy" in texture_text or "polished" in texture_text:
            texture_cat = TextureEmphasis.SMOOTH
        elif "synthetic" in texture_text or "materials" in texture_text or "manufactured" in texture_text:
            texture_cat = TextureEmphasis.SYNTHETIC
        else:
            texture_cat = TextureEmphasis.ORGANIC
        
        return VisualTreatmentProfile(
            color_palette=visual.get("color_palette", ""),
            color_category=color_cat,
            lighting=visual.get("lighting", ""),
            lighting_approach=lighting_cat,
            contrast=visual.get("contrast", ""),
            contrast_profile=contrast_cat,
            texture=visual.get("texture", ""),
            texture_emphasis=texture_cat
        )
    
    @staticmethod
    def photography_to_technical_profile(photography: Dict) -> PhotographyTechnicalProfile:
        """
        Extract technical profile from photography style definition.
        Morphism: PhotographyStyle → PhotographyTechnicalProfile
        """
        technical = photography.get("technical", {})
        aesthetic = photography.get("aesthetic", {})
        context = photography.get("context", {})
        
        # Deterministic composition strategy
        composition_text = aesthetic.get("composition", "").lower()
        if "grid" in composition_text or "geometric" in composition_text or "symmetric" in composition_text:
            composition_cat = CompositionStrategy.GEOMETRIC
        elif "asymmetric" in composition_text or "balanced" in composition_text:
            composition_cat = CompositionStrategy.ASYMMETRICAL
        elif "crop" in composition_text or "tight" in composition_text or "close" in composition_text:
            composition_cat = CompositionStrategy.TIGHT_CROP
        elif "environment" in composition_text or "context" in composition_text:
            composition_cat = CompositionStrategy.ENVIRONMENTAL
        elif "minimal" in composition_text or "sparse" in composition_text or "negative space" in composition_text:
            composition_cat = CompositionStrategy.MINIMALIST
        else:
            composition_cat = CompositionStrategy.ASYMMETRICAL
        
        # Deterministic focal length categorization
        focal_text = technical.get("focal_length", "").lower()
        if "ultra" in focal_text or "14" in focal_text or "16" in focal_text:
            focal_cat = FocalLengthCategory.ULTRA_WIDE
        elif "wide" in focal_text or "24" in focal_text or "35" in focal_text:
            focal_cat = FocalLengthCategory.WIDE
        elif "50" in focal_text or "35-50" in focal_text or "standard" in focal_text:
            focal_cat = FocalLengthCategory.STANDARD
        elif "85" in focal_text or "70" in focal_text or "50-85" in focal_text or "medium telephoto" in focal_text:
            focal_cat = FocalLengthCategory.MEDIUM_TELEPHOTO
        elif "telephoto" in focal_text or "100" in focal_text or "200" in focal_text:
            focal_cat = FocalLengthCategory.TELEPHOTO
        else:
            focal_cat = FocalLengthCategory.STANDARD
        
        # Deterministic subject context
        typical_uses = " ".join(context.get("typical_uses", [])).lower()
        if "portrait" in typical_uses or "people" in typical_uses or "fashion" in typical_uses:
            subject_cat = SubjectContext.PEOPLE
        elif "product" in typical_uses or "still life" in typical_uses:
            subject_cat = SubjectContext.OBJECTS
        elif "architecture" in typical_uses or "landscape" in typical_uses or "place" in typical_uses:
            subject_cat = SubjectContext.PLACES
        elif "candid" in typical_uses or "moment" in typical_uses or "event" in typical_uses:
            subject_cat = SubjectContext.MOMENTS
        else:
            subject_cat = SubjectContext.ABSTRACT
        
        # Deterministic depth of field
        aperture_text = technical.get("typical_aperture_range", "").lower()
        if "f/1" in aperture_text or "shallow" in aperture_text:
            dof = "shallow"
        elif "f/5.6" in aperture_text or "f/8" in aperture_text or "deep" in aperture_text:
            dof = "deep"
        else:
            dof = "moderate"
        
        return PhotographyTechnicalProfile(
            composition_strategy=composition_cat,
            focal_length_category=focal_cat,
            subject_context=subject_cat,
            framing_description=aesthetic.get("composition", ""),
            depth_of_field=dof,
            typical_aperture_range=technical.get("typical_aperture_range", "f/2.8-f/5.6")
        )
    
    @staticmethod
    def compatibility_mapping(
        magazine_profile: VisualTreatmentProfile,
        photography_profile: PhotographyTechnicalProfile,
        magazine_era: str,
        photography_name: str
    ) -> CompatibilityScore:
        """
        Deterministic compatibility calculation using categorical alignment.
        Morphism: (VisualTreatment, PhotographyTechnique) → CompatibilityScore
        """
        
        # Calculate technical score
        technical_score = 5  # Base
        
        # Match focal length to composition needs
        if photography_profile.focal_length_category == FocalLengthCategory.MEDIUM_TELEPHOTO:
            technical_score += 1  # Good for portraits
        if photography_profile.composition_strategy == CompositionStrategy.TIGHT_CROP:
            technical_score += 1  # Works with closer focal lengths
        if photography_profile.focal_length_category == FocalLengthCategory.WIDE:
            if photography_profile.composition_strategy == CompositionStrategy.ENVIRONMENTAL:
                technical_score += 1  # Natural fit
        
        # Calculate aesthetic score
        aesthetic_score = 5  # Base
        
        # Color harmony
        if magazine_profile.color_category == ColorPaletteCategory.MUTED:
            if magazine_profile.lighting_approach == LightingApproach.SOFT_DIFFUSED:
                aesthetic_score += 1  # Natural pairing
        
        if magazine_profile.color_category == ColorPaletteCategory.VIBRANT:
            if magazine_profile.contrast_profile in [ContrastProfile.HIGH, ContrastProfile.EXTREME]:
                aesthetic_score += 1  # Supports bold color
        
        # Lighting-contrast harmony
        if magazine_profile.lighting_approach == LightingApproach.HARD_DIRECTIONAL:
            if magazine_profile.contrast_profile in [ContrastProfile.HIGH, ContrastProfile.EXTREME]:
                aesthetic_score += 1  # Natural pairing
        
        # Texture compatibility
        if magazine_profile.texture_emphasis == TextureEmphasis.SHARP:
            if photography_profile.composition_strategy == CompositionStrategy.GEOMETRIC:
                aesthetic_score += 1  # Detail-focused
        
        # Temporal alignment
        if "1960" in magazine_era or "1970" in magazine_era:
            if "documentary" in photography_name.lower() or "street" in photography_name.lower():
                temporal_align = TemporalAlignment.ERA_MATCHED
            elif "studio" in photography_name.lower() or "fashion" in photography_name.lower():
                temporal_align = TemporalAlignment.ERA_MATCHED
            else:
                temporal_align = TemporalAlignment.CREATIVE_ANACHRONISM
        elif "contemporary" in magazine_era or "2000" in magazine_era or "2010" in magazine_era:
            if "cinematic" in photography_name.lower() or "drone" in photography_name.lower():
                temporal_align = TemporalAlignment.ERA_MATCHED
            else:
                temporal_align = TemporalAlignment.CREATIVE_ANACHRONISM
        else:
            temporal_align = TemporalAlignment.CREATIVE_ANACHRONISM
        
        # Creative tension (interesting mismatches)
        tension = 5  # Base
        if temporal_align == TemporalAlignment.CREATIVE_ANACHRONISM:
            tension += 2
        if magazine_profile.contrast_profile == ContrastProfile.EXTREME:
            if photography_profile.composition_strategy == CompositionStrategy.MINIMALIST:
                tension += 1  # Interesting contrast
        
        # Overall harmony (inverse of tension for most cases)
        harmony = (technical_score + aesthetic_score) // 2
        if tension > 7:
            harmony -= 1  # High tension reduces harmony
        
        harmony = max(1, min(10, harmony))
        technical_score = max(1, min(10, technical_score))
        aesthetic_score = max(1, min(10, aesthetic_score))
        tension = max(1, min(10, tension))
        
        rationale = (
            f"Magazine: {magazine_profile.color_category.value} colors, "
            f"{magazine_profile.lighting_approach.value} lighting. "
            f"Photography: {photography_profile.composition_strategy.value} composition, "
            f"{photography_profile.focal_length_category.value} focal length. "
            f"Temporal: {temporal_align.value}."
        )
        
        return CompatibilityScore(
            overall_harmony=harmony,
            technical_score=technical_score,
            aesthetic_score=aesthetic_score,
            creative_tension=tension,
            temporal_alignment=temporal_align,
            rationale=rationale
        )
