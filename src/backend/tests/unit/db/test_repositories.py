def test_placeholder_repos_importable():
    from app.db.repositories import EmbeddingRepository, LeadRepository, SessionRepository

    assert SessionRepository is not None
    assert EmbeddingRepository is not None
    assert LeadRepository is not None
