# Frontier Pulse QA Checklist

## Pre-export gates
- [ ] Generated claims include inline citations/provenance.
- [ ] Contradictions include confidence score and linked sources.
- [ ] Output quality meets minimum precision target (0.70+) on benchmark sample.
- [ ] No absolute local filesystem paths in export content.
- [ ] Twitter export is classic thread format.
- [ ] LinkedIn export tone is founder-voice.
- [ ] Export mode is one-click clipboard.

## Weekly validation
- [ ] Ingestion includes revised older papers.
- [ ] Dedupe executed with fuzzy title+abstract strategy.
- [ ] Backup snapshot created and retention policy respected (7 days).
