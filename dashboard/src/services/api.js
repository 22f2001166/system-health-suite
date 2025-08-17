import axios from "axios";

const API_BASE = "http://localhost:8000"; // backend server

export async function getMachines() {
  const res = await fetch("http://127.0.0.1:8000/machines");
  if (!res.ok) {
    throw new Error("Failed to fetch machines");
  }
  const data = await res.json();
  return data.items || [];   // 👈 return only the array
}

