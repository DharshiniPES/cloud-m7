"""
Base Dataset Adapter and Unified Normalizer Interface for CLOUD-M7.

Provides standard abstractions to convert heterogeneous external forensic
datasets (DARPA OpTC, DARPA TC, TON_IoT, IoT-23) into the Canonical
Provenance Schema (Equation 1: E_i).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import os

from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class BaseDatasetAdapter(ABC):
    """Abstract Base Class for all external dataset adapters."""

    dataset_name: str = "BaseDataset"

    @abstractmethod
    def can_handle(self, sample_line_or_data: Any) -> bool:
        """Determines if this adapter can process the given data format."""
        pass

    @abstractmethod
    def parse_records(
        self,
        data_source: Any,
        max_events: Optional[int] = None,
        default_tier: TierType = TierType.EDGE,
    ) -> List[ProvenanceEvent]:
        """Parses the data source and normalizes records into ProvenanceEvent instances."""
        pass
