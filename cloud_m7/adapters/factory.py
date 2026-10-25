"""
Dataset Normalizer Factory and Auto-Detection Engine.

Automatically identifies the underlying schema of an uploaded or local file
(DARPA OpTC, DARPA TC, TON_IoT, Aposemat IoT-23, or CLOUD-M7 native)
and converts it into Canonical Provenance Schema E_i tuples.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import os

from cloud_m7.adapters.base import BaseDatasetAdapter
from cloud_m7.adapters.optc_adapter import DarpaOpTCAdapter
from cloud_m7.adapters.tc_adapter import DarpaTCAdapter
from cloud_m7.adapters.ton_iot_adapter import TonIotAdapter
from cloud_m7.adapters.iot23_adapter import IoT23Adapter
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import TierType


class DatasetNormalizerFactory:
    """Auto-detects and normalizes multi-format cyber datasets."""

    def __init__(self):
        self.adapters: List[BaseDatasetAdapter] = [
            DarpaOpTCAdapter(),
            DarpaTCAdapter(),
            TonIotAdapter(),
            IoT23Adapter(),
        ]

    def detect_adapter(self, sample_content: str) -> Optional[BaseDatasetAdapter]:
        """Inspects the first few lines or JSON objects to identify the matching adapter."""
        sample_lines = [l for l in sample_content.splitlines() if l.strip() and not l.startswith("#")][:10]
        if not sample_lines:
            return None

        sample_block = "\n".join(sample_lines)

        # Check each adapter
        for adapter in self.adapters:
            # Check whole block or line-by-line
            if adapter.can_handle(sample_block) or any(adapter.can_handle(line) for line in sample_lines):
                return adapter

        return None

    def normalize(
        self,
        content_or_path: str,
        adapter_name: Optional[str] = None,
        max_events: Optional[int] = None,
        tier: Optional[TierType] = None,
    ) -> Tuple[List[ProvenanceEvent], str]:
        """
        Normalizes dataset content or file into ProvenanceEvent list.
        Returns: (events_list, detected_adapter_name)
        """
        # Read content if it's a file path
        if os.path.exists(content_or_path) and os.path.isfile(content_or_path):
            with open(content_or_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        else:
            content = content_or_path

        # Check if it's already CLOUD-M7 native JSON
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list) and len(parsed) > 0 and "tamper_hash" in parsed[0]:
                events = [ProvenanceEvent.from_dict(d) for d in parsed[:max_events]]
                return events, "CLOUD-M7_Native"
        except Exception:
            pass

        # Select adapter
        selected_adapter = None
        if adapter_name:
            for ad in self.adapters:
                if ad.dataset_name.lower() == adapter_name.lower():
                    selected_adapter = ad
                    break

        if selected_adapter is None:
            selected_adapter = self.detect_adapter(content)

        if selected_adapter is None:
            # Default fallback to OpTC/Generic
            selected_adapter = self.adapters[0]

        default_tier = tier or (
            TierType.CLOUD if "optc" in selected_adapter.dataset_name.lower() else
            (TierType.FOG if "tc" in selected_adapter.dataset_name.lower() else TierType.EDGE)
        )

        events = selected_adapter.parse_records(content, max_events=max_events, default_tier=default_tier)
        return events, selected_adapter.dataset_name
