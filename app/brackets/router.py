from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.database import supabase
from app.auth.utils import get_current_user
from app.brackets.schemas import BracketResponse, BracketRound, BracketTie

router = APIRouter(prefix="/brackets", tags=["brackets"])


@router.get("/tournaments")
def get_tournaments(
    competition: Optional[str] = Query(None, description="UCL or WC"),
    current_user: dict = Depends(get_current_user)
):
    query = supabase.table("tournaments").select("*")
    if competition:
        query = query.eq("competition", competition)
    result = query.order("year", desc=True).execute()
    return {"tournaments": result.data}


@router.get("/{competition}/{year}")
def get_bracket(
    competition: str,
    year: str,
    difficulty: str = Query("medium", description="easy, medium, hard, extreme"),
    current_user: dict = Depends(get_current_user)
):
    # Get tournament
    tournament = supabase.table("tournaments")\
        .select("*")\
        .eq("competition", competition)\
        .eq("year", year)\
        .execute()

    if not tournament.data:
        raise HTTPException(status_code=404, detail="Tournament not found")

    tournament_id = tournament.data[0]["id"]

    # Get bracket question for this difficulty
    bracket_q = supabase.table("bracket_questions")\
        .select("*")\
        .eq("tournament_id", tournament_id)\
        .eq("difficulty", difficulty)\
        .execute()

    blank_tie_ids = []
    if bracket_q.data:
        blank_tie_ids = bracket_q.data[0].get("blank_tie_ids", [])

    # Get all rounds
    rounds_result = supabase.table("bracket_rounds")\
        .select("*")\
        .eq("tournament_id", tournament_id)\
        .order("round_order")\
        .execute()

    rounds = []
    for round_row in rounds_result.data:
        # Get ties for this round
        ties_result = supabase.table("bracket_ties")\
            .select("*, home_team:home_team_id(name), away_team:away_team_id(name), winner:winner_team_id(name)")\
            .eq("bracket_round_id", round_row["id"])\
            .execute()

        ties = []
        for tie in ties_result.data:
            is_blank = tie["id"] in blank_tie_ids
            ties.append(BracketTie(
                id=tie["id"],
                home_team=None if is_blank else tie.get("home_team", {}).get("name"),
                away_team=None if is_blank else tie.get("away_team", {}).get("name"),
                score_home=None if is_blank else tie.get("score_home"),
                score_away=None if is_blank else tie.get("score_away"),
                winner=None if is_blank else tie.get("winner", {}).get("name"),
                is_blank=is_blank
            ))

        rounds.append(BracketRound(
            round_name=round_row["round_name"],
            round_order=round_row["round_order"],
            ties=ties
        ))

    return BracketResponse(
        competition=competition,
        year=year,
        difficulty=difficulty,
        rounds=rounds,
        total_blanks=len(blank_tie_ids)
    )