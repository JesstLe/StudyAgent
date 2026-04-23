# StudyAgent - 设计文档总览

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## Project Vision

StudyAgent 是一个 AI 驱动的学习助手，专为具有高认知能力的成年学习者设计。它以"发生认识论"为核心教学哲学——**知识不是凭空产生的，而是为了解决特定历史时期的特定"痛点"而发明的。**

系统提供 TUI（终端）和 Web 双界面，后端采用 Python FastAPI + LangGraph 多 Agent 架构，结合知识图谱、间隔重复（FSRS-5）、贝叶斯知识追踪（BKT）和最近发展区（ZPD）估计，实现自适应学习。

## Document Index

| # | Document | Content |
|---|----------|---------|
| 01 | [Agent Architecture Design](01-agent-architecture-design.md) | 系统架构、多Agent设计、记忆系统、知识图谱、MCP集成 |
| 02 | [TUI & Web UI Design](02-tui-webui-design.md) | Textual TUI设计、Next.js 16 Web UI、SSE流式架构、REST API |
| 03 | [Database Schema Design](03-database-schema-design.md) | PostgreSQL完整Schema、Redis键结构、迁移策略 |
| 04 | [Implementation Spec](04-implementation-spec.md) | 技术栈、项目结构、分阶段计划、关键实现细节、测试策略 |
| 05 | [Research Findings](05-research-findings.md) | 2026 Agent框架调研、学习算法、知识追踪、参考文献 |
| 06 | [Tutor Persona Spec](06-tutor-persona-spec.md) | 导师角色原始系统提示词、教学协议、认知工具、质量评估 |
| 07 | [Agent Prompts Design](07-agent-prompts-design.md) | 所有Agent系统提示词、上下文构建、对话流程示例 |
| 08 | [Development Roadmap](08-development-roadmap.md) | 5阶段开发路线图、任务拆解、风险评估、成功指标 |
| 09 | [Learning Algorithms Spec](09-learning-algorithms-spec.md) | FSRS-5完整数学公式、BKT知识追踪、ZPD估计、学习路径优化 |

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────┐
│                     Client Layer                      │
│   ┌─────────────────┐   ┌────────────────────────┐  │
│   │  TUI (Textual)  │   │  Web UI (Next.js 16)   │  │
│   └────────┬────────┘   └───────────┬────────────┘  │
└────────────┼────────────────────────┼────────────────┘
             │  SSE / WebSocket       │
┌────────────▼────────────────────────▼────────────────┐
│              API Gateway (FastAPI + JWT)               │
└────────────┬──────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────┐
│           Agent Orchestrator (LangGraph)               │
│                                                       │
│  ┌──────────┐ ┌─────────┐ ┌──────────────┐           │
│  │  Tutor   │ │  Quiz   │ │  Knowledge   │           │
│  │  Agent   │ │  Agent  │ │  Graph Agent │           │
│  └──────────┘ └─────────┘ └──────────────┘           │
│  ┌──────────┐ ┌─────────┐ ┌──────────────┐           │
│  │Scheduler │ │Analyzer │ │  Document    │           │
│  │(FSRS-5)  │ │ Agent   │ │  Processor   │           │
│  └──────────┘ └─────────┘ └──────────────┘           │
└────────────┬──────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────┐
│               Infrastructure Layer                     │
│  ┌────────────┐ ┌─────────┐ ┌──────────────────────┐ │
│  │ PostgreSQL │ │  Redis  │ │  LLM Providers       │ │
│  │ + pgvector │ │ (cache) │ │  (OpenAI/Claude/     │ │
│  │            │ │         │ │   Ollama)             │ │
│  └────────────┘ └─────────┘ └──────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

## Core Agent Specializations

| Agent | Role | Key Algorithm |
|-------|------|--------------|
| **Tutor Agent** | 核心教学——发生认识论三步曲 | Pain-Point Framework |
| **Quiz Agent** | 生成测验和闪卡 | ZPD自适应难度 |
| **Scheduler Agent** | 间隔重复调度 | FSRS-5 |
| **Knowledge Graph Agent** | 概念图谱构建与学习路径 | 拓扑排序 + 图搜索 |
| **Analyzer Agent** | 学习分析与进度追踪 | BKT/DKT 知识追踪 |
| **Document Processor** | 多模态文档处理 | NLP概念提取 |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+ / FastAPI / LangGraph / LiteLLM |
| Frontend | Next.js 16 / Vercel AI SDK / shadcn/ui |
| TUI | Textual v4+ / Rich |
| Database | PostgreSQL 16 + pgvector / Redis 7 |
| Local Mode | SQLite + sqlite-vec |
| Containerization | Docker + Docker Compose |

## Key Algorithms

- **FSRS-5**: Free Spaced Repetition Scheduler（间隔重复）
- **BKT**: Bayesian Knowledge Tracing（知识状态追踪）
- **ZPD**: Zone of Proximal Development（最近发展区估计）
- **Pain-Point Framework**: 发生认识论三步教学法（核心教学协议）
