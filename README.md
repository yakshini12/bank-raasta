# Bank Raasta

Bank Raasta is a voice-first guide for people who have a problem with a bank, loan, card, or digital payment and need to work out the next official step. It helps the user record what happened, keep the complaint dates together, and see the RBI escalation route that applies to the information they entered.

## Why this is a real problem

The Reserve Bank reported 13.34 lakh complaints received in FY 2024–25 across its grievance processing system. Its Ombudsman offices received 2.96 lakh complaints; loans, credit cards, mobile/electronic banking, and deposit accounts made up around four-fifths of those cases. RBI also says that a customer generally needs to approach the regulated entity first, and that a case may go to the Ombudsman after an unsatisfactory response or no response within the applicable time. The current scheme took effect on 1 July 2026.

Existing bank apps and RBI’s CMS portal handle complaints. Bank Raasta is a consumer-side case organizer and guide; it does not replace those channels or file a case for the user.

## Run locally

Requires Node.js 20 or later.

```powershell
Copy-Item .env.example .env
notepad .env
npm start
```

Open <http://127.0.0.1:3003>. The sample works without an API key. Add your Gnani API key to the local `.env` file to enable Prisma transcription and Timbre read-aloud. Do not paste the key into chat or commit `.env`.

## Gnani integration

- Prisma transcription: `POST https://api.vachana.ai/stt/v3`
- Timbre synthesis: `POST https://api.vachana.ai/api/v1/tts/inference`
- The browser calls the local Node server. The server keeps `GNANI_API_KEY` private.
- The voice transcript is shown for the user to review; it never decides eligibility or fills complaint dates automatically.

## Current prototype boundary

- Speech input language selector for Gnani Prisma: Bengali, English, Gujarati, Hindi, Kannada, Malayalam, Marathi, Punjabi, Tamil, and Telugu
- Hindi and English complaint guidance, summaries, and read-aloud; Gnani speech APIs do not translate the guidance text
- Four broad banking issue categories
- Deterministic next-step check from the user’s complaint date and reply status
- Local-only case timeline and a copyable complaint summary
- Links to RBI’s official CMS and contact center
- No account access, payment credentials, OTP/PIN collection, complaint submission, or outcome guarantee
- This is general process guidance, not legal or financial advice. The user should confirm the applicable rules with RBI or their regulated entity.

## Sources

- [RBI Annual Report on the Integrated Ombudsman Scheme, FY 2024–25](https://www.rbi.org.in/scripts/PublicationsView.aspx?id=23441)
- [RBI Integrated Ombudsman Scheme 2026 FAQs](https://www.rbi.org.in/commonperson/english/scripts/FAQs.aspx?Id=3407)
- [RBI Contact Center and complaint management information](https://www.rbi.org.in/commonman/English/Scripts/SMSCMS.aspx/RBICMS.aspx)
- [Gnani Prisma speech-to-text documentation](https://docs.gnani.ai/api/STT/speech-to-text)
- [Gnani Timbre text-to-speech documentation](https://docs.gnani.ai/api/TTS/tts-inference)

## Demo video

The narrated demo film and its script live in [`submission/`](submission/README.md):
`Bank-Raasta-demo.mp4` is the final narrated cut (2:13, 1920×1080); `demo-video-script.md`
explains scene by scene what is real (working-prototype screens, stock photography)
and what is illustrative (drawn sample screens).

The film is re-generable from this repository:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install -r submission\requirements-video.txt
# the opening/walkthrough footage uses Pexels stock; fetch it once:
# https://www.pexels.com/video/local-market-in-india-12544665/ -> save as submission/assets/market-video.mp4
cd submission
..\.venv\Scripts\python -X utf8 render_final_cut.py    # silent visual cut
..\.venv\Scripts\python -X utf8 create_dialogue_track.py  # adds the English-India narration
```

Stock media credits are listed in `demo-video-script.md`.
