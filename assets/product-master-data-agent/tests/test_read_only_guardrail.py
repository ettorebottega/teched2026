"""Unit tests for the read-only safety guardrail in the agent."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add app to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestReadOnlyGuardrail:
    """Tests verifying the agent refuses any write/modification request."""

    @pytest.fixture
    def agent(self, add_agent_to_path):
        """Create a SampleAgent instance with mocked dependencies."""
        with patch("mcp_providers.agw.get_user_sub", return_value="test-user"), \
             patch("agent.create_checkpointer", return_value=None):
            from agent import SampleAgent
            ag = SampleAgent()
            return ag

    @pytest.mark.asyncio
    async def test_refuses_create_product(self, agent):
        """Agent must refuse requests to create a product."""
        results = []
        async for chunk in agent.stream(
            "Create a new product called SuperWidget with unit EA",
            context_id="test-1",
            tools=[],
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(word in content for word in ["read-only", "cannot", "only retrieve", "can only"])

    @pytest.mark.asyncio
    async def test_refuses_update_product(self, agent):
        """Agent must refuse requests to update a product."""
        results = []
        async for chunk in agent.stream(
            "Update product TG11 description to something new",
            context_id="test-2",
            tools=[],
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(word in content for word in ["read-only", "cannot", "only retrieve", "can only"])

    @pytest.mark.asyncio
    async def test_refuses_delete_product(self, agent):
        """Agent must refuse requests to delete a product."""
        results = []
        async for chunk in agent.stream(
            "Delete product P-100 from the system",
            context_id="test-3",
            tools=[],
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(word in content for word in ["read-only", "cannot", "only retrieve", "can only"])

    @pytest.mark.asyncio
    async def test_refuses_modify_classification(self, agent):
        """Agent must refuse requests to modify product classification."""
        results = []
        async for chunk in agent.stream(
            "Change the classification of product TG11",
            context_id="test-4",
            tools=[],
        ):
            results.append(chunk)

        final = results[-1]
        assert final["is_task_complete"] is True
        content = final["content"].lower()
        assert any(word in content for word in ["read-only", "cannot", "only retrieve", "can only"])

    @pytest.mark.asyncio
    async def test_no_tool_called_on_write_intent(self, agent):
        """Agent must NOT call any tool when it detects write intent."""
        mock_tool = MagicMock()
        mock_tool.name = "some_tool"
        mock_tool.arun = AsyncMock()

        results = []
        async for chunk in agent.stream(
            "Update the product material hierarchy",
            context_id="test-5",
            tools=[mock_tool],
        ):
            results.append(chunk)

        # Tool must never be called for a write intent
        mock_tool.arun.assert_not_called()

    @pytest.mark.asyncio
    async def test_allows_read_query(self, agent):
        """Agent must NOT block a legitimate read query."""
        with patch("agent.SampleAgent._run_agent", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Product TG11: Notebook Basic 15, BaseUnit: EA"

            results = []
            async for chunk in agent.stream(
                "What is the unit of measure for product TG11?",
                context_id="test-6",
                tools=[],
            ):
                results.append(chunk)

            final = results[-1]
            assert final["is_task_complete"] is True
            # _run_agent should have been called (read query passes guardrail)
            mock_run.assert_called_once()
