# BRIDGE Measurements: design notes

*BER hackathon, 2026-09-30. Companion to [`bridge_measurements.yaml`](bridge_measurements.yaml)
(validated with `linkml lint` / `gen-pydantic`; example instances in
[`examples/`](examples/) validate with `linkml validate`).*

## The problem

The harmonization-targets matrix shows three incompatible ways BER schemas say
"we measured X on Y and got Z":

| Pattern | Who | Property identity | Value | Weakness for a union |
|---|---|---|---|---|
| **Slot-per-property** | NMDC (166 MIxS `QuantityValue` slots, 139 `TextValue` slots on Biosample) | the slot name / `slot_uri` (MIxS CURIE) | inlined `AttributeValue` objects (`has_numeric_value`, `has_unit`) | new property = schema change; property is not queryable as data |
| **Column-per-analyte** | BASALT (~30 wide `*Product` tables) | the column name (`total_carbon_id`, `sand_pct_id`, `respiration_co2_c_ug_per_g`) | mixed: `QuantityValue` refs, bare doubles with units in the column name | no property vocabulary at all, no unit field for many columns |
| **Row-per-observation** (OGC O&M) | BASIN-3D (`MeasurementTimeseriesTVPObservation`) | data: `observed_property` → a 166-term synthesis vocabulary | `TimeValuePair` series + `unit_of_measurement` | vocabulary is basin3d-local; single (non-series) measurement class never materialized |

The harmonization row for Measurement/observation itself says it: *"No shared
slot names across families — harmonize against O&M/SOSA semantics rather than
slot spellings."*

## The union model

**Only the row-per-observation shape can host the other two.** A slot-per-property
record trivially unpivots into rows (one per populated MIxS slot); a wide product
table unpivots into rows (one per analyte column); an O&M observation already is
a row. The reverse projections are impossible without schema-per-source. So the
BRIDGE `Measurement` class is O&M/SOSA-shaped:

```
Measurement
  observed_property  → ObservedProperty (BERVO-first vocabulary)   "what"
  feature_of_interest + type + position                            "of what"
  result             → polymorphic MeasurementValue                "the value"
  phenomenon_time / result_time                                    "when"
  statistic / aggregation_duration / replicate_role                "as summarized how"
  quality_status / quality_flags                                   "how trustworthy"
  method / instrument / was_generated_by / part_of_collection      "how produced"
  datasource + *_source_* slots                                    "round-trip provenance"
```

Every source-facing controlled slot has a verbatim-source companion
(`observed_property_source_term`, `source_quality_label`, `raw_value`) so the
union is lossless: you can always recover what the source actually said. This
is BASIN-3D's `MappedAttribute` lesson (keep source and synthesis terms side by
side), flattened into paired slots plus an external `SourceTermMapping`
crosswalk table instead of a nested object per slot — friendlier to Parquet/
lakehouse layouts.

### Precedents deliberately reused

- **NMDC `PropertyAssertion`** is NMDC's own property-as-data class (used only
  by `misc_param`, aligned with BERtron's properties pattern). `Measurement`
  is declared `close_mappings: nmdc:PropertyAssertion`, and its slots carry
  `exact_mappings` to `nmdc:has_attribute_id`, `nmdc:has_numeric_value`, etc.
- **BASIN-3D enums** are adopted nearly verbatim: `StatisticEnum`,
  `ResultQualityStatusEnum` (with basin3d's documented synonym sets in the
  descriptions), `SamplingMediumEnum`, `AggregationDurationEnum`,
  `TimeReferencePositionEnum`, and the `TimeValuePair` result.
- **BASALT QC and replicate semantics**: `QualityFlagEnum` is
  `ProcessedDataFlag` + plate-well flags; `replicate_role`/`replicate_number`/
  `summary_of` capture Single/Replicate/Average including the average→members
  link BASALT keeps as `_avg` columns; `feature_position` captures
  `core_section` and well position; `MeasurementCollection` is the product/run
  (shared method, instrument, activity, data file, `summary_metrics`).
- **Two-level quality** on purpose: coarse `quality_status`
  (validated/unvalidated/suspect/rejected/estimated — the search facet) and
  fine `quality_flags` (below-detection, outlier, blank... — the analytics
  detail). Sources populate one, the other, or both.

## Enumerations vs permissible values vs subclassing

The rule proposed here: **closed enums for process/QC dimensions, an open
vocabulary class for the observed property, and subclasses only for result
structure.**

1. **Closed enums** (statistic, quality, medium, aggregation, replicate role):
   small, stable, cross-domain value spaces. Source codes map in via
   `SourceTermMapping`; each enum keeps an `OTHER`/`NOT_APPLICABLE` escape.
2. **Open vocabulary** for `observed_property`: thousands of properties,
   growing per campaign — an enum would relive NMDC's 166-slot problem inside
   an enum. Instead `ObservedProperty` is a first-class descriptor
   (id, label, categories, `measurement_of`, `measured_in`, `canonical_unit`,
   `value_type`) that is **exactly the shape of a BERVO Variable term**
   (`bervo:BERVO_measurement_of`, `measured_in`, `has_unit`,
   `has_value_type` pre-coordinations). BERVO term exists → use its CURIE;
   BERVO term missing → mint a descriptor with the same slots and treat it as
   a BERVO candidate. BERVO adoption becomes an id swap, not a remodel.
3. **Subclassing**: only structural — `TimeSeriesMeasurement` pins
   `result: TimeSeriesValue`. Domain subclasses ("RespirationMeasurement",
   "PHMeasurement"…) are discouraged: BASALT's 30 product classes and NMDC's
   166 slots are both cautionary tales of encoding the property in the schema.
   If a portal wants typed views (as geochem-demo's `RadonObservation` does),
   define them as profiles/views that constrain `observed_property`, not as
   the storage model.
4. **Value polymorphism** replaces the has_*/plain naming schism
   (harmonization row 17, "strongest centralization target"):
   `MeasurementValue` → `QuantityValue | ControlledTermValue | TextValue |
   BooleanValue | TimestampValue | TimeSeriesValue`, plain slot names
   (`numeric_value`, `unit`) with `exact_mappings` to the NMDC `has_*` family,
   NMDC's `type`-designator convention for polymorphic documents, and
   `raw_value` everywhere. Units: UCUM strings now; seed a future shared
   `UnitEnum` from NMDC's 109-code UCUM enum.

## Projection recipes

- **NMDC**: for each populated measurement slot on Biosample →
  one `Measurement`: `observed_property_source_term` = the slot's `slot_uri`,
  `observed_property` via the crosswalk, `feature_of_interest` = biosample id,
  result copied field-for-field (`has_numeric_value`→`numeric_value`…).
  `ControlledTermValue` slots (`env_medium`…) land as term results. NMDC's
  flattener (`nmdc-lakehouse-schema`) already emits per-slot columns; the same
  transform targets rows instead.
- **BASALT**: each `*Product` row → one `MeasurementCollection` + one
  `Measurement` per analyte column. Column name → `observed_property_source_term`;
  unit comes from the linked `QuantityValue.has_unit` or is parsed from the
  column-name suffix (`_ug_per_g`, `_mg_per_kg`) — recorded in
  `SourceTermMapping.unit` once, not re-parsed per row. `flag_<analyte>` →
  `quality_flags`; `measure_type`/`replicate` → `replicate_role`/
  `replicate_number`; `<x>_avg` columns become AVERAGE rows with `summary_of`
  pointing at the replicate rows. `WellReading` → a Measurement with
  `feature_position` = well, its parent `PlateProduct` = the collection.
- **BASIN-3D / USGS / AmeriFlux**: `MeasurementTimeseriesTVPObservation` →
  `TimeSeriesMeasurement` almost 1:1; a compound mapping row (USGS `00010` →
  water-temperature + WATER) fills `observed_property` and `sampling_medium`
  from one source code, exactly as basin3d's `:`-compound mappings do.

## Open questions for the group

1. **BERVO scope**: BERVO today is EcoSIM-simulation-variable heavy. Do we
   grow BERVO to cover lab analytes (total C, ions, enzymes) and phenotyping
   traits, or federate (BERVO + MIxS + TO/PATO) under `ObservedProperty.mappings`?
2. **Naming family**: this draft uses plain value-slot names with mappings to
   NMDC `has_*`. If NMDC/BASALT ingest friction matters more than
   lambda/BERtron/CDM alignment, flip it — the crosswalk is symmetric.
3. **Identity/granularity**: is a `Measurement` row id-worthy
   (`{datasource}:{record}:{term}` deterministic ids proposed), and do we
   materialize replicate-level rows or only averages for the search index?
4. **Feature of interest**: this module keeps `feature_of_interest` as a
   loose `uriorcurie` + type enum. It should eventually range over the
   central BRIDGE FeatureOfInterest role class (harmonization row 3), which is
   its own hackathon-sized design.
5. **Timeseries storage**: inline `TimeValuePair` lists work for exchange, but
   lakehouse storage likely wants the points in a long table keyed by
   measurement id — same schema, different physical layout.
6. **Where it lives**: drop this module into `bridge-central-schema`
   (`ber_central_schema.yaml` is currently a template stub) as its first
   real content?
