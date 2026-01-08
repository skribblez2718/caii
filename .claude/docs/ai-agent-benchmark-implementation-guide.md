# AI Agent Benchmark Implementation Guide for Penny AI

**Document Version:** 1.0
**Created:** 2026-01-02
**Author:** synthesis
**Status:** Implementation Ready

---

## Executive Summary

This guide synthesizes comprehensive research on 10+ major AI agent benchmarks to provide Penny AI with a strategic evaluation framework. Research spanned 39 queries across academic sources (arXiv, ICLR, NeurIPS), official benchmark repositories, and AI company publications.

**Key Finding:** Anthropic's multi-agent research demonstrates **90.2% improvement** of multi-agent (Opus lead + Sonnet subagents) over single-agent systems, directly validating Penny's 6-agent cognitive architecture.

**Recommendation:** Implement benchmarking in 3 tiers, starting with GAIA and tau-bench (low effort, high signal), progressing to MultiAgentBench (architecture differentiation), then SWE-bench for full capability validation.

---

## 1. BENCHMARK COMPARISON MATRIX

### 1.1 Complete Benchmark Overview

| Benchmark | Domain Focus | Tasks | Primary Metric | SOTA Performance | Human Baseline | Implementation Effort | Penny Applicability |
|-----------|--------------|-------|----------------|------------------|----------------|----------------------|---------------------|
| **GAIA** | General assistant | 466 | Accuracy (3 levels) | h2oGPTe 65% | 92% | MEDIUM | **HIGH** |
| **tau-bench** | Reliability | 2 domains | pass^k | - | - | LOW | **HIGH** |
| **MultiAgentBench** | Coordination | Variable | Milestone achievement | Graph topology best | - | MEDIUM | **HIGH** |
| **AgentBench** | Multi-environment | 8 envs | Task completion | - | - | HIGH | MEDIUM |
| **ToolBench** | API/Tool calling | 16,464 APIs | Call success rate | - | - | MEDIUM | MEDIUM |
| **BFCL** | Function calling | Real-world APIs | Accuracy | - | - | LOW | MEDIUM |
| **SWE-bench** | Software engineering | 2,294 | % Resolved | Claude Opus 4.5: 81.5% | ~78% | HIGH | MEDIUM |
| **SWE-bench Pro** | Complex SW engineering | Subset | % Resolved | 23% (GPT-5.2) | - | HIGH | LOW |
| **WebArena** | Web navigation | 812 | Functional correctness | 61.7% (2025) | - | HIGH | LOW |
| **OSWorld** | Desktop/OS tasks | 369 | Task success rate | Claude Sonnet 4.5: 61.4% | 72.36% | VERY HIGH | LOW |
| **TheAgentCompany** | Enterprise workplace | 175 | % Autonomous | Claude 4.1: 24% | ~100% | HIGH | MEDIUM |
| **MLE-bench** | ML engineering | 75 Kaggle | Medal % | - | - | HIGH | LOW |

### 1.2 Applicability Analysis for Penny

| Applicability | Benchmarks | Rationale |
|---------------|------------|-----------|
| **HIGH** | GAIA, tau-bench, MultiAgentBench | Match Penny's cognitive orchestration, multi-step reasoning, tool use |
| **MEDIUM** | AgentBench, ToolBench, BFCL, SWE-bench, TheAgentCompany | Require adaptation but evaluate core capabilities |
| **LOW** | WebArena, OSWorld, SWE-bench Pro, MLE-bench | Require infrastructure Penny lacks or evaluate narrow domains |

### 1.3 Evaluation Dimension Coverage

| Dimension | Covered By | Penny Architecture Mapping |
|-----------|------------|---------------------------|
| Task Completion | GAIA, AgentBench, SWE-bench | Full workflow completion |
| Tool Usage | ToolBench, BFCL | Tool access via Claude Code |
| Multi-step Reasoning | GAIA, AgentBench | Cognitive agent orchestration |
| Reliability | tau-bench | Memory + state management |
| Multi-agent Coordination | MultiAgentBench | 6-agent architecture (key differentiator) |
| Memory/Context | Context-Bench (emerging) | Johari window, markdown memory |
| Enterprise Realism | TheAgentCompany | Skill-based workflow orchestration |

---

## 2. RECOMMENDED BENCHMARK STRATEGY (3-Tier)

### 2.1 Tier 1: IMMEDIATE (Low Effort, High Value)

**Timeline:** 1-2 weeks
**Goal:** Establish baseline capabilities and production readiness metrics

#### 2.1.1 GAIA Benchmark

**Why First:**
- 466 well-defined questions with simple answer verification
- Tests general assistant capabilities matching Penny's broad scope
- No complex infrastructure requirements
- Clear human baseline (92%) for comparison

**Penny Architecture Fit:**
- Multi-step reasoning maps to research -> analysis -> synthesis flow
- Tool use requirements match Claude Code's capabilities
- 3 difficulty levels allow progressive evaluation

**Implementation Path:**
1. Download GAIA validation set from HuggingFace
2. Create Penny adapter that routes questions through cognitive agents
3. Implement answer extraction from synthesis output
4. Run evaluation against ground truth

**Expected Outcome:** Establish Penny's general capability baseline

#### 2.1.2 tau-bench

**Why Early:**
- Measures **reliability** via pass^k metric (consistency over N runs)
- Critical for production deployment confidence
- Low setup overhead (2 domains: retail, airline)
- Sierra AI created specifically for real-world deployment validation

**Penny Architecture Fit:**
- Tests consistency of multi-agent orchestration
- Validates memory system integrity across invocations
- Measures token efficiency under repeated execution

**Implementation Path:**
1. Clone Sierra's tau-bench repository
2. Configure Penny as the agent interface
3. Run 5-10 iterations per task
4. Calculate pass^k scores at k=1,3,5

**Expected Outcome:** Reliability baseline for production readiness

#### 2.1.3 BFCL (Berkeley Function Calling Leaderboard)

**Why Tier 1:**
- Tests core tool/function calling capability
- Simple API-based evaluation
- Direct mapping to Claude Code's tool access
- Quick turnaround for results

**Implementation Path:**
1. Access BFCL evaluation framework
2. Map Penny's tool interfaces to BFCL format
3. Run function calling accuracy tests
4. Compare against leaderboard

**Expected Outcome:** Tool use capability baseline

### 2.2 Tier 2: STRATEGIC (Medium Effort)

**Timeline:** 2-4 weeks
**Goal:** Demonstrate Penny's multi-agent architecture advantages

#### 2.2.1 MultiAgentBench (MARBLE Framework)

**Why Critical for Penny:**
- Only benchmark specifically evaluating multi-agent coordination
- Tests star/chain/tree/graph coordination topologies
- Directly validates Penny's 6-agent cognitive architecture
- Research shows cognitive planning adds +3% over baselines

**Penny Architecture Fit:**
- 6 cognitive agents (clarification, research, analysis, synthesis, generation, validation) map to coordination protocols
- Graph topology (best performing) matches Penny's orchestration patterns
- Can demonstrate 90.2% multi-agent improvement from Anthropic research

**Implementation Path:**
1. Clone MultiAgentBench/MARBLE repository
2. Map Penny's cognitive agents to benchmark agent roles
3. Implement coordination topology configurations
4. Run milestone-based evaluations

**Expected Outcome:** Quantified multi-agent advantage vs single-agent baselines

#### 2.2.2 AgentBench (Subset: 3-4 Environments)

**Why Strategic:**
- Tests multi-environment, multi-turn evaluation
- ICLR'24 peer-reviewed methodology
- 8 environments but start with subset

**Recommended Subset:**
1. **OS Environment:** File operations (maps to Claude Code)
2. **Web Shopping:** Multi-step task completion
3. **Knowledge Graph:** Reasoning over structured data
4. **Database:** SQL generation and execution

**Implementation Path:**
1. Clone AgentBench repository
2. Configure Docker environments for selected subset
3. Implement Penny-to-AgentBench adapter
4. Run multi-turn evaluations

**Expected Outcome:** Multi-environment capability profile

#### 2.2.3 ToolBench (API Subset)

**Why Include:**
- 16,464 APIs from RapidAPI
- Tests tool composition and chaining
- Relevant metrics: Act.EM, HalluRate, Avg.F1

**Implementation Path:**
1. Select API subset matching Penny's typical use cases
2. Configure API credentials
3. Run tool composition tasks
4. Measure hallucination rate and accuracy

**Expected Outcome:** Tool composition proficiency

### 2.3 Tier 3: EXTENDED (High Effort)

**Timeline:** 4-8 weeks
**Goal:** Full capability validation and enterprise readiness

#### 2.3.1 SWE-bench Verified

**Why Full Effort:**
- Industry standard for software engineering AI
- 500 validated samples from 2,294 total
- Claude Opus 4.5 leads at 81.5% - Penny should compare
- Requires significant infrastructure

**Requirements:**
- x86_64 machine
- 120GB free storage
- 16GB RAM, 8 CPU cores
- Docker installed
- Python 3.10+

**Implementation Path:**
```bash
git clone git@github.com:princeton-nlp/SWE-bench.git
cd SWE-bench
pip install -e .
# Load dataset
from datasets import load_dataset
ds = load_dataset('princeton-nlp/SWE-bench', split='test')
# Run inference with Penny agent
# Evaluate
python -m swebench.harness.run_evaluation
```

**Architecture Extension Needed:**
- Code-specific cognitive agents or generation specialization
- Git integration for patch creation
- Test execution feedback loop

**Expected Outcome:** Software engineering capability comparison with SOTA

#### 2.3.2 TheAgentCompany

**Why Enterprise:**
- 175 enterprise workplace tasks
- Only 24% autonomous completion (Claude 4.1)
- Tests real-world enterprise scenarios
- December 2024 benchmark - cutting edge

**Implementation Path:**
1. Clone TheAgentCompany benchmark
2. Configure simulated enterprise environment
3. Adapt Penny's skill orchestration
4. Run enterprise task evaluation

**Architecture Extension Needed:**
- Enterprise tool integrations
- Longer-horizon workflow support
- Human-in-the-loop fallback handling

**Expected Outcome:** Enterprise deployment readiness assessment

---

## 3. IMPLEMENTATION ROADMAP

### 3.1 Tier 1 Implementation Guide

#### Phase 1A: GAIA Setup (Week 1)

**Prerequisites:**
- HuggingFace account and API access
- Python 3.10+
- Penny operational with Claude Code

**Setup Steps:**
```bash
# Install GAIA evaluation toolkit
pip install datasets evaluate

# Download GAIA validation set
python -c "
from datasets import load_dataset
ds = load_dataset('gaia-benchmark/GAIA', 'validation')
ds.save_to_disk('./gaia_validation')
"
```

**Penny Adapter:**
```python
# gaia_adapter.py
class PennyGAIAAdapter:
    def __init__(self, penny_client):
        self.penny = penny_client

    def answer_question(self, question: str, level: int) -> str:
        """Route GAIA question through Penny's cognitive flow"""
        # Invoke perform-research skill for information gathering
        # Route to analysis for reasoning
        # Extract final answer from synthesis output
        result = self.penny.invoke_skill(
            'perform-research',
            query=question,
            depth='MEDIUM' if level == 1 else 'DEEP'
        )
        return self.extract_answer(result)

    def extract_answer(self, synthesis_output: str) -> str:
        """Extract concise answer from synthesis output"""
        # Parse synthesis output for final answer
        pass
```

**Evaluation:**
```python
# evaluate_gaia.py
def evaluate_penny_on_gaia():
    results = {'level_1': [], 'level_2': [], 'level_3': []}

    for item in gaia_dataset:
        predicted = penny_adapter.answer_question(
            item['question'],
            item['level']
        )
        correct = (predicted.lower().strip() ==
                   item['answer'].lower().strip())
        results[f"level_{item['level']}"].append(correct)

    return {
        level: sum(r)/len(r)
        for level, r in results.items()
    }
```

**Expected Timeline:** 3-5 days

#### Phase 1B: tau-bench Setup (Week 1-2)

**Prerequisites:**
- Sierra tau-bench repository access
- Python 3.10+
- Penny operational

**Setup Steps:**
```bash
# Clone tau-bench
git clone https://github.com/sierra-research/tau-bench.git
cd tau-bench
pip install -r requirements.txt
```

**Penny Integration:**
```python
# tau_bench_adapter.py
class PennyTauBenchRunner:
    def __init__(self, penny_client, k_runs=5):
        self.penny = penny_client
        self.k = k_runs

    def run_task(self, task_id: str, domain: str) -> list[bool]:
        """Run task k times and record success/failure"""
        results = []
        for run in range(self.k):
            try:
                output = self.penny.invoke_skill(
                    'develop-project',  # or appropriate skill
                    task=task_id,
                    domain=domain
                )
                results.append(self.validate_output(output, task_id))
            except Exception as e:
                results.append(False)
        return results

    def calculate_pass_k(self, results: list[bool], k: int) -> float:
        """Calculate pass^k: probability all k runs succeed"""
        # pass^k = (successes/total)^k
        success_rate = sum(results) / len(results)
        return success_rate ** k
```

**Metrics:**
- pass^1: Single-run success rate
- pass^3: 3-consecutive-run success rate
- pass^5: 5-consecutive-run success rate

**Expected Timeline:** 3-5 days

#### Phase 1C: BFCL Setup (Week 2)

**Prerequisites:**
- Berkeley BFCL API access
- Claude Code tool definitions

**Setup Steps:**
1. Register at Berkeley BFCL leaderboard
2. Download evaluation harness
3. Map Penny tool interfaces to BFCL format

**Expected Timeline:** 2-3 days

### 3.2 Multi-Agent Architecture Adaptation

**Key Insight:** Most benchmarks assume single-agent architectures. Penny's 6-agent orchestration needs explicit mapping.

**Agent Role Mapping for Benchmarks:**

| Penny Agent | Benchmark Role | Notes |
|-------------|----------------|-------|
| clarification | Intent parsing | First-pass understanding |
| research | Information gathering | Tool use, search |
| analysis | Reasoning | Problem decomposition |
| synthesis | Solution integration | Plan formation |
| generation | Action execution | Code/output generation |
| validation | Verification | Result checking |

**Orchestration Strategies:**

1. **Full Pipeline:** Route through all 6 agents (comprehensive but slow)
2. **Fast Path:** Direct to relevant agent (trade-off: lower quality)
3. **Adaptive:** Memory agent decides pipeline depth

**Benchmark-Specific Adaptations:**

| Benchmark | Recommended Pipeline |
|-----------|---------------------|
| GAIA | Full (research -> analysis -> synthesis) |
| tau-bench | Adaptive (based on task complexity) |
| MultiAgentBench | Full (demonstrates coordination) |
| SWE-bench | generation-heavy (clarify -> generate -> validate) |
| ToolBench | research -> generation (tool focused) |

---

## 4. CUSTOM PENNY METRICS

### 4.1 Cognitive Handoff Quality (CHQ)

**Definition:** Measures information preservation and enhancement across agent transitions.

**Formula:**
```
CHQ = (Info_retained + Info_synthesized) / (Info_provided + Info_expected)
```

**Implementation:**
```python
def measure_chq(predecessor_output: dict, successor_input: dict,
                successor_output: dict) -> float:
    """
    Measure Cognitive Handoff Quality between agents.

    - Info_retained: Critical facts preserved from predecessor
    - Info_synthesized: New insights added by successor
    - Info_provided: Total information in predecessor output
    - Info_expected: Information successor should have produced
    """
    retained = count_preserved_facts(predecessor_output, successor_input)
    synthesized = count_new_insights(successor_output, predecessor_output)
    provided = count_total_facts(predecessor_output)
    expected = estimate_expected_output(task_type)

    return (retained + synthesized) / (provided + expected)
```

**Target:** CHQ > 0.85 for production readiness

### 4.2 Unknown Resolution Rate (URR)

**Definition:** Tracks how effectively the research->analysis->synthesis pipeline reduces uncertainty.

**Formula:**
```
URR = (Unknowns_initial - Unknowns_final) / Unknowns_initial
```

**Implementation:**
```python
def measure_urr(task_memory_files: list[str]) -> float:
    """
    Track unknown resolution across workflow.

    Uses Johari 'unknown' quadrant from each agent's memory file.
    """
    initial_unknowns = extract_unknowns(task_memory_files[0])  # clarification
    final_unknowns = extract_unknowns(task_memory_files[-1])   # validation

    if not initial_unknowns:
        return 1.0  # No unknowns to resolve

    resolved = len(initial_unknowns) - len(final_unknowns)
    return resolved / len(initial_unknowns)
```

**Target:** URR > 0.70 (resolve 70%+ of identified unknowns)

### 4.3 Johari Window Evolution (JWE)

**Definition:** Measures knowledge state progression across cognitive workflow.

**Quadrant Transitions:**
- Unknown -> Blind (research reveals)
- Blind -> Hidden (analysis processes)
- Hidden -> Open (synthesis surfaces)
- Unknown -> Open (direct discovery)

**Implementation:**
```python
def track_jwe(memory_files: list[str]) -> dict:
    """
    Track Johari quadrant transitions across agents.
    """
    transitions = {
        'unknown_to_blind': 0,
        'blind_to_hidden': 0,
        'hidden_to_open': 0,
        'unknown_to_open': 0,
        'regression': 0  # Bad: open->hidden, etc.
    }

    for i in range(len(memory_files) - 1):
        current = extract_johari(memory_files[i])
        next_state = extract_johari(memory_files[i+1])
        transitions = update_transitions(transitions, current, next_state)

    # JWE score: forward transitions - regressions
    score = (transitions['unknown_to_open'] * 3 +
             transitions['unknown_to_blind'] * 1 +
             transitions['blind_to_hidden'] * 1 +
             transitions['hidden_to_open'] * 2 -
             transitions['regression'] * 2)

    return {'score': score, 'transitions': transitions}
```

**Target:** JWE score > 0 with no regressions

### 4.4 Token Efficiency (TE)

**Definition:** Task completion quality per token consumed.

**Formula:**
```
TE = (Task_score * Quality_multiplier) / Tokens_consumed
```

**Implementation:**
```python
def measure_te(task_output: dict, benchmark_score: float,
               total_tokens: int) -> float:
    """
    Calculate token efficiency for task completion.

    Quality_multiplier:
    - 1.0: No errors, complete output
    - 0.8: Minor issues
    - 0.5: Significant gaps
    - 0.2: Major failures
    """
    quality = assess_output_quality(task_output)

    # Normalize to tokens per 1000
    normalized_tokens = total_tokens / 1000

    return (benchmark_score * quality) / normalized_tokens
```

**Comparison Targets:**
- Penny TE should be >= single-agent TE for equivalent task scores
- Track TE improvement over iterations

### 4.5 Orchestration Overhead (OO)

**Definition:** Additional cost of multi-agent coordination vs single-agent baseline.

**Formula:**
```
OO = (Tokens_penny - Tokens_single_agent) / Tokens_single_agent
```

**Target:** OO < 50% (orchestration should not more than double token usage)

**Justification Threshold:** If quality improvement > OO * 2, overhead is justified

---

## 5. SUCCESS CRITERIA

### 5.1 Target Percentiles vs SOTA

| Benchmark | Current SOTA | Target (6 months) | Stretch Goal |
|-----------|--------------|-------------------|--------------|
| GAIA (Overall) | h2oGPTe 65% | 55% (85th percentile) | 60% |
| GAIA (Level 1) | - | 70% | 80% |
| GAIA (Level 2) | - | 50% | 60% |
| GAIA (Level 3) | - | 35% | 45% |
| tau-bench pass^1 | - | 0.70 | 0.85 |
| tau-bench pass^3 | - | 0.35 | 0.60 |
| MultiAgentBench | Graph topology best | Top 25% | Top 10% |
| SWE-bench Verified | Claude 4.5: 81.5% | 50% | 65% |
| BFCL | - | Top 50% | Top 25% |

### 5.2 Architecture-Specific Win Conditions

**Multi-Agent Advantage:**
- Demonstrate >= 50% improvement over single-agent Claude baseline on tasks requiring:
  - Multi-step reasoning (GAIA Level 3)
  - Information synthesis (research questions)
  - Reliability (tau-bench pass^3+)

**Cognitive Handoff Value:**
- CHQ > 0.85 across all agent transitions
- URR > 0.70 for complex tasks
- JWE positive with zero regressions

**Token Efficiency Parity:**
- TE within 80% of single-agent for equivalent scores
- OO < 50% for standard tasks
- OO justified by quality on complex tasks

### 5.3 Production Readiness Indicators

| Indicator | Threshold | Measurement |
|-----------|-----------|-------------|
| **Reliability** | pass^3 > 0.50 | tau-bench |
| **General Capability** | GAIA > 55% | GAIA benchmark |
| **Tool Proficiency** | BFCL top 50% | BFCL leaderboard |
| **Coordination Quality** | MultiAgentBench top 25% | MARBLE evaluation |
| **Memory Integrity** | CHQ > 0.85 | Custom metric |
| **Unknown Resolution** | URR > 0.70 | Custom metric |
| **Error Rate** | < 10% critical failures | Task completion monitoring |
| **Latency** | < 5min for simple tasks | End-to-end timing |

### 5.4 Benchmark Milestone Timeline

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| Tier 1 Complete | Week 2 | GAIA, tau-bench, BFCL baselines established |
| Custom Metrics Implemented | Week 3 | CHQ, URR, JWE, TE operational |
| Tier 2 Started | Week 4 | MultiAgentBench running |
| Architecture Advantage Demonstrated | Week 6 | >= 50% multi-agent improvement shown |
| Tier 2 Complete | Week 8 | AgentBench subset + ToolBench done |
| Production Readiness Assessment | Week 10 | All indicators at threshold |
| Tier 3 Started | Week 12 | SWE-bench infrastructure ready |
| Full Evaluation Complete | Week 16 | All benchmarks with results |

---

## 6. APPENDICES

### Appendix A: Benchmark Repository Links

| Benchmark | Repository | Documentation |
|-----------|------------|---------------|
| SWE-bench | [GitHub](https://github.com/princeton-nlp/SWE-bench) | [Paper](https://arxiv.org/abs/2310.06770) |
| GAIA | [HuggingFace](https://huggingface.co/gaia-benchmark) | [Paper](https://arxiv.org/abs/2311.12983) |
| AgentBench | [GitHub](https://github.com/THUDM/AgentBench) | [ICLR'24](https://arxiv.org/abs/2308.03688) |
| tau-bench | [GitHub](https://github.com/sierra-research/tau-bench) | [Blog](https://sierra.ai/blog/benchmarking-ai-agents) |
| MultiAgentBench | [GitHub](https://github.com/multiagentbench/MARBLE) | [Paper](https://arxiv.org/abs/2503.01935) |
| ToolBench | [GitHub](https://github.com/OpenBMB/ToolBench) | [ICLR'24](https://arxiv.org/abs/2307.16789) |
| BFCL | [Berkeley](https://gorilla.cs.berkeley.edu/leaderboard.html) | Official leaderboard |
| WebArena | [Website](https://webarena.dev/) | [Paper](https://arxiv.org/abs/2307.13854) |
| OSWorld | [GitHub](https://github.com/xlang-ai/OSWorld) | [NeurIPS'24](https://arxiv.org/abs/2404.07972) |
| TheAgentCompany | [GitHub](https://github.com/TheAgentCompany/TheAgentCompany) | [Paper](https://arxiv.org/abs/2412.14161) |

### Appendix B: Enterprise Evaluation Frameworks

**CLASSic (ICLR 2025):**
- Cost
- Latency
- Accuracy
- Stability
- Security

**CLEAR:**
- Cost
- Latency
- Efficacy
- Assurance
- Reliability

### Appendix C: Coordination Protocol Reference

| Protocol | Description | Performance | Penny Mapping |
|----------|-------------|-------------|---------------|
| Star | Central coordinator + workers | Baseline | clarification as hub |
| Chain | Sequential agent pipeline | +1% vs star | Standard Penny flow |
| Tree | Hierarchical delegation | +2% vs star | Skill orchestration |
| Graph | Flexible interconnection | Best (+3%) | Full cognitive network |

---

## Document Metadata

**Research Sources:** 39 queries across academic papers, benchmark repositories, AI company publications
**Benchmarks Covered:** 12 major benchmarks
**Implementation Guides:** 6 detailed (GAIA, tau-bench, BFCL, MultiAgentBench, AgentBench, SWE-bench)
**Custom Metrics Defined:** 5 (CHQ, URR, JWE, TE, OO)
**Success Criteria:** 4 categories with quantified targets

**Next Steps:**
1. Begin Tier 1 implementation (GAIA first)
2. Instrument Penny for custom metric collection
3. Establish baseline measurements
4. Report initial results at Week 2 milestone
