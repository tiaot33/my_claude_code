# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个个人 Claude Code 插件仓库，用于管理和存储自定义的 Claude Code 提示词、命令、代理和技能。

## 仓库结构

```
my_claude_code/
├── .claude-plugin/          # 插件配置目录
│   └── marketplace.json.example  # 插件市场配置示例
└── note/                    # 提示词内容目录
    ├── agents/              # 自定义代理（Agents）
    ├── commands/            # 自定义命令（Commands）
    └── skills/              # 自定义技能（Skills）
```

## 插件配置

插件通过 `.claude-plugin/marketplace.json.example` 配置。配置结构包含：

- **name**: 插件名称
- **owner**: 所有者信息（姓名和邮箱）
- **metadata**: 插件元数据（描述、版本）
- **plugins**: 插件列表数组
  - **commands**: 自定义命令文件路径（Markdown）
  - **agents**: 自定义代理文件路径（Markdown）
  - **skills**: 自定义技能目录路径

## 内容组织原则

### Agents（代理）
- 位置：`note/agents/`
- 格式：Markdown 文件
- 用途：定义专门的 AI 代理，用于处理特定类型的复杂任务

### Commands（命令）
- 位置：`note/commands/`
- 格式：Markdown 文件
- 用途：定义斜杠命令（如 `/doc-generate`），用于快速执行常见任务

### Skills（技能）
- 位置：`note/skills/`
- 格式：目录结构，每个技能一个子目录
- 用途：定义可重用的技能模块，提供专门的能力和领域知识

## 插件引用示例

参考配置中的插件示例：

1. **document-skills**: 文档处理套件（Excel, Word, PowerPoint, PDF）
2. **example-skills**: 示例技能集合（技能创建、MCP构建、视觉设计等）

## 注意事项

- 所有提示词文件应使用 Markdown 格式
- 保持文件命名清晰且具有描述性
- 遵循 Claude Code 插件的标准结构
- 插件源路径（source）相对于配置文件位置
