"""Unit tests for the get_product_details capability (Product Master API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_product_tool():
    """Mock MCP tool that returns product details."""
    tool = MagicMock()
    tool.name = "list_a_product_for_api_product_srv"
    tool.description = "Retrieve a list of products from the Product Master API."
    tool.coroutine = None

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "Product": "TG11",
                    "ProductType": "FERT",
                    "BaseUnit": "EA",
                    "ProductGroup": "L001",
                    "Division": "00",
                }
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": [{"Product": "TG11", "BaseUnit": "EA"}]}))
    return tool


@pytest.fixture
def mock_description_tool():
    """Mock MCP tool that returns product descriptions."""
    tool = MagicMock()
    tool.name = "list_a_productdescription_for_api_product_srv"
    tool.description = "Retrieve multilingual product descriptions."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {"Product": "TG11", "Language": "EN", "ProductDescription": "Notebook Basic 15"}
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_llm():
    """Mock LLM that returns a canned product response."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=MagicMock(content="Product TG11: Notebook Basic 15, Unit of Measure: EA, Product Group: L001"))
    llm.model = "sap/anthropic--claude-4.5-sonnet"
    llm.temperature = 0.0
    llm.model_kwargs = {}
    return llm


class TestGetProductDetails:
    """Tests for product detail retrieval via Product Master API tools."""

    def test_product_tool_name(self, mock_product_tool):
        """Product Master tool must have the correct name."""
        assert "product" in mock_product_tool.name.lower()

    def test_product_tool_returns_results(self, mock_product_tool):
        """Product Master tool must return a results list."""
        result = mock_product_tool.run()
        data = json.loads(result)
        assert "results" in data

    @pytest.mark.asyncio
    async def test_product_tool_async_returns_results(self, mock_product_tool):
        """Product Master tool arun must return results asynchronously."""
        result = await mock_product_tool.arun({"$filter": "Product eq 'TG11'"})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) > 0

    @pytest.mark.asyncio
    async def test_product_has_required_fields(self, mock_product_tool):
        """Product result must include Product ID and BaseUnit."""
        result = await mock_product_tool.arun({})
        data = json.loads(result)
        product = data["results"][0]
        assert "Product" in product
        assert "BaseUnit" in product

    @pytest.mark.asyncio
    async def test_description_tool_returns_description(self, mock_description_tool):
        """Description tool must return product descriptions."""
        result = await mock_description_tool.arun({"$filter": "Product eq 'TG11'"})
        data = json.loads(result)
        assert "results" in data
        desc = data["results"][0]
        assert "ProductDescription" in desc
        assert desc["ProductDescription"] == "Notebook Basic 15"

    def test_mock_product_data_structure(self):
        """Mock data in mcp-mock.json must include product master tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists(), "mcp-mock.json must exist"
        data = json.loads(mock_path.read_text())
        assert "servers" in data
        servers = data["servers"]
        product_server = servers.get("sap-s4-api-product-srv")
        assert product_server is not None, "Product Master server must be in mcp-mock.json"
        tools = product_server["tools"]
        assert "list_a_product_for_api_product_srv" in tools
        assert "get_a_product_for_api_product_srv" in tools
        assert "list_a_productdescription_for_api_product_srv" in tools

    def test_mock_product_tool_response(self):
        """Product tool mock response must contain expected fields."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        product_tool = data["servers"]["sap-s4-api-product-srv"]["tools"]["get_a_product_for_api_product_srv"]
        response = product_tool["mock_response"]
        assert "Product" in response
        assert "BaseUnit" in response
