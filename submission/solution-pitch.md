# Bank Raasta
### A voice-first guide to the next step in a bank complaint

People often know that a UPI payment failed, a card was charged unexpectedly, or a bank has not replied to a complaint, but may not know what to document or which official route to check next. Bank Raasta helps a customer organize the incident and understand a possible next step without logging into a bank account or filing anything on the customer’s behalf.

The customer selects the issue, describes what happened, records relevant dates and the bank’s response, and chooses a preferred language. With a Gnani API key configured, **Gnani Prisma** transcribes an uploaded voice note in one of its supported Indian languages. The customer reviews the transcript before using it. A transparent, date-and-status rule flow then displays a checklist, a plain-language summary, and links to RBI’s official complaint resources. **Gnani Timbre** can read the Hindi or English guidance aloud.

Bank Raasta is designed for common digital-payment and banking problems, including UPI disputes, card charges, loan or EMI concerns, and account services. It keeps notes in the customer’s browser and avoids collecting PINs, OTPs, passwords, or full account numbers. AI supports accessible speech input and output; it does not decide complaint eligibility or invent a resolution. The prototype explains that timelines and eligibility can depend on the institution and applicable rules, and directs customers to verify details with official sources.

**Technology:** Gnani Prisma speech-to-text, Gnani Timbre text-to-speech, Node.js API server, browser-based interface, deterministic complaint-stage guidance.

**Prototype boundary:** Bank Raasta is an independent consumer guide, not affiliated with RBI or a bank. It does not submit complaints, guarantee an outcome, or replace official channels.
