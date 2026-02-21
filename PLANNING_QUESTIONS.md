# Frontier Pulse Planning Questions

Answer as many as possible; defaults can be applied where needed.

## Product and Workflow
1. Which exact audience do you optimize for in V1: only you, or a small research team?

Reasearch Community. I want this to be the first step in an automated AI researcher that I want to build.

2. Do you want weekly ingestion to run automatically at a fixed local time? If yes, which day/time/timezone?

Yes, can we run this each night at 2 AM PT

3. Is your 45-minute review target strict for every week or acceptable as a median target?


Yes that is acceptable

4. Should the dashboard optimize for keyboard-heavy workflows (hotkeys) in V1?

Whatever is the quickest. I will be infront of a computer and review it.


5. Do you want drafts versioned so edits across weeks are auditable?

Yes, full versioning of drafts. Moreover, all the backgorund research you have done should all be kept in a neat indexable memory. See answer to question 1. This is a first step in building an automated AI researcher.


## Data Scope and Retrieval
6. Do you want ingestion to include only arXiv or also OpenReview/Anthropic/OpenAI blogs in V1?

All sources. Blogs from frontier labs, X threads, Reddit discussions, Arxiv, OpenReview. Also search for AI blogs from major universities like Stanford, MIT, Berkeley


1. What initial keyword filters should be applied beyond categories (`cs.CL`, `cs.LG`, `stat.ML`)?

Let us start with those three + cs.AI, cs.DS, cs.GT, cs.MA


2. Should we include only papers submitted in the past 7 days or include revised older papers too?

Revised older papers too. Those are critical, since alpha might have changed. Having a good memory model is critical so that we can add these updates.


3.  Maximum papers per batch: keep hard cap at 80?

No hard cap per batch. Analyze all the relevant material on the focussed topic area. Eventually, we will expand topics. So he memory model should account for this.  


5.  Should duplicate detection be by arXiv ID only or also fuzzy title matching?

Fuzzy title + abstract matching.  


## Parsing and Preprocessing
11. Preferred PDF parser priority: `pymupdf` first, then `pdfminer` fallback?

Use your best judgement and do this. You know what code works well.

12. Should we drop appendices/references by default in V1?

Yes, lets use the main paper and claims. If the appendix/reference helps with understanding use it, but stick to the main paper otherwise.

13. Keep equations as plain text, or strip aggressive math artifacts?

Screenshot the equations and use multimodal LLMs, if its useful. For the first version, we can use it as plain text.

14. Target chunk size and overlap (e.g., 1,500 tokens with 200 overlap)?

Dont understand this question. Use your best judgement.

15. Should sections be recognized semantically (Intro/Method/Results) even if headings are noisy?

Yea, the goal is to understand the key hypothesis, claims and results. So the headings should be interpreted in the lens that helps you derive it.


## LLM and Inference
16. Primary local runner: Ollama or vLLM?
17. Which exact extraction model should be default on your machine?
18. Do you want a second “synthesis model” separate from extraction model?
19. Is optional cloud fallback acceptable in V1, or local-only hard requirement?
20. Max acceptable runtime per weekly batch on your hardware?
21. Do you want deterministic outputs (temperature near 0) for alpha cards?

## Embeddings and Retrieval
22. Which embedding model should be default (`nomic-embed-text`, `bge-large`, etc.)?
23. Should embeddings be generated for full paper, section chunks, or both?
24. Must vector search support metadata filters (date/source/cluster) in V1?

## Schema and Domain Model
25. Should `PaperAlphaCard` be immutable snapshots or editable with history?
26. For `novelty_score`, use numeric 0–100 or ordinal buckets?
27. Should `strength_score` for hypotheses be model-only or model + human override?
28. Should contradictions be explicit edges with confidence score?
29. Do you need provenance per field (which chunk/passage justified it)?

## Human-in-the-Loop UX
30. Do you want login/auth skipped entirely for local V1?
31. Are merge/split cluster operations mandatory for V1 or okay as V1.1?
32. For hypothesis table, should user rating be binary, 1-5, or weighted confidence?
33. Should we include inline citations/snippets beside each generated claim?
34. Rich text editor preference: Markdown textarea or WYSIWYG?
35. Any required hotkeys (approve/reject/edit-next) for rapid review?

## Exports and Publishing
36. For Twitter output, target X long posts or strict classic tweet thread constraints?
37. For LinkedIn output, preferred tone: analytical, conversational, or founder-voice?
38. Should export include optional visual assets (graph image) by default?
39. Need per-platform style templates editable in UI?
40. Should we generate one-click clipboard blocks or downloadable files?

## Infrastructure and Ops
41. Deployment target for V1: local-only app, or local + remote backup?
42. DB choice confirmed as Postgres only, or SQLite fallback for portability?
43. Do you want Docker-first development or native local runtime first?
44. Should scheduler run inside API process, separate worker, or external cron?
45. Any requirement for incremental backups/snapshots of DB and outputs?

## Evaluation and Quality
46. What is your minimum acceptable extraction precision before weekly use?
47. Do you want a manual QA checklist embedded in UI before export?
48. Should we track model drift across weeks (same prompt, different behavior)?
49. Need benchmark set of 10-20 known papers for regression testing?
50. Which metric matters most initially: time saved, output quality, or insight novelty?

## Security and Privacy
51. Any sensitive documents beyond public papers expected in V1?
52. Should local filesystem paths and logs be redacted in exported outputs?
53. Do you want at-rest encryption for DB in V1 or defer?

## Roadmap Prioritization
54. Which three V1 features are absolutely non-negotiable?
55. Which three items can be explicitly deferred to V1.1?
56. Should we optimize first for robust backend correctness or review UX speed?
57. Target date for first real weekly run?
