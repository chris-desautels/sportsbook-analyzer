from app.models import PinnedGame, db


def test_pin_and_unpin_game(client, app, sample_game):
    # sample_game is now the game ID (int), not the ORM object
    game_id = sample_game
    response = client.post(f"/games/{game_id}/pin")
    assert response.status_code == 302

    with app.app_context():
        pinned = PinnedGame.query.filter_by(game_id=game_id).first()
        assert pinned is not None

    response = client.post(f"/games/{game_id}/unpin")
    assert response.status_code == 302

    with app.app_context():
        pinned = PinnedGame.query.filter_by(game_id=game_id).first()
        assert pinned is None
