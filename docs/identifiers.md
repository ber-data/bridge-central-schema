# Identifiers across the BRIDGE central model

This page records the state on 2026-11-04. The classes are on open pull requests rather than on `main`, and each row names its pull request. Nothing here is a decision. The last section lists the questions.

## What an id is in this schema

`core.yaml` on https://github.com/doe-bridge/bridge-central-schema/pull/16 defines one `id` slot: `identifier: true`, range `uriorcurie`, no pattern. Every class that `is_a: NamedThing` inherits it, and LinkML treats an identifier slot as required. The feature model (https://github.com/doe-bridge/bridge-central-schema/pull/5) and the measurements first pass (https://github.com/doe-bridge/bridge-central-schema/pull/9) predate that file and name their identifiers differently.

No identifier slot on the open pull requests carries a pattern. The two single-prefix patterns are on reference slots. `observed_property` on https://github.com/doe-bridge/bridge-central-schema/pull/9 has range `uriorcurie` and pattern `^bridge_property:[a-z0-9_]+$`, and the terms it points at are rows of `src/ber_central_schema/terms/bridge_property.tsv` on that branch, added by pull request with a label and a definition. The hackathon page there says a term's id does not change once merged. `taxon` on https://github.com/doe-bridge/bridge-central-schema/pull/16 has range `uriorcurie` and pattern `^NCBITaxon:\d+$`.

A follow-up pull request is planned after the measurements pull request. In words, since none of it is public yet: the `bridge_property:` terms become rows of an `ObservedProperty` table, a `Unit` table gets `bridge_unit:` ids whose local part is derived from the UCUM code, `Measurement` gets a required `id` that the loader builds from `source_system`, `source_record_id` and `source_field` plus a sequence number when a row arrives without one (the three fields alone do not tell measurements apart: at e431b4c, `Measurement-005`, a range from 0 to 30, and `Measurement-006`, a value of 10, share all three, so which discriminator to use is still open), a `SourceMapping` table gets an id built the same way from `source_system` and `source_field`, the two SSSOM mapping tables stay keyed by `subject_id`, `predicate_id` and `object_id` with no id of their own, and tests require that each table's identifier is named `id`, has range `curie`, and carries a pattern that opens with prefixes the schema declares. The rows below are the state before that work.

## Where each table's id comes from

Read from each pull request head on 2026-11-04: https://github.com/doe-bridge/bridge-central-schema/pull/5 at 15b0e06, https://github.com/doe-bridge/bridge-central-schema/pull/9 at e431b4c, https://github.com/doe-bridge/bridge-central-schema/pull/12 at bd6c14d, https://github.com/doe-bridge/bridge-central-schema/pull/16 at ced63d4 and https://github.com/doe-bridge/bridge-central-schema/pull/21 at 7359746. Examples are from `tests/data/valid/` on the same branch. An example marked placeholder is illustrative and not a source record.

| Class | Pull request | Identifier slot | Range | Id made by | Example | Pattern | Notes |
|---|---|---|---|---|---|---|---|
| `Study` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `id` | `uriorcurie` | source system | `gold:Gs0114820` | no | A real GOLD study. `nmdc:sty-11-example` is a placeholder in the shape of nmdc-schema's `Study` pattern. |
| `Site` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `id` | `uriorcurie` | source system | `ameriflux:US-Ha1` | no | No example at ced63d4. Commit 399f24d, pushed later on 2026-11-04, adds this AmeriFlux site and declares `ameriflux` in core.yaml, since AmeriFlux has no registered prefix (see the prefix table). |
| `Organism` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `id` | `uriorcurie` | source system | `gold:Go0459731` | no | A real GOLD organism. `nmdc:orgn-11-example` is a placeholder in the shape of nmdc-schema's `Organism` pattern. |
| `Sample` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `id` | `uriorcurie` | source system | `gold:Gb0239762` | no | A real GOLD biosample. `nmdc:bsm-11-example` and `nmdc:procsm-11-example` are placeholders, and both kinds sit in the one `Sample` table. |
| `MaterialProcessing` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `id` | `uriorcurie` | source system | `nmdc:extrp-11-example` (placeholder) | no | Abstract, so no example file of its own. The example is the `processing` value in `ProcessingSampleLink-nmdc-input.yaml`. |
| `ProcessingSampleLink` | https://github.com/doe-bridge/bridge-central-schema/pull/16 | none | not applicable | nobody | none | not applicable | A join row: `processing`, `sample`, `role`. No `id` and no `unique_keys`. |
| `Person` | https://github.com/doe-bridge/bridge-central-schema/pull/21 | `id` | `uriorcurie` | undecided | none | no | Inherits `id` through `Agent`. `orcid` is a separate slot with range `uriorcurie`. The branch has no example data. What `id` a person without an ORCID gets is open in https://github.com/doe-bridge/bridge-central-schema/issues/17. |
| `Organization` | https://github.com/doe-bridge/bridge-central-schema/pull/21 | `id` | `uriorcurie` | undecided | none | no | Inherits `id` through `Agent`. `ror` is a separate slot with range `uriorcurie`. No example data. |
| `CreditAssociation` | https://github.com/doe-bridge/bridge-central-schema/pull/21 | none | not applicable | nobody | none | not applicable | A join row: `applies_to_agent`, `applied_roles`, `applies_to_study`. No `id` and no `unique_keys`. The branch also shows a nested form inside `Study`. |
| `Measurement` | https://github.com/doe-bridge/bridge-central-schema/pull/9 | `measurement_id`, optional | `uriorcurie` | source system, or BRIDGE on ingest | `example:nitrate-0001` (placeholder) | no | Not an identifier slot. The slot comment says `id` was avoided because LinkML would make it required and most measurements have none. |
| `Contig` | https://github.com/doe-bridge/bridge-central-schema/pull/5 | `contig_id` | `string` | source system | `insdc:NC_001422.1` | no | Not named `id`, range is the default `string`. `nmdc:wfmgas-11-19jh9v28.1_scf_10_c1` is an NMDC contig. Neither `ber_feature_model.yaml` nor `ber_central_schema.yaml` on that branch declares `insdc`. |
| `ContigCollection` | https://github.com/doe-bridge/bridge-central-schema/pull/5 | `collection_id` | `string` | source system | `nmdc:wfmgas-11-19jh9v28.1` | no | The slot note says to use a CURIE when the identifier has one. |
| `Feature` | https://github.com/doe-bridge/bridge-central-schema/pull/5 | `feature_id` | `string` | source file, or the converter | `insdc:NC_001422.1:feature-1` | no | Unique only within one `Dataset`. The slot note says it is a file-local key, not a persistent identifier, and that authority-assigned ids go in `stable_identifiers`. |
| `Dataset` | https://github.com/doe-bridge/bridge-central-schema/pull/5 | none | not applicable | nobody | none | not applicable | A document holding contigs, collections and features. No identifier slot. |
| `Attribute` | https://github.com/doe-bridge/bridge-central-schema/pull/12 | none | not applicable | nobody | none | not applicable | Nested in the record it describes. Its note says a key is not an identifier. `attribute_cv_id` is an optional `uriorcurie` for the key. |

Two things the table shows without any decision. First, the `NamedThing` tables hold ids from more than one source in one column: `gold:` and `nmdc:` in `Study`, `Sample` and `Organism`. Second, nothing yet says which prefixes an `id` column may hold.

## Which ids BRIDGE would make and manage

Ids from a source system (`gold:`, `nmdc:`, `insdc:`) cost BRIDGE nothing to make, and the source decides whether they persist. Two kinds would be BRIDGE's own.

Curated vocabularies: the `bridge_property:` terms already on https://github.com/doe-bridge/bridge-central-schema/pull/9, and the planned `bridge_unit:` terms. A term is added by pull request, its id never changes, and its label and definition can be edited. The term is the thing the id names, so the id has to outlive any one load.

Keys built from data: the planned `Measurement` and `SourceMapping` ids. The loader builds the id from the row's own fields when the row arrives without one. Nothing has to be stored to make the id again, and a second load of the same source row builds the same id. These ids name a row in a BRIDGE table and nothing outside it.

Two colleagues have spoken to this. @mslarae13 asked in https://github.com/doe-bridge/bertron-schema/issues/37 that an attribute's id be optional but a CURIE when given, and on 2025-07-31 wrote "making the attribute ID optional means we don't need fake IDs" (https://github.com/doe-bridge/bertron-schema/issues/37#issuecomment-3140659081). Her example was `FAKE:####` for an attribute no standard defines, which in this model is a `bridge_property:` term. On 2025-08-14 she added "Make label required, make ID recommended. If your attribute is from an ontology or standard the ID should ALWAYS be provided." @dschristianson asked of `measurement_id` on https://github.com/doe-bridge/bridge-central-schema/pull/9 "why not just "id"?" (https://github.com/doe-bridge/bridge-central-schema/pull/9#discussion_r4230719718) and on 2026-10-21 wrote "We could give ESS-DIVE measurement_ids or ids (if I understand the identifier rules correctly) upon ETL but probably no guarantee that they would be stable between versions or persistent outside of the lakehouse." (https://github.com/doe-bridge/bridge-central-schema/pull/9#discussion_r4339981188)

## Prefixes

Any URL can be condensed to a CURIE by declaring a prefix for the part before the local id. The question is who vouches for the prefix. The order proposed here, open for discussion:

1. The namespace owner's own prefix, registered in a registry such as Bioregistry (https://bioregistry.io).
2. A prefix BRIDGE registers in Bioregistry for a namespace whose owner has not. Bioregistry takes requests through an issue form (`new-prefix.yml` in https://github.com/biopragmatics/bioregistry).
3. A prefix declared only in this schema.

Checked against https://bioregistry.io/api/registry/ on 2026-11-04, one prefix per row:

| Prefix | In Bioregistry | Where it appears | What it is used for |
|---|---|---|---|
| `gold` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `Study`, `Sample` and `Organism` ids |
| `nmdc` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/16 and https://github.com/doe-bridge/bridge-central-schema/pull/5 | placeholder `NamedThing` ids, and `Contig`, `ContigCollection` and `Feature` ids |
| `insdc` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/5 | `Contig` and `Feature` ids, not declared in the schema |
| `emsl.project` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/16 | an `external_identifiers` example, not declared in the schema |
| `orcid` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/21 | `orcid` slot values, no example yet |
| `ror` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/21 | `ror` slot values, no example yet |
| `ncbitaxon` | yes | https://github.com/doe-bridge/bridge-central-schema/pull/16 | `taxon` values, declared as `NCBITaxon` |
| `ameriflux` | no | https://github.com/doe-bridge/bridge-central-schema/pull/16 at 399f24d | `Site` ids, declared in core.yaml only, the third choice in the order above |
| `ameriflux.site` | no | nowhere | checked as a possible `Site` source |
| `essdive` | no | nowhere | checked as a possible measurement source |
| `ess.dive` | no | nowhere | checked as a possible measurement source |
| `bridge_property` | no | https://github.com/doe-bridge/bridge-central-schema/pull/9 | `observed_property` values |
| `ber_registry` | no | https://github.com/doe-bridge/bridge-central-schema/pull/9 | `source_system` values |
| `bfm` | no | https://github.com/doe-bridge/bridge-central-schema/pull/5 | the feature model's own namespace |
| `bridge_unit` | no | planned follow-up | `Unit` ids |
| `bridge_measurement` | no | planned follow-up | `Measurement` ids |
| `bridge_source_mapping` | no | planned follow-up | `SourceMapping` ids |

The `bridge_*` prefixes, `ber_registry` and `bfm` are the third kind. All of them expand under https://w3id.org/ber-data/, which returned 404 on 2026-11-04. https://github.com/doe-bridge/bridge-central-schema/issues/26 proposes registering that path with one redirect per prefix. One prefix per table means one redirect per table.

## Patterns

The planned follow-up gives each table BRIDGE owns a pattern that opens with one prefix, as https://github.com/doe-bridge/bridge-central-schema/pull/9 already does for `observed_property`. That works because BRIDGE is the only authority for those tables. `NamedThing`'s `id` has no pattern, and its tables hold ids from several sources. `feature_of_interest` on `Measurement` is a `uriorcurie` with no restriction at e431b4c. Its description names samples, organisms, sites or plots and streams, and a planned `feature_of_interest_type` would name one of the Sample, Organism, Site and Study tables. Four choices, none preferred here:

1. A pattern that lists the allowed prefixes, such as `^(nmdc|gold):[A-Za-z0-9._-]+$`. Every new source adds to the list.
2. A general CURIE pattern plus a test that every prefix in the data is declared. nmdc-schema's base `id` slot uses `^[a-zA-Z0-9][a-zA-Z0-9_\.]+:[a-zA-Z0-9_][a-zA-Z0-9_\-\/\.,]*$`, read from `src/schema/basic_slots.yaml` in https://github.com/microbiomedata/nmdc-schema on 2026-11-04. The pattern then says nothing about which table an id belongs to.
3. A pattern on the local part, as nmdc-schema does per class: `{id_nmdc_prefix}:sty-{id_shoulder}-{id_blade}` for `Study` and `{id_nmdc_prefix}:bsm-{id_shoulder}-{id_blade}` for `Biosample`, with `id_shoulder` set to `([0-9][a-z]{0,6}[0-9])` and `id_blade` to `([A-Za-z0-9]{1,})`. A reference slot lists the type codes it accepts, as `has_input` does with `(bsm|procsm)`. In this schema the type code would overlap a slot that says which table a reference joins to. This works only for ids BRIDGE issues. A `gold:` id has its own shape.
4. One BRIDGE prefix with a type code in the local part, as nmdc-schema does with `nmdc:` (type code, shoulder, blade: its own example is `nmdc:sty-11-076c9980`), compared with one prefix per table (`bridge_property:`, `bridge_unit:`, `bridge_measurement:`, `bridge_source_mapping:`). Four points of comparison:
    - What the id says about its table. Under one prefix per table the prefix names the table. Under one prefix with a type code the first segment of the local part names it. Both say it, in different places.
    - How many w3id paths to register. One prefix per table is one path per table: five on the open pull requests (`bridge_central_schema`, `bridge_property`, `ber_registry`, `bfm`, `battr`) and eight with the planned ones. One prefix is one path, and the redirect rule can branch on the type code.
    - How readable the curated terms are. `bridge_property:air_temperature` carries its meaning. nmdc-schema's identifier page asks that ids be opaque, and its blades are random, so a term in that form would carry its label only in the row. A type code with a readable local part is also possible and is not what nmdc-schema does.
    - What minting needs. NMDC's minter is in nmdc-runtime (https://github.com/microbiomedata/nmdc-runtime, `nmdc_runtime/minter/`, served at `/pids/mint`): it reads each class's type code from the schema's id pattern, holds the shoulder `11` for the central minting service, and generates a random blade, so it has to record what it issued. Curated terms and keys built from data need no service: a pull request or the loader makes them, and tests can check uniqueness across tables.

## A naming rule for key slots, as a proposal

The open pull requests already follow most of this rule. Writing it down would make the rest follow. Ranges below were read from each pull request head on 2026-11-04.

1. `id` is used only for a row's own primary key.
2. A foreign key is named for the thing it points to, with no `_id`: `associated_studies` (`Study`), `collected_at` (`Site`), `organism` (`Organism`), `processing` (`MaterialProcessing`) and `sample` (`Sample`) on https://github.com/doe-bridge/bridge-central-schema/pull/16, `observed_property` (`uriorcurie`, constrained to `bridge_property:`) and `feature_of_interest` (`uriorcurie`) on https://github.com/doe-bridge/bridge-central-schema/pull/9, and `member_of` (`ContigCollection`), `parent` (`Feature`) and `seqid` (`Contig` or `Feature`) on https://github.com/doe-bridge/bridge-central-schema/pull/5. The exception is a name an outside standard fixes: the planned mapping tables keep SSSOM's `subject_id`, so they can be written out as SSSOM files.
3. `_id` marks an identifier from outside, kept as data, with no table here to join to: `attribute_cv_id` (`uriorcurie`, https://github.com/doe-bridge/bridge-central-schema/pull/12), `target_id` (`string`, https://github.com/doe-bridge/bridge-central-schema/pull/5), `source_record_id` (`string`) and the source's own measurement identifier `measurement_id` (`uriorcurie`), both on https://github.com/doe-bridge/bridge-central-schema/pull/9. In the planned mapping tables `object_id` is the other vocabulary's term and `predicate_id` is an enum value, not a key.

Under this rule the feature model's `contig_id`, `collection_id` and `feature_id` would become `id`. That rename waits on a rule for making a CURIE for a feature, since `feature_id` today is unique only within one `Dataset`.

## Open questions

1. Do ids the loader builds from a row's own fields, as planned for `Measurement` and `SourceMapping`, count as the "fake IDs" @mslarae13 described, or does a key that any loader can rebuild stand apart from an invented one?
2. Is an id built from source fields stable enough to be `Measurement`'s primary key, given what @dschristianson said about ESS-DIVE ids between versions, or should the optional `measurement_id` with a generated row id stay?
3. For the tables that hold ids from several sources, which of the four pattern choices above should the `id` slot carry?
4. Should BRIDGE use one prefix with a type code, or one prefix per table, for the ids it makes itself?
5. What `id` does a `Person` without an ORCID, or an `Organization` without a ROR, get?
6. Should `ProcessingSampleLink` and `CreditAssociation` declare a unique key, get an id, or stay as they are?
7. Should the schema declare `insdc` and `emsl.project`, which the example data already uses?
8. Does the naming rule above hold, and if so, when do the feature model's three identifier slots become `id`?
