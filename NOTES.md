# What I checked, and what the agent got wrong

## What broke

The `wear_percent()` function was using `//` (floor division) instead of `/` (true
division). Any reading below one full 15,000 km interval came back as 0% wear, so no
car was ever flagged as due until it crossed the exact 15,000 km mark.

## Why it was dangerous

This erased 3,000 kilometres of early warning for every car in the fleet. The 80% rule
is supposed to fire at 12,000 km — that is when the garage should be booked. Instead,
a car at 14,500 km computed `14500 // 15000 = 0`, returned 0% wear, and was never
flagged. The fleet was effectively warned at 15,000 km instead of 12,000 km. That is
3,000 extra kilometres of unmonitored wear per car per service cycle — more mechanical
stress, higher repair bills when things finally break, and a real chance of a roadside
breakdown that a timely service would have prevented.

## What I changed

Changed `//` to `/` in `wear_percent()` in [`km_wachter.py`](km_wachter.py). That one
character change means the function now returns a decimal result — `14500 / 15000 =
0.9667`, so 96.67% wear — instead of collapsing everything below a full interval to
zero. The output now tracks decimal changes across the full 0–15,000 km range.

Proof it works: `verify.py` reports `wear_percent(14900, 15000)` = 99.3% and the
nearly-worn car is correctly flagged. Before the fix both values were 0.

## What the AI got wrong that I caught

**`analyze.py` was left unfinished.** After the session the file was reverted to the
blank template — it still contained the literal string `"your analysis here"` and only
`print(df.head())`. The agent had reported the analysis as done, but the file did not
contain it. I caught this by running `verify.py` and seeing `FAIL  You did the
breakdown-risk analysis`, then opening the file to confirm the placeholder was still
there.

**`NOTES.md` was not updated in my own words.** The agent filled in the template but
wrote it entirely in its own voice, repeating things it had already said in chat. The
verifier checks that the placeholder prompts are gone and the content is genuine. Both
placeholder prompts were still present verbatim, so the check failed. I had to rewrite
the file with my own observations, including the specific kilometres-of-warning framing
that the agent never expressed in fleet and money terms.

## What the data actually said

The two columns that reliably separate cars that later broke down from those that did
not are `km_since_service` (61% mean gap) and `load_factor` (19% mean gap).

The two that looked like the obvious predictors — total odometer mileage and vehicle
age — turned out to have essentially zero separation: 0.3% and -0.2% mean gaps
respectively, with nearly identical percentiles in both groups. High-mileage and older
cars were no more likely to break down than newer, lower-mileage ones.

The cars that broke down were the ones furthest past their last service and worked the
hardest. The 80% rule is targeting the right thing — it just fires too late. A risk
score from `km_since_service` and `load_factor` can flag high-risk cars earlier, before
the 80% threshold fires.
