# CS-30 学生画像双方案与 KG-RAG 完整架构

**项目：** Personalised AI Learning Assistant using Retrieval-Augmented Generation and Large Language Models  
**版本日期：** 2026-08-23  
**状态：** 当前建议架构，尚未冻结  

## 1. 架构目标

本架构支持两种学生画像初始化方式：

1. 经授权的成绩单或 Academic Profile；
2. 学生自主选择水平，可选用轻量诊断测验校准。

两种方式只在“学生画像初始化”阶段不同。它们最终都转换成统一的 Topic-Level Proficiency，之后共用同一套检索、Restricted KG-RAG、Level-Aware Reranking、生成、拒答和反馈更新流程。

## 2. 统一学生画像格式

```yaml
student_profile:
  student_id: anonymous_or_internal_id
  topics:
    programming:
      level: advanced
      confidence: 0.86
      source: transcript
      last_updated: 2026-08-23
    statistics:
      level: beginner
      confidence: 0.70
      source: self_report
      last_updated: 2026-08-23
```

字段说明：

- `level`：`beginner`、`intermediate` 或 `advanced`；
- `confidence`：当前水平判断的置信度，范围为 0–1；
- `source`：`transcript`、`self_report`、`diagnostic` 或 `interaction`；
- `last_updated`：最近一次画像更新日期。

当某个 Topic 没有足够信息时，应设置为 `unknown`，再由学生选择或诊断测验补充，不应随意推断。

---

## 3. 方案 A：成绩单生成学生画像

### 3.1 适用条件

该方案只在以下条件全部满足时启用：

- 客户确认确实需要成绩单；
- 学生明确授权；
- 隐私和伦理要求已经确认；
- 明确成绩单的访问者、存储期限和删除方式；
- 原始成绩单不会未经许可发送给第三方 LLM 或 Embedding API。

如果任一条件不满足，应切换到方案 B。

### 3.2 完整流程

```text
成绩单 / Academic Profile
        ↓
授权、隐私与伦理检查
        ↓
最小化字段提取
课程名称、成绩、完成时间
        ↓
课程 → Topic 映射
        ↓
成绩标准化与加权
        ↓
Topic Proficiency Score
        ↓
Beginner / Intermediate / Advanced
        ↓
Initial Topic-Level Proficiency
        ↓
学生问题
        ↓
识别问题 Topic 与复杂度
        ↓
BM25 + Dense / Hybrid Retrieval
        ↓
复杂问题才执行 Restricted KG Expansion
        ↓
Level-Aware Weighted Reranking
        ↓
Top-K Personalised Evidence
        ↓
证据质量检查与 Abstention
        ↓
Personalised Prompt
        ↓
LLM Grounded Answer + Sources
        ↓
可选 Mini Quiz / Feedback
        ↓
更新对应 Topic Proficiency
```

### 3.3 课程到 Topic 的映射

```text
COMP1001 → Programming: 0.8
         → Algorithms:  0.2

DATA1001 → Statistics:   0.6
         → Data Science: 0.4
```

建议采用透明的规则或加权估计器，不在缺乏训练数据和人工标签时训练黑箱分类器。

概念计算方式：

```text
Topic Score =
Σ（标准化课程成绩 × 课程与 Topic 的关联权重）
÷
Σ（课程与 Topic 的关联权重）
```

阈值示例仅用于初始原型，最终阈值应经过团队和客户确认：

```text
0–49   → Beginner
50–79  → Intermediate
80–100 → Advanced
```

### 3.4 方案 A 的主要风险

- 成绩单可能无法反映学生对某个具体概念的当前掌握程度；
- 不同课程和评分制度之间可能不可直接比较；
- 课程到 Topic 的关联权重带有人工判断；
- 真实成绩属于敏感个人信息；
- 画像结果必须允许学生查看、纠正或拒绝使用。

---

## 4. 方案 B：学生自主选择水平

### 4.1 定位

该方案是默认推荐入口。它不依赖真实成绩单，实施成本低，隐私风险较小，也更容易用于可复现的研究实验。

### 4.2 完整流程

```text
学生首次使用
        ↓
选择整体水平或各 Topic 水平
        ↓
选择学习目标
        ↓
可选：5–10 题 Diagnostic Quiz
        ↓
Initial Topic-Level Proficiency
        ↓
学生问题
        ↓
识别问题 Topic 与复杂度
        ↓
BM25 + Dense / Hybrid Retrieval
        ↓
复杂问题才执行 Restricted KG Expansion
        ↓
Level-Aware Weighted Reranking
        ↓
Top-K Personalised Evidence
        ↓
证据质量检查与 Abstention
        ↓
Personalised Prompt
        ↓
LLM Grounded Answer + Sources
        ↓
可选 Mini Quiz / Feedback
        ↓
更新对应 Topic Proficiency
```

### 4.3 学生选择方式

最低成本版本允许学生选择一个全局水平：

```text
Beginner / Intermediate / Advanced
```

推荐版本允许学生按 Topic 选择：

```text
Programming       Advanced
Mathematics       Intermediate
Statistics        Beginner
Machine Learning  Intermediate
Deep Learning     Beginner
```

还可以记录学习目标：

- 快速理解概念；
- 准备考试；
- 学习实际应用；
- 理解数学推导。

### 4.4 可选诊断测验

如果学生不参加诊断测验：

```text
level = 学生选择
confidence = 较低，例如 0.60
source = self_report
```

如果学生参加诊断测验：

```text
level = 自选水平与诊断结果共同决定
confidence = 较高，例如 0.80
source = self_report + diagnostic
```

系统不应强制覆盖学生选择。若诊断结果不同，可以显示建议并允许学生确认：

> 你选择了 Advanced，但诊断结果更接近 Intermediate。是否采用系统建议？

### 4.5 方案 B 的主要风险

- 学生可能高估或低估自己的水平；
- 单一全局 Level 不能表达不同 Topic 之间的差异；
- 诊断测验过短可能产生不稳定判断；
- 诊断题不能来自正式 Test Set，也不能造成评估泄漏。

---

## 5. 两个方案共用的检索与 KG-RAG

### 5.1 知识库准备

```text
课程资料
    ↓
解析、清洗与去重
保留 source / page / char_start / char_end
    ↓
结构化 Chunking
    ↓
Evidence Role 标注
definition / example / derivation / boundary / application
    ↓
┌────────────────────────────┐
│ BM25 Index                 │
│ Dense Vector Index         │
│ Restricted Knowledge Graph │
└────────────────────────────┘
```

### 5.2 问题路由

普通定义或单一概念问题：

```text
Question
→ BM25 + Dense / Hybrid
→ Level-Aware Reranking
```

Cross-topic 或 Multi-hop 问题：

```text
Question
→ Hybrid Initial Retrieval
→ 识别核心概念
→ Restricted KG Neighbour Expansion
→ 获取关联课程证据
→ Level-Aware Reranking
```

KG-RAG 不替代 BM25 或 Dense Retrieval，也不直接充当答案来源。图中的关系必须链接回课程资料中的原始证据。

### 5.3 Level-Aware Weighted Reranking

不同水平优先不同类型的 evidence：

```text
Beginner
→ definition、example、intuitive explanation

Intermediate
→ explanation、comparison、application

Advanced
→ derivation、boundary、technical detail
```

概念评分方式：

```text
final_score =
retrieval_score
+ level_role_weight
+ optional_KG_relation_weight
```

主方法应采用软加权，而不是直接删除不符合画像的证据，以降低误删正确 evidence 的风险。

### 5.4 Abstention 与生成

```text
Retrieved Evidence
        ↓
证据分数或覆盖度是否足够？
        ├── 否 → Insufficient evidence in course materials
        └── 是
              ↓
Student Profile + Question + Evidence + Answer Rules
              ↓
Personalised Prompt
              ↓
LLM
              ↓
Grounded Answer + Verifiable Sources
```

---

## 6. 两个方案的比较

| 维度 | 方案 A：成绩单 | 方案 B：学生自选 |
|---|---|---|
| 初始画像来源 | 历史课程成绩 | 学生自我判断 |
| 默认地位 | 获批后的增强功能 | 默认主方案 |
| 隐私风险 | 高 | 低 |
| 伦理审批 | 可能需要 | 通常不需要 |
| 实现成本 | 中高 | 低 |
| 冷启动体验 | 可自动生成 | 需要学生选择 |
| 主要误差 | 成绩与具体概念掌握不一致 | 自我判断偏差 |
| 校准方法 | Diagnostic Quiz / Interaction | Diagnostic Quiz / Interaction |
| 下游 RAG 架构 | 共用 | 共用 |

---

## 7. 实验建议

正式的个性化实验应使用固定的 Synthetic Profiles：

```text
Synthetic Beginner Profile
Synthetic Intermediate Profile
Synthetic Advanced Profile
```

这样可以控制变量并保证实验可重复。画像来源的比较可以作为独立的小型实验，不应与主要 RAG 实验全部交叉组合。

建议拆分为：

1. **Personalisation Experiment**：固定画像，比较 Retrieval Personalisation 和 Prompt Personalisation；
2. **KG Experiment**：在 cross-topic/multi-hop 子集比较 Hybrid 与 Hybrid + KG；
3. **Profile Initialisation Pilot**：比较 transcript-based、自选和自选 + diagnostic 的画像差异；
4. **Optional Longitudinal Simulation**：使用 synthetic student trajectories 验证 Mini Quiz 更新机制。

---

## 8. 推荐实施顺序

1. 完成课程资料解析、清洗和可追溯 Chunking；
2. 跑通 BM25 与 Dense Baseline；
3. 实现学生自选的 Topic-Level Proficiency；
4. 实现 Level-Aware Weighted Reranking；
5. 完成 Personalised Prompt、引用与 Abstention；
6. 增加 Hybrid Retrieval；
7. 核心系统稳定后增加 Restricted KG-RAG；
8. 时间允许时增加 Diagnostic Quiz 和 Lightweight Profile Update；
9. 只有获得明确授权后才增加真实 Transcript 入口。

## 9. 最终推荐

系统同时保留两个画像入口，但以方案 B 为默认：

```text
Profile Initialisation
├── A. Transcript-Based
│     仅在授权与数据治理允许时启用
│
└── B. Self-Selected
      默认启用，可用 Diagnostic Quiz 校准
             ↓
      Topic-Level Proficiency
             ↓
      Hybrid / Restricted KG Retrieval
             ↓
      Level-Aware Reranking
             ↓
      Personalised Prompt
             ↓
      Grounded Answer + Sources
             ↓
      Optional Profile Update
```

这样即使成绩单方案最终不可行，也只需关闭 Transcript Profile Builder，不需要修改核心 RAG 架构。
