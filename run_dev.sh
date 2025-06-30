#!/bin/bash

# Run development servers for both backend and frontend

# Start backend server in the background
echo "Starting backend server..."
cd backend
python -m uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start frontend server in the background
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit 0
}

# Register the cleanup function for when script is terminated
trap cleanup INT TERM

# Keep script running
echo "Development servers are running. Press Ctrl+C to stop."
wait
