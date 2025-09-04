# The Lanesborough Protocol  
*Finalized Specification – September 2025*

---

## Purpose  
The Lanesborough Protocol governs collaboration between human and AI agents in multi-step workflows. It ensures clarity, recoverability, accountability, and convergence toward auditable outcomes.

---

## Roles  

- **Human Orchestrator (HO)**  
  - Defines high-level goals.  
  - Sets iteration limits.  
  - Grants final execution approval.  
  - Intervenes in case of impasse.  

- **Generalizing AI (GA)**  
  - Architect role.  
  - Produces high-level proposals, abstractions, and plans.  
  - Issues tasks/questions to the IA.  

- **Inspecting AI (IA)**  
  - Ground-truth role.  
  - Paraphrases GA’s proposals, challenges them, and validates against concrete details.  
  - Executes tests and records decisions in the log.  

---

## Protocol Phases  

### 1. Initiation  
- **Actor:** HO  
- **Action:** States the goal and sets the maximum number of refinement iterations.  
- **Example:**  

      === HANDSHAKE TURN 1 (GA) ===
      /tag GA
      Goal: Migrate Supernote repository with metadata intact. 
      Max iterations: 3.

### 2. Proposal  
- **Actor:** GA  
- **Action:** Produces the initial high-level plan or architectural approach.  
- **Output:** Must be specific enough for IA to test and refine.  

### 3. Refinement Loop  
- **Actor:** GA and IA alternate turns.  
- **Process:**  
  1. **Mirror & Counter (IA):** IA paraphrases GA’s proposal, offers critique or alternative.  
  2. **Refine & Re-task (GA):** GA accepts/corrects IA’s understanding, adjusts plan.  
  3. **Closure Condition (Handshake):**  
     - One agent issues a **Summary of Agreement**:  

           Summary of Agreement:
           [final converged plan/spec text]
           Agreed.

     - The partner agent replies with:  

           Agreed.

- **Exit:** Loop continues until handshake or max iterations.  

### 4. Escalation  
- **If successful handshake:** Last AI requests HO approval to execute.  
- **If impasse (max iterations reached):** IA reports:  

      Impasse reached after N iterations. Requesting HO intervention.

### 5. Execution & Logging  
- **Actor:** IA  
- **Action:** Upon HO approval, IA executes or records the decision.  
- **Mandatory Logging:** Append to `acp_log.md`.  
- **Format:**  

      ---
      **Timestamp:** YYYY-MM-DD HH:MM:SS TZ
      **Decision:** [Summary of Agreement]
      **GA Contribution:** [one-sentence summary]
      **IA Contribution:** [one-sentence summary]
      ---

---

## Exception Handling  
- **Actor:** IA  
- **Trigger:** If IA cannot complete a task (error, missing file, failed test).  
- **Action:** Halt process and issue:  

      EXCEPTION: [description of error, relevant logs, blocked task]

- **Resolution:** Resume only when GA revises plan or HO provides new instructions.  

---

## Structural Rules  
- Every exchange is prefixed with **Handshake Turn Markers**:  

      === HANDSHAKE TURN N (agent) ===
      /tag {agent}

- These ensure deterministic sequencing and allow recovery if context is lost.  

---

## Naming & Versioning  
- The protocol is officially and permanently named:  
  **The Lanesborough Protocol**.  
- Supersedes the working title “Asymmetric Convergence Protocol (ACP).”  

---

✅ This specification is now finalized.  
