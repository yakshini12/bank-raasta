# Bank Raasta demo video

**Runtime:** about 2:13 · **Format:** 1920×1080 MP4 · **Audio:** dialogue-only narration with burned-in subtitle pills in the teaser; no music or ambience noise.

**Final file:** `Bank-Raasta-demo.mp4` (narrated) · silent visual cut: `Bank-Raasta-demo-final.mp4` · dialogue text: [dialogue-script.md](dialogue-script.md)

Rendering scripts: `render_final_cut.py` builds the visual cut (teaser plates, drawn problem mocks, app screens, closing card), and `create_dialogue_track.py` places the 18 narration segments on scene beats over a full-length ambience bed.

## Structure

| Time | Beat |
|---|---|
| 0:00–0:03 | Cinematic opener: the brand mark glows over a dimmed QR-payment photograph, with a vignette and a subtitle pill. |
| 0:03–0:19 | The problem shown through pictures: a real over-the-shoulder photo of a man holding his phone (red alert rings on his screen) with a zoom callout to the drawn failed-payment screen (₹2,450 debited, no confirmation); a split-screen over the shop photo — the customer's phone ("₹2,450 debited") against the shopkeeper's phone ("₹0 received", no record); an elderly man's photo with a giant ghost "12" numeral beside the drawn complaint timeline. Subtitle pills carry each line on screen. |
| 0:19–0:26 | Scale: 13,34,244 complaints under RBI's Integrated Ombudsman Scheme in FY 2024–25 over market photography. |
| 0:26–0:30 | Bank Raasta bridge: organize the case, see the next official step, no bank login. |
| 0:30–2:04 | Working prototype walkthrough: issue intake and next-step panel, issue and language selection, case details, Gnani Prisma speech input with editable transcript review, dated rule-based next-step path, evidence checklist, summary with copy/download, device-local notes and privacy boundaries, Gnani Timbre read-aloud. |
| 2:04–2:13 | Closing card over market photography. |

## Truthful demo notes

- The teaser problem screens combine real people photography with drawn samples labelled "Sample screen"; the app walkthrough uses screenshots of the working prototype with animated transitions, not a live browser recording.
- The people in the teaser photos (a man checking his phone, an elderly man holding his phone) and the shop photo are stock imagery; the payout scene the RBI statistic sits on uses a frame from a market video.
- Gnani Prisma and Timbre endpoints are wired in the prototype, but this recording uses sample mode because no API key is configured. It does not claim to show a live transcript or live Timbre output.
- The narration is generated off-screen dialogue (Microsoft neural voices: `en-IN-NeerjaExpressiveNeural` for the guide, `en-IN-PrabhatNeural` for the customer), with per-line pitch and rate variation for a natural read. This is separate from the app's Gnani Timbre feature.
- The RBI statistic is 13,34,244 complaints received under the Reserve Bank–Integrated Ombudsman Scheme during FY 2024–25, rounded to 13.34 lakh. Source: [RBI Annual Report of Ombudsman Scheme, 2024–25](https://www.rbi.org.in/scripts/PublicationsView.aspx?id=23441).
- The case and transaction scenario are illustrative. Stock media does not depict a real complainant nor the narration's speakers.
- Stock media (Pexels license): [Indian market video by Aviraj Bhadauria](https://www.pexels.com/video/local-market-in-india-12544665/), [QR-payment photo by iMin Technology](https://www.pexels.com/photo/a-close-up-shot-of-a-person-scanning-a-qr-code-12935064/), [man using a phone in rural Odisha by Parij Photography, Pexels #8887518](https://www.pexels.com/photo/person-holding-a-mobile-phone-8887518/), [elderly man holding a smartphone by Ajay Kumar, Pexels #18083457](https://www.pexels.com/photo/elderly-man-holding-smartphone-18083457/), [shop-counter photo, Pexels](https://www.pexels.com/).
