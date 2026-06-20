from fastapi import FastAPI, HTTPException, Query
import requests
import pandas as pd
from typing import List, Optional
import uvicorn

app = FastAPI(title="F1 Data Visualization API")

BASE_URL = "https://api.openf1.org/v1"

def fetch_from_api(endpoint: str, params: dict):
    """Helper to fetch and handle API errors."""
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

@app.get("/api/driver-positions/{session_key}")
async def get_driver_positions(
    session_key: int, 
    driver_number: Optional[int] = None
):
    """
    Fetches position data and cleans it for charting.
    """
    params = {"session_key": session_key}
    if driver_number:
        params["driver_number"] = driver_number
    
    raw_data = fetch_from_api("position", params)
    
    if not raw_data:
        return {"message": "No data found for this session/driver."}

    # Use Pandas for data processing
    df = pd.DataFrame(raw_data)
    
    # Convert 'date' to readable format for X-axis plotting
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%H:%M:%S')
    
    # Grouping data for a line chart (e.g., Position over Time)
    # We return the list of records
    return {
        "session_key": session_key,
        "count": len(df),
        "data": df.to_dict(orient="records")
    }

@app.get("/api/lap-times/{session_key}")
async def get_lap_times(session_key: int):
    """
    Fetches lap duration data.
    """
    data = fetch_from_api("laps", {"session_key": session_key})
    df = pd.DataFrame(data)
    
    # Filter for valid laps only (remove non-racing laps if needed)
    df = df[df['lap_duration'].notnull()]
    
    return {"data": df[['driver_number', 'lap_number', 'lap_duration']].to_dict(orient="records")}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)