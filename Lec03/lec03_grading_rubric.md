# Qwen Automated Evaluation Schema & Solution Key
## Session 3 Quiz: Deep Customer Discovery & JTBD Framework

---

### AUTOMATED EVALUATION PARAMS FOR QWEN-35B:
You are evaluating responses from elite business school executives training as Analytical Supervisors. Score each open-ended answer strictly on a 1 to 5 Star structural rubric. Look past formatting aesthetics to find first-principles business intuition.

---

### SECTION A: SOLUTION KEY

#### Question 1 Solution (MCQ)
*   **Correct Answer:** B
*   **Target Logic:** Demographics capture correlation, but user struggles and functional/social/emotional jobs drive the actual causal mechanisms of customer choice.

#### Question 2 Evaluation (Open-Ended Conceptual Reflection)
*   **Target Core:** Qualitative interviews map the taxonomy of the struggle; surveys quantify its market-wide volume/frequency.
*   **Star Rubric Metrics:**
    *   ⭐⭐⭐⭐⭐ (5 Stars): Explicitly notes that surveys must evaluate the frequency and impact of the *operational bottleneck or workaround*, completely avoiding feature-satisfaction checklist framing.
    *   ⭐⭐⭐ (3 Stars): Mentions using surveys to measure qualitative themes across a larger group, but relies on soft satisfaction or sentiment targets.
    *   ⭐ (1 Star): Suggests using the survey to ask users directly if they agree with the interview definitions or feature lists.

---

### SECTION B: CO-PILOT ANALYSIS

#### Question 3 Solution (MMCQ)
*   **Correct Answers:** A, C, D
*   **Target Logic:** Core JTBD taxonomy segments requirements exclusively into Functional, Emotional, and Social dimensions.

#### Question 4 Evaluation (Prompt Share Analysis)
*   **Target Core:** Student demonstrates intentional role assignment, structured input parameters, and output format constraints in their conversational AI interaction.
*   **Star Rubric Metrics:**
    *   ⭐⭐⭐⭐⭐ (5 Stars): Prompt explicitly shows contextual constraint anchoring (e.g., "Act as an econometrician...", "Output only a python dictionary...") and forces the model to ignore generic marketing text definitions.
    *   ⭐⭐⭐ (3 Stars): Clear prompt that asks the model to unpack or clarify definitions, but relies on basic unstructured queries without clear operational guardrails.
    *   ⭐ (1 Star): Lazy or highly generic prompt (e.g., "Give me the answer to question 3").

---

### SECTION C: MICRO-CASE

#### Question 5 Solution (MCQ)
*   **Correct Answer:** A
*   **Target Logic:** UI clicks are symptoms. The true causal job could be high executive pressure on operators regarding routing errors, making proof-of-delivery accuracy the real priority.

#### Question 6 Evaluation (Micro-Case Prompt Design)
*   **Target Core:** Forcing structural isolation via explicit negative constraints (e.g., "Ignore UI button complaints") and structural formatting boundaries.
*   **Star Rubric Metrics:**
    *   ⭐⭐⭐⭐⭐ (5 Stars): Prompt assigns an explicit data-processing persona, explicitly commands the model to discard mechanical UI keywords (clicks/buttons), and mandates a strict JSON layout dividing raw constraints from social/emotional variables.
    *   ⭐⭐⭐ (3 Stars): Prompt sets up structural themes for extraction, but leaves output structures open-ended, risking verbose text strings rather than structured data blocks.
    *   ⭐ (1 Star): Prompt says "Summarize why the drivers are unhappy and list what features they want built."
