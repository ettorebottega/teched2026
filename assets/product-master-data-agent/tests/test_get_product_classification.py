"""Unit tests for the get_product_classification capability (Classification API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_classification_tool():
    """Mock MCP tool that returns product classification data."""
    tool = MagicMock()
    tool.name = "list_a_clfnproduct_for_api_clfn_product_srv"
    tool.description = "Retrieve a list of classified products."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {"Product": "TG11", "ClassType": "001", "Class": "NOTEBOOK_SPECS"}
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_characteristics_tool():
    """Mock MCP tool that returns product characteristics."""
    tool = MagicMock()
    tool.name = "list_a_productcharc_for_api_clfn_product_srv"
    tool.description = "Retrieve product characteristics for classification."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "Product": "TG11",
                    "ClassType": "001",
                    "Class": "NOTEBOOK_SPECS",
                    "Characteristic": "SCREEN_SIZE",
                    "CharcValue": "15.6",
                },
                {
                    "Product": "TG11",
                    "ClassType": "001",
                    "Class": "NOTEBOOK_SPECS",
                    "Characteristic": "RAM_GB",
                    "CharcValue": "8",
                },
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


class TestGetProductClassification:
    """Tests for product classification retrieval via Classification API tools."""

    def test_classification_tool_name(self, mock_classification_tool):
        """Classification tool must have 'clfn' in its name."""
        assert "clfn" in mock_classification_tool.name.lower()

    @pytest.mark.asyncio
    async def test_classification_tool_returns_results(self, mock_classification_tool):
        """Classification tool must return a list of classified products."""
        result = await mock_classification_tool.arun({"Product": "TG11"})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) > 0

    @pytest.mark.asyncio
    async def test_classification_has_required_fields(self, mock_classification_tool):
        """Classification result must include Product, ClassType, and Class."""
        result = await mock_classification_tool.arun({})
        data = json.loads(result)
        item = data["results"][0]
        assert "Product" in item
        assert "ClassType" in item
        assert "Class" in item

    @pytest.mark.asyncio
    async def test_characteristics_tool_returns_results(self, mock_characteristics_tool):
        """Characteristics tool must return a list of characteristics."""
        result = await mock_characteristics_tool.arun({"Product": "TG11"})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_characteristics_has_required_fields(self, mock_characteristics_tool):
        """Each characteristic must have Characteristic name and CharcValue."""
        result = await mock_characteristics_tool.arun({})
        data = json.loads(result)
        for item in data["results"]:
            assert "Characteristic" in item
            assert "CharcValue" in item

    def test_mock_classification_server_exists(self):
        """mcp-mock.json must include the classification server."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists()
        data = json.loads(mock_path.read_text())
        clfn_server = data["servers"].get("sap-s4-api-clfn-product-srv")
        assert clfn_server is not None, "Classification server must be in mcp-mock.json"

    def test_mock_classification_tools_present(self):
        """Classification server must expose all required tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tools = data["servers"]["sap-s4-api-clfn-product-srv"]["tools"]
        required_tools = [
            "list_a_clfnproduct_for_api_clfn_product_srv",
            "list_a_productcharc_for_api_clfn_product_srv",
            "list_a_productclass_for_api_clfn_product_srv",
        ]
        for t in required_tools:
            assert t in tools, f"Tool {t} must be in classification server"

    def test_mock_classification_response_structure(self):
        """Classification tool mock response must contain expected fields."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tool = data["servers"]["sap-s4-api-clfn-product-srv"]["tools"]["list_a_productcharc_for_api_clfn_product_srv"]
        response = tool["mock_response"]
        assert "results" in response
        first = response["results"][0]
        assert "Characteristic" in first
        assert "CharcValue" in first
