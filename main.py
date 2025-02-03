from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HappyRobot Carrier API",
    description="API for carrier load management and verification",
    version="1.0.0"
)

# Load the CSV data on server start, create an index on reference number for faster lookups when lots of data present
try:
    df = pd.read_csv("data/loads.csv")
    df.set_index("reference_number", inplace=True)
except FileNotFoundError:
    print("Warning: loads.csv not found. Please ensure it exists in the data directory.")
    df = pd.DataFrame()

class Load(BaseModel):
    reference_number: str
    origin: str
    destination: str
    equipment_type: str
    rate: float
    commodity: str

@app.get("/loads", response_model=Load)
async def get_load(reference_number: str = Query(..., description="Reference number of the load")):
    """
    Retrieve load details by reference number (passed as query parameter)
    Example: /loads?reference_number=REF09460
    """
    try:
        load = df.loc[reference_number]
        return {
            "reference_number": reference_number,
            "origin": load["origin"],
            "destination": load["destination"],
            "equipment_type": load["equipment_type"],
            "rate": float(load["rate"]),
            "commodity": load["commodity"]
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Load not found")

@app.get("/validate-carrier")
async def validate_carrier(mc_number: str = Query(..., description="MC number of the carrier")):
    """
    Validate carrier using FMCSA API (mc_number passed as query parameter)
    Example: /validate-carrier?mc_number=44110
    """
    FMCSA_API_KEY = os.getenv("FMCSA_API_KEY")
    FMCSA_BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services"
    
    if not FMCSA_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FMCSA API key not configured"
        )

    try:
        async with httpx.AsyncClient() as client:
            # Query using the docket-number endpoint
            response = await client.get(
                f"{FMCSA_BASE_URL}/carriers/docket-number/{mc_number}",
                params={"webKey": FMCSA_API_KEY}
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Carrier not found"
                )
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid FMCSA API key"
                )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Check if we got any content
            if not response_data.get('content'):
                raise HTTPException(
                    status_code=404,
                    detail="No carrier found for this MC number"
                )
            
            # Get carrier data from nested structure
            carrier_data = response_data['content'][0]['carrier']
            
            # Check if carrier is allowed to operate
            if carrier_data.get("allowedToOperate") != "Y":
                raise HTTPException(
                    status_code=403,
                    detail="Carrier is not authorized to operate"
                )
            
            # Check if carrier is out of service
            if carrier_data.get("oosDate"):
                raise HTTPException(
                    status_code=403,
                    detail=f"Carrier is out of service since {carrier_data.get('oosDate')}"
                )
            
            # Return relevant carrier information based on API documentation
            return {
                "mc_number": mc_number,
                "dot_number": carrier_data.get("dotNumber"),
                "legal_name": carrier_data.get("legalName"),
                "dba_name": carrier_data.get("dbaName"),
                "allowed_to_operate": carrier_data.get("allowedToOperate") == "Y",
                "out_of_service": bool(carrier_data.get("oosDate")),
                "out_of_service_date": carrier_data.get("oosDate"),
                "address": {
                    "street": carrier_data.get("phyStreet"),
                    "city": carrier_data.get("phyCity"),
                    "state": carrier_data.get("phyState"),
                    "zip": carrier_data.get("phyZipcode"),  # Note: API uses 'phyZipcode' not 'phyZip'
                    "country": carrier_data.get("phyCountry")
                },
                "telephone": carrier_data.get("telephone")
            }
            
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to reach FMCSA service"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
