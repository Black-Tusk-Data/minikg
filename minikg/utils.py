def scrub_title_key(d: dict):
    """
    Helpful because pydantic schema dumps include an unecessary 'title' attribute;
    """
    d.pop("title", None)
    if d.get("type") == "object":
        assert "properties" in d
        for prop in d["properties"].keys():
            scrub_title_key(d["properties"][prop])
    return d
