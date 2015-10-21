# -*- coding:utf-8 -*-

# ----------------------
# Arnold
# ----------------------
mayaShader_to_aiStandard_mappingTable = [
    ("color",             "color"),
    ("reflectedColor",    "KsColor"),
    ("transparency",      "opacity"),
    ("normalCamera",      "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    ]

VRayMtl_to_aiStandard_mappingTable = [
    ("color",             "color"),
    ("reflectionColor",   "KsColor"),
    ("opacityMap",        "opacity"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    #("bumpMult",          "normalCamera"),
    ]

# ----------------------
# VRay
# ----------------------
miaMaterialX_To_VRayMtl_mappingTable = [
    ("diffuse",             "color"),
    ("diffuse_weight",      "diffuseColorAmount"),
    ("diffuse_roughness",   "roughnessAmount"),
    ("refl_color",          "reflectionColor"),
    ("reflectivity",        "reflectionColorAmount"),
    ("refl_gloss",          "reflectionGlossiness"),
    ("refl_gloss_samples",  "reflectionSubdivs"),
    ("refl_falloff_on",     "reflectionDimDistanceOn"),
    ("refl_falloff_dist",   "reflectionDimDistance"),
    ("refl_depth",          "reflectionsMaxDepth"),
    ("refr_ior",            "refractionIOR"),
    ("refr_color",          "refractionColor"),
    ("transparency",        "refractionColorAmount"),
    ("refr_gloss",          "refractionGlossiness"),
    ("refr_gloss_samples",  "refractionSubdivs"),
    ("thin_walled",         "refractionIOR")
    ]

# ----------------------
# Software
# ----------------------
VRayMtl_To_Blinn_mappingTable = [
    ("diffuse",             "color"),
    ("diffuse_weight",      "diffuseColorAmount"),
    ("diffuse_roughness",   "roughnessAmount"),
    ("refl_color",          "reflectionColor"),
    ("reflectivity",        "reflectionColorAmount"),
    ("refl_gloss",          "reflectionGlossiness"),
    ("refl_gloss_samples",  "reflectionSubdivs"),
    ("refl_falloff_on",     "reflectionDimDistanceOn"),
    ("refl_falloff_dist",   "reflectionDimDistance"),
    ("refl_depth",          "reflectionsMaxDepth"),
    ("refr_ior",            "refractionIOR"),
    ("refr_color",          "refractionColor"),
    ("transparency",        "refractionColorAmount"),
    ("refr_gloss",          "refractionGlossiness"),
    ("refr_gloss_samples",  "refractionSubdivs"),
    ("thin_walled",         "refractionIOR")
    ]