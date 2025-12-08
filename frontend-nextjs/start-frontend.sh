#!/bin/bash

echo "Starting Local Recall Frontend..."
echo ""

cd "$(dirname "$0")"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting Next.js development server on port 3000..."
npm run dev
