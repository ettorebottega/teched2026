"""Unit tests for get_pricing_procedures capability (Pricing Procedure API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_procedure_list_tool():
    """Mock MCP tool that returns a list of pricing procedures."""
    tool = MagicMock()
    tool.name = "list_a_slspricingprocedure_for_api_slspricingprocedure_srv"
    tool.description = "Retrieve a list of sales pricing procedures."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {"SalesPricingProcedure": "RVAA01", "SalesPricingProcedureName": "Standard Sales Procedure"},
                {"SalesPricingProcedure": "RVAA02", "SalesPricingProcedureName": "Export Sales Procedure"},
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_procedure_get_tool():
    """Mock MCP tool that returns a single pricing procedure."""
    tool = MagicMock()
    tool.name = "get_a_slspricingprocedure_for_api_slspricingprocedure_srv"
    tool.description = "Retrieve a specific sales pricing procedure by key."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "SalesPricingProcedure": "RVAA01",
            "SalesPricingProcedureName": "Standard Sales Procedure",
            "IsIntercompanyPricingProcedure": False
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({}))
    return tool


@pytest.fixture
def mock_procedure_items_tool():
    """Mock MCP tool that returns steps of a pricing procedure."""
    tool = MagicMock()
    tool.name = "list_a_slspricingprocedureitem_for_api_slspricingprocedure_srv"
    tool.description = "Retrieve steps of a sales pricing procedure."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "SalesPricingProcedure": "RVAA01",
                    "PricingProcedureStep": "10",
                    "PricingProcedureCounter": "0",
                    "ConditionType": "PR00",
                    "ConditionTypeName": "Price",
                    "IsConditionMandatory": True,
                },
                {
                    "SalesPricingProcedure": "RVAA01",
                    "PricingProcedureStep": "20",
                    "PricingProcedureCounter": "0",
                    "ConditionType": "K007",
                    "ConditionTypeName": "Customer Discount",
                    "IsConditionMandatory": False,
                },
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


class TestGetPricingProcedures:
    """Tests for pricing procedure retrieval via Pricing Procedure API tools."""

    def test_procedure_list_tool_name(self, mock_procedure_list_tool):
        """Pricing procedure list tool must include 'slspricingprocedure' in name."""
        assert "slspricingprocedure" in mock_procedure_list_tool.name.lower()

    @pytest.mark.asyncio
    async def test_procedure_list_returns_results(self, mock_procedure_list_tool):
        """Pricing procedure list tool must return a list of procedures."""
        result = await mock_procedure_list_tool.arun({})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_procedure_has_required_fields(self, mock_procedure_list_tool):
        """Each pricing procedure must include SalesPricingProcedure and SalesPricingProcedureName."""
        result = await mock_procedure_list_tool.arun({})
        data = json.loads(result)
        proc = data["results"][0]
        assert "SalesPricingProcedure" in proc
        assert "SalesPricingProcedureName" in proc

    @pytest.mark.asyncio
    async def test_get_procedure_by_key(self, mock_procedure_get_tool):
        """Single-procedure tool must return procedure attributes for a specific key."""
        result = await mock_procedure_get_tool.arun({"SalesPricingProcedure": "RVAA01"})
        data = json.loads(result)
        assert data["SalesPricingProcedure"] == "RVAA01"
        assert "SalesPricingProcedureName" in data

    @pytest.mark.asyncio
    async def test_procedure_items_returns_steps(self, mock_procedure_items_tool):
        """Procedure items tool must return steps with condition type info."""
        result = await mock_procedure_items_tool.arun({"SalesPricingProcedure": "RVAA01"})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2
        step = data["results"][0]
        assert "ConditionType" in step
        assert "PricingProcedureStep" in step

    def test_mock_pricing_procedure_server_exists(self):
        """mcp-mock.json must include the pricing procedure server."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists()
        data = json.loads(mock_path.read_text())
        server = data["servers"].get("sap-s4-slspricingprocedure-srv")
        assert server is not None, "Pricing procedure server must be in mcp-mock.json"

    def test_mock_procedure_tools_present(self):
        """Pricing procedure server must expose required read-only tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tools = data["servers"]["sap-s4-slspricingprocedure-srv"]["tools"]
        required = [
            "list_a_slspricingprocedure_for_api_slspricingprocedure_srv",
            "get_a_slspricingprocedure_for_api_slspricingprocedure_srv",
            "list_a_slspricingprocedureitem_for_api_slspricingprocedure_srv",
        ]
        for t in required:
            assert t in tools, f"Tool {t} must be in pricing procedure server"

    def test_mock_procedure_response_has_name(self):
        """Pricing procedure mock response must contain procedure name."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tool = data["servers"]["sap-s4-slspricingprocedure-srv"]["tools"][
            "list_a_slspricingprocedure_for_api_slspricingprocedure_srv"
        ]
        response = tool["mock_response"]
        assert "results" in response
        proc = response["results"][0]
        assert "SalesPricingProcedureName" in proc
