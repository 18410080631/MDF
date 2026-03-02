from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()

TASK_FHM = """
###Harmful dimension:
*H1*: Targeted Attack on Protected Groups:  
The combined image and text constitute a direct or indirect attack on people based on one or more of the following protected characteristics:  
(1) Race, ethnicity, or nationality  
(2) Immigration status  
(3) Religion  
(4) Caste  
(5) Sex, gender identity, or sexual orientation  
(6) Disability or disease  
*H2*: Form of Attack Includes At Least One of the Following:  
(1) Dehumanization: Comparing people to animals, objects, or non-human entities (e.g., implying a group “smells like a skunk” to degrade them).  
(2) Statements of Inferiority: Claiming a group is inherently lesser, dirty, dangerous, or unworthy.  
(3) Calls for Exclusion or Segregation: Advocating that a group be banned, isolated, or removed from society.  
(4) Mocking Hate Crimes: Making light of violence or discrimination against protected groups.  
*H3*: Multimodal Dependency:  
(1) The harmful meaning only emerges from the combination of image and text.  
(2) If you replace the image with a semantically similar but neutral alternative (e.g., swap a skunk for a rose), the meme becomes harmless.  
(3) If you replace the text with a neutral but contextually plausible alternative (e.g., change “Love the way you smell today” to “Skunks have a strong odor”), the meme becomes harmless.  
(4) If the meme remains harmful when either modality is removed or replaced, it may be unimodally harmful—but for this task, we focus on truly multimodal harm.  
###Harmless demension:
*N1*: No Attack on Protected Groups:  
The content does not target any group based on the protected characteristics listed above.  
*N2*: Falls Under Explicit Exceptions:  
(1) It criticizes or mocks specific individuals or public figures (e.g., politicians, celebrities), provided the criticism is not based on their protected characteristics.  
(2) It condemns or ridicules groups that promote hate or violence (e.g., terrorist organizations, white supremacist groups)—this is not considered harmful.  
*N3*: Lacks Combined Harmful Intent:  
(1) The text alone is benign (e.g., “Look how many people love you”).  
(2) The image alone is benign (e.g., a tumbleweed, a skunk, or a crowd).  
(3) Only when combined do they potentially imply mockery or exclusion—but if that implication does not meet the criteria for dehumanization, inferiority, or exclusion, it remains harmless.  
*N4*: Neutral or Factual Statements:  
Descriptive, humorous, or ironic statements that do not demean or attack a protected group (e.g., “Skunks have a very particular smell”) are harmless, even if paired with relevant imagery.  
*N5*: Contextual Understanding:  
(1) Evaluators should assess the societal and cultural implications of the meme to ensure accurate interpretation and prevent misjudgments.  
(2) Memes that highlight complex social phenomena without attacking protected groups should be classified as harmless.  
*N6*: Cultural Sensitivity:  
Assess whether the meme contains elements that, within a specific cultural context, might be perceived as demeaning or mocking toward protected groups. This dimension aims to capture subtle nuances that might not be overtly violent but still fall under culturally sensitive interpretations.  
*N7*: Contextual Nuance:  
Evaluate the cultural and social context surrounding the meme’s text and imagery, ensuring a comprehensive understanding of its intent and potential misinterpretation risks.  
### Important Instructions:  
① Do not classify based on keywords alone (e.g., the word “black” or an image of a religious symbol is not automatically harmful).  
② Consider real-world context and implied meaning, not just literal content.  
③ The presence of benign confounders confirms multimodal nuance: if changing either the image or text flips the meaning to non-harmful, then the original must be evaluated as a unified whole.  
④ When in doubt, ask: “Would a reasonable person interpret this as an attack on a protected group based on who they are—not what they believe or do?”  
"""
TASK_FHM_J_H = """
### A meme is harmful if and only if all of the following conditions are met:  
*H1*: Targeted Attack on Protected Groups:  
The combined image and text constitute a direct or indirect attack on people based on one or more of the following protected characteristics:  
(1) Race, ethnicity, or nationality  
(2) Immigration status  
(3) Religion  
(4) Caste  
(5) Sex, gender identity, or sexual orientation  
(6) Disability or disease  
*H2*: Form of Attack Includes At Least One of the Following:  
(1) Dehumanization: Comparing people to animals, objects, or non-human entities (e.g., implying a group “smells like a skunk” to degrade them).  
(2) Statements of Inferiority: Claiming a group is inherently lesser, dirty, dangerous, or unworthy.  
(3) Calls for Exclusion or Segregation: Advocating that a group be banned, isolated, or removed from society.  
(4) Mocking Hate Crimes: Making light of violence or discrimination against protected groups.  
*H3*: Multimodal Dependency:  
(1) The harmful meaning only emerges from the combination of image and text.  
(2) If you replace the image with a semantically similar but neutral alternative (e.g., swap a skunk for a rose), the meme becomes harmless.  
(3) If you replace the text with a neutral but contextually plausible alternative (e.g., change “Love the way you smell today” to “Skunks have a strong odor”), the meme becomes harmless.  
(4) If the meme remains harmful when either modality is removed or replaced, it may be unimodally harmful—but for this task, we focus on truly multimodal harm.  
### A meme is harmless if any of the following is true:  
*N1*: No Attack on Protected Groups:  
The content does not target any group based on the protected characteristics listed above.  
*N2*: Falls Under Explicit Exceptions:  
(1) It criticizes or mocks specific individuals or public figures (e.g., politicians, celebrities), provided the criticism is not based on their protected characteristics.  
(2) It condemns or ridicules groups that promote hate or violence (e.g., terrorist organizations, white supremacist groups)—this is not considered harmful.  
*N3*: Lacks Combined Harmful Intent:  
(1) The text alone is benign (e.g., “Look how many people love you”).  
(2) The image alone is benign (e.g., a tumbleweed, a skunk, or a crowd).  
(3) Only when combined do they potentially imply mockery or exclusion—but if that implication does not meet the criteria for dehumanization, inferiority, or exclusion, it remains harmless.  
*N4*: Neutral or Factual Statements:  
Descriptive, humorous, or ironic statements that do not demean or attack a protected group (e.g., “Skunks have a very particular smell”) are harmless, even if paired with relevant imagery.  
*N5*: Contextual Understanding:  
(1) Evaluators should assess the societal and cultural implications of the meme to ensure accurate interpretation and prevent misjudgments.  
(2) Memes that highlight complex social phenomena without attacking protected groups should be classified as harmless.  
*N6*: Cultural Sensitivity:  
Assess whether the meme contains elements that, within a specific cultural context, might be perceived as demeaning or mocking toward protected groups. This dimension aims to capture subtle nuances that might not be overtly violent but still fall under culturally sensitive interpretations.  
*N7*: Contextual Nuance:  
Evaluate the cultural and social context surrounding the meme’s text and imagery, ensuring a comprehensive understanding of its intent and potential misinterpretation risks.  
### Important Instructions:  
① Do not classify based on keywords alone (e.g., the word “black” or an image of a religious symbol is not automatically harmful).  
② Consider real-world context and implied meaning, not just literal content.  
③ The presence of benign confounders confirms multimodal nuance: if changing either the image or text flips the meaning to non-harmful, then the original must be evaluated as a unified whole.  
④ When in doubt, ask: “Would a reasonable person interpret this as an attack on a protected group based on who they are—not what they believe or do?”  
### Scoring Protocol (Mandatory)  
Evaluate the meme along harmful criteria frameworks. Assign a score from **1 to 9** for each primary dimension below (1 = completely absent, 9 = fully and clearly present).  
> **Notice:  
> - Score **objectively**—a harmless meme can still have moderate H2/H3 scores if it flirts with ambiguity.  
> - N1 and H1 are generally inversely related, but both can be low in unclear cases.  
> - High N2 (e.g., ridiculing Nazis) overrides high H1/H2.  
### Scoring Protocol (Mandatory)  
Evaluate the meme along harmless criteria frameworks. Assign a score from **1 to 9** for each primary dimension below (1 = completely absent, 9 = fully and clearly present).  
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
    "N4": int,
    "N5": int,
    "N6": int,
    "N7": int
  },
  "reasoning": "Explaining which pathway dominates and why, referencing key scores."
  "prediction": "Harmful" or "Harmless" based on the dominant scores and reasoning.
}
```  
Do not output anything outside the JSON block.
"""

TASK_HARM = """
###Harmful dimension:
- **H1: Targeted Entity Existence**  
  Score high if the meme explicitly/implicitly targets a specific real individual with derogatory language or factual claims.
- **H2: Form of Harm**  
  Score high if it causes defamation, emotional disturbance, or promotes real conspiracies.  
  ⚠️ Apply H2.5 strictly: Only score H2 ≤4 if ALL H2.5 conditions are met.
- **H3: Multimodal Nature of Harm**  
  Score high if harm depends on BOTH image and text working together.
###Harmless dimension:
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
#####
You are an expert evaluator tasked with scoring a meme along **twelve predefined dimensions** based on the HarMeme annotation guidelines (ACL-IJCNLP 2021). Your role is **NOT** to output a final 'harmful' or 'harmless' label, but to assign a score from 1 to 9 for each dimension, where 1 = completely absent and 9 = fully and clearly present.  
**Critical Instructions Before Scoring:**  
1. **Distinguish Sarcasm vs. Satire (CRITICAL)**  
   - **Sarcasm**: "Praise that is actually an insult; generally involves malice, the desire to put someone down"  
     (e.g., calling a specific person "the village idiot")  
   - **Satire**: "Ironical exposure of the vices or follies of an individual, group, or institution, usually with the aim of correcting it"  
   - **Sarcasm targeting specific individuals is HARMFUL**; **satire using fictional/exaggerated elements is generally HARMLESS**  
2. **H2.5 Exception – Applies ONLY when ALL conditions are met:**  
   - The content uses **fictional, surreal, hyperbolic, or cartoonish exaggeration**  
     (e.g., depicting a person as a monster, alien, or zombie)  
   - The meme makes **NO factual or pseudo-factual claims** about the target  
     (e.g., "this is what Trump actually looks like")  
   - The content **does not directly label the target with derogatory terms**  
     (e.g., "idiot," "liar")  
   - The exaggeration is **clearly fantastical** and not presented as reality  
   - The meme **does not promote real-world stigma or conspiracy theories**  
   → If **ANY** condition fails, **H2.5 does NOT apply**  
3. **Targeting Specific Individuals:**  
   - Using a real person's image with a derogatory label (e.g., "village idiot") = **DIRECT TARGETING** (H1 high)  
   - Using a real person's image with fictional transformation (e.g., "will become a monster") = **INDIRECT TARGETING** (H1 moderate)  
   - Using a real person's image for general commentary without derogatory labels = **POTENTIALLY HARMLESS**  
4. **Context Matters:**  
   - Ask: *"Is this meme asserting something as factual about the target, or is it clearly fantastical humor?"*  
   - Ask: *"Could a reasonable person interpret this as directly demeaning a specific individual?"*  
**Scoring Dimensions:**  
**Harmful Criteria:**  
- **H1: Targeted Entity Existence**  
  Score high if the meme explicitly/implicitly targets a specific real individual with derogatory language or factual claims. Pay special attention to implicit attacks that may suggest demeaning of particular groups.  
- **H2: Form of Harm**  
  Score high if it causes defamation, emotional disturbance, or promotes real conspiracies. Consider the distinction between mild emotional disturbance and significant harm, particularly in the context of humor/satire.  
  ⚠️ **Apply H2.5 strictly**: Only score H2 ≤ 4 if **ALL H2.5 conditions are met**.  
- **H3: Multimodal Nature of Harm**  
  Score high if harm depends on **BOTH image and text working together**, particularly in how they structure viewer interpretation.  
- **H4: Social-Cultural Impact**  
  Evaluate potential effects on specific social groups or cultures, especially if stereotypes or biases are present. Score high if the meme reinforces negative stereotypes or biases.  
- **H5: Cultural Sensitivity**  
  Assess the meme’s potential to affect specific cultural groups negatively, evaluating if it may invoke negative emotions or reinforce stereotypes. Score high if cultural insensitivity is evident.  
- **H6: Humor Type and Social Impact Assessment**  
  Evaluate the type of humor used in the meme (e.g., exaggeration, satire, dark humor) and its potential to marginalize or demean social groups, enhancing the ability to identify harmful intent.  
- **H7: Antagonistic Humor Evaluation**  
  Specifically assess whether the humor in the meme may marginalize or demean specific groups, enhancing the ability to identify harmful intent.  
- **H8: Social Psychological Impact Assessment**  
  Assess the potential impact of the meme on individual psychological health within the context of social discussions and its sensitivity to cultural background.  
**Harmless Criteria:**  
- **N1: No Targeted Entity**  
  Score high **ONLY** if no real social entity is identifiable or targeted with derogatory language. Consider the broader social implications of the content.  
- **N2: Rejection Criteria Met**  
  Score high **only** if the meme is non-English, unreadable, unimodal, or hand-drawn cartoon.  
- **N3: Harm is Absent or Negligible**  
  Score high **ONLY** if:  
    - The content is clearly fantastical/surreal with **NO factual claims**, **OR**  
    - It critiques general behavior without naming/depicting specific individuals with derogatory terms.  
  → **If a real person is depicted AND labeled with a derogatory term (e.g., "idiot"), N3 ≤ 3.**  
  → **If a real person is depicted but transformed FANTASTICALLY with NO derogatory labels, N3 ≥ 6.**  
- **N4: Humor Type Assessment**  
  Score high if the humor type is clearly non-offensive and understood as general or self-deprecating, lacking malicious intent.  
- **N5: Contextual Humor Relevance**  
  Score high if the meme's humor is contextualized and relevant, lacking unintended harmful implications.  
**Output Format (STRICT JSON):**  
{
  "harmful_scores": {
    "H1": int,
    "H2": int,
    "H3": int,
    "H4": int,
    "H5": int,
    "H6": int,
    "H7": int,
    "H8": int
  },
  "harmless_scores": {
    "N1": int,
    "N2": int,
    "N3": int,
    "N4": int,
    "N5": int
  },
  "reasoning": "Concise explanation distinguishing between sarcasm (harmful) and satire (harmless), explaining H2.5 applicability, and the appropriateness of scores for H1-H8 and N1-N5 while considering the cultural and social impacts."
  "prediction": "Harmful" or "Harmless" based on the dominant scores and reasoning.
}
"""

TASK_MAMI = """
###Harmful dimension:
- **H1: Targeted Entity Existence**  
  Score high if the meme explicitly or implicitly targets women (as individuals or as a group) with offensive, sexist, or hateful framing.  
- **H2: Offensive/Sexist/Hateful Content**  
  Score high if the meme conveys content that is offensive, sexist, or hateful toward women — whether **implicit or explicit**.  
- **H3: Multimodal Nature of Harm**  
  Score high if the misogynous meaning depends on **BOTH image and text working together** (e.g., neutral text + suggestive image, or vice versa).  
- **H4: Cultural or Political Background Influence**  
  Score high if the meme's content reflects specific cultural or political contexts that enhance its harmful implications toward women.  
- **H5: Humor/Satirical Nature**  
  Score high if the meme employs humor or satire that affects its interpretation, especially when considering cultural context.  
- **H6: Humor Analysis**  
  Score high if the meme's humorous nature is evaluated clearly, distinguishing absurd humor from genuine derogatory content that may not be perceived as harmful.
- **H7: Humor and Cultural Impact Assessment**  
  Score high if the meme's humor and cultural context are evaluated to discern the potential harmfulness effectively, especially in ambiguous cases.
- **H8: Cultural and Humor Context Evaluation**  
  Score high if the meme's type of humor and its cultural context are analyzed, combining social and cultural backgrounds to derive potential harm interpretation.
###Harmless dimension:
- **N1: No Targeted Entity**  
  Score high **ONLY** if no woman or female group is identifiable or targeted with derogatory framing.  
- **N2: Rejection Criteria Met**  
  Score high **only** if the meme meets MAMI's filtering conditions: non-English, unreadable, unimodal (text-only or image-only without meaningful combination), or clearly hand-drawn cartoon without realistic depiction.  
- **N3: Harm is Absent or Negligible**  
  Score high **ONLY** if:  
    - The content is clearly fantastical/surreal with **NO factual claims about women**, **OR**  
    - It critiques gender norms, patriarchal structures, or social issues **without depicting/labeling specific women with offensive, sexist, or hateful framing**.  
  → **If a real woman is depicted AND labeled with a derogatory term, N3 ≤ 3.**  
  → **If a woman is depicted but in a clearly fictional/fantastical context with NO derogatory framing, N3 ≥ 6.**  
- **N4: Contextual Factors**  
  Score high if the meme shows a level of humor or critique that reduces the likelihood of harm, taking into account its cultural context.  
"""

TASK_MAMI_J_H = """
You are an expert evaluator tasked with scoring a meme along predefined dimensions based on the MAMI annotation guidelines (SemEval-2022 Task 5). Your role is **NOT** to output a final 'misogynous' or 'not misogynous' label, but to assign a score from 1 to 9 for each dimension, where 1 = completely absent and 9 = fully and clearly present.  
**Critical Instructions Before Scoring:**  
1. **Core Definition (MAMI Sub-task A)**  
   - **Misogynous (Harmful)**: "a meme is misogynous if it conceptually describes an offensive, sexist or hateful scene (weak or strong, implicitly or explicitly) having as target a woman or a group of women"  
   - **Not Misogynous (Harmless)**: a meme that does not express any form of hate against women — either because it is unrelated to women, or because it relates to women but does not convey offensive, sexist, or hateful concepts against them.  
2. **Implicit vs. Explicit Harm (MAMI annotation principle)**  
   - Harm may be conveyed **implicitly** (e.g., visual suggestion + neutral text) or **explicitly** (e.g., direct derogatory label). Both count toward harmful scoring if the target is women.  
3. **Multimodal Dependency (MAMI core premise)**  
   - The offensive/sexist/hateful meaning may emerge **only when image AND text are interpreted together**. This is a key design principle of MAMI and must be explicitly evaluated.  
4. **Contextual Disambiguation**  
   - Ask: *"Could a reasonable person interpret this as offensive, sexist, or hateful toward women (as individuals or as a group)?"*  
   - Ask: *"Is the negative content about women presented as factual assertion, or as clearly absurdist/fictional humor with no real-world harmful implication?"*  
   - Ask: *"Does the meme critique gender norms or social issues without targeting women with derogatory framing?"* → If yes, lean toward harmless.  

**Scoring Dimensions:**  

**Harmful Criteria (Misogynous):**  
- **H1: Targeted Entity Existence**  
  Score high if the meme explicitly or implicitly targets women (as individuals or as a group) with offensive, sexist, or hateful framing.  

- **H2: Offensive/Sexist/Hateful Content**  
  Score high if the meme conveys content that is offensive, sexist, or hateful toward women — whether **implicit or explicit**.  

- **H3: Multimodal Nature of Harm**  
  Score high if the misogynous meaning depends on **BOTH image and text working together** (e.g., neutral text + suggestive image, or vice versa).  

- **H4: Cultural or Political Background Influence**  
  Score high if the meme's content reflects specific cultural or political contexts that enhance its harmful implications toward women.  

- **H5: Humor/Satirical Nature**  
  Score high if the meme employs humor or satire that affects its interpretation, especially when considering cultural context.  

- **H6: Humor Analysis**  
  Score high if the meme's humorous nature is evaluated clearly, distinguishing absurd humor from genuine derogatory content that may not be perceived as harmful.

- **H7: Humor and Cultural Impact Assessment**  
  Score high if the meme's humor and cultural context are evaluated to discern the potential harmfulness effectively, especially in ambiguous cases.

- **H8: Cultural and Humor Context Evaluation**  
  Score high if the meme's type of humor and its cultural context are analyzed, combining social and cultural backgrounds to derive potential harm interpretation.

**Harmless Criteria (Not Misogynous):**  
- **N1: No Targeted Entity**  
  Score high **ONLY** if no woman or female group is identifiable or targeted with derogatory framing.  

- **N2: Rejection Criteria Met**  
  Score high **only** if the meme meets MAMI's filtering conditions: non-English, unreadable, unimodal (text-only or image-only without meaningful combination), or clearly hand-drawn cartoon without realistic depiction.  

- **N3: Harm is Absent or Negligible**  
  Score high **ONLY** if:  
    - The content is clearly fantastical/surreal with **NO factual claims about women**, **OR**  
    - It critiques gender norms, patriarchal structures, or social issues **without depicting/labeling specific women with offensive, sexist, or hateful framing**.  
  → **If a real woman is depicted AND labeled with a derogatory term, N3 ≤ 3.**  
  → **If a woman is depicted but in a clearly fictional/fantastical context with NO derogatory framing, N3 ≥ 6.**  

- **N4: Contextual Factors**  
  Score high if the meme shows a level of humor or critique that reduces the likelihood of harm, taking into account its cultural context.  

**Output Format (STRICT JSON):**  
{  
  "harmful_scores": {  
    "H1": int,  
    "H2": int,  
    "H3": int,  
    "H4": int,  
    "H5": int,  
    "H6": int,  
    "H7": int,  
    "H8": int  
  },  
  "harmless_scores": {  
    "N1": int,  
    "N2": int,  
    "N3": int,  
    "N4": int  
  },  
  "reasoning": "Concise explanation per MAMI guidelines: (1) whether the meme targets women with offensive/sexist/hateful content (implicit/explicit), (2) whether harm emerges from image-text interaction, (3) why N3 score is appropriate given the presence/absence of derogatory framing or fantastical context, (4) how cultural or political context may influence the interpretation of the meme."  
  "prediction": "Harmful" or "Harmless" based on the dominant scores and reasoning.
  }
"""
UNIVERSAL_MEME_EVALUATION = """
Definitions & Core Principles:
Multimodal Dependency: A meme is "Multimodally Harmful" only if the harm arises from the combination of image and text. If the text alone is a neutral fact and the image is a neutral object, but their combination creates a slur or dehumanizing attack, it is harmful.
Sarcasm vs. Satire:
Sarcasm (Harmful Potential): Mockery intended to insult or degrade a specific individual or protected group.
Satire (Harmless Potential): Irony or exaggeration used to expose the vices or follies of institutions, power structures, or social norms, often with an intent to provoke thought or change.
Targeting: Distinguish between attacking a person for who they are (protected characteristics: Race, Gender, Religion, etc.) vs. what they do/say (actions, political decisions, public statements).
II. Scoring Dimensions (1-9 Scale)
A. Harmful Dimensions (Misogyny & General Harm)
H1: Targeted Entity Existence: Explicit or implicit targeting of a protected group or a real individual based on identity.
H2: Form of Attack: Presence of dehumanization (comparing to animals/objects), statements of inferiority, or calls for exclusion.
H3: Multimodal Harm Intensity: The degree to which the visual and textual elements synthesize to create an offensive meaning.
H4: Socio-Cultural Impact: The extent to which the meme reinforces harmful stereotypes or historical prejudices (e.g., misogyny, racism).
H5: Antagonistic Humor: Humor that relies on the misfortune, degradation, or biological traits of a protected group.
H6: Cultural Insensitivity: Mockery of sacred symbols, religious practices, or cultural heritage.
H7: Psychological Harm/Stigma: Potential to cause emotional distress or promote real-world stigma (e.g., mocking disabilities or diseases).
H8: Conspiracy & Fact-Distortion: Use of pseudo-facts or conspiracy theories to incite hatred against a group.
B. Harmless Dimensions (Anti-False Positive Focus)
N1: Absence of Targeted Group: The content is generic, involving no identifiable protected group or individual.
N2: Technical Exclusion: The meme is unimodal (text/image don't interact), unreadable, or purely fictional/hand-drawn without real-world parallels.
N3: Surrealism & Absurdism: The logic is clearly fantastical, nonsensical, or "shitposting" where no factual claim or attack is intended.
N4: Counter-Speech & Empowerment: The meme ridicules hate groups (e.g., mocking Nazis) or empowers a marginalized group (e.g., "Girl Power").
N5: In-group/Self-Deprecating Humor: Content created within a community to mock their own traits or struggles (e.g., "Self-aware" humor).
N6: Structural/Political Satire: Criticism directed at institutions, governments, or public figures' actions/policies, not their identity.
N7: Factual/Neutral Observation: The meme states a cultural fact, a common preference, or a benign observation without malicious intent.
N8: Contextual Defense: Subcultural "inside jokes" or memes that use "edgy" aesthetics but lack a genuine intent to harm or demean.
"""
UNIVERSAL_MEME_EVALUATION_PROMPT = """
You are a Senior Multimodal Content Auditor specializing in social-cultural linguistics and visual semiotics. Your task is to evaluate a meme’s potential for harm by analyzing the interplay between text and image.
I. Core Evaluative Principles
Multimodal Dependency: A meme is "Multimodally Harmful" only if the harm arises from the combination of image and text. If the text alone is a neutral fact and the image is a neutral object, but their combination creates a slur or dehumanizing attack, it is harmful.
Sarcasm vs. Satire:
Sarcasm (Harmful Potential): Mockery intended to insult or degrade a specific individual or protected group.
Satire (Harmless Potential): Irony or exaggeration used to expose the vices or follies of institutions, power structures, or social norms, often with an intent to provoke thought or change.
Targeting: Distinguish between attacking a person for who they are (protected characteristics: Race, Gender, Religion, etc.) vs. what they do/say (actions, political decisions, public statements).
II. Scoring Dimensions (1-9 Scale)
A. Harmful Dimensions (Misogyny & General Harm)
H1: Targeted Entity Existence: Explicit or implicit targeting of a protected group or a real individual based on identity.
H2: Form of Attack: Presence of dehumanization (comparing to animals/objects), statements of inferiority, or calls for exclusion.
H3: Multimodal Harm Intensity: The degree to which the visual and textual elements synthesize to create an offensive meaning.
H4: Socio-Cultural Impact: The extent to which the meme reinforces harmful stereotypes or historical prejudices (e.g., misogyny, racism).
H5: Antagonistic Humor: Humor that relies on the misfortune, degradation, or biological traits of a protected group.
H6: Cultural Insensitivity: Mockery of sacred symbols, religious practices, or cultural heritage.
H7: Psychological Harm/Stigma: Potential to cause emotional distress or promote real-world stigma (e.g., mocking disabilities or diseases).
H8: Conspiracy & Fact-Distortion: Use of pseudo-facts or conspiracy theories to incite hatred against a group.
B. Harmless Dimensions (Anti-False Positive Focus)
N1: Absence of Targeted Group: The content is generic, involving no identifiable protected group or individual.
N2: Technical Exclusion: The meme is unimodal (text/image don't interact), unreadable, or purely fictional/hand-drawn without real-world parallels.
N3: Surrealism & Absurdism: The logic is clearly fantastical, nonsensical, or "shitposting" where no factual claim or attack is intended.
N4: Counter-Speech & Empowerment: The meme ridicules hate groups (e.g., mocking Nazis) or empowers a marginalized group (e.g., "Girl Power").
N5: In-group/Self-Deprecating Humor: Content created within a community to mock their own traits or struggles (e.g., "Self-aware" humor).
N6: Structural/Political Satire: Criticism directed at institutions, governments, or public figures' actions/policies, not their identity.
N7: Factual/Neutral Observation: The meme states a cultural fact, a common preference, or a benign observation without malicious intent.
N8: Contextual Defense: Subcultural "inside jokes" or memes that use "edgy" aesthetics but lack a genuine intent to harm or demean.
III. Critical Rule: The H2.5 Exception
Score H2 ≤ 4 and N3/N6 ≥ 7 if the following are true:
The depiction is clearly exaggerated/cartoonish (e.g., a person as a "gigachad" or a "soyjak").
The meme makes no factual claim about the target’s character.
The humor targets a public figure’s specific, documented behavior rather than their identity.
IV. Mandatory Output Format (JSON)
You must output the evaluation in the following JSON structure only:
{
  "harmful_scores": {
    "H1": int, "H2": int, "H3": int, "H4": int, "H5": int, "H6": int, "H7": int, "H8": int
  },
  "harmless_scores": {
    "N1": int, "N2": int, "N3": int, "N4": int, "N5": int, "N6": int, "N7": int, "N8": int
  },
  "reasoning": "1. Target Identification: [Who is being targeted, if anyone?]. 2. Multimodal Synthesis: [How do image and text interact?]. 3. Intent Analysis: [Is it Satire (N6), Self-deprecating (N5), or Malicious (H2)?]. 4. Justification: [Explain why the N-scores outweigh H-scores or vice-versa]."，
  "prediction": "Harmful" or "Harmless" based on the dominant scores and reasoning.
}
"""
# ========== Saving Config ==========
AUTO_SAVE = True

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
    "Rebuttal": "##Previous speech:{opponent_text}\n\n Rebutt your opponent's opening.",
    "Free": "##Previous speech:{opponent_text}\n\nDirectly counter the opponent and cite one criterion (H1-N6) to defend your stance.",
    "Closing": "##Previous speech:{opponent_text}\n\n Present your closing statement."
}


# ========== API & Model Config ==========
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-d2e7a6ce8c2d425ab5498a77b7f1c7ac") # sk-nXhyMEwSWPyCh94GBeXr6kdeIsbP2euit1vrCQPM5Xw4Awge
# OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")  # https://api.chatanywhere.tech/v1
# MODEL_NAME = 'qwen3-vl-flash'  # gpt-4o-mini

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-aFthrMPCNNtUreZpql2B0C2BxylbzRwxgRwrn6wsjkRJn4ac") # sk-nXhyMEwSWPyCh94GBeXr6kdeIsbP2euit1vrCQPM5Xw4Awge sk-aFthrMPCNNtUreZpql2B0C2BxylbzRwxgRwrn6wsjkRJn4ac
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.chatanywhere.tech/v1")  # https://api.chatanywhere.tech/v1
MODEL_NAME = 'gpt-4o-mini'  # gpt-4o-mini


TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

# ========== Dataset Config ==========
DATASET_NAME = "MAMI"  # Options: "FHM", "HARM","MAMI", 

# ========== Debate Process Config ==========
FREE_ROUNDS = 1
ENABLE_EVIDENCE = True
EVIDENCE_PHASE = "Opening"  # Options: "Opening", "Free", "Rebuttal"

# ========== Other Config ==========
DYNAMIC_JUDGES = True

SEARCH_KEY = "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"