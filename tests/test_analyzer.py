from app.services.analyzer import MarketOdds, detect_arbitrage, detect_value_bets


def test_detect_arbitrage():
    odds = [
        MarketOdds(bookmaker="A", market_type="h2h", home_price=200, away_price=-150),
        MarketOdds(bookmaker="B", market_type="h2h", home_price=-150, away_price=200),
    ]
    results = detect_arbitrage(odds, min_profit_percent=0.1)
    assert results
    assert results[0]["profit_percentage"] > 0


def test_detect_value_bets():
    odds = [
        MarketOdds(bookmaker="A", market_type="h2h", home_price=150, away_price=-160),
        MarketOdds(bookmaker="B", market_type="h2h", home_price=110, away_price=-130),
    ]
    results = detect_value_bets(odds, min_edge_percent=1.0)
    assert results
    assert any(result["edge_percentage"] >= 1.0 for result in results)
