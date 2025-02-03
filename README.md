# HappyRobot Carrier API

This is a FastAPI-based server implementation for the HappyRobot carrier sales use case. The application provides endpoints for load retrieval and carrier validation through the FMCSA API.

## Features

- Load retrieval by reference number
- Carrier validation using FMCSA API
- Efficient CSV data handling with pandas
- Docker support
- Deployment ready for fly.io

## Setup

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
FMCSA_API_KEY=your_api_key_here
```

4. Run the server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### Docker Setup

1. Build the Docker image:
```bash
docker build -t happyrobot-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e FMCSA_API_KEY=your_api_key_here happyrobot-api
```

### Deployment to fly.io

1. Install the flyctl CLI:
```bash
brew install flyctl  # On macOS
```

2. Login to fly.io:
```bash
fly auth login
```

3. Deploy the application:
```bash
fly deploy
```

4. Set the FMCSA API key:
```bash
fly secrets set FMCSA_API_KEY=your_api_key_here
```

## API Endpoints

### Get Load Details
```
GET /loads?reference_number={reference_number}
```
Retrieves load details for the given reference number.

Example:
```bash
curl "http://localhost:8000/loads?reference_number=REF09460"
```

Response:
```json
{
    "reference_number": "REF09460",
    "origin": "Denver CO",
    "destination": "Detroit MI",
    "equipment_type": "Dry Van",
    "rate": 868,
    "commodity": "Automotive Parts"
}
```

### Validate Carrier
```
GET /validate-carrier?mc_number={mc_number}
```
Validates a carrier using their MC number through the FMCSA API.

Example:
```bash
curl "http://localhost:8000/validate-carrier?mc_number=524034"
```

Response:
```json
{
    "mc_number": "524034",
    "dot_number": 524034,
    "legal_name": "704337 ONT INC",
    "dba_name": "DONALDSON'S",
    "allowed_to_operate": true,
    "out_of_service": false,
    "out_of_service_date": null,
    "address": {
        "street": "32W82 PETTIT RD - RR #1",
        "city": "WAINFLEET",
        "state": "ON",
        "zip": "L0S 1V0",
        "country": "CA"
    }
}
```

## Error Responses

### Load Not Found
```json
{
    "detail": "Load not found"
}
```

### Carrier Validation Errors
```json
{
    "detail": "No carrier found for this MC number"
}
```
```json
{
    "detail": "Carrier is not authorized to operate"
}
```
```json
{
    "detail": "Carrier is out of service since [date]"
}
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Data Structure

The load data is stored in `data/loads.csv` with the following structure:
- reference_number: Unique identifier for each load
- origin: Starting location
- destination: Final destination
- equipment_type: Required equipment type
- rate: Load rate
- commodity: Type of goods being transported
