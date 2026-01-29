from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()

TASK_FHM = """A meme is harmful if and only if all of the following conditions are met:
① Targeted Attack on Protected Groups:
The combined image and text constitute a direct or indirect attack on people based on one or more of the following protected characteristics:
(1)Race, ethnicity, or nationality
(2)Immigration status
(3)Religion
(4)Caste
(5)Sex, gender identity, or sexual orientation
(6)Disability or disease
② Form of Attack Includes At Least One of the Following:
(1)Dehumanization: Comparing people to animals, objects, or non-human entities (e.g., implying a group “smells like a skunk” to degrade them).
(2)Statements of Inferiority: Claiming a group is inherently lesser, dirty, dangerous, or unworthy.
(3)Calls for Exclusion or Segregation: Advocating that a group be banned, isolated, or removed from society.
(4)Mocking Hate Crimes: Making light of violence or discrimination against protected groups.
③ Multimodal Dependency:
(1)The harmful meaning only emerges from the combination of image and text.
(2)If you replace the image with a semantically similar but neutral alternative (e.g., swap a skunk for a rose), the meme becomes harmless.
(3)If you replace the text with a neutral but contextually plausible alternative (e.g., change “Love the way you smell today” to “Skunks have a strong odor”), the meme becomes harmless.
(4)If the meme remains harmful when either modality is removed or replaced, it may be unimodally harmful—but for this task, we focus on truly multimodal harm.
Definition of "Harmless"
A meme is harmless if any of the following is true:
① No Attack on Protected Groups:
The content does not target any group based on the protected characteristics listed above.
② Falls Under Explicit Exceptions:
(1)It criticizes or mocks specific individuals or public figures (e.g., politicians, celebrities), provided the criticism is not based on their protected characteristics.
(2)It condemns or ridicules groups that promote hate or violence (e.g., terrorist organizations, white supremacist groups)—this is not considered harmful.
③ Lacks Combined Harmful Intent:
(1)The text alone is benign (e.g., “Look how many people love you”).
(2)The image alone is benign (e.g., a tumbleweed, a skunk, or a crowd).
(3)Only when combined do they potentially imply mockery or exclusion—but if that implication does not meet the criteria for dehumanization, inferiority, or exclusion, it remains harmless.
④ Neutral or Factual Statements:
Descriptive, humorous, or ironic statements that do not demean or attack a protected group (e.g., “Skunks have a very particular smell”) are harmless, even if paired with relevant imagery.
Important Instructions
① Do not classify based on keywords alone (e.g., the word “black” or an image of a religious symbol is not automatically harmful).
② Consider real-world context and implied meaning, not just literal content.
③ The presence of benign confounders confirms multimodal nuance: if changing either the image or text flips the meaning to non-harmful, then the original must be evaluated as a unified whole.
④ When in doubt, ask: “Would a reasonable person interpret this as an attack on a protected group based on who they are—not what they believe or do?”
"""
TASK_FHM2 = """
A meme is classified as harmful if and only if all three of the following conditions are met. If any condition is not met, it is classified as harmless.
① Targeted Attack on Protected Groups
The combined image and text constitute a direct or indirect attack on people based on one or more of the following protected characteristics:
(1) Race, ethnicity, or nationality
(2) Immigration status
(3) Religion
(4) Caste
(5) Sex, gender identity, or sexual orientation
(6) Disability or disease
② Form of Attack Includes At Least One of the Following
(1) Dehumanization: Comparing people to animals, objects, or non-human entities (e.g., implying a group "smells like a skunk" to degrade them).
(2) Statements of Inferiority: Claiming a group is inherently lesser, dirty, dangerous, or unworthy.
(3) Calls for Exclusion or Segregation: Advocating that a group be banned, isolated, or removed from society.
(4) Mocking Hate Crimes: Making light of violence or discrimination against protected groups.
③ Multimodal Dependency
(1) The harmful meaning only emerges from the combination of image and text.
(2) If you replace the image with a semantically similar but neutral alternative (e.g., swap a skunk for a rose), the meme becomes harmless.
(3) If you replace the text with a neutral but contextually plausible alternative (e.g., change "Love the way you smell today" to "Skunks have a strong odor"), the meme becomes harmless.
(4) If the meme remains harmful when either modality is removed or replaced, it may be unimodally harmful—but this task focuses on truly multimodal harm.
Definition of "Harmless"
A meme is harmless if any of the following is true:
① No Attack on Protected Groups
The content does not target any group based on the protected characteristics listed above.
② Falls Under Explicit Exceptions
(1) Criticism or mockery of specific individuals or public figures: e.g., politicians, celebrities, provided the criticism is not based on their protected characteristics.
(2) Condemnation or ridicule of groups that promote hate or violence: e.g., terrorist organizations, white supremacist groups, extremist ideologies, and their widely recognized hate symbols (e.g., Nazi swastika, ISIS flag). This is considered opposition to hate itself and is not classified as harmful.
Key Distinction: Strictly distinguish between "attacking people with certain characteristics" and "criticizing a hate ideology/symbol." The latter targets ideas, organizations, or their symbols, not people's inherent identities like race or religion. For example, burning a swastika criticizes Nazism, not German people or a specific religious group.
③ Lacks Combined Harmful Intent
(1) The text alone is benign (e.g., "Look how many people love you").
(2) The image alone is benign (e.g., a tumbleweed, a skunk, or a crowd).
(3) Only when combined do they potentially imply mockery or exclusion—but if that implication does not meet the criteria for dehumanization, inferiority, or exclusion, it remains harmless.
④ Neutral or Factual Statements
Descriptive, humorous, or ironic statements that do not demean or attack a protected group (e.g., "Skunks have a very particular smell") are harmless, even if paired with relevant imagery.
Important Instructions & Supplementary Principles
No Keyword-Only Classification: Do not classify based on keywords alone (e.g., the word "black" or an image of a religious symbol is not automatically harmful).
Consider Real-World Context & Implied Meaning: Analyze by considering real-world context and implied meaning, not just literal content.
Benign Confirmer of Multimodal Nuance: If changing either the image or text flips the meaning to non-harmful, then the original must be evaluated as a unified whole.
Intent & Target Analysis: When in doubt, ask: "Would a reasonable person interpret this as an attack on a protected group based on who they are (their identity), rather than what they believe or do (their beliefs or actions)?"
Specific Guidance on Criticizing Hate Symbols:
Criticism, mockery, or negative depiction of widely recognized hate ideologies, organizations, or their symbols should have its dominant, reasonable interpretation viewed as opposition to hate, falling under the harmless exception ②(2).
Ensure the content does not implicitly or explicitly attack the entire ethnic, religious, racial, or other protected group associated with that ideology. The core distinction is whether the target is an "idea" or "people."
"""
TASK_FHM_J_H = """
### A meme is harmful if and only if all of the following conditions are met:  
*H1*:Targeted Attack on Protected Groups:  
The combined image and text constitute a direct or indirect attack on people based on one or more of the following protected characteristics:  
(1) Race, ethnicity, or nationality  
(2) Immigration status  
(3) Religion  
(4) Caste  
(5) Sex, gender identity, or sexual orientation  
(6) Disability or disease  
*H2*:Form of Attack Includes At Least One of the Following:  
(1) Dehumanization: Comparing people to animals, objects, or non-human entities (e.g., implying a group “smells like a skunk” to degrade them).  
(2) Statements of Inferiority: Claiming a group is inherently lesser, dirty, dangerous, or unworthy.  
(3) Calls for Exclusion or Segregation: Advocating that a group be banned, isolated, or removed from society.  
(4) Mocking Hate Crimes: Making light of violence or discrimination against protected groups.  
*H3*:Multimodal Dependency:  
(1) The harmful meaning only emerges from the combination of image and text.  
(2) If you replace the image with a semantically similar but neutral alternative (e.g., swap a skunk for a rose), the meme becomes harmless.  
(3) If you replace the text with a neutral but contextually plausible alternative (e.g., change “Love the way you smell today” to “Skunks have a strong odor”), the meme becomes harmless.  
(4) If the meme remains harmful when either modality is removed or replaced, it may be unimodally harmful—but for this task, we focus on truly multimodal harm.  
### A meme is harmless if any of the following is true:  
*N1*:No Attack on Protected Groups:  
The content does not target any group based on the protected characteristics listed above.  
*N2*:Falls Under Explicit Exceptions:  
(1) It criticizes or mocks specific individuals or public figures (e.g., politicians, celebrities), provided the criticism is not based on their protected characteristics.  
(2) It condemns or ridicules groups that promote hate or violence (e.g., terrorist organizations, white supremacist groups)—this is not considered harmful.  
*N3*:Lacks Combined Harmful Intent:  
(1) The text alone is benign (e.g., “Look how many people love you”).  
(2) The image alone is benign (e.g., a tumbleweed, a skunk, or a crowd).  
(3) Only when combined do they potentially imply mockery or exclusion—but if that implication does not meet the criteria for dehumanization, inferiority, or exclusion, it remains harmless.  
*N4*:Neutral or Factual Statements:  
Descriptive, humorous, or ironic statements that do not demean or attack a protected group (e.g., “Skunks have a very particular smell”) are harmless, even if paired with relevant imagery.  
### Important Instructions: 
① Do not classify based on keywords alone (e.g., the word “black” or an image of a religious symbol is not automatically harmful).  
② Consider real-world context and implied meaning, not just literal content.  
③ The presence of benign confounders confirms multimodal nuance: if changing either the image or text flips the meaning to non-harmful, then the original must be evaluated as a unified whole.  
④ When in doubt, ask: “Would a reasonable person interpret this as an attack on a protected group based on who they are—not what they believe or do?”  
### Scoring Protocol (Mandatory)
Evaluate the meme along harmless criteria frameworks: . Assign a score from **1 to 9** for each primary dimension below (1 = completely absent, 9 = fully and clearly present).
> **Notice:  
> - Score **objectively**—a harmless meme can still have moderate H2/H3 scores if it flirts with ambiguity.  
> - N1 and H1 are generally inversely related, but both can be low in unclear cases.  
> - High N2 (e.g., ridiculing Nazis) overrides high H1/H2.
### Scoring Protocol (Mandatory)
Evaluate the meme along harmful criteria frameworks: . Assign a score from **1 to 9** for each primary dimension below (1 = completely absent, 9 = fully and clearly present).
Note that your role is not to judge whether the meme is harmful or harmless, but to score the meme on each evaluation dimension based on how well it satisfies the criteria of that dimension.
```json
{
"harmful_scores": {
    "H1": int,
    "H2": int,
    "H3": int
  },
"harmless_scores": {
    "N1": int,
    "N2": int,
    "N3": int,
    "N4": int
  }
"reasoning": "Explaining which pathway dominates and why, referencing key scores."
}
Do not output anything outside the JSON block.
"""

TASK_HARM = """
**Scoring Dimensions:**

**Harmful Criteria:**
- **H1: Targeted Entity Existence**  
  Score high if the meme explicitly/implicitly targets a specific real individual with derogatory language or factual claims.

- **H2: Form of Harm**  
  Score high if it causes defamation, emotional disturbance, or promotes real conspiracies.  
  ⚠️ Apply H2.5 strictly: Only score H2 ≤4 if ALL H2.5 conditions are met.

- **H3: Multimodal Nature of Harm**  
  Score high if harm depends on BOTH image and text working together.

**Harmless Criteria:**
- **N1: No Targeted Entity**  
  Score high ONLY if no real social entity is identifiable or targeted with derogatory language.

- **N2: Rejection Criteria Met**  
  Score high only if the meme is non-English, unreadable, unimodal, or hand-drawn cartoon.

- **N3: Harm is Absent or Negligible**  
  Score high ONLY if:  
  - The content is clearly fantastical/surreal with NO factual claims, OR  
  - It critiques general behavior without naming/depicting specific individuals with derogatory terms.  
  → **If a real person is depicted AND labeled with a derogatory term (e.g., "idiot"), N3 ≤3.**  
  → **If a real person is depicted but transformed FANTASTICALLY with NO derogatory labels, N3 ≥6.**
"""

TASK_HARM_J_H = """
You are an expert evaluator scoring a meme on six dimensions: H1, H2, H3 (harmful) and N1, N2, N3 (harmless), per the HarMeme annotation guidelines.

**Critical Instructions Before Scoring:**

1. **Harmful Meme Definition (from paper p.2786):**  
   "Multi-modal units consisting of an image and a piece of text embedded that has the potential to cause harm to an individual, an organization, a community, or the society more generally. Here, harm includes mental abuse, defamation, psycho-physiological injury, proprietary damage, emotional disturbance, and compensated public image."

2. **Key Distinction (from paper p.2787):**  
   - **Sarcasm**: "Praise that is actually an insult; generally involves malice, the desire to put someone down"
   - **Satire**: "Ironical exposure of the vices or follies of an individual, group, institution, or idea, usually with the aim of correcting it"
   - **Note**: Not all satire is harmless - satire can be harmful if it causes real harm

3. **Harmful vs. Harmless Criteria:**
   - A meme is **harmful** if it is "implicitly or explicitly intended to cause harm to an entity" (p.2787)
   - Harmful content "is often implicit and might require critical judgment to establish its potential to do harm" (p.2787)
   - "Harmful memes may or may not be offensive, hateful, or biased in nature" (p.2787)

4. **Rejection Criteria (DO NOT USE FOR SCORING):**  
   The following memes were rejected in the dataset and should not be considered:
   - Non-English or code-mixed text
   - Unreadable text (blurry, incomplete)
   - Unimodal content (text-only or image-only)
   - Cartoons (hand-drawn animation style)

**Scoring Rules (1-9 scale):**

**H1: Targeted Entity Existence**  
Score high (7-9) if the meme explicitly or implicitly targets a specific entity (individual, organization, community, or society).  
→ Score moderate (4-6) if the targeting is general or ambiguous.

**H2: Form of Harm**  
Score high (7-9) if the meme has the potential to cause mental abuse, defamation, emotional disturbance, or other forms of harm as defined in the paper.  
→ Consider whether the content is "intended to cause harm" (p.2787) and whether it "exposes vices, allegations, and other negative aspects of an entity" (p.2787).

**H3: Multimodal Nature of Harm**  
Score high (7-9) if the harmful intent is expressed through the combination of image and text such that removing either modality significantly reduces perceived harm.

**N1: No Targeted Entity**  
Score high (7-9) if no specific social entity is identifiable as a target, or if targeting is general and not directed at specific individuals or groups.

**N2: Rejection Criteria Met**  
Score high (7-9) ONLY if the meme meets one of the rejection criteria (non-English, unreadable, unimodal, cartoon).  
→ For valid memes, this should always be low (1-3).

**N3: Harm is Absent or Negligible**  
Score high (7-9) ONLY if:
- The content is clearly satirical with the intent to correct rather than harm
- No defamation or emotional disturbance is likely to result
- The meme does not "expose vices, allegations, and other negative aspects of an entity based on verified or unfounded claims" (p.2787)
- There is no malice or "desire to put someone down" (p.2787)

**Critical Scoring Principles:**
1. Do NOT assume all satire is harmless - satire can be harmful if it causes real harm
2. Do NOT assume all sarcasm is harmful - context matters
3. Always consider: "Is this implicitly or explicitly intended to cause harm to an entity?" (p.2787)
4. For N3: High score requires evidence that harm is truly absent or negligible, not just that it's satire

**Output Format (STRICT JSON):**
{
  "harmful_scores": {
    "H1": int,
    "H2": int,
    "H3": int
  },
  "harmless_scores": {
    "N1": int,
    "N2": int,
    "N3": int
  },
  "reasoning": "Concise explanation referencing paper definitions (p.2786-2787), whether the content is intended to cause harm, and why scores reflect the HarMeme annotation guidelines."
}
"""
# ========== Saving Config ==========
AUTO_SAVE = True
SAVE_DIR = "results"
SAVE_FMT = "json"

DEBATE_PHASES = ["Opening", "Rebuttal", "Free", "Closing"]
DEBATE_ROLES = ["Opening", "Rebuttal", "Free", "Closing"]

SCORING_JUDGE_ROLES = [
    ("Accuracy", "Evaluate factual accuracy of arguments"),
    ("SourceReliability", "Evaluate reliability of cited sources"),
    ("Reasoning", "Evaluate logical consistency and reasoning"),
    ("Clarity", "Evaluate clarity and neutrality of language"),
    ("Ethics", "Evaluate ethical responsibility and harm potential"),
]

SUMMARY_JUDGE_CONFIG = (
    "Summary",
    """Summarize the debate with this structure:
    **Summary**
    1. **Main Event**: [Describe the meme]
    2. **Affirmative Position**: [Key points for harm]
    3. **Negative Position**: [Key points against harm]
    4. **Evidence Presented**: [Summary of evidence]
    5. **Key Points of Contention**: [Main disagreements]
    6. **Conclusion**: [Verdict and reasoning]"""
)

PHASE_TEMPLATES = {
    "Opening": "Meme: \"{meme_text}\"\nGive your opening statement.",
    "Rebuttal": "Rebutt your opponent's opening.",
    "Free": "Free debate round {turn}. Opponent said:\n{opponent_text}\nRespond.",
    "Free_Evidence": "Free debate round {turn}. Opponent:\n{opponent_text}\n\nEvidence:\n{evidence}\nUse evidence to respond.",
    "Closing": "Present your closing statement."
}


# ========== API & Model Config ==========
OPENAI_API_KEY = ""
OPENAI_API_BASE = ""

MODEL_NAME = 'gpt-4o-mini'  # gpt-4o-mini
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

# ========== Dataset Config ==========
DATASET_NAME = "HARM"  # Options: "FHM", "MAMI", "HARM"

# ========== Debate Process Config ==========
FREE_ROUNDS = 1
ENABLE_EVIDENCE = True
EVIDENCE_PHASE = "Opening"  # Options: "Opening", "Free", "Rebuttal"

# ========== Other Config ==========
DYNAMIC_JUDGES = True

SEARCH_KEY = "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"