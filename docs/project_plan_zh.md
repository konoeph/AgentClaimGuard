# AgentClaimGuard 开源项目策划书

## 一、项目名称

**AgentClaimGuard**

副标题：**一个与框架无关的 LLM 结论证据门控工具**

英文定位：

> AgentClaimGuard is a framework-agnostic evidence gate for LLM agent claims.

中文定位：

> AgentClaimGuard 是一个面向 LLM 应用的通用可靠性插件层，用于检查模型输出中的关键结论是否被证据、工具结果和用户定义策略支持。

核心口号：

> **No evidence, no claim.**  
> **No tool result, no numeric conclusion.**  
> **No source, no compliance judgment.**

中文表达：

> **没有证据，不给结论。**  
> **没有工具结果，不下数值结论。**  
> **没有来源依据，不做合规判断。**

---

## 二、项目背景

随着 LLM、RAG、Agent、工具调用和工作流编排技术的发展，越来越多开发者开始构建垂直领域的专业型 AI 应用，例如法律合同分析、金融报告核查、医学指南问答、工程技术判断、企业知识库问答、代码审查 Agent、数据分析 Agent 等。

但在实际应用中，一个普遍问题逐渐暴露出来：

> LLM 可以把答案组织得很完整、逻辑看起来很顺，但关键结论未必可靠。

典型问题包括：

1. **模型凭记忆下结论**  
   在没有证据、规范、数据或工具结果的情况下，模型直接给出确定性判断。

2. **RAG 检索与最终答案脱节**  
   系统虽然检索到了上下文，但模型最终答案不一定真正基于这些上下文。

3. **工具结果没有被强制使用**  
   Agent 可能调用了计算器、数据库、检索器或 API，但最终结论并没有严格引用这些工具结果。

4. **结构化输出不等于可靠输出**  
   很多系统可以稳定输出 JSON，但 JSON 内部的专业判断可能仍然是错误的。

5. **缺少统一的失败回退机制**  
   当证据不足、工具失败、上下文冲突时，很多系统仍然强行输出 pass、fail、yes、no 等确定性结论。

当前已有很多优秀项目分别解决了 RAG、Agent 编排、结构化输出、评测、Guardrails、安全过滤等问题，但在“LLM 关键结论是否有资格成立”这个问题上，仍缺少一个足够轻量、通用、可插拔的工程层。

AgentClaimGuard 的目标就是补上这一层。

---

## 三、项目愿景

AgentClaimGuard 不做新的 Agent 框架，不做新的 RAG 平台，也不做行业专用审查系统。

它只专注于一件事：

> **验证 LLM 输出中的关键结论是否被证据、工具结果和用户定义策略支持。**

更具体地说，AgentClaimGuard 希望成为所有 LLM 应用都可以接入的“结论可信度约束层”。

它可以作为：

- LangChain / LangGraph 的 middleware 或 node；
- Dify / RAGFlow / FastGPT 等平台的外部工具插件；
- DSPy / Instructor / Pydantic 输出链路后的 verifier；
- 自研 Agent 系统中的 runtime guard；
- CI/Eval 阶段的自动检查器；
- 企业知识库问答系统的答案可信度门控层。

最终愿景：

> 让开发者不再只关心“LLM 能不能回答”，还要关心“LLM 的关键结论是否有资格输出”。

---

## 四、项目定位

### 4.1 AgentClaimGuard 是什么

AgentClaimGuard 是一个通用的 LLM 结论验证与证据门控工具。

它接收：

- LLM 输出的 claims；
- 支撑这些 claims 的 evidence；
- 相关 tool results；
- 用户自定义 policy；

然后判断：

- 这个 claim 是否有证据支持；
- 是否缺少必要工具结果；
- 是否违反策略；
- 是否应该允许输出；
- 是否需要降级为 need_check / insufficient_evidence / conflicting_evidence；
- 是否需要让 Agent 重新检索、重新调用工具或请求人工确认。

### 4.2 AgentClaimGuard 不是什么

AgentClaimGuard 不是：

- 不是 Agent 框架；
- 不是 RAG 系统；
- 不是向量数据库；
- 不是结构化输出库；
- 不是通用安全审查框架；
- 不是行业知识库；
- 不是工程报告审查系统。

AgentClaimGuard 只做一层：

> **Claim Verification Layer：LLM 关键结论验证层。**

---

## 五、核心理念：CETV

AgentClaimGuard 的核心流程可以概括为：

```text
Claim → Evidence → Tool → Verify
```

### 5.1 Claim

Claim 指模型输出中的关键结论、判断、断言或建议。

例如：

- “该合同存在违约责任约定不明确的问题。”
- “A 部门和 B 部门的销售额数据不一致。”
- “该药物剂量符合指南推荐。”
- “这段代码存在空指针异常风险。”
- “该报告中的投资金额前后不一致。”

AgentClaimGuard 不关心具体行业，只关心这些结论是否可验证。

### 5.2 Evidence

Evidence 是支持 claim 的材料，可以来自：

- RAG 检索片段；
- PDF / Word / HTML 原文；
- 数据库记录；
- API 返回值；
- 表格单元格；
- 用户输入；
- 规范、政策、合同条款；
- 代码文件；
- 网页搜索结果；
- 其他系统输出。

### 5.3 Tool Result

Tool Result 是工具执行结果。

例如：

- 计算器结果；
- 单位换算结果；
- SQL 查询结果；
- 表格比对结果；
- 测试运行结果；
- 静态代码扫描结果；
- 标准条文检索结果；
- API 查询结果。

AgentClaimGuard 的核心原则是：

> 凡是应由工具验证的结论，不允许模型仅凭语言推理直接下判断。

### 5.4 Verify

Verify 是根据用户自定义 policy，对 claim、evidence、tool result 之间的关系进行验证。

验证后可能返回：

- `passed`：允许输出；
- `blocked`：阻断输出；
- `need_check`：证据不足，需要进一步核查；
- `insufficient_evidence`：缺少必要证据；
- `conflicting_evidence`：证据互相矛盾；
- `tool_required`：需要调用工具；
- `tool_error`：工具结果不可用；
- `repair_required`：需要重新生成或修正答案。

---

## 六、目标用户

### 6.1 LLM 应用开发者

他们已经在使用 LLM 构建问答、分析、审查、搜索、客服、数据分析、代码助手等应用，希望提升答案可靠性。

### 6.2 Agent 框架使用者

他们使用 LangChain、LangGraph、Dify、RAGFlow、CrewAI、AutoGen、DSPy 等框架，希望为现有流程增加证据门控能力。

### 6.3 RAG 系统开发者

他们已经完成文档解析、向量检索、rerank 和上下文拼接，但担心模型最终答案没有真正被检索结果支撑。

### 6.4 企业内部知识库团队

他们希望 AI 回答内部制度、合同、流程、报告、技术文档时，能明确引用来源，避免无依据输出。

### 6.5 垂直领域应用团队

法律、金融、医疗、工程、科研、代码审查等场景，都需要更严格的证据链和不确定性处理。

---

## 七、核心功能设计

### 7.1 Claim Schema

Claim 是 AgentClaimGuard 的最小验证单位。

示例结构：

```json
{
  "id": "claim_1",
  "text": "The revenue increased by 15% compared with last year.",
  "type": "numeric_conclusion",
  "verdict": "pass",
  "evidence_refs": ["ev_1", "ev_2"],
  "tool_result_refs": ["tool_1"],
  "confidence": 0.82
}
```

核心字段：

- `id`：claim 唯一标识；
- `text`：claim 文本；
- `type`：claim 类型；
- `verdict`：模型给出的判断；
- `evidence_refs`：引用的证据；
- `tool_result_refs`：引用的工具结果；
- `confidence`：可选置信度。

### 7.2 Evidence Schema

示例结构：

```json
{
  "id": "ev_1",
  "type": "source_fact",
  "source": "annual_report.pdf",
  "locator": "page 12, table 3",
  "content": "Revenue in 2025 was 115 million yuan.",
  "metadata": {
    "page": 12,
    "section": "Financial Summary"
  }
}
```

核心字段：

- `id`：证据唯一标识；
- `type`：证据类型；
- `source`：来源；
- `locator`：位置；
- `content`：证据内容；
- `metadata`：额外信息。

常见 evidence type：

```text
source_fact
regulation
guideline
contract_clause
database_record
retrieved_context
user_input
code_snippet
table_cell
web_source
api_response
```

### 7.3 Tool Result Schema

示例结构：

```json
{
  "id": "tool_1",
  "tool_name": "calculator",
  "status": "success",
  "input": {
    "current": 115,
    "previous": 100
  },
  "output": {
    "growth_rate": "15%"
  },
  "evidence_refs": ["ev_1", "ev_2"]
}
```

核心字段：

- `id`：工具结果唯一标识；
- `tool_name`：工具名称；
- `status`：执行状态；
- `input`：工具输入；
- `output`：工具输出；
- `evidence_refs`：工具结果依赖的证据。

### 7.4 Policy Schema

Policy 定义不同类型 claim 的验证规则。

示例：

```yaml
name: strict_policy
version: 0.1

claim_types:
  numeric_conclusion:
    required_evidence:
      - type: source_fact
        min_count: 2
    required_tool_results:
      - calculator
    forbidden:
      - numeric_claim_without_tool
    fallback:
      verdict: insufficient_evidence
      reason: Numeric conclusions require source facts and calculation results.

  compliance_judgement:
    required_evidence:
      - type: regulation
        min_count: 1
      - type: source_fact
        min_count: 1
    forbidden:
      - use_model_memory_as_authority
      - unsupported_pass_fail
    fallback:
      verdict: need_check
      reason: Compliance judgments require rule evidence and source facts.

  citation_required_answer:
    required_evidence:
      - type: retrieved_context
        min_count: 1
    forbidden:
      - answer_without_citation
    fallback:
      verdict: insufficient_evidence
```

AgentClaimGuard 不内置行业结论，只内置验证机制。行业逻辑通过 policy 扩展。

---

## 八、核心验证能力

### 8.1 Evidence Required Check

检查 claim 是否绑定了足够证据。

示例：

```text
合规判断必须有 regulation evidence。
数值结论必须有 source_fact evidence。
医学建议必须有 guideline evidence。
RAG 问答必须有 retrieved_context evidence。
```

### 8.2 Tool Result Required Check

检查 claim 是否引用了必要工具结果。

示例：

```text
增长率、差异率、汇总值必须有 calculator 结果。
代码正确性判断必须有 test / linter / static_analyzer 结果。
数据库统计结论必须有 sql_query 结果。
单位换算结论必须有 unit_converter 结果。
```

### 8.3 Citation Binding Check

检查 claim 中的引用是否真的存在于 evidence 列表中。

防止模型输出不存在的引用 ID、虚假来源或不匹配引用。

### 8.4 Unsupported Verdict Check

检查模型是否在证据不足时给出了确定性结论。

例如：

- 没有标准依据却判断“符合”；
- 没有计算结果却判断“增长 15%”；
- 没有上下文证据却判断“该条款违法”；
- 证据冲突却判断“完全一致”。

### 8.5 Conflicting Evidence Check

当多个 evidence 给出冲突信息时，阻止模型直接输出确定性结论。

返回：

```text
conflicting_evidence
```

### 8.6 Fallback / Repair

当验证失败时，AgentClaimGuard 可以返回安全输出。

例如：

```json
{
  "status": "blocked",
  "safe_verdict": "need_check",
  "reason": "The claim requires regulation evidence, but no regulation evidence was provided.",
  "missing_evidence": ["regulation"]
}
```

---

## 九、运行模式

### 9.1 Post-check 模式

最简单、最容易接入。

```text
LLM 生成答案
    ↓
AgentClaimGuard 检查 claims
    ↓
通过 / 阻断 / 降级 / 重试
```

适合：

- RAG 问答；
- Dify 工作流；
- LangChain 链式调用；
- 企业知识库问答；
- 自研 API 服务。

### 9.2 In-loop 模式

适合 Agent。

```text
Agent 提出 claim
    ↓
AgentClaimGuard 判断缺少哪些证据或工具
    ↓
Agent 继续检索 / 调用工具
    ↓
再次验证
    ↓
输出最终答案
```

适合：

- LangGraph；
- AutoGen；
- CrewAI；
- ReAct Agent；
- 自研多步 Agent。

### 9.3 CI/Eval 模式

适合开发阶段评测。

```text
测试集
    ↓
模型输出
    ↓
AgentClaimGuard 批量检查
    ↓
统计 unsupported claims / missing evidence / ignored tool results
```

适合：

- 模型对比；
- RAG 系统评测；
- prompt 回归测试；
- Agent 流程升级前后评测。

---

## 十、插件形态规划

### 10.1 Core Python SDK

最基础的使用方式：

```python
from agentclaimguard import AgentClaimGuard, Policy

guard = AgentClaimGuard(policy=Policy.load("strict.yaml"))

result = guard.verify(
    claims=claims,
    evidence=evidence,
    tool_results=tool_results,
)

print(result.status)
print(result.violations)
print(result.safe_output)
```

### 10.2 OpenAPI Server

提供 HTTP 服务，方便任何框架接入。

核心接口：

```text
POST /v1/verify
POST /v1/check-evidence
POST /v1/check-tools
POST /v1/repair
```

适合：

- Dify；
- RAGFlow；
- FastGPT；
- 自研平台；
- 任意支持 HTTP Tool 的 Agent 框架。

### 10.3 LangChain Adapter

形态：middleware / Runnable wrapper。

目标：在 LangChain 调用链后增加 AgentClaimGuard 验证。

### 10.4 LangGraph Adapter

形态：node / subgraph。

目标：在 Agent 图中增加一个 evidence guard node。

示意：

```text
agent_node → agentclaimguard_node → route_by_status
```

### 10.5 DSPy Adapter

形态：assertion pack / module wrapper。

目标：将 AgentClaimGuard 的证据规则变成 DSPy pipeline 中可复用的断言。

### 10.6 Dify Plugin

第一阶段：Tool Plugin。

Dify 工作流中：

```text
Knowledge Retrieval → LLM → AgentClaimGuard Tool → Conditional Branch
```

第二阶段：Agent Strategy Plugin。

将 CETV 作为一种 Agent 策略。

### 10.7 RAGFlow-Style Evidence Mapping

形态：API adapter / post-verifier。

目标：将 RAGFlow 检索结果转换成 AgentClaimGuard evidence schema，再验证最终答案。

---

## 十一、MVP 范围

v0.1 不追求完整生态，只做最小但有价值的闭环。

### 11.1 v0.1 必做功能

1. Core schema
   - Claim
   - Evidence
   - ToolResult
   - Policy
   - VerificationResult

2. Policy runtime
   - YAML policy 加载；
   - required evidence 检查；
   - required tool result 检查；
   - forbidden verdict 检查；
   - fallback 输出。

3. Core verifier
   - `verify_claims()`；
   - `check_evidence()`；
   - `check_tool_results()`；
   - `repair_or_fallback()`。

4. OpenAPI Server
   - `/v1/verify`；
   - `/v1/repair`。

5. 三个 demo
   - numeric conclusion demo；
   - compliance judgement demo；
   - RAG citation demo。

### 11.2 v0.1 暂不做

- 不做复杂 UI；
- 不做向量数据库；
- 不做文档解析；
- 不做完整 Agent 框架；
- 不做行业知识库；
- 不做复杂自动 claim 抽取；
- 不做 LLM-as-verifier 复杂判断。

v0.1 应该先证明：

> 只要模型输出结构化 claims，AgentClaimGuard 就能稳定判断这些 claims 是否满足证据和工具约束。

---

## 十二、项目架构设计

建议仓库结构：

```text
agentclaimguard/
  README.md
  LICENSE
  pyproject.toml
  docs/
    concepts.md
    policy_spec.md
    schema_spec.md
    adapters.md
    roadmap.md

  agentclaimguard/
    __init__.py

    core/
      claim.py
      evidence.py
      tool_result.py
      policy.py
      verifier.py
      result.py
      runtime.py

    validators/
      evidence_required.py
      tool_required.py
      citation_binding.py
      forbidden_verdict.py
      conflict_check.py

    policies/
      generic_strict.yaml
      generic_rag.yaml
      generic_numeric.yaml
      generic_compliance.yaml

    adapters/
      langchain/
      langgraph/
      dspy/
      dify/
      ragflow/

    server/
      main.py
      schemas.py

    utils/
      ids.py
      json_schema.py
      yaml_loader.py

  examples/
    numeric_conclusion/
      demo.py
      policy.yaml
      sample_input.json

    compliance_judgement/
      demo.py
      policy.yaml
      sample_input.json

    rag_citation/
      demo.py
      policy.yaml
      sample_input.json

  tests/
    test_policy_loader.py
    test_evidence_required.py
    test_tool_required.py
    test_fallback.py
```

---

## 十三、示例场景

### 13.1 数值结论场景

输入 claim：

```json
{
  "id": "claim_1",
  "type": "numeric_conclusion",
  "text": "Revenue increased by 15%.",
  "evidence_refs": ["ev_1", "ev_2"],
  "tool_result_refs": []
}
```

Policy 要求：

```yaml
numeric_conclusion:
  required_evidence:
    - type: source_fact
      min_count: 2
  required_tool_results:
    - calculator
```

验证结果：

```json
{
  "status": "blocked",
  "violations": [
    {
      "claim_id": "claim_1",
      "type": "missing_required_tool_result",
      "required": "calculator"
    }
  ],
  "safe_verdict": "insufficient_evidence"
}
```

### 13.2 合规判断场景

输入 claim：

```json
{
  "id": "claim_2",
  "type": "compliance_judgement",
  "text": "This practice is compliant.",
  "verdict": "pass",
  "evidence_refs": ["ev_1"]
}
```

但是 evidence 只有用户事实，没有 regulation evidence。

验证结果：

```json
{
  "status": "blocked",
  "safe_verdict": "need_check",
  "missing_evidence": ["regulation"],
  "reason": "Compliance judgment requires regulation evidence."
}
```

### 13.3 RAG 问答场景

LLM 输出答案，但没有引用任何 retrieved context。

验证结果：

```json
{
  "status": "blocked",
  "safe_verdict": "insufficient_evidence",
  "violations": ["answer_without_citation"]
}
```

---

## 十四、与现有项目的关系

AgentClaimGuard 不与现有项目正面竞争，而是作为补充层存在。

| 类型 | 已有项目常见能力 | AgentClaimGuard 的补充 |
|---|---|---|
| Agent 框架 | 编排、工具调用、状态管理 | 验证结论是否有证据和工具支撑 |
| RAG 平台 | 文档解析、检索、rerank、引用 | 检查最终答案是否真正被证据支撑 |
| Guardrails | 安全、合规、输出格式、话题控制 | 面向 claim 的证据和工具约束 |
| 结构化输出库 | 保证 JSON / schema 合法 | 检查 JSON 内部结论是否可靠 |
| Eval 框架 | 离线评测、指标统计 | 运行时阻断、降级、回退 |

项目差异化一句话：

> 不是验证输出格式是否正确，而是验证关键结论是否有资格成立。

---

## 十五、技术栈建议

### 15.1 语言

Python。

原因：

- LLM / Agent / RAG 生态主要集中在 Python；
- 易于接入 LangChain、LangGraph、DSPy、FastAPI；
- 适合快速开源迭代。

### 15.2 数据模型

建议使用 Pydantic。

用于定义：

- Claim；
- Evidence；
- ToolResult；
- Policy；
- VerificationResult。

### 15.3 API 服务

建议使用 FastAPI。

原因：

- 自动生成 OpenAPI；
- 方便 Dify / RAGFlow / 自研系统通过 HTTP 调用；
- 易于部署。

### 15.4 配置语言

YAML + JSON Schema。

YAML 用于 policy 编写，JSON Schema 用于校验 policy 格式。

### 15.5 测试

使用 pytest。

第一阶段测试重点：

- policy 加载；
- required evidence；
- required tool result；
- fallback；
- schema validation。

---

## 十六、路线图

### v0.1：Core Runtime

目标：证明 AgentClaimGuard 的核心概念可用。

内容：

- Core schema；
- YAML policy；
- 基础 verifier；
- fallback；
- OpenAPI server；
- 3 个 demo。

### v0.2：Framework Adapters

目标：让主流开发者能接入。

内容：

- LangChain adapter；
- LangGraph node；
- 基础文档；
- 更多示例。

### v0.3：Claim Extraction

目标：降低接入成本。

内容：

- 从普通 LLM 输出中抽取 claims；
- 自动生成 evidence binding 提示；
- 支持结构化输出转换。

### v0.4：Dify / RAGFlow Integration

目标：进入低代码和 RAG 平台生态。

内容：

- Dify Tool Plugin；
- RAGFlow-style evidence mapping example；
- HTTP 工作流示例。

### v0.5：LLM-as-Verifier 可选模块

目标：处理更复杂的语义支撑关系。

内容：

- evidence 是否真正支持 claim；
- claim 与 evidence 是否矛盾；
- 多证据综合判断；
- 可配置模型接口。

### v1.0：稳定版本

目标：形成可用于生产系统的通用可靠性插件。

内容：

- 稳定 API；
- 完整文档；
- 多框架适配；
- 完整测试；
- 可扩展 policy 规范；
- CLI / Server / SDK 三种使用方式。

---

## 十七、开源策略

### 17.1 许可证

建议选择 Apache-2.0 或 MIT。

如果希望企业更容易采用，可以选择 Apache-2.0。

### 17.2 README 重点

README 应该直接讲清楚：

1. LLM 的关键问题不是不会输出，而是会无证据下结论；
2. AgentClaimGuard 不替代任何框架；
3. AgentClaimGuard 是 claim-level evidence gate；
4. 三分钟 demo 展示“没有证据就阻断”；
5. 提供 LangGraph / LangChain / OpenAPI 示例。

### 17.3 文档结构

建议 docs 包含：

- Concepts：核心概念；
- Quickstart：快速开始；
- Policy Spec：策略规范；
- Schema Spec：数据结构；
- Adapters：框架接入；
- Examples：示例；
- Roadmap：路线图。

### 17.4 示例优先级

示例不要只放一个行业，避免用户误解为行业工具。

建议第一批示例：

1. 通用 RAG 问答；
2. 数值结论校验；
3. 合规判断；
4. 代码审查；
5. 合同条款分析。

工程审查可以作为后续 advanced example，而不是主示例。

---

## 十八、项目风险与应对

### 18.1 风险一：被误解为普通 Guardrails

应对：

- 避免使用 Guardrails 作为主名称；
- 强调 claim-level evidence verification；
- 强调工具结果绑定；
- 强调 no evidence, no claim。

### 18.2 风险二：被误解为 RAG Eval 工具

应对：

- 强调 runtime gate，而不是只做离线评测；
- 提供阻断、降级、回退能力；
- 提供 API 和 adapter。

### 18.3 风险三：过早做行业功能导致失去通用性

应对：

- 核心不包含行业规则；
- 行业只放 examples 或 community policy packs；
- policy DSL 保持通用。

### 18.4 风险四：自动 claim 抽取过难

应对：

- v0.1 先要求结构化 claims；
- 后续再做 claim extractor；
- 支持人工或上游 Agent 生成 claims。

### 18.5 风险五：语义支撑关系难以完全规则化

应对：

- 规则验证先解决 60% 高频问题；
- LLM-as-verifier 作为可选模块；
- 不把 AgentClaimGuard 承诺成绝对真理判断器，而是定位成可靠性约束层。

---

## 十九、MVP 开发计划

### 第 1 阶段：项目骨架

目标：初始化 GitHub 仓库。

任务：

- 创建仓库；
- 编写 README 初版；
- 选择许可证；
- 配置 pyproject.toml；
- 搭建核心目录结构；
- 添加基础测试框架。

### 第 2 阶段：核心 Schema

目标：定义最小数据结构。

任务：

- Claim model；
- Evidence model；
- ToolResult model；
- Policy model；
- VerificationResult model。

### 第 3 阶段：Policy Runtime

目标：让 YAML policy 可以执行。

任务：

- YAML 加载；
- policy 校验；
- claim type 匹配；
- required evidence 检查；
- required tool 检查；
- fallback 生成。

### 第 4 阶段：Verifier

目标：完成核心验证器。

任务：

- evidence required validator；
- tool required validator；
- citation binding validator；
- forbidden verdict validator；
- result aggregation。

### 第 5 阶段：Demo

目标：完成 3 个最小示例。

任务：

- numeric conclusion demo；
- compliance judgement demo；
- RAG citation demo。

### 第 6 阶段：OpenAPI Server

目标：让外部系统可以接入。

任务：

- FastAPI 服务；
- `/v1/verify`；
- `/v1/repair`；
- OpenAPI 文档；
- curl 示例。

### 第 7 阶段：首版发布

目标：发布 v0.1。

任务：

- 完善 README；
- 添加安装说明；
- 添加快速开始；
- 添加 roadmap；
- 打 tag；
- 发布 GitHub Release。

---

## 二十、README 初始文案建议

```markdown
# AgentClaimGuard

AgentClaimGuard is a framework-agnostic evidence gate for LLM agent claims.

It verifies whether important claims in LLM outputs are supported by evidence, tool results, and user-defined policies.

No evidence, no claim.  
No tool result, no numeric conclusion.  
No source, no compliance judgment.

## Why AgentClaimGuard?

LLM applications can produce fluent, structured, and confident answers — even when the key claims are unsupported.

RAG gives context, but does not guarantee the answer is grounded.  
Tool calling gives results, but does not guarantee the model uses them.  
Structured output gives JSON, but does not guarantee the judgment is valid.

AgentClaimGuard adds a lightweight runtime layer to verify claims before they are returned to users.

## Core Flow

Claim → Evidence → Tool → Verify

## What AgentClaimGuard is not

AgentClaimGuard is not an agent framework, RAG engine, vector database, or general-purpose safety guardrail.

It is a claim-level reliability layer for LLM applications.
```

---

## 二十一、项目成败关键

AgentClaimGuard 要成功，关键不是一开始功能多，而是概念要清楚、MVP 要锋利。

最重要的是打透这三个场景：

1. **没有证据时，阻止模型给确定性结论。**
2. **没有工具结果时，阻止模型给数值/计算结论。**
3. **RAG 有上下文时，要求答案中的关键 claim 绑定 evidence。**

只要这三个场景跑通，项目就有清晰价值。

---

## 二十二、最终总结

AgentClaimGuard 的核心价值不是替代现有框架，而是给现有 LLM 应用补上一层通用可靠性机制。

它不关心开发者使用什么模型、什么 RAG、什么 Agent 框架、什么行业知识库。

它只关心一个问题：

> **模型输出的关键结论，是否有证据、工具结果和策略约束支撑？**

最终目标：

> 让每一个关键 LLM claim 都可追溯、可验证、可降级、可阻断。

这就是 AgentClaimGuard 的开源价值。
