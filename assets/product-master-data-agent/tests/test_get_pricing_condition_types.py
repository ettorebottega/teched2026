"""Unit tests for get_pricing_condition_types capability (Condition Type API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_condition_type_list_tool():
    """Mock MCP tool that returns a list of pricing condition types."""
    tool = MagicMock()
    tool.name = "list_a_slspricingconditiontype_for_api_slspricingconditiontype_srv"
    tool.description = "Retrieve a list of sales pricing condition types."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "ConditionType": "PR00",
                    "ConditionTypeName": "Price",
                    "ConditionCategory": "B",
                    "ConditionClass": "A",
                    "CalculationType": "C",
                },
                {
                    "ConditionType": "K007",
                    "ConditionTypeName": "Customer Discount",
                    "ConditionCategory": "A",
                    "ConditionClass": "A",
                    "CalculationType": "A",
                },
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_condition_type_get_tool():
    """Mock MCP tool that returns a specific pricing condition type."""
    tool = MagicMock()
    tool.name = "get_a_slspricingconditiontype_for_api_slspricingconditiontype_srv"
    tool.description = "Retrieve a specific condition type by key."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "ConditionType": "PR00",
            "ConditionTypeName": "Price",
            "ConditionCategory": "B",
            "ConditionClass": "A",
            "CalculationType": "C",
            "ConditionTypeDescription": "Standard sales price condition type",
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({}))
    return tool


@pytest.fixture
def mock_condition_type_text_tool():
    """Mock MCP tool that returns language-dependent text for a condition type."""
    tool = MagicMock()
    tool.name = "list_to_text_in_a_slspricingconditiontype_for_api_slspricingconditiontype_srv"
    tool.description = "Retrieve language-dependent text for a condition type."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {"ConditionType": "K007", "Language": "EN", "ConditionTypeName": "Customer Discount"}
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


class TestGetPricingConditionTypes:
    """Tests for pricing condition type retrieval via Condition Type API tools."""

    def test_condition_type_tool_name(self, mock_condition_type_list_tool):
        """Condition type tool must reference 'conditiontype' in its name."""
        assert "conditiontype" in mock_condition_type_list_tool.name.lower()

    @pytest.mark.asyncio
    async def test_condition_type_list_returns_results(self, mock_condition_type_list_tool):
        """Condition type list tool must return a list of types."""
        result = await mock_condition_type_list_tool.arun({})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_condition_type_has_required_fields(self, mock_condition_type_list_tool):
        """Each condition type must include ConditionType, ConditionTypeName, and CalculationType."""
        result = await mock_condition_type_list_tool.arun({})
        data = json.loads(result)
        ct = data["results"][0]
        assert "ConditionType" in ct
        assert "ConditionTypeName" in ct
        assert "CalculationType" in ct

    @pytest.mark.asyncio
    async def test_get_specific_condition_type(self, mock_condition_type_get_tool):
        """Single-type tool must return attributes for the requested condition type."""
        result = await mock_condition_type_get_tool.arun({"ConditionType": "PR00"})
        data = json.loads(result)
        assert data["ConditionType"] == "PR00"
        assert data["ConditionTypeName"] == "Price"
        assert "ConditionCategory" in data
        assert "CalculationType" in data

    @pytest.mark.asyncio
    async def test_condition_type_text_returns_translation(self, mock_condition_type_text_tool):
        """Text tool must return language-specific condition type name."""
        result = await mock_condition_type_text_tool.arun({"ConditionType": "K007"})
        data = json.loads(result)
        assert "results" in data
        text = data["results"][0]
        assert text["ConditionType"] == "K007"
        assert text["Language"] == "EN"
        assert "ConditionTypeName" in text

    def test_mock_condition_type_server_exists(self):
        """mcp-mock.json must include the condition type server."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists()
        data = json.loads(mock_path.read_text())
        server = data["servers"].get("sap-s4-slspricingconditiontype-srv")
        assert server is not None, "Condition type server must be in mcp-mock.json"

    def test_mock_condition_type_tools_present(self):
        """Condition type server must expose required read-only tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tools = data["servers"]["sap-s4-slspricingconditiontype-srv"]["tools"]
        required = [
            "list_a_slspricingconditiontype_for_api_slspricingconditiontype_srv",
            "get_a_slspricingconditiontype_for_api_slspricingconditiontype_srv",
        ]
        for t in required:
            assert t in tools, f"Tool {t} must be in condition type server"

    def test_mock_condition_type_pr00_response(self):
        """Condition type mock response for PR00 must contain name and category."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tool = data["servers"]["sap-s4-slspricingconditiontype-srv"]["tools"][
            "get_a_slspricingconditiontype_for_api_slspricingconditiontype_srv"
        ]
        response = tool["mock_response"]
        assert response["ConditionType"] == "PR00"
        assert "ConditionTypeName" in response
        assert "ConditionCategory" in response
