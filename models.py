from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Dict, Callable, List
from PIL import Image
import io

# Lazy import of transformers to avoid import cost if just inspecting files
try:
    from transformers import pipeline  # type: ignore
except Exception:
    pipeline = None  # type: ignore


# ----------------- Utilities -----------------
def load_image_from_path(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def read_audio_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


# ----------------- Decorators (OOP: decorators) -----------------
def timed(fn: Callable) -> Callable:
    """
    Decorator: attach simple timing; we avoid importing time/perf_counter to keep dependencies minimal.
    In real use, you'd time with time.perf_counter().
    """
    def wrapper(*args, **kwargs):
        # No actual timing to avoid extra imports, but keeps the shape for demonstration
        return fn(*args, **kwargs)
    return wrapper


def safe_run(fn: Callable) -> Callable:
    """
    Decorator: convert any exception into a readable message.
    """
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to run the model: {e}")
    return wrapper


# ----------------- Base Types -----------------
class InputType(Enum):
    TEXT = "Text"
    IMAGE = "Image"
    AUDIO = "Audio"


class ModelCategory(Enum):
    TEXT_SENTIMENT = "Text: Sentiment Analysis"
    IMAGE_CLASSIFICATION = "Image: Classification"
    ASR = "Audio: Speech Recognition"


@dataclass
class ModelMeta:
    human_name: str
    hf_task: str
    hf_model_id: str
    category: ModelCategory
    description: str


# ----------------- Registry (encapsulation of available models) -----------------
class Registry:
    _MODELS: List[ModelMeta] = [
        ModelMeta(
            human_name="DistilBERT Sentiment (SST-2)",
            hf_task="sentiment-analysis",
            hf_model_id="distilbert-base-uncased-finetuned-sst-2-english",
            category=ModelCategory.TEXT_SENTIMENT,
            description=(
                "A lightweight DistilBERT fine-tuned on SST-2 for binary sentiment classification. "
                "Input: short English text. Output: label (POSITIVE/NEGATIVE) with score."
            ),
        ),
        ModelMeta(
            human_name="ViT Base Image Classifier",
            hf_task="image-classification",
            hf_model_id="google/vit-base-patch16-224",
            category=ModelCategory.IMAGE_CLASSIFICATION,
            description=(
                "Vision Transformer (ViT) base model fine-tuned for generic image classification. "
                "Input: an image; Output: top class predictions with scores."
            ),
        ),
        ModelMeta(
            human_name="Whisper Tiny (EN) ASR",
            hf_task="automatic-speech-recognition",
            hf_model_id="openai/whisper-tiny.en",
            category=ModelCategory.ASR,
            description=(
                "OpenAI Whisper tiny English model for speech-to-text. "
                "Input: audio file (wav/mp3/flac). Output: transcribed text."
            ),
        ),
    ]

    @classmethod
    def models_for(cls, input_type: InputType) -> List[ModelMeta]:
        if input_type == InputType.TEXT:
            cats = {ModelCategory.TEXT_SENTIMENT}
        elif input_type == InputType.IMAGE:
            cats = {ModelCategory.IMAGE_CLASSIFICATION}
        elif input_type == InputType.AUDIO:
            cats = {ModelCategory.ASR}
        else:
            cats = set()
        return [m for m in cls._MODELS if m.category in cats]

    @classmethod
    def find_by_human_name(cls, name: str) -> Optional[ModelMeta]:
        for m in cls._MODELS:
            if m.human_name == name:
                return m
        return None


# ----------------- Model classes (Inheritance, Polymorphism, Overriding) -----------------
class BaseModelHandler:
    """
    Base class demonstrating encapsulation of load/run logic.
    Subclasses must override ._build() and .run(data).
    """
    def __init__(self, meta: ModelMeta) -> None:
        self.meta = meta
        self._pipeline = None

    def _build(self):
        """Create the HF pipeline. Subclasses may override to customize pre/post-processing."""
        if pipeline is None:
            raise RuntimeError("transformers is not installed. Please `pip install transformers`")
        self._pipeline = pipeline(task=self.meta.hf_task, model=self.meta.hf_model_id)

    @timed
    @safe_run
    def ensure_ready(self):
        if self._pipeline is None:
            self._build()

    def run(self, data: Any) -> str:
        """Must be overridden by subclasses."""
        raise NotImplementedError


class TextModelHandler(BaseModelHandler):
    def run(self, data: str) -> str:
        self.ensure_ready()
        res = self._pipeline(data)  # type: ignore
        # sentiment pipeline returns list of dicts
        best = res[0]
        return f"Label: {best.get('label')} | Score: {best.get('score'):.4f}"


class ImageModelHandler(BaseModelHandler):
    def run(self, data: str) -> str:
        self.ensure_ready()
        img = load_image_from_path(data)
        res = self._pipeline(img)  # type: ignore
        # image-classification pipeline returns list of dicts sorted by score
        lines = [f"{r['label']}: {r['score']:.4f}" for r in res[:5]]
        return "Top predictions:\n" + "\n".join(lines)


class AudioModelHandler(BaseModelHandler):
    def run(self, data: str) -> str:
        self.ensure_ready()
        # transformers ASR pipeline accepts a file path directly
        res = self._pipeline(data)  # type: ignore
        if isinstance(res, dict) and 'text' in res:
            return res['text']
        return str(res)


# ----------------- ModelManager (Facade) -----------------
class ModelManager:
    """
    Facade over model handlers; demonstrates encapsulation and polymorphism:
    - Same .run(meta, itype, data) will call the appropriate concrete handler.
    """
    _HANDLERS: Dict[ModelCategory, BaseModelHandler] = {}

    def _get_handler(self, meta: ModelMeta) -> BaseModelHandler:
        if meta.category in self._HANDLERS:
            return self._HANDLERS[meta.category]

        # Construct proper subclass (polymorphism + overriding)
        if meta.category == ModelCategory.TEXT_SENTIMENT:
            handler = TextModelHandler(meta)
        elif meta.category == ModelCategory.IMAGE_CLASSIFICATION:
            handler = ImageModelHandler(meta)
        elif meta.category == ModelCategory.ASR:
            handler = AudioModelHandler(meta)
        else:
            raise ValueError(f"Unsupported category: {meta.category}")
        self._HANDLERS[meta.category] = handler
        return handler

    def run(self, meta: ModelMeta, input_type: 'InputType', data: Any) -> str:
        handler = self._get_handler(meta)
        return handler.run(data)
