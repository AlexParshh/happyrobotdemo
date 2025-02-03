# HappyRobot Carrier API

This is a FastAPI-based server implementation for the HappyRobot carrier sales use case. The API provides endpoints for load retrieval and carrier validation.

## Setup

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

## API Endpoints

### Get Load Details
```
GET /loads/{reference_number}
```
Returns load details for the given reference number.

### Validate Carrier
```
GET /validate-carrier/{mc_number}
```
Validates a carrier using their MC number through the FMCSA API.

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
