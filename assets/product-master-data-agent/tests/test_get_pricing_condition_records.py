"""Unit tests for get_pricing_condition_records capability (Condition Record API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_condition_record_list_tool():
    """Mock MCP tool that returns a list of condition records."""
    tool = MagicMock()
    tool.name = "list_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv"
    tool.description = "Retrieve a list of sales pricing condition records."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "ConditionRecord": "0000000001",
                    "ConditionType": "PR00",
                    "Material": "TG11",
                    "SalesOrganization": "1010",
                    "DistributionChannel": "10",
                    "ConditionRateValue": "100.00",
                    "ConditionRateValueUnit": "EUR",
                },
                {
                    "ConditionRecord": "0000000002",
                    "ConditionType": "K007",
                    "Material": "TG11",
                    "CustomerPriceGroup": "01",
                    "ConditionRateValue": "-5.00",
                    "ConditionRateValueUnit": "%",
                },
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_condition_record_get_tool():
    """Mock MCP tool that returns a specific condition record."""
    tool = MagicMock()
    tool.name = "get_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv"
    tool.description = "Retrieve a specific pricing condition record."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "ConditionRecord": "0000000001",
            "ConditionType": "PR00",
            "Material": "TG11",
            "ConditionRateValue": "100.00",
            "ConditionRateValueUnit": "EUR",
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({}))
    return tool


@pytest.fixture
def mock_validity_list_tool():
    """Mock MCP tool that returns condition record validity entries."""
    tool = MagicMock()
    tool.name = "list_a_slsprcgcndnrecdvalidity_for_api_slspricingconditionrecord_srv"
    tool.description = "Retrieve a list of condition record validity entries."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "ConditionRecord": "0000000001",
                    "ConditionType": "PR00",
                    "ValidityStartDate": "/Date(1609459200000)/",
                    "ValidityEndDate": "/Date(1767225600000)/",
                    "ConditionRateValue": "100.00",
                    "ConditionRateValueUnit": "EUR",
                    "ConditionQuantity": "1",
                    "ConditionQuantityUnit": "EA",
                }
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


class TestGetPricingConditionRecords:
    """Tests for pricing condition record retrieval via Condition Record API tools."""

    def test_condition_record_tool_name(self, mock_condition_record_list_tool):
        """Condition record tool must reference 'conditionrecord' in its name."""
        assert "conditionrecord" in mock_condition_record_list_tool.name.lower() or \
               "cndnrecd" in mock_condition_record_list_tool.name.lower() or \
               "slsprcg" in mock_condition_record_list_tool.name.lower()

    @pytest.mark.asyncio
    async def test_condition_record_list_returns_results(self, mock_condition_record_list_tool):
        """Condition record list tool must return a list of records."""
        result = await mock_condition_record_list_tool.arun({})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_condition_record_has_required_fields(self, mock_condition_record_list_tool):
        """Each condition record must include ConditionRecord, ConditionType, and rate."""
        result = await mock_condition_record_list_tool.arun({})
        data = json.loads(result)
        record = data["results"][0]
        assert "ConditionRecord" in record
        assert "ConditionType" in record
        assert "ConditionRateValue" in record
        assert "ConditionRateValueUnit" in record

    @pytest.mark.asyncio
    async def test_get_specific_condition_record(self, mock_condition_record_get_tool):
        """Single-record tool must return attributes for the requested record."""
        result = await mock_condition_record_get_tool.arun({"ConditionRecord": "0000000001"})
        data = json.loads(result)
        assert data["ConditionRecord"] == "0000000001"
        assert data["ConditionType"] == "PR00"
        assert data["Material"] == "TG11"

    @pytest.mark.asyncio
    async def test_validity_returns_results(self, mock_validity_list_tool):
        """Validity tool must return validity date and rate for condition records."""
        result = await mock_validity_list_tool.arun({})
        data = json.loads(result)
        assert "results" in data
        validity = data["results"][0]
        assert "ValidityStartDate" in validity
        assert "ValidityEndDate" in validity
        assert "ConditionRateValue" in validity

    def test_mock_condition_record_server_exists(self):
        """mcp-mock.json must include the condition record server."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists()
        data = json.loads(mock_path.read_text())
        server = data["servers"].get("sap-s4-slspricingconditionrecord-srv")
        assert server is not None, "Condition record server must be in mcp-mock.json"

    def test_mock_condition_record_tools_present(self):
        """Condition record server must expose required read-only tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tools = data["servers"]["sap-s4-slspricingconditionrecord-srv"]["tools"]
        required = [
            "list_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv",
            "get_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv",
            "list_a_slsprcgcndnrecdvalidity_for_api_slspricingconditionrecord_srv",
        ]
        for t in required:
            assert t in tools, f"Tool {t} must be in condition record server"

    def test_mock_condition_record_response_has_rate(self):
        """Condition record mock response must contain rate and currency."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tool = data["servers"]["sap-s4-slspricingconditionrecord-srv"]["tools"][
            "list_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv"
        ]
        response = tool["mock_response"]
        assert "results" in response
        record = response["results"][0]
        assert "ConditionRateValue" in record
        assert "ConditionRateValueUnit" in record
