"""CPU-only claimant-standing institutional research harness."""

from .experiment import run_experiment
from .model import ExperimentConfig

__all__ = ["run_experiment", "ExperimentConfig"]
