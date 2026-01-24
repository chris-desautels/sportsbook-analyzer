from app.models import PinnedGame, db


def test_pin_and_unpin_game(client, app, sample_game):
    response = client.post(f"/games/{sample_game.id}/pin")
    assert response.status_code == 302

    with app.app_context():
        pinned = PinnedGame.query.filter_by(game_id=sample_game.id).first()
        assert pinned is not None

    response = client.post(f"/games/{sample_game.id}/unpin")
    assert response.status_code == 302

    with app.app_context():
        pinned = PinnedGame.query.filter_by(game_id=sample_game.id).first()
        assert pinned is None
