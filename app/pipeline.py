# pipeline.py
import os, re
import time
import json
from .step_1_audio_to_transcript import update_transcript
from .step_2_transcript_to_statement import update_statements
from .step_3_statement_to_query import update_query
from .step_4_query_to_link import query_to_link
from .step_5_link_to_summary import link_to_summary
from .step_6_reduce_to_evidence import reduce_to_evidence
from .step_7_statement_to_truthness import statement_to_truthness
from .step_8_statment_to_score import statement_to_score

CHECK_PROMPT_TMPL = (
    "You are a medical fact-checker.\n"
    "Given the statement below, reply ONLY with an integer score from 0 (false) to 100 (true).\n"
    "NO verdict, NO explanation, ONLY the number.\n\n"
    "STATEMENT:\n{statement}\n"
)
score_re = re.compile(r"\b([0-9]{1,3})\b")

def run_pipeline(tmp_path: str) -> dict:
    """
    1) Transcribe with Whisper
    2) Feed the transcript to an LLM (e.g. fact-check, summary, follow-up Q&A…)
    3) Return a dict you’ll JSON-encode later
    """
    # 1️⃣ Whisper
    start = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step1 --- ")
    print(" \n --------------------------------------------------------------- \n")
    t0 = time.time()
    transcript = update_transcript("app/json_example.json", tmp_path)
    t1 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step2 --- ")
    print(" \n --------------------------------------------------------------- \n")
    statments = update_statements(transcript)
    t2 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step3 --- ")
    print(" \n --------------------------------------------------------------- \n")
    query = update_query(statments)
    t3 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step4 --- ")
    print(" \n --------------------------------------------------------------- \n")
    link = query_to_link(query)
    t4 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step5 --- ")
    print(" \n --------------------------------------------------------------- \n")
    summary = link_to_summary(link)
    t5 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step6 --- ")
    print(" \n --------------------------------------------------------------- \n")
    evidence = reduce_to_evidence(summary)
    t6 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step7 --- ")
    print(" \n --------------------------------------------------------------- \n")
    truthness = statement_to_truthness(evidence)
    t7 = time.time()

    print(" \n\n\n\n\n\n  --------------------------------------------------------------- \n")
    print(" --- Step8 --- ")
    print(" \n --------------------------------------------------------------- \n")
    scores = statement_to_score(truthness)
    t8 = time.time()

    elapsed = t8 - start

    print(" \n\n\n\n\n\n --------------------------------------------------------------- \n")
    print(" --- Runtime Analysis ---")
    print(" \n --------------------------------------------------------------- \n")
    print(f"update_transcript: {t1 - t0:.6f} seconds")
    print(f"update_statements: {t2 - t1:.6f} seconds")
    print(f"update_query: {t3 - t2:.6f} seconds")
    print(f"query_to_link: {t4 - t3:.6f} seconds")
    print(f"link_to_summary: {t5 - t4:.6f} seconds")
    print(f"reduce_to_evidence: {t6 - t5:.6f} seconds")
    print(f"statement_to_truthness: {t7 - t6:.6f} seconds")
    print(f"statement_to_score: {t8 - t7:.6f} seconds")
    print(f"Total elapsed time: {elapsed:.6f} seconds")


    print(" \n\n\n\n\n\n --------------------------------------------------------------- \n")
    print(" --- Final Output (JSON) ---")
    print(" \n --------------------------------------------------------------- \n")
    print(scores)

    return scores
