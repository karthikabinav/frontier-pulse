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

I dont know much about this. The other option is to use openRouter or other free tiers. Let's do some research on this first.

17. Which exact extraction model should be default on your machine?

See the answer to question above.

18. Do you want a second “synthesis model” separate from extraction model?

Let us try to use a free good model and use it for everything, atleast for v1. Just add the flexibility to change these models later.

19. Is optional cloud fallback acceptable in V1, or local-only hard requirement?

See the answers above. Let's research and go with the best judgement you have

20. Max acceptable runtime per weekly batch on your hardware?

Same as above. If we are running API, we can use budget hard caps.

21. Do you want deterministic outputs (temperature near 0) for alpha cards?

No, I want good quality. Determinism is not a requirement


## Embeddings and Retrieval
22. Which embedding model should be default (`nomic-embed-text`, `bge-large`, etc.)?

Use your best judgement and take a call

23. Should embeddings be generated for full paper, section chunks, or both?

This depends on how we use it. Since we are retrieving alpha, not sure why emebeddings matter. But use your best judgement


24. Must vector search support metadata filters (date/source/cluster) in V1?

Use your best judgement


## Schema and Domain Model
25. Should `PaperAlphaCard` be immutable snapshots or editable with history?

Yea, we need strong versioning. Otherwise there wont be structure


26. For `novelty_score`, use numeric 0–100 or ordinal buckets?

Ordinal buckets are better

27. Should `strength_score` for hypotheses be model-only or model + human override?

Model-only as default. But a human can override. Eventually the goal is to have a good enough corpus to build the AI researcher


28. Should contradictions be explicit edges with confidence score?

Yes please/


29. Do you need provenance per field (which chunk/passage justified it)?


Yeah, citation are important. We need to be able to trace back, just like a researcher.

## Human-in-the-Loop UX
30. Do you want login/auth skipped entirely for local V1?

Yes, for v1 no need any of these.

31. Are merge/split cluster operations mandatory for V1 or okay as V1.1?

Use your best judgement

32. For hypothesis table, should user rating be binary, 1-5, or weighted confidence?

Binary is better for this.


33. Should we include inline citations/snippets beside each generated claim?

yes citation are important.

34. Rich text editor preference: Markdown textarea or WYSIWYG?

Either is fine. Use your best judgement


35. Any required hotkeys (approve/reject/edit-next) for rapid review?

Yeah, hotkeys to make it faster


## Exports and Publishing
36. For Twitter output, target X long posts or strict classic tweet thread constraints?

Export to twitter with classic tweet thread.


37. For LinkedIn output, preferred tone: analytical, conversational, or founder-voice?

Founder voice


38. Should export include optional visual assets (graph image) by default?

For V1, let it be text only.

39. Need per-platform style templates editable in UI?

For v1, let them be same. But allow for optionality in the future

40. Should we generate one-click clipboard blocks or downloadable files?

One click clipboard


## Infrastructure and Ops
41. Deployment target for V1: local-only app, or local + remote backup?

Local only app. In the future we will host on a web, may be. HOwever, I want to push the code to github.


42. DB choice confirmed as Postgres only, or SQLite fallback for portability?

Use your best judgement

43. Do you want Docker-first development or native local runtime first?

Use your judgement. But native local seems the right choice?

44. Should scheduler run inside API process, separate worker, or external cron?

Use your best judgement

45. Any requirement for incremental backups/snapshots of DB and outputs?

Yeah, always keep last 7 days backup of the db, so if the code is screwed up, we can roll back safely


## Evaluation and Quality
46. What is your minimum acceptable extraction precision before weekly use?

I will take a look at back testing the last few days. And then if its say > 0.7 precision, we can start to roll it out. Roll out in the beginning will just be a seperate X and linkedIn acocunt for this project, and then start posting on it. In parallel, I will also post the long-form blog post on **how** this is built, which you are also helping me with this project.


47. Do you want a manual QA checklist embedded in UI before export?

Sure, if its helpful

48. Should we track model drift across weeks (same prompt, different behavior)?

No seems overkill

49. Need benchmark set of 10-20 known papers for regression testing?

Good point. In the initial test, we can build this, and then use this as regression test.

50. Which metric matters most initially: time saved, output quality, or insight novelty?

Output quality > insight novelty 



## Security and Privacy
51. Any sensitive documents beyond public papers expected in V1?

No, nothing sensitive

52. Should local filesystem paths and logs be redacted in exported outputs?

Yeah, make it relative paths.

53. Do you want at-rest encryption for DB in V1 or defer?

Use your best judgement



## Roadmap Prioritization
54. Which three V1 features are absolutely non-negotiable?

Ability to scour Arxiv papers, coming from authors in frontier labs and having a unique insight. HOwever, I have trimmed down to the best possible. Note we are building a grand ambition of **open** AI researcher, and this is the first step in cataloging and understanding what are the questions that matter. We can think of the AI researcher we are building learning to do lit survey.


55. Which three items can be explicitly deferred to V1.1?

Use your judgement

56. Should we optimize first for robust backend correctness or review UX speed?

BAckend correctness > review UX speed


57. Target date for first real weekly run?

I want to start it Monday morning. So this is the weekend project.


