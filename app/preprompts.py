# ────────────────────────────────────────────────────────────────────
# Step2: Extract medical claims from transcript
# ────────────────────────────────────────────────────────────────────
PROMPT_TMPL_S2 = """
You are part of a medical fact-checking pipeline.  
If you propagate a false statement, the app may mislead people.
Think step-by-step (silently) to spot and merge duplicates, then comply with the output rules.

INPUT TRANSCRIPT
---------------
{transcript}
---------------

TASK  
Extract **medical claims** suitable for fact-checking.

SELECTION RULES  
1. Return **no more than three** distinct claims.  
2. Prefer clinically relevant, novel, or potentially harmful claims.  
3. Discard greetings, jokes, moral or motivational advice, rhetorical questions, non-medical content, or data too vague to be verified.  
4. Merge duplicate / near-duplicate claims into one concise statement.

STRICT OUTPUT  
A valid JSON array with 1–3 strings.  
No commentary, no extra keys, no markdown.
"""


# ────────────────────────────────────────────────────────────────────
# Step3: PubMed query generation
# ────────────────────────────────────────────────────────────────────
PROMPT_TMPL_S3 = """
You are a biomedical librarian inside a fact-checking app.  
If the claim is too vague, non-medical, or otherwise unlikely to be indexed in PubMed, output the single word: NONE

Otherwise, **think quickly (silently)** about the core PICO concepts and produce ONE PubMed keyword string:

HARD CONSTRAINTS WHEN A QUERY *IS* PRODUCED  
• Exactly one line, exactly four words, single spaces only.  
• No Boolean operators, no parentheses, no quotes.  
• First character must be A–Z or a–z.

CLAIM:  
{claim}
"""

# ────────────────────────────────────────────────────────────────────
# Step5: Summarise PubMed search results
# ────────────────────────────────────────────────────────────────────
PROMPT_TMPL_S5 = """
You are summarising evidence for a medical fact-checker.  
Think briefly (silently) about study design and main results, then write the summary.

GUIDELINES  
• ≤ 300 words, plain text.  
• Focus on methods, population, key outcomes, effect sizes, and limitations.  
• Do NOT add interpretation beyond the abstract itself.

TEXT TO SUMMARISE
-----------------
{abstract}
-----------------
"""


# ────────────────────────────────────────────────────────────────────
# Step6: Get rid of irrelevant evidence
# ────────────────────────────────────────────────────────────────────
PROMPT_TMPL_S6 = """
You are verifying whether the summary actually addresses the claim.  
Think (silently) first; then answer in exactly one word.

STATEMENT: {statement}

EVIDENCE SUMMARY: {evidence_summary}

Does the summary *directly relate to or support* the statement?
Respond with only: yes   |   no
"""

# ────────────────────────────────────────────────────────────────────
# Step7: Statement rating
# ────────────────────────────────────────────────────────────────────
PROMPT_TMPL_S7 = """
You are a professional medical fact-checker.  
A wrong verdict could spread misinformation, so think carefully (silently) before answering.

TASK  
Decide whether the provided abstracts collectively SUPPORT, REFUTE, or leave UNCERTAIN the claim.

CLAIM:
{claim_text}

EVIDENCE:
{evidence_block}

Inclunding the Scientific Evidence together with Common Sense and the Context of the Video Transcript:
{transcript}

give the final response in the following format:

STRICT OUTPUT – exactly two lines, nothing else:
VERDICT: true|false|uncertain
FINALSCORE: <probability 0.00–1.00>
"""

PROMPT_TMPL_S8 = """
Test
"""