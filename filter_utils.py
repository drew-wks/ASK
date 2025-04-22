from typing import List, Optional
from datetime import datetime, timezone
from qdrant_client.http import models


def build_retrieval_filter(
    filter_conditions: Optional[dict[str, str | bool | None]] = None
) -> Optional[models.Filter]:
    """
    Build a Qdrant Filter from the user's `filter_conditions`.

    ── Logic ──────────────────────────────────────────────────────────────
    • Everything in `must` is an AND that applies to *all* documents
      (public_release, exclude_expired, other boolean flags, …).

    • `scope` and `unit` live in `should` so we can say
        (scope = user's scope  [AND unit = user's unit, if any])
        OR
        (scope = "national")

      This returns national documents **plus** the user‑requested district/local
      docs, but still respects the other global requirements in `must`.
      
      EXAMPLE OUTPUT:
      should=[                ← This is doing the OR of `scope` national or district
        Filter(               ← top‑level “should” list
            should=None,        ← this is the **nested** Filter’s own should (it’s doing an AND of scope+unit)
            must=[
                FieldCondition(scope="District"),
                FieldCondition(unit="7")
            ]
        ),
            FieldCondition(scope="national")  ← second branch of the top‑level should
        ]
        must=[
            FieldCondition(public_release=True)
        ]
    """

    fc = (filter_conditions or {}).copy()      # defensive copy
    must: list[models.Filter | models.FieldCondition] = []
    should: list[models.Filter | models.FieldCondition] = []

    # ── 1.  Global requirements (goes in MUST (AND)───────────────────────────────
    # Handle Expiration_date
    if fc.pop("exclude_expired", False):
        must.append(
            models.FieldCondition(
                key="metadata.expiration_date",
                range=models.DatetimeRange(gt=datetime.now(timezone.utc).isoformat()),
            )
        )

    # Handle other boolean flags
    for key, value in list(fc.items()):
        if key in {"aux_specific"}:
            continue
        if value is True: 
            must.append(
                models.FieldCondition(
                    key=f"metadata.{key}", match=models.MatchValue(value=True)
                )
            )

    # ── 2.  Handle scope & unit (goes in SHOULD) ─────────────────────────
    scope_val: str | None = fc.get("scope")
    unit_val: str | None = fc.get("unit")

    if scope_val and scope_val.lower() != "national":
        # (a) District / Local filter  ➜ scope AND (optional) unit
        scope_unit_must: list[models.FieldCondition] = [
            models.FieldCondition(
                key="metadata.scope", match=models.MatchValue(value=scope_val)
            )
        ]
        if unit_val:
            scope_unit_must.append(
                models.FieldCondition(
                    key="metadata.unit", match=models.MatchValue(value=unit_val)
                )
            )
        should.append(models.Filter(must=scope_unit_must))

        # (b) National fallback
        should.append(
            models.FieldCondition(
                key="metadata.scope", match=models.MatchValue(value="national")
            )
        )

    elif scope_val and scope_val.lower() == "national":
        # User explicitly asked for national only
        must.append(
            models.FieldCondition(
                key="metadata.scope", match=models.MatchValue(value="national")
            )
        )
        if unit_val:                     # unlikely, but honour it if supplied
            must.append(
                models.FieldCondition(
                    key="metadata.unit", match=models.MatchValue(value=unit_val)
                )
            )

    else:
        # No scope given ⇒ leave scope open; but still pin unit if supplied
        if unit_val:
            must.append(
                models.FieldCondition(
                    key="metadata.unit", match=models.MatchValue(value=unit_val)
                )
            )

    # ── 3.  Return assembled filter ─────────────────────────────────────
    if not must and not should:
        return None                      # no filters at all

    return models.Filter(must=must, should=should)
