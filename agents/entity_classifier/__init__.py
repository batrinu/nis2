"""
Entity Classifier Agent for NIS2 compliance assessment.
"""
from .classifier import EntityClassifier, UnknownSectorError

__all__ = ["EntityClassifier", "UnknownSectorError"]
