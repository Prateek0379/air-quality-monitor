// =============================================================
// api.js
//
// PURPOSE: All API calls to the FastAPI backend in one place.
//
// Why centralise API calls?
// If the backend URL changes, we change it in ONE place.
// If an endpoint changes, we change it in ONE place.
// Components never need to know where data comes from.
// =============================================================

import axios from 'axios'

// Base URL of our FastAPI backend
// In production this would be your deployed server URL
const BASE_URL = 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000, // 10 seconds before giving up
})

// Get summary statistics for the header cards
export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}

// Get recent readings for the chart
export const getReadings = async (limit = 100) => {
  const response = await api.get(`/readings?limit=${limit}`)
  return response.data
}

// Get the single latest reading
export const getLatestReading = async () => {
  const response = await api.get('/readings/latest')
  return response.data
}

// Get anomalous readings for the table
export const getAnomalies = async (limit = 20) => {
  const response = await api.get(`/readings/anomalies?limit=${limit}`)
  return response.data
}

// Simulate a new reading (calls our /readings/simulate endpoint)
export const simulateReading = async () => {
  const response = await api.post('/readings/simulate')
  return response.data
}