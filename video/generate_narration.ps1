# Regenerates the scratch narration WAVs (Microsoft Zira, natural rate).
# Text matches video/FINAL_VIDEO_SCRIPT.md with phonetic tweaks (Diya -> "Deeya",
# ULIP -> "you-lip", romanized Hindi) and personas aligned to the actual footage.
Add-Type -AssemblyName System.Speech
$dir = "E:\sbi hack\video\narration"
New-Item -ItemType Directory -Force $dir | Out-Null

$scenes = @(
  "YONO has eighty-five million users, but most only ever touch UPI. The deeper features go undiscovered, because the channel that sells them is distrusted: over twelve thousand mis-selling complaints in one year. Deeya is an agentic copilot that fixes the trust, not just the funnel: a fully autonomous perceive, reason, act, learn loop over a user's own consented transactions.",
  "Rahul pays twelve hundred forty rupees a month to a competitor insurer. Before Deeya even analyses that, it asks permission, in Hindi: Kya main aapka len-den dekh sakti hoon? He agrees, and gets an honest comparison, including the row where the competitor wins, and a Do Nothing column showing what staying put costs. Every number is grounded in a cited corpus; a human advisor is always one tap away.",
  "Then Deeya does something no bank app has done. For Shanti Devi, a retired pensioner, it flags a you-lip she already owns, sold to her years ago, as unsuitable, and lays out an honest exit versus stay path: surrender charges, what she keeps, what she loses either way. Deeya doesn't just refuse to mis-sell. It un-sells.",
  "Tap Why am I seeing this, and there's a second A.I. in the room: a devil's advocate agent that argued against this recommendation before you ever saw it. Its objections are printed on the card, and when they're strong enough, the nudge is suppressed entirely. Deeya has to win a debate before it's allowed to speak.",
  "For the Idle Saver, forty-seven thousand rupees sitting idle becomes a guided sweep F.D. journey, in the user's language, read aloud for low-literacy users. But notice the meter: Deeya has used two of its four interruptions this month. When the budget runs out, it stays silent. Restraint you can see, not just a promise.",
  "For elderly users, Deeya adds a Sahayak. When Shanti Devi proceeds with a thirty-thousand-rupee step, nothing moves until her son co-approves on his own phone. Maa ke liye, saath mein: for mother, together. Mis-selling to pensioners is where trust broke; this is where it's rebuilt.",
  "And every decision: nudge, suppression, objection, co-approval, lands in a hash-chained audit trail. Mission Control's Compliance tab replays any recommendation exactly as a regulator would see it. Tamper with one entry, and the chain breaks visibly.",
  "The business case: YONO earns about one hundred crore rupees a quarter distributing these products. Deeya lifts that, and removes the mis-selling risk SBI is under regulatory pressure to fix. This is mis-selling remediation disguised as an adoption engine: the sale moves from a coercive human channel to a transparent, consented, suitability-filtered digital one.",
  "One agent loop, a hundred-plus YONO journeys, white-label to any bank, live right now. Honesty is the moat. That's Deeya."
)

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $synth.SelectVoice('Microsoft Zira Desktop') } catch { Write-Host "Zira unavailable, using default: $($synth.Voice.Name)" }
$synth.Rate = 0

for ($i = 0; $i -lt $scenes.Count; $i++) {
  $n = '{0:d2}' -f ($i + 1)
  $path = Join-Path $dir "scene$n.wav"
  $synth.SetOutputToWaveFile($path)
  $synth.Speak($scenes[$i])
}
$synth.SetOutputToNull()
$synth.Dispose()

Get-ChildItem $dir | ForEach-Object { "{0}  {1:n0} bytes" -f $_.Name, $_.Length }
