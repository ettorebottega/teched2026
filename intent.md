# Product Master Data AI Agent for Sales Representatives

SAP S/4HANA Public Cloud Edition — Natural Language Product Inquiry Agent

## Business challenge

Sales Representatives spend too much time navigating SAP S/4HANA directly to find product master data. The system is complex and not designed for quick lookups during sales interactions. An AI agent embedded in SAP Joule will allow reps to ask questions in plain language and receive instant, accurate answers about product details, descriptions, categories, and units of measure — without needing to know how to operate S/4HANA.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to find product information | 5 minutes | Under 30 seconds | — | Product Master Data Lookup / Lead to Cash | user |

## Key Milestones

1. **Data Access Established** — Agent successfully retrieves product master data from SAP S/4HANA Cloud Public Edition via the Product Master API.
2. **Natural Language Query Working** — Agent correctly interprets and responds to free-text product questions (name, description, category, unit of measure).
3. **Joule Integration Complete** — Agent is accessible and functional within the SAP Joule copilot interface.
4. **Accuracy Validation** — Sales team validates response accuracy; agent meets quality threshold agreed with stakeholders.
5. **Regional Rollout** — Agent deployed and available to 50–200 Sales Representatives across 1–3 regions.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash

### Process Hierarchy

```
Lead to Cash (E2E)
└── Plan to Optimize Marketing and Sales (generic)
    └── Plan sales and manage performance (generic) (BPS-369)
        └── Access and retrieve product master data
        └── Support sales rep decision-making with product information
```

### Summary

Sales Representatives querying product master data in natural language maps to the Lead to Cash E2E process, specifically within the sales planning and performance sub-process, where timely access to accurate product information directly supports sales effectiveness.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|-------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Retrieve basic product details (name, description, category, UOM) | SAP S/4HANA Cloud Public Edition — Product Master (A2X) | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | No | Core API available; no MCP server — custom integration required |
| Retrieve product classification and technical specifications | SAP S/4HANA Cloud Public Edition — Product Master Data Including Classification | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | — | No | Available via OData; no MCP server |
| Retrieve product hierarchy and grouping | SAP S/4HANA Cloud Public Edition — Products to Product Hierarchies Assignment | `sap.s4:apiResource:PRODHIERPRODS_0001:v1` | — | — | — | — | No | Available via OData; no MCP server |
| Natural language interface for Sales Reps | No standard SAP product | — | — | — | — | — | Yes | Custom AI agent (Python/A2A) required |
| Embedded experience in SAP Joule | SAP Joule (A2A agent integration) | — | — | — | — | — | Maybe | Agent must follow A2A protocol for Joule embedding |
| Retrieve pricing procedure information for a product | SAP S/4HANA Cloud Public Edition — Pricing Procedure in Sales - Read | `sap.s4:apiResource:API_SLSPRICINGPROCEDURE_SRV:v1` | — | — | — | — | No | Available via OData; no MCP server — custom integration required |
| Retrieve pricing condition records for a product | SAP S/4HANA Cloud Public Edition — Condition Record for Pricing in Sales | `sap.s4:apiResource:API_SLSPRICINGCONDITIONRECORD_SRV:v1` | — | — | — | — | No | Available via OData; no MCP server |
| Retrieve pricing condition types | SAP S/4HANA Cloud Public Edition — Condition Type for Pricing in Sales – Read | `sap.s4:apiResource:API_SLSPRICINGCONDITIONTYPE_SRV:v1` | — | — | — | — | No | Available via OData; no MCP server |
| Pricing service integration (REST) | Not available in landscape | — | — | — | — | — | Yes | Pricing REST API marked unavailable; excluded from scope |

### Key findings

- SAP S/4HANA Cloud Public Edition exposes the required product master data through OData APIs (Product Master, Classification, Hierarchy), but no pre-built MCP servers exist — the agent must integrate directly via these APIs.
- The Pricing REST API and a generic Product Information REST API are unavailable in this landscape and are excluded from scope.
- A custom Python AI agent using the A2A protocol is required to deliver the natural language interface.
- The agent will be surfaced within SAP Joule, requiring adherence to the A2A protocol for seamless copilot embedding.
- Scope covers read-only product master data queries (name, description, category, unit of measure) plus pricing procedure information (pricing procedures, condition records, condition types) for a team of 50–200 Sales Representatives across 1–3 regions.
- Three pricing OData APIs are available: Pricing Procedure in Sales, Condition Record for Pricing in Sales, and Condition Type for Pricing in Sales. No pre-built MCP servers exist — custom MCP integration required, consistent with the product master data pattern.
- No n8n workflow is required; the solution is a standalone AI agent.

## Recommendations

### Natural Language Product Master Data Agent for SAP Joule

#### Executive Summary

Pro-code Python AI agent surfaced in SAP Joule for instant product lookups.

#### Recommended Solution

Build a pro-code Python AI agent following the A2A protocol that connects to SAP S/4HANA Cloud Public Edition product master data and pricing APIs. The agent will interpret natural language questions from Sales Representatives and translate them into API calls to retrieve accurate product information (name, description, category, unit of measure, classification) as well as pricing procedure information (applicable pricing procedures, condition records, and condition types). The agent is deployed on SAP BTP and embedded within SAP Joule so reps can interact with it without leaving their standard work environment.

#### Problem Statement

Sales Representatives must navigate complex SAP S/4HANA screens to find basic product information, which takes approximately 5 minutes per lookup and disrupts sales workflows. There is no conversational or simplified interface for product data today.

#### Affected User Roles

- Sales Representatives (primary users, 50–200, across 1–3 regions)
- Sales Managers (indirect benefit — reps are more productive and better informed)

#### Important factors

##### Reduces manual effort through natural language interaction
Sales Reps can ask questions like "What is the unit of measure for product X?" instead of navigating S/4HANA transactions, reducing lookup time from 5 minutes to under 30 seconds.

##### No disruption to existing S/4HANA landscape
The agent reads data via standard OData APIs — no changes to S/4HANA configuration or data model are required.

##### Embedded in SAP Joule for seamless adoption
Surfacing the agent inside SAP Joule means Sales Reps use a familiar interface, lowering the learning curve and driving adoption.

#### Potential risks

##### API availability and data quality
The agent's accuracy depends on the quality and completeness of product master data in S/4HANA. Incomplete or inconsistent master data will result in incomplete answers.

##### A2A protocol compliance for Joule embedding
The agent must strictly follow the A2A protocol. Any deviation may prevent proper embedding within SAP Joule.

#### Recommended solution category

AI Agent

#### Intent fit
92%
