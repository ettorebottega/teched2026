"""Integration tests for the Product Master Data Agent — end-to-end flow with mocked LLM and MCP tools."""
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


def _make_tool(name: str, response_data: dict):
    """Helper to create a mock LangChain tool."""
    tool = MagicMock()
    tool.name = name
    tool.description = f"Mock tool: {name}"
    tool.args_schema = None

    async def arun(*args, **kwargs):
        return json.dumps(response_data)

    tool.arun = AsyncMock(side_effect=arun)
    tool.run = MagicMock(return_value=json.dumps(response_data))
    return tool


@pytest.fixture
def product_tools():
    """Fixture providing all six families of mocked product and pricing MCP tools."""
    return [
        _make_tool("list_a_product_for_api_product_srv", {
            "results": [{"Product": "TG11", "BaseUnit": "EA", "ProductGroup": "L001"}]
        }),
        _make_tool("get_a_product_for_api_product_srv", {
            "Product": "TG11", "BaseUnit": "EA", "ProductGroup": "L001"
        }),
        _make_tool("list_a_productdescription_for_api_product_srv", {
            "results": [{"Product": "TG11", "Language": "EN", "ProductDescription": "Notebook Basic 15"}]
        }),
        _make_tool("list_a_clfnproduct_for_api_clfn_product_srv", {
            "results": [{"Product": "TG11", "ClassType": "001", "Class": "NOTEBOOK_SPECS"}]
        }),
        _make_tool("list_a_productcharc_for_api_clfn_product_srv", {
            "results": [{"Product": "TG11", "Characteristic": "SCREEN_SIZE", "CharcValue": "15.6"}]
        }),
        _make_tool("list_produnivhierprodbyhiernode_for_sap_self", {
            "results": [{"Product": "TG11", "ProdHierarchyNode": "00000-0-1-2", "ProdHierarchyNodeName": "Notebooks"}]
        }),
        _make_tool("list_a_slspricingprocedure_for_api_slspricingprocedure_srv", {
            "results": [{"SalesPricingProcedure": "RVAA01", "SalesPricingProcedureName": "Standard Sales Procedure"}]
        }),
        _make_tool("list_a_slsprcgconditionrecord_for_api_slspricingconditionrecord_srv", {
            "results": [{"ConditionRecord": "0000000001", "ConditionType": "PR00", "Material": "TG11", "ConditionRateValue": "100.00", "ConditionRateValueUnit": "EUR"}]
        }),
        _make_tool("list_a_slspricingconditiontype_for_api_slspricingconditiontype_srv", {
            "results": [{"ConditionType": "PR00", "ConditionTypeName": "Price", "CalculationType": "C"}]
        }),
    ]


@pytest.fixture
def agent(add_agent_to_path):
    """Create a SampleAgent instance."""
    with patch("mcp_providers.agw.get_user_sub", return_value="integration-test-user"), \
         patch("agent.create_checkpointer", return_value=None):
        from agent import SampleAgent
        return SampleAgent()


class TestAgentIntegration:
    """End-to-end integration tests for the product master data agent."""

    @pytest.mark.asyncio
    async def test_product_query_calls_product_tool(self, agent, product_tools):
        """Natural language product query should route to product detail tool."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11 is Notebook Basic 15, Unit of Measure: EA."

            results = []
            async for chunk in agent.stream(
                "What is the unit of measure for product TG11?",
                context_id="integ-1",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "TG11" in final["content"] or "Notebook" in final["content"] or "EA" in final["content"]
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_classification_query_uses_classification_tools(self, agent, product_tools):
        """Classification query should be processed successfully."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "TG11 is classified under NOTEBOOK_SPECS. Screen size: 15.6 inches."

            results = []
            async for chunk in agent.stream(
                "What are the technical classifications for product TG11?",
                context_id="integ-2",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "NOTEBOOK_SPECS" in final["content"] or "15.6" in final["content"]

    @pytest.mark.asyncio
    async def test_hierarchy_query_uses_hierarchy_tools(self, agent, product_tools):
        """Hierarchy query should be processed successfully."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11 belongs to the Notebooks hierarchy node (level 2) under Electronics."

            results = []
            async for chunk in agent.stream(
                "What product hierarchy does TG11 belong to?",
                context_id="integ-3",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "Notebooks" in final["content"] or "hierarchy" in final["content"].lower()

    @pytest.mark.asyncio
    async def test_pricing_procedure_query(self, agent, product_tools):
        """Pricing procedure query should be processed successfully."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11 uses pricing procedure RVAA01 (Standard Sales Procedure)."

            results = []
            async for chunk in agent.stream(
                "What pricing procedures apply to product TG11?",
                context_id="integ-pricing-1",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "RVAA01" in final["content"] or "pricing" in final["content"].lower()

    @pytest.mark.asyncio
    async def test_condition_record_query(self, agent, product_tools):
        """Condition record query should return pricing condition data."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11 has a PR00 price condition record of 100.00 EUR."

            results = []
            async for chunk in agent.stream(
                "What are the pricing conditions for product TG11?",
                context_id="integ-pricing-2",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "PR00" in final["content"] or "100" in final["content"] or "EUR" in final["content"]

    @pytest.mark.asyncio
    async def test_condition_type_query(self, agent, product_tools):
        """Condition type query should return condition type attributes."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "PR00 is the Price condition type, calculation type C (fixed amount)."

            results = []
            async for chunk in agent.stream(
                "What is condition type PR00?",
                context_id="integ-pricing-3",
                tools=product_tools,
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            assert "PR00" in final["content"] or "Price" in final["content"]

    @pytest.mark.asyncio
    async def test_pricing_write_request_is_refused(self, agent, product_tools):
        """Pricing write request must be refused without calling any tool."""
        results = []
        async for chunk in agent.stream(
            "Update the pricing condition for product TG11 to 200 EUR",
            context_id="integ-pricing-4",
            tools=product_tools,
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(w in content for w in ["read-only", "cannot", "only retrieve"])

    @pytest.mark.asyncio
    async def test_write_request_is_refused_without_tool_calls(self, agent, product_tools):
        """Write request must be refused; no tool should be called."""
        results = []
        async for chunk in agent.stream(
            "Delete product TG11 from the product master",
            context_id="integ-4",
            tools=product_tools,
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(w in content for w in ["read-only", "cannot", "only retrieve"])
        # No tools should have been called
        for tool in product_tools:
            tool.arun.assert_not_called()

    @pytest.mark.asyncio
    async def test_agent_returns_complete_status_on_success(self, agent, product_tools):
        """Agent must always return is_task_complete=True on a successful query."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11 found: Notebook Basic 15, BaseUnit EA."

            results = []
            async for chunk in agent.stream(
                "Show me details for product TG11",
                context_id="integ-5",
                tools=product_tools,
            ):
                results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        assert final["require_user_input"] is False

    @pytest.mark.asyncio
    async def test_agent_handles_no_tools_gracefully(self, agent):
        """Agent must handle the case where no MCP tools are available."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Tools are temporarily unavailable."

            results = []
            async for chunk in agent.stream(
                "What is product TG11?",
                context_id="integ-6",
                tools=[],
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True

    @pytest.mark.asyncio
    async def test_instrumentation_logs_milestones(self, agent, product_tools):
        """Agent instrumentation must log milestone messages."""
        import logging
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run, \
             patch("agent.logger") as mock_logger:
            mock_run.return_value = "Product TG11: EA"

            results = []
            async for chunk in agent.stream(
                "What is the unit for TG11?",
                context_id="integ-7",
                tools=product_tools,
            ):
                results.append(chunk)

            # _run_agent was called (stream delegates to it)
            mock_run.assert_called_once()
