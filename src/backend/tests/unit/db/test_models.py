def test_placeholder_models_importable():
    from app.db.models import ContentEmbedding, Destination, DiveSite, Lead, SessionModel

    assert SessionModel is not None
    assert ContentEmbedding is not None
    assert Lead is not None
    assert Destination is not None
    assert DiveSite is not None
