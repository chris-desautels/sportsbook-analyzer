from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from app.models import OddsSnapshot


@dataclass(frozen=True)
class BestLine:
    price: int
    bookmaker: str
    point: float | None = None


def latest_snapshots_for_game(game_id: int) -> list[OddsSnapshot]:
    snapshots = (
        OddsSnapshot.query.filter_by(game_id=game_id).order_by(OddsSnapshot.timestamp.desc()).all()
    )
    return _dedupe_latest_snapshots(snapshots)


def best_lines_for_game(game_id: int) -> dict[str, dict[str, BestLine]]:
    snapshots = latest_snapshots_for_game(game_id)
    return best_lines_from_snapshots(snapshots)


def best_lines_from_snapshots(
    snapshots: Iterable[OddsSnapshot],
) -> dict[str, dict[str, BestLine]]:
    grouped: dict[str, list[OddsSnapshot]] = defaultdict(list)
    for snapshot in snapshots:
        if snapshot.home_price is None or snapshot.away_price is None:
            continue
        grouped[snapshot.market_type].append(snapshot)

    best_lines: dict[str, dict[str, BestLine]] = {}
    for market_type, market_snaps in grouped.items():
        best_lines[market_type] = _best_lines_for_market(market_type, market_snaps)
    return best_lines


def detect_steam_moves(
    snapshots: Iterable[OddsSnapshot],
    window_minutes: int,
    min_books: int,
    min_price_move: int,
    min_point_move: float,
) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    recent = [snap for snap in snapshots if snap.timestamp >= cutoff]
    grouped: dict[str, dict[str, list[OddsSnapshot]]] = defaultdict(lambda: defaultdict(list))
    for snap in recent:
        grouped[snap.market_type][snap.bookmaker].append(snap)

    steam_moves: list[dict] = []
    for market_type, by_book in grouped.items():
        if market_type == "totals":
            moves = _detect_point_moves(by_book, "total_point", min_point_move)
            steam_moves.extend(_summarize_moves(market_type, "total", moves, min_books))
            continue
        if market_type == "spreads":
            moves = _detect_point_moves(by_book, "home_point", min_point_move)
            steam_moves.extend(_summarize_moves(market_type, "spread", moves, min_books))
            continue

        home_moves = _detect_price_moves(by_book, "home_price", min_price_move)
        away_moves = _detect_price_moves(by_book, "away_price", min_price_move)
        steam_moves.extend(_summarize_moves(market_type, "home", home_moves, min_books))
        steam_moves.extend(_summarize_moves(market_type, "away", away_moves, min_books))

    return steam_moves


def _dedupe_latest_snapshots(snapshots: Iterable[OddsSnapshot]) -> list[OddsSnapshot]:
    seen = set()
    latest = []
    for snapshot in snapshots:
        key = (snapshot.bookmaker, snapshot.market_type)
        if key in seen:
            continue
        seen.add(key)
        latest.append(snapshot)
    return latest


def _best_lines_for_market(
    market_type: str, snapshots: Iterable[OddsSnapshot]
) -> dict[str, BestLine]:
    if market_type == "totals":
        return {
            "over": _select_best_line(snapshots, "home_price", "total_point"),
            "under": _select_best_line(snapshots, "away_price", "total_point"),
        }
    if market_type == "spreads":
        best_home = _select_best_line(snapshots, "home_price", "home_point")
        best_away = _select_best_line(snapshots, "away_price", "home_point")
        if best_away and best_away.point is not None:
            best_away = BestLine(
                price=best_away.price,
                bookmaker=best_away.bookmaker,
                point=-best_away.point,
            )
        return {"home": best_home, "away": best_away}
    return {
        "home": _select_best_line(snapshots, "home_price"),
        "away": _select_best_line(snapshots, "away_price"),
    }


def _select_best_line(
    snapshots: Iterable[OddsSnapshot],
    price_attr: str,
    point_attr: str | None = None,
) -> BestLine | None:
    best_snapshot = None
    best_price = None
    for snapshot in snapshots:
        price = getattr(snapshot, price_attr, None)
        if price is None:
            continue
        if best_price is None or price > best_price:
            best_price = price
            best_snapshot = snapshot

    if best_snapshot is None:
        return None

    point = getattr(best_snapshot, point_attr, None) if point_attr else None
    return BestLine(
        price=best_price,
        bookmaker=best_snapshot.bookmaker,
        point=point,
    )


def _detect_point_moves(
    by_book: dict[str, list[OddsSnapshot]],
    point_attr: str,
    min_point_move: float,
) -> list[dict]:
    moves = []
    for bookmaker, snaps in by_book.items():
        snaps_sorted = sorted(snaps, key=lambda snap: snap.timestamp)
        if len(snaps_sorted) < 2:
            continue
        start = getattr(snaps_sorted[0], point_attr, None)
        end = getattr(snaps_sorted[-1], point_attr, None)
        if start is None or end is None:
            continue
        delta = end - start
        if abs(delta) < min_point_move:
            continue
        direction = "up" if delta > 0 else "down"
        moves.append({"bookmaker": bookmaker, "direction": direction})
    return moves


def _detect_price_moves(
    by_book: dict[str, list[OddsSnapshot]],
    price_attr: str,
    min_price_move: int,
) -> list[dict]:
    moves = []
    for bookmaker, snaps in by_book.items():
        snaps_sorted = sorted(snaps, key=lambda snap: snap.timestamp)
        if len(snaps_sorted) < 2:
            continue
        start = getattr(snaps_sorted[0], price_attr, None)
        end = getattr(snaps_sorted[-1], price_attr, None)
        if start is None or end is None:
            continue
        delta = end - start
        if abs(delta) < min_price_move:
            continue
        direction = "up" if delta > 0 else "down"
        moves.append({"bookmaker": bookmaker, "direction": direction})
    return moves


def _summarize_moves(
    market_type: str, side: str, moves: Iterable[dict], min_books: int
) -> list[dict]:
    by_direction: dict[str, list[str]] = defaultdict(list)
    for move in moves:
        by_direction[move["direction"]].append(move["bookmaker"])

    summaries = []
    for direction, books in by_direction.items():
        if len(books) < min_books:
            continue
        summaries.append(
            {
                "market_type": market_type,
                "side": side,
                "direction": direction,
                "bookmakers": sorted(books),
            }
        )
    return summaries
