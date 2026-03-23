#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "convert_hf_to_gguf.py"


spec = importlib.util.spec_from_file_location("convert_hf_to_gguf", MODULE_PATH)
assert spec is not None and spec.loader is not None
convert_hf_to_gguf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(convert_hf_to_gguf)


class TestDotsOCRTensorMapping(unittest.TestCase):
    def _map_name(self, name: str) -> str:
        dummy = object.__new__(convert_hf_to_gguf.DotsOCRVisionModel)

        with patch.object(convert_hf_to_gguf.Qwen2VLVisionModel, "modify_tensors", autospec=True) as mock_modify:
            mock_modify.side_effect = lambda _self, data_torch, mapped_name, bid: [(mapped_name, data_torch)]
            mapped = list(convert_hf_to_gguf.DotsOCRVisionModel.modify_tensors(dummy, None, name, 0))

        self.assertEqual(len(mapped), 1)
        return mapped[0][0]

    def test_gate_projection_mapping(self):
        mapped = self._map_name("vision_tower.blocks.0.mlp.fc1.weight")
        self.assertEqual(mapped, "visual.blocks.0.mlp.gate_proj.weight")

    def test_up_projection_mapping(self):
        mapped = self._map_name("vision_tower.blocks.0.mlp.fc3.weight")
        self.assertEqual(mapped, "visual.blocks.0.mlp.up_proj.weight")

    def test_down_projection_mapping(self):
        mapped = self._map_name("vision_tower.blocks.0.mlp.fc2.weight")
        self.assertEqual(mapped, "visual.blocks.0.mlp.down_proj.weight")


if __name__ == "__main__":
    unittest.main()
