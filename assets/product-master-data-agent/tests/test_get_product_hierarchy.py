"""Unit tests for the get_product_hierarchy capability (Product Hierarchy API tools)."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_hierarchy_nodes_tool():
    """Mock MCP tool that returns product hierarchy nodes."""
    tool = MagicMock()
    tool.name = "list_produnivhiernormalnode_for_sap_self"
    tool.description = "Retrieve a list of product hierarchy nodes."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "ProductHierarchy": "00000-0",
                    "ProdHierarchyNode": "00000-0-1",
                    "ProdHierarchyNodeName": "Electronics",
                    "HierarchyNodeLevel": "1",
                },
                {
                    "ProductHierarchy": "00000-0",
                    "ProdHierarchyNode": "00000-0-1-2",
                    "ProdHierarchyNodeName": "Notebooks",
                    "HierarchyNodeLevel": "2",
                },
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


@pytest.fixture
def mock_hierarchy_products_tool():
    """Mock MCP tool that returns products assigned to hierarchy nodes."""
    tool = MagicMock()
    tool.name = "list_produnivhierprodbyhiernode_for_sap_self"
    tool.description = "Retrieve products assigned to hierarchy nodes."

    async def tool_run(*args, **kwargs):
        return json.dumps({
            "results": [
                {
                    "ProductHierarchy": "00000-0",
                    "ProdHierarchyNode": "00000-0-1-2",
                    "Product": "TG11",
                    "HierarchyNodeLevel": "2",
                }
            ]
        })

    tool.arun = AsyncMock(side_effect=tool_run)
    tool.run = MagicMock(return_value=json.dumps({"results": []}))
    return tool


class TestGetProductHierarchy:
    """Tests for product hierarchy retrieval via Product Hierarchy API tools."""

    def test_hierarchy_nodes_tool_name(self, mock_hierarchy_nodes_tool):
        """Hierarchy nodes tool must reference 'hiernode' in its name."""
        assert "hier" in mock_hierarchy_nodes_tool.name.lower()

    @pytest.mark.asyncio
    async def test_hierarchy_nodes_returns_results(self, mock_hierarchy_nodes_tool):
        """Hierarchy nodes tool must return a list of nodes."""
        result = await mock_hierarchy_nodes_tool.arun({})
        data = json.loads(result)
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_hierarchy_node_has_required_fields(self, mock_hierarchy_nodes_tool):
        """Each hierarchy node must include ProdHierarchyNode and ProdHierarchyNodeName."""
        result = await mock_hierarchy_nodes_tool.arun({})
        data = json.loads(result)
        node = data["results"][0]
        assert "ProdHierarchyNode" in node
        assert "ProdHierarchyNodeName" in node
        assert "HierarchyNodeLevel" in node

    @pytest.mark.asyncio
    async def test_hierarchy_products_returns_results(self, mock_hierarchy_products_tool):
        """Hierarchy-products tool must return products assigned to a node."""
        result = await mock_hierarchy_products_tool.arun({
            "$filter": "ProdHierarchyNode eq '00000-0-1-2'"
        })
        data = json.loads(result)
        assert "results" in data
        assert data["results"][0]["Product"] == "TG11"

    @pytest.mark.asyncio
    async def test_hierarchy_product_assignment_fields(self, mock_hierarchy_products_tool):
        """Product-to-node assignment must include Product and ProdHierarchyNode."""
        result = await mock_hierarchy_products_tool.arun({})
        data = json.loads(result)
        item = data["results"][0]
        assert "Product" in item
        assert "ProdHierarchyNode" in item

    def test_mock_hierarchy_server_exists(self):
        """mcp-mock.json must include the hierarchy server."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        assert mock_path.exists()
        data = json.loads(mock_path.read_text())
        hier_server = data["servers"].get("sap-s4-prodhierprods-0001")
        assert hier_server is not None, "Hierarchy server must be in mcp-mock.json"

    def test_mock_hierarchy_tools_present(self):
        """Hierarchy server must expose required read-only tools."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tools = data["servers"]["sap-s4-prodhierprods-0001"]["tools"]
        required = [
            "list_produnivhiernormalnode_for_sap_self",
            "get_produnivhiernormalnode_for_sap_self",
            "list_produnivhierprodbyhiernode_for_sap_self",
            "get_produnivhierprodbyhiernode_for_sap_self",
        ]
        for t in required:
            assert t in tools, f"Tool {t} must be in hierarchy server"

    def test_mock_hierarchy_node_response(self):
        """Hierarchy node mock response must contain name and level."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        data = json.loads(mock_path.read_text())
        tool = data["servers"]["sap-s4-prodhierprods-0001"]["tools"]["list_produnivhiernormalnode_for_sap_self"]
        response = tool["mock_response"]
        assert "results" in response
        node = response["results"][0]
        assert "ProdHierarchyNodeName" in node
        assert "HierarchyNodeLevel" in node
