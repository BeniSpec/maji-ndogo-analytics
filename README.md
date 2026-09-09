<!--
DRAFT — read every line before this goes public.
Headline: Scale (code priced for a million records)
Reader: engineering lead
Anything that doesn't sound like you: cut it or rewrite it in your own words.
Delete this comment block when you're done.
-->

# Pricing the Maji Ndogo Field Registry for a Million Records

## The Business Problem

The Maji Ndogo farm survey currently holds 5,654 field records, stored as
plain dictionaries in submission order — no index, no sort, no structure
enforcing what a valid record even looks like. That's tolerable at 5,654
rows. It stops being tolerable as the survey grows toward a million.

Two failure modes compound at scale. First, an unsorted, unindexed list
means every lookup — "what's the yield on Field 39924?" — is a linear scan:
`O(n)`. At 5,654 records that's unnoticeable. At a million, it's the
difference between an inspector getting a reading over the radio and
missing her window. Second, a dictionary enforces nothing: there's nothing
stopping `Pollution_level` from being set to `7000` on a 0–1 scale, and a
corrupted value like that doesn't crash anything — it just silently drags
down every average it touches downstream.

This project rebuilds the registry against both failure modes: an auditing
engine with search and sort algorithms chosen for their scaling behavior,
and a class hierarchy where invalid data is rejected at the point of entry
instead of discovered later, after it's already polluted an analysis.

## The Tech Stack

- **Algorithms & Big O** — the core of the scale argument. Linear search
  (`O(n)`) versus binary search (`O(log n)`) on the Field Registry, and
  recursive merge sort (`O(n log n)`) versus the naive `O(n²)` alternative
  for ranking the harvest.
- **Object-Oriented Programming** — a `Field` base class with a validated
  `pollution_level` property, crop-specific subclasses (`TeaField`,
  `CoffeeField`, `WheatField`) via inheritance and polymorphism, an
  `AbstractCropField` base that makes an unimplemented crop type impossible
  to instantiate, and a `FieldRegistry` that aggregates across the full
  survey.
- **Data Validation** — the `pollution_level` setter raises
  `ValueError('Pollution level must be between 0 and 1.')` outside `[0, 1]`,
  so bad sensor data fails loudly at the boundary instead of quietly
  corrupting a mean.
- **Python** — implementation throughout.
- **Pandas / SQL / SQLite** — used downstream once the registry is
  structured, to load, filter, and aggregate the survey for the final
  crop recommendation.

## The Deliverable

### 1. Searching and Scale
![Linear vs binary search](images/01-search-scale.png)
`linear_search_field` scans up to all 5,654 records in the worst case —
`O(n)`. `binary_search_yield`, run against the same data pre-sorted by
`Field_ID`, needs roughly 13 comparisons at this scale and about 20 at a
million records, `O(log n)`. The cost is real — the data has to be sorted
first — which is exactly what the next stage buys.

### 2. Object-Oriented Validation
![Field class validation](images/02-oop-validation.png)
The `Field` class backs `pollution_level` with a `@property`. Passing
`7000` on a 0–1 scale doesn't get stored — it raises
`ValueError('Pollution level must be between 0 and 1.')` at construction
time, before the value can reach an aggregate.

### 3. Sorting and Processing
![Merge sort implementation](images/03-sorting.png)
`merge_sort_yields` recursively splits the field list and merges sorted
halves back together — `O(n log n)`. The naive alternative, bubble sort,
is `O(n²)`: doubling the record count would quadruple its work instead of
roughly doubling merge sort's.

### 4. Data Analysis
![Groupby and filter operations](images/04-data-analysis.png)
With the registry structured, Pandas takes over: grouping by `Soil_type`
and `Crop_type` to compare fertility and climate averages across all
5,654 records in a handful of lines.

### 5. Agricultural Recommendation
![Tea recommendation trace](images/05-recommendation.png)
Filtering to fields where `Crop_type == 'tea'`, `Standard_yield` is above
tea's own group mean, `Ave_temps` falls between 12–15°C, and
`Pollution_level` is below `0.0001` narrows the full survey down to
**14 fields** — the traceable basis for recommending tea in the northern
highlands, not an opinion.

### 6. Git Workflow
![Commit history](images/06-git-log.png)
The commit log shows the `.gitignore`, evidence, and case study shipped
as separate, scoped commits rather than one dump — the same incremental
discipline the rest of this project argues for.

## So What?

A linear scan and an unvalidated dictionary both work fine at 5,654
records and both become liabilities as Maji Ndogo's survey grows toward a
million — one silently gets slower, the other silently gets wrong. Binary
search over a sorted registry turns that lookup from a potential
million-record scan into ~20 comparisons, and a validating `Field` class
turns a `7000` pollution reading from a silent corruption into a
`ValueError` at the door. Neither fix changes today's answer — tea, in
the northern highlands, traced through 14 qualifying fields — but both
are what keep that answer trustworthy once the dataset outgrows what
anyone can eyeball.
