import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mlaos_serving")

def log_feature_serving(feature_id: str, features: Dict[Any, Any]) -> None:
    """Logs features at serving time per Rule #29."""
    logger.info(f"SERVING_LOG | Feature ID: {feature_id} | Payload: {features}")
