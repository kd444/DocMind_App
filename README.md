
# Project README

## Project Overview
This project contains two main components:
1. **Frontend**: A Next.js application.
2. **Backend**: A FastAPI application.

**App Name**: DocMind_App (Owner Avatar)

## Project Structure
```
root/
|-- frontend/    # Next.js app
|-- backend/     # FastAPI app
```

## Prerequisites
Ensure you have the following installed on your system:
- **Node.js** (for the frontend)
- **Python** (with `Poetry` for the backend)

## Setup Instructions

### Frontend Setup
Navigate to the `frontend` directory and install the dependencies.

```bash
cd frontend
npm install
```

To start the development server:
```bash
npm run dev
```

To build the project for production:
```bash
npm run build
```

To run the built project:
```bash
npm start
```

### Backend Setup
Navigate to the `backend` directory and set up the Python environment using Poetry.

```bash
cd backend
poetry install
```

To activate the Poetry shell:
```bash
poetry shell
```

To run the FastAPI application:
```bash
uvicorn main:app --reload
```
*Ensure that `main.py` is the entry point of your FastAPI app.*

## Additional Commands
- **Linting and Formatting**:
  - Frontend: `npm run lint`
  - Backend: Utilize Poetry commands or include `black` and `flake8` in your `pyproject.toml` for code quality checks.

## Frontend Dependencies
Refer to `package.json` for complete details:
- Key dependencies include `axios`, `react`, `next`, and `tailwindcss`.

## Backend Dependencies
Refer to `pyproject.toml` for all Python dependencies managed by Poetry.


