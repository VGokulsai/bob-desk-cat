# Funding estimate

Checked live on 10 Nov 2026. Prices change, so check again before ordering.
Exchange rate: 1 USD = Rs 93.93 (open.er-api.com, 10 Nov 2026 00:02 UTC).

## What Fallen's docs say

Source: fallen.hackclub.com/docs/project-funding (the page text is inside the
site's JS bundle, read on 10 Nov 2026).

- The money request lives in `bom.csv`: "please only request the funding amount
  you need (in your bom.csv)".
- Funding is a grant card from HCB that "counts as a credit card", usable online.
- Amount is "based on the project's quality, polish, and complexity", not on
  hours or XP.
- Include: "the minimum amount of each component", "the cheapest manufacturing
  options" (HASL, not ENIG).
- Do not include: "Extra parts!", overly expensive tools, "Modules/kits for parts
  you're supposed to design", e.g. an ESP32 devboard.
- The submitting page asks for "a link to each item (even if you already own the
  item - mention it!)".

**The docs do not name** required columns, a currency, a per-project cap, or any
rule about shipping, tax, customs, LCSC or JLCPCB. Nothing found is not the same
as no rule: ask in #fallen if it matters.

## Per-part check

Robu prices are from each product page's own data (Robu blocks plain fetches;
read through a real browser). LCSC prices come from LCSC's product API at the
quantity actually bought (LCSC minimum order applied).

### Robu (India)

| Part | Qty | Unit Rs | Total Rs | Stock |
|---|---|---|---|---|
| ESP32-S3-WROOM-1-N8R8 | 1 | 409 | 409 | in stock |
| GC9A01 round TFT | 1 | 449 | 449 | in stock |
| SG90 servo, Good Quality | 3 | 185 | 555 | in stock (Rs 89 Standard is also back in stock) |
| GSPK3005TN speaker | 1 | 91 | 91 | in stock |
| AP2114H-3.3 LDO | 1 | 35 | 35 | in stock |
| MCP6001T-I/OT op-amp | 1 | 37 | 37 | **OUT OF STOCK** |
| 6x6x5 tactile switch (10) | 1 | 19 | 19 | in stock |
| 1x40 header strip | 2 | 8 | 16 | in stock |
| 470uF 16V SMD cap | 3 | 4.87 | 14.61 | in stock |
| F-F jumper wires (40) | 1 | 49 | 49 | in stock |
| **Robu subtotal** | | | **1674.61** | matches the 4 Nov cart |

The SG90 link in `bom.csv` is a search that now returns 0 results. The product
page is robu.in/product/towerpro-sg90-9gm-1-2kg-180-degree-rotation-servo-motor-good-quality/.

MCP6001T is out of stock at Robu. LCSC has it: C116490, 44,525 in stock,
$0.3212 each, minimum 5, so $1.61 (Rs 151) instead of Rs 37.

Robu shipping was not checked.

### LCSC

| LCSC | Part | Need | Min order | Buy | Unit $ | Line $ | Stock |
|---|---|---|---|---|---|---|---|
| C165948 | TYPE-C-31-M-12 | 1 | 5 | 5 | 0.1887 | 0.94 | 276,185 |
| C113367 | PAM8302AASCR | 3 | 1 | 3 | 0.4064 | 1.22 | 20,321 |
| C20200114 | AMF-O97L45-DB mic | 1 | 5 | 5 | 0.2313 | 1.16 | **105** (low) |
| C15850 | 10uF 0805 | 5 | 20 | 20 | 0.0317 | 0.63 | 1,776,540 |
| C49678 | 100nF 0805 | 5 | 20 | 20 | 0.0207 | 0.41 | 12,737,300 |
| C28323 | 1uF 0805 | 2 | 10 | 10 | 0.0283 | 0.28 | 425,410 |
| C1710 | 10nF 0805 | 1 | 50 | 50 | 0.0099 | 0.50 | 119,800 |
| C27834 | 5.1k 0805 | 2 | 100 | 100 | 0.0055 | 0.55 | 866,000 |
| C17414 | 10k 0805 | 1 | 100 | 100 | 0.0034 | 0.34 | 37,288,900 |
| C17513 | 1k 0805 | 3 | 100 | 100 | 0.0035 | 0.35 | 33,361,100 |
| C17520 | 2.2k 0805 | 1 | 100 | 100 | 0.0050 | 0.50 | 2,285,800 |
| C149504 | 100k 0805 | 3 | 100 | 100 | 0.0060 | 0.60 | 670,100 |
| | **LCSC subtotal** | | | | | **7.49** | all 12 in stock |

The PAM8302 line buys 3 (2 spares). The docs say not to include extra parts.
That is his call.

### JLCPCB board

5 boards, 2-layer, 73 x 62.5 mm, HASL, 1.6 mm: **$2.00**, the advertised price for
5 boards up to 100 x 100 mm.

Via sizes, from jlcpcb.com/capabilities/pcb-capabilities: "0.2mm or 0.25mm hole
size with via diameter less than 0.45mm, will cost more." Bob's 0.2 mm holes sit
in 0.45 mm and 0.6 mm pads, so they are not under 0.45 mm and should not cost
extra. The order page has the final say.

## Total

| | USD | INR |
|---|---|---|
| Robu parts | 17.83 | 1674.61 |
| LCSC parts | 7.49 | 703.53 |
| JLCPCB boards | 2.00 | 187.86 |
| **Goods** | **27.32** | **2566** |
| Shipping from China, ESTIMATE | 9.50 to 28.00 | 892 to 2630 |
| Indian customs, GUESS | 0 to 11.25 | 0 to 1057 |
| **All in** | **36.82 to 66.57** | **3458 to 6252** |

Moving MCP6001 from Robu to LCSC adds about Rs 114 (Rs 151 minus Rs 37).

### Shipping (estimate, not a quote)

- JLCPCB's own price only appears at checkout. Third-party write-ups put Global
  Standard Direct Line to India at about $3 to $8 (zbotic.in, Mar 2026). One
  discount of $1.50 for 5 small boards was reported in 2025 (chiptron.eu), but
  for the EU.
- LCSC ships separately unless the orders are combined. LCSC can combine an LCSC
  order with a JLCPCB order (lcsc.com help, "Combine LCSC and JLCPCB Orders"),
  but the JLCPCB order then has to ship to LCSC's Hong Kong warehouse address,
  and shipping is recalculated.
- The range above is $1.50 + $8 at the low end and $8 + $20 at the high end.
  The $20 for a separate LCSC parcel is a guess.

### Customs (a guess)

- JLCPCB lists India's import-tax threshold as **0 USD**, and India needs KYC
  documents for clearance (jlcpcb.com/help/article/customs,-duties-and-taxes).
- A PCB maker's blog puts duty on PCBs at about 28 to 30% (10% BCD + 10% SWS on
  that + 18% IGST). Hobby reports say small parcels often clear with no duty.
- The high end above is 30% of goods-from-China plus shipping. Courier clearance
  fees (DHL lists Rs 1,100 minimum for duty processing) are not included, so the
  cheap post-based shipping is the safer choice.
