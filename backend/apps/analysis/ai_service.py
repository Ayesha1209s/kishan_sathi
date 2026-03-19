"""
===============================================================
🌱 KISHAN SATHI – AI Analysis Service
Pluggable AI model interface.
Switch AI_MODEL_TYPE in settings: 'placeholder' | 'tensorflow' | 'pytorch'
===============================================================
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from django.conf import settings

logger = logging.getLogger('apps.analysis')


# ──────────────────────────────────────────────────────────────
# 🔌 BASE MODEL INTERFACE
# All model adapters must implement this interface
# ──────────────────────────────────────────────────────────────
class BaseCropDiseaseModel(ABC):
    """Abstract base class for all AI model adapters."""

    @abstractmethod
    def predict(self, image_path: str) -> dict:
        """
        Run inference on an image file.

        Args:
            image_path: Absolute path to the image file

        Returns:
            {
                "disease_name":             str,
                "scientific_name":          str,
                "confidence_score":         float (0–100),
                "is_healthy":               bool,
                "severity":                 str,
                "description":              str,
                "symptoms":                 str,
                "cause":                    str,
                "chemical_treatment":       str,
                "organic_treatment":        str,
                "preventive_measures":      str,
                "alternative_predictions":  list[dict],
                "model_version":            str,
                "processing_time":          float,
            }
        """
        pass


# ──────────────────────────────────────────────────────────────
# 🔬 PLACEHOLDER MODEL (NO AI DEPENDENCY REQUIRED)
# Simulates AI responses for development/testing
# ──────────────────────────────────────────────────────────────
class PlaceholderModel(BaseCropDiseaseModel):
    """
    Mock AI model for development/testing.
    Returns realistic-looking responses without any ML libraries.
    Replace with TensorFlowModel or PyTorchModel in production.
    """

    DISEASE_DB = [
        {
            "disease_name":       "Wheat Leaf Rust",
            "scientific_name":    "Puccinia triticina",
            "is_healthy":         False,
            "severity":           "high",
            "description":        "Wheat Leaf Rust is a fungal disease causing orange-brown pustules on leaves. It severely reduces photosynthesis and can lower yields by 30–70% if untreated.",
            "symptoms":           "Orange-brown urediospore pustules on the upper leaf surface, yellow halos around pustules, premature leaf death in severe cases.",
            "cause":              "Fungal pathogen Puccinia triticina, spread by wind-borne spores. Favoured by cool temperatures (15–22°C) and high humidity.",
            "chemical_treatment": "Propiconazole 25% EC @ 1 ml/litre water. Apply twice at 15-day intervals. Tebuconazole 250 EC also effective.",
            "organic_treatment":  "Neem oil spray (5 ml/litre). Trichoderma harzianum seed treatment. Sulphur dust (20 kg/ha) as preventive.",
            "preventive_measures":"Use resistant wheat varieties (HD-2967, WH-1105). Timely sowing in recommended period. Avoid excessive nitrogen fertilisation.",
        },
        {
            "disease_name":       "Tomato Late Blight",
            "scientific_name":    "Phytophthora infestans",
            "is_healthy":         False,
            "severity":           "critical",
            "description":        "Late Blight is one of the most destructive tomato diseases worldwide. It spreads rapidly in cool, wet conditions and can destroy an entire crop within days.",
            "symptoms":           "Water-soaked, dark brown lesions on leaves and stems. White fuzzy growth on undersides of leaves. Dark brown patches on fruit.",
            "cause":              "Oomycete pathogen Phytophthora infestans. Spreads via air and water. Favoured by temperatures 10–24°C and relative humidity >90%.",
            "chemical_treatment": "Mancozeb 75% WP @ 2g/litre every 7–10 days. Metalaxyl + Mancozeb (Ridomil) @ 2.5g/litre for systemic control.",
            "organic_treatment":  "Copper oxychloride @ 3g/litre as preventive spray. Bacillus subtilis-based biocontrol agents.",
            "preventive_measures":"Plant resistant varieties (Pusa Ruby, Arka Vikas). Avoid overhead irrigation. Ensure proper plant spacing for airflow.",
        },
        {
            "disease_name":       "Rice Blast",
            "scientific_name":    "Magnaporthe oryzae",
            "is_healthy":         False,
            "severity":           "moderate",
            "description":        "Rice Blast is the most devastating rice disease globally, causing leaf blast, collar rot, and neck rot. Can reduce yields by 50–80% in severe outbreaks.",
            "symptoms":           "Diamond-shaped lesions with grey centers and brown borders on leaves. Neck rot causing panicle to fall. White empty grains.",
            "cause":              "Fungal pathogen Magnaporthe oryzae. Favoured by high humidity, temperature 24–28°C, and excessive nitrogen.",
            "chemical_treatment": "Tricyclazole 75% WP @ 0.6g/litre at tillering and booting stages. Isoprothiolane 40% EC @ 1.5 ml/litre.",
            "organic_treatment":  "Silicon-enriched fertilisers improve plant resistance. Pseudomonas fluorescens seed treatment @ 10g/kg seed.",
            "preventive_measures":"Use blast-resistant varieties (IR64, Samba Mahsuri). Balanced N–P–K fertilisation. Drain fields periodically.",
        },
        {
            "disease_name":       "Potato Early Blight",
            "scientific_name":    "Alternaria solani",
            "is_healthy":         False,
            "severity":           "moderate",
            "description":        "Early Blight of potato causes characteristic target-board lesions and significant defoliation, reducing tuber yield and quality.",
            "symptoms":           "Dark brown, concentrically ringed lesions (target-board pattern) on older leaves. Yellow halo around lesions. Premature defoliation.",
            "cause":              "Fungal pathogen Alternaria solani. Most severe during warm, humid conditions (24–29°C). Spread by wind and rain splash.",
            "chemical_treatment": "Chlorothalonil 75% WP @ 2g/litre. Mancozeb 75% WP @ 2g/litre at 10-day intervals.",
            "organic_treatment":  "Neem oil 2% spray. Copper-based fungicide (Bordeaux mixture 1%). Remove and destroy infected plant debris.",
            "preventive_measures":"Use certified disease-free seed tubers. Maintain adequate spacing. Avoid water-stressed plants.",
        },
        {
            "disease_name":       "Healthy Crop",
            "scientific_name":    "—",
            "is_healthy":         True,
            "severity":           "none",
            "description":        "Your crop appears completely healthy with no visible signs of disease, pest damage, or nutrient deficiency. Continue current management practices.",
            "symptoms":           "No disease symptoms detected.",
            "cause":              "No pathogen or stress factor identified.",
            "chemical_treatment": "No chemical treatment required.",
            "organic_treatment":  "Continue regular neem oil spray (preventive) every 2–3 weeks.",
            "preventive_measures":"Regular field scouting every 3–5 days. Maintain soil health with organic matter. Balanced NPK fertilisation.",
        },
        {
            "disease_name":       "Maize Gray Leaf Spot",
            "scientific_name":    "Cercospora zeae-maydis",
            "is_healthy":         False,
            "severity":           "high",
            "description":        "Gray Leaf Spot is a major foliar disease of maize that can cause severe yield losses. It thrives in warm, humid environments.",
            "symptoms":           "Long, rectangular, tan to grey lesions parallel to leaf veins. Lesions have distinct yellow borders. Severe cases cause premature senescence.",
            "cause":              "Fungal pathogen Cercospora zeae-maydis. Spread by wind-borne conidia. Favoured by extended leaf wetness and temperatures 25–30°C.",
            "chemical_treatment": "Azoxystrobin + Propiconazole @ 1 ml/litre. Trifloxystrobin + Propiconazole @ 0.5 ml/litre.",
            "organic_treatment":  "Bacillus amyloliquefaciens-based bioagents. Spray potassium silicate (1%) to strengthen leaf epidermis.",
            "preventive_measures":"Plant resistant hybrids. Crop rotation with non-host crops. Avoid dense planting.",
        },
    ]

    def predict(self, image_path: str) -> dict:
        start = time.time()

        # Simulate processing delay
        time.sleep(random.uniform(0.3, 0.8))

        # Randomly pick a disease (weighted: 80% disease, 20% healthy)
        weights = [0.16, 0.16, 0.16, 0.16, 0.20, 0.16]
        disease = random.choices(self.DISEASE_DB, weights=weights, k=1)[0]

        # Generate realistic confidence score
        confidence = round(random.uniform(82.0, 97.5), 2)

        # Generate alternative predictions
        others = [d for d in self.DISEASE_DB if d['disease_name'] != disease['disease_name']]
        remaining = round(100 - confidence, 2)
        alt_confs = sorted(
            [round(random.uniform(0.5, remaining * 0.6), 2) for _ in range(3)],
            reverse=True
        )
        alternatives = [
            {"disease": d['disease_name'], "confidence": c}
            for d, c in zip(random.sample(others, 3), alt_confs)
        ]

        processing_time = round(time.time() - start, 3)

        return {
            **disease,
            "confidence_score":          confidence,
            "alternative_predictions":   alternatives,
            "model_version":             "v1.0-placeholder",
            "processing_time":           processing_time,
        }


# ──────────────────────────────────────────────────────────────
# 🧠 TENSORFLOW MODEL ADAPTER (Production)
# Uncomment and configure when TF model is ready
# ──────────────────────────────────────────────────────────────
class TensorFlowModel(BaseCropDiseaseModel):
    """
    TensorFlow/Keras model adapter.
    Requires: tensorflow, Pillow
    Configure AI_MODEL_PATH in .env
    """

    LABELS = [
        'Wheat___Leaf_Rust', 'Wheat___Healthy',
        'Tomato___Late_blight', 'Tomato___Healthy',
        'Rice___Blast', 'Rice___Healthy',
        'Potato___Early_blight', 'Potato___Healthy',
        'Maize___Gray_leaf_spot', 'Maize___Healthy',
        'Cotton___Bacterial_blight', 'Cotton___Healthy',
    ]

    def __init__(self):
        self.model      = None
        self.model_path = settings.AI_MODEL_PATH
        self._load_model()

    def _load_model(self):
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"✅ TF model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load TF model: {e}")
            self.model = None

    def _preprocess(self, image_path: str):
        import numpy as np
        from PIL import Image
        img = Image.open(image_path).convert('RGB')
        img = img.resize(settings.AI_IMAGE_SIZE)
        arr = np.array(img) / 255.0
        return np.expand_dims(arr, axis=0)

    def predict(self, image_path: str) -> dict:
        if not self.model:
            logger.warning("TF model not loaded, falling back to placeholder")
            return PlaceholderModel().predict(image_path)

        start  = time.time()
        tensor = self._preprocess(image_path)

        import numpy as np
        predictions = self.model.predict(tensor)[0]
        top_idx     = int(np.argmax(predictions))
        top_label   = self.LABELS[top_idx] if top_idx < len(self.LABELS) else 'Unknown'
        confidence  = round(float(predictions[top_idx]) * 100, 2)

        # Parse label
        parts       = top_label.split('___')
        crop        = parts[0] if len(parts) > 0 else 'Unknown'
        condition   = parts[1] if len(parts) > 1 else 'Unknown'
        is_healthy  = 'Healthy' in condition
        disease_name = f"{crop} – {condition.replace('_', ' ')}" if not is_healthy else f"Healthy {crop}"

        # Top-3 alternatives
        top3_idx = np.argsort(predictions)[-4:-1][::-1]
        alternatives = [
            {"disease": self.LABELS[i] if i < len(self.LABELS) else 'Unknown',
             "confidence": round(float(predictions[i]) * 100, 2)}
            for i in top3_idx
        ]

        return {
            "disease_name":          disease_name,
            "scientific_name":       "",
            "is_healthy":            is_healthy,
            "severity":              "none" if is_healthy else "moderate",
            "confidence_score":      confidence,
            "description":           f"AI detected {disease_name} with {confidence:.1f}% confidence.",
            "symptoms":              "See disease library for detailed symptoms.",
            "cause":                 "See disease library for causal agent details.",
            "chemical_treatment":    "Consult local agricultural extension officer.",
            "organic_treatment":     "Neem oil spray as general preventive measure.",
            "preventive_measures":   "Regular monitoring, resistant varieties, crop rotation.",
            "alternative_predictions": alternatives,
            "model_version":         "v2.0-tensorflow",
            "processing_time":       round(time.time() - start, 3),
        }


# ──────────────────────────────────────────────────────────────
# 🏭 MODEL FACTORY
# Selects the right model based on settings.AI_MODEL_TYPE
# ──────────────────────────────────────────────────────────────
class ModelFactory:
    _instance = None

    @classmethod
    def get_model(cls) -> BaseCropDiseaseModel:
        """Singleton: returns a single model instance per process."""
        if cls._instance is None:
            model_type = getattr(settings, 'AI_MODEL_TYPE', 'placeholder')
            logger.info(f"Initialising AI model: type={model_type}")

            if model_type == 'tensorflow':
                cls._instance = TensorFlowModel()
            else:
                cls._instance = PlaceholderModel()
                logger.info("Using placeholder AI model (development mode)")

        return cls._instance


# ──────────────────────────────────────────────────────────────
# 🔍 MAIN ANALYSIS FUNCTION
# Called by the view — single entry point for AI inference
# ──────────────────────────────────────────────────────────────
def run_analysis(image_path: str) -> dict:
    """
    Main entry point for AI inference.
    Returns standardised prediction dict.
    """
    try:
        model  = ModelFactory.get_model()
        result = model.predict(image_path)
        logger.info(
            f"Analysis complete: {result['disease_name']} "
            f"({result['confidence_score']:.1f}%) in {result['processing_time']:.3f}s"
        )
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return {
            "disease_name":          "Analysis Failed",
            "scientific_name":       "",
            "is_healthy":            False,
            "severity":              "none",
            "confidence_score":      0.0,
            "description":           "The AI model encountered an error. Please try again with a clearer image.",
            "symptoms":              "",
            "cause":                 "Technical error during analysis.",
            "chemical_treatment":    "",
            "organic_treatment":     "",
            "preventive_measures":   "",
            "alternative_predictions": [],
            "model_version":         "error",
            "processing_time":       0.0,
        }
