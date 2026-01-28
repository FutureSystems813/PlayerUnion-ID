import httpx

STEAM_API_KEY = "7EE60BB0BB2E91DD391DC6B11356EBBC"

async def get_owned_games(steam_id: str):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "include_appinfo": 1}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        return res.json().get("response", {}).get("games", [])

async def get_player_summary(steam_id: str):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        players = res.json().get("response", {}).get("players", [])
        return players[0] if players else None
