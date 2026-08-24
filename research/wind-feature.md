# Wind on high-risk days — feature spec

## The core idea

Average wind is worse than useless for wildfire. In coastal Los Angeles the average
wind is the onshore sea breeze from the west. The wind that burned Pacific Palisades
and Altadena was Santa Ana — offshore, from the northeast. An average-wind arrow
points roughly 180 degrees away from the danger.

So: filter to the days that actually matter, then look at direction on those days only.

**Dangerous day definition** (Red Flag-like, both conditions together):
- wind speed >= ~25 mph sustained, AND
- minimum relative humidity <= 15%

Dryness is what makes wind dangerous. A windy damp day is not a fire day.

## THE TRAP: direction is circular

350 degrees and 10 degrees are both essentially north, but their arithmetic mean is
180 degrees — due south, exactly backwards. Directions MUST be averaged as vectors:
convert each to a unit vector, sum, convert back. Nothing looks broken if you skip
this; you just get confidently wrong arrows.

## The six statistics to show a homeowner

1. **Which direction the dangerous wind comes from.** One compass word. Nothing else
   on this list matters without it.

2. **What share of dangerous days come from that direction.** The honesty check.
   80% from one sector is a real pattern worth acting on. 25% means wind is scattered
   there and they should NOT prioritise one side of the house. Same data, opposite
   advice — most products never tell you which case you are in.

3. **How many dangerous days per year, and which months.** Makes it concrete, and the
   months tell them when the work needs to be finished by.

4. **What sits upwind of them.** THE differentiator, and it uses data we already have.
   Look ~500 m upwind in the dangerous direction: open wildland, or 180 houses?
   Wildland upwind = flame front and burning brush.
   Dense housing upwind = burning houses throwing embers, which is what destroyed
   Altadena per NIST/FEMA.
   Same wind, different threat, different priorities.
   This is also what makes a 4 km regional dataset feel personal: the wind arrow is
   identical for the whole neighbourhood, but what is upwind of THIS house is not.

5. **Whether they are uphill of the dangerous direction.** Fire runs much faster
   uphill. We already have the terrain. Wind from the northeast + ground rising toward
   the house from the northeast = the bad combination. A single yes/no that carries
   real meaning.

6. **Which side of the house to do first.** The translation into an instruction:
   "if you can only afford part of it, start with your northeast wall and that yard."

## Deliberately excluded

- **Average wind speed** — describes ordinary days, which is when houses do not burn.
- **A wind risk score** — CAL FIRE hazard zones already account for wind. Adding our
  own number double-counts it and invents a rating we cannot defend.
- **Peak gust numbers** — "gusts to 95 mph" is frightening and not actionable.

## Honesty framing

gridMET cells are 4 km across, so every house in a neighbourhood gets identical wind
figures. Label it "wind pattern for your area", never "for your property". The
property-specific insight comes from combining regional wind with what is upwind,
which way their ground slopes, and which wall faces the danger.

## Data

- **gridMET** (UC Merced), 4 km, 1979-present, free, no key.
  Variables: `vs` wind speed (m/s, 10 m), `th` wind direction (deg from north),
  `rmin` minimum relative humidity (%).
  Grid: 1386 lon x 585 lat, daily, UInt16. CONUS year = ~594 MB uncompressed,
  ~150-300 MB stored. California is ~7% of that.
  OPeNDAP allows server-side subsetting so the national file is never downloaded.
- **Derived product**: dominant fire-weather direction + speed per cell.
  56,523 California cells -> ~0.45 MB for the entire state.
- **WindNinja** (USFS Missoula Fire Sciences Lab), free/open source, ~100 m terrain
  downscaling. Generates rather than downloads. Use only where terrain matters;
  on flat ground it adds nothing.
