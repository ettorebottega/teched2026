# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full context before starting
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using the `sap-agent-bootstrap` skill instructions (invoke from inside `assets/product-master-data-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies and validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

Based on the PRD, the agent's queries are single-step lookups (retrieve product details, classification, or hierarchy). No complex multi-step workflow or conditional branching is required. **No runtime skills are needed** — product lookup instructions are concise enough to live in the system prompt.

---

## Project-Specific Tasks

## System Prompt

- [x] Open `assets/product-master-data-agent/app/agent.py` and write the system prompt for the agent:
  - The agent is a Product Master Data assistant for Sales Representatives
  - It answers natural language questions about products by querying SAP S/4HANA product master data
  - It must ONLY return information retrieved via MCP tools — never fabricate, guess, or invent product data
  - It must only answer questions about product master data (name, description, base category, unit of measure, classification, hierarchy); politely decline any request outside this scope
  - It must communicate clearly when no matching product is found, and suggest the user refine their query
  - It must NEVER attempt to create, update, or delete any product data
  - When calling tools that support pagination, always set the page size parameter (`top`, `limit`, etc.) to a maximum of 100
  - If a tool returns an error, relay the exact error message without embellishment or workarounds

## Product Master Data Tool (REQ-01, REQ-02)

- [x] Implement agent tool `get_product_details`:
  - Purpose: Retrieve basic product information (name/description, base unit of measure, product group/category) from SAP S/4HANA for a given product ID or search term
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx`
  - Returns: product ID, product name/description, base unit of measure, product group
  - If no product is found, return a clear "no results" response
- [x] Write unit test `tests/test_get_product_details.py` and run it immediately

## Product Classification Tool (REQ-03)

- [x] Implement agent tool `get_product_classification`:
  - Purpose: Retrieve classification details (class type, class name, characteristic values) for a given product ID from SAP S/4HANA
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/API_CLFN_PRODUCT_SRV.edmx`
  - Returns: classification class, characteristic names and values
  - If no classification data exists for the product, inform the user clearly
- [x] Write unit test `tests/test_get_product_classification.py` and run it immediately

## Product Hierarchy Tool (REQ-04)

- [x] Implement agent tool `get_product_hierarchy`:
  - Purpose: Retrieve the product hierarchy assignment (hierarchy node, hierarchy node name, level) for a given product ID from SAP S/4HANA
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/PRODHIERPRODS_0001.edmx`
  - Returns: hierarchy node ID, hierarchy node name, hierarchy level
  - If no hierarchy assignment exists for the product, inform the user clearly
- [x] Write unit test `tests/test_get_product_hierarchy.py` and run it immediately

## Pricing Procedure Tool (REQ-05b)

- [x] Update the system prompt to include:
  - The agent can also answer questions about pricing procedures, condition records, and condition types for a product
  - It must ONLY return pricing data retrieved via MCP tools — never fabricate pricing information
  - Pricing data is read-only; the agent must NEVER attempt to create, update, or delete any pricing records
- [x] Implement agent tool `get_pricing_procedures`:
  - Purpose: Retrieve applicable sales pricing procedures (procedure name, description) for a given product or sales context
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/API_SLSPRICINGPROCEDURE_SRV.edmx`
  - Returns: pricing procedure ID and description
  - If no pricing procedure is found, return a clear "no results" response
- [x] Implement agent tool `get_pricing_condition_records`:
  - Purpose: Retrieve condition records (prices, discounts) linked to a given product from SAP S/4HANA
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/API_SLSPRICINGCONDITIONRECORD_SRV.edmx`
  - Returns: condition type, condition rate/amount, currency, validity dates
  - If no condition records are found, inform the user clearly
- [x] Implement agent tool `get_pricing_condition_types`:
  - Purpose: Retrieve condition type descriptions and attributes for a given condition type key
  - Calls MCP tools generated from `specification/product-master-data-agent/api-specs/API_SLSPRICINGCONDITIONTYPE_SRV.edmx`
  - Returns: condition type key, name, calculation type, condition category
  - If no condition type data is found, inform the user clearly
- [x] Write unit test `tests/test_get_pricing_procedures.py` and run it immediately
- [x] Write unit test `tests/test_get_pricing_condition_records.py` and run it immediately
- [x] Write unit test `tests/test_get_pricing_condition_types.py` and run it immediately

## Read-Only Safety Guardrail (REQ-06)

- [x] In the system prompt, explicitly instruct the agent:
  - "You are a read-only assistant. You MUST NEVER create, update, or delete product data. If asked to do so, politely decline and explain that you can only retrieve product information."
- [x] Add a guardrail check in the agent: if a user query contains intent to modify product data, respond with a clear refusal before calling any tool
- [x] Write unit test `tests/test_read_only_guardrail.py` that verifies the agent refuses modification requests

## Integration Test

- [x] Write `tests/test_agent_integration.py`: end-to-end test that:
  - Sends a natural language product query (e.g. "What is the unit of measure for product P-100?")
  - Verifies the agent calls the correct tool (`get_product_details`)
  - Verifies the response contains product information (mocked)
  - Sends a classification query and verifies `get_product_classification` is called
  - Sends a hierarchy query and verifies `get_product_hierarchy` is called
  - Sends a pricing procedure query and verifies `get_pricing_procedures` is called
  - Sends a condition record query and verifies `get_pricing_condition_records` is called
  - Sends a condition type query and verifies `get_pricing_condition_types` is called
  - Sends a write-intent query and verifies the agent refuses without calling any tool
  - Mocks all LLM calls and MCP tool calls — test must run fully offline

---

## API Integration (MCP)

- [x] Verify `specification/product-master-data-agent/api-specs/` contains all six EDMX files:
  - `API_PRODUCT_SRV.edmx` — Product Master (A2X)
  - `API_CLFN_PRODUCT_SRV.edmx` — Product Master Data Including Classification
  - `PRODHIERPRODS_0001.edmx` — Products to Product Hierarchies Assignment
  - `API_SLSPRICINGPROCEDURE_SRV.edmx` — Pricing Procedure in Sales
  - `API_SLSPRICINGCONDITIONRECORD_SRV.edmx` — Condition Record for Pricing in Sales
  - `API_SLSPRICINGCONDITIONTYPE_SRV.edmx` — Condition Type for Pricing in Sales
- [x] Invoke `mcp-translation-file` skill for each API spec file to generate MCP translation files:
  - `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_PRODUCT_SRV:v1`
  - `specification/product-master-data-agent/api-specs/API_CLFN_PRODUCT_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1`
  - `specification/product-master-data-agent/api-specs/PRODHIERPRODS_0001.edmx` → ORD ID: `sap.s4:apiResource:PRODHIERPRODS_0001:v1`
  - `specification/product-master-data-agent/api-specs/API_SLSPRICINGPROCEDURE_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_SLSPRICINGPROCEDURE_SRV:v1`
  - `specification/product-master-data-agent/api-specs/API_SLSPRICINGCONDITIONRECORD_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_SLSPRICINGCONDITIONRECORD_SRV:v1`
  - `specification/product-master-data-agent/api-specs/API_SLSPRICINGCONDITIONTYPE_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_SLSPRICINGCONDITIONTYPE_SRV:v1`
- [x] Invoke `setup-solution` skill to create MCP server assets for each translation file
- [x] Extract the exact `ordId` from each generated MCP server `asset.yaml` (use `grep '^ordId:' assets/<mcp-server-asset-name>/asset.yaml`) — NEVER invent ORD IDs
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — NEVER import directly from `sap_cloud_sdk.agentgateway`
- [x] Add all three MCP server dependencies to `asset.yaml` under `requires` (one entry per MCP server with exact ORD IDs from generated assets)
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill (required before tests can run)

**MCP Tool Scope — API_PRODUCT_SRV:**
```
MCP API: sap.s4:apiResource:API_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_Product, A_ProductDescription, A_ProductBasicText
```

**MCP Tool Scope — API_CLFN_PRODUCT_SRV:**
```
MCP API: sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_ClfnProduct, A_ClfnProductCharc
```

**MCP Tool Scope — PRODHIERPRODS_0001:**
```
MCP API: sap.s4:apiResource:PRODHIERPRODS_0001:v1
MCP tool scope: read-only
Resources in scope: ProductToProductHierarchy
```

**MCP Tool Scope — API_SLSPRICINGPROCEDURE_SRV:**
```
MCP API: sap.s4:apiResource:API_SLSPRICINGPROCEDURE_SRV:v1
MCP tool scope: read-only
Resources in scope: A_SalesPricingProcedure, A_SalesPricingProcedureStep
```

**MCP Tool Scope — API_SLSPRICINGCONDITIONRECORD_SRV:**
```
MCP API: sap.s4:apiResource:API_SLSPRICINGCONDITIONRECORD_SRV:v1
MCP tool scope: read-only
Resources in scope: A_SlsPrcgCndnRecdValidity, A_SlsPrcgConditionRecord
```

**MCP Tool Scope — API_SLSPRICINGCONDITIONTYPE_SRV:**
```
MCP API: sap.s4:apiResource:API_SLSPRICINGCONDITIONTYPE_SRV:v1
MCP tool scope: read-only
Resources in scope: A_SlsPricingConditionType
```

---

## Business Instrumentation

- [x] Implement structured logging and OpenTelemetry spans for all 5 milestones from the PRD:

  **M1 — Data Access Established:**
  - Log on achievement: `M1.achieved: S/4HANA Product Master API connection established and data retrieval confirmed`
  - Log on miss: `M1.missed: S/4HANA Product Master API connection could not be established`
  - OTel span: `m1_data_access_established`

  **M2 — Natural Language Query Working:**
  - Log on achievement: `M2.achieved: Natural language query interpreted and product data retrieved successfully`
  - Log on miss: `M2.missed: Natural language query could not be interpreted or no matching product data returned`
  - OTel span: `m2_natural_language_query`

  **M3 — Joule Integration Complete:**
  - Log on achievement: `M3.achieved: Agent successfully invoked from SAP Joule via A2A protocol`
  - Log on miss: `M3.missed: Agent invocation from SAP Joule failed or A2A protocol integration incomplete`
  - OTel span: `m3_joule_integration`

  **M4 — Accuracy Validation:**
  - Log on achievement: `M4.achieved: Accuracy validation completed and quality threshold confirmed by Sales team`
  - Log on miss: `M4.missed: Accuracy validation not completed or quality threshold not met`
  - OTel span: `m4_accuracy_validation`

  **M5 — Regional Rollout:**
  - Log on achievement: `M5.achieved: Agent rolled out to target Sales Representative population across all target regions`
  - Log on miss: `M5.missed: Rollout to target regions not completed within planned window`
  - OTel span: `m5_regional_rollout`

- [x] Extract all business logic from `stream()` into a plain async helper (e.g. `_run_agent()`) and instrument that helper — NEVER use `with tracer.start_as_current_span(...)` inside an async generator
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`
- [x] Verify instrumentation: `grep -r "M[0-9]\.achieved" assets/product-master-data-agent/app/` must return results

---

## Testing

- [x] Ensure `conftest.py` sets only `IBD_TESTING=true`
- [x] Run all unit tests (one per tool): `test_get_product_details.py`, `test_get_product_classification.py`, `test_get_product_hierarchy.py`, `test_read_only_guardrail.py`, `test_get_pricing_procedures.py`, `test_get_pricing_condition_records.py`, `test_get_pricing_condition_types.py`
- [x] Run the integration test: `test_agent_integration.py`
- [x] Run full test suite from `assets/product-master-data-agent/`: `pytest` (no args, no extra flags)
- [x] If coverage < 70%, add targeted tests until threshold is met
- [x] Run `pytest` again (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists: `ls assets/product-master-data-agent/test_report.json`
