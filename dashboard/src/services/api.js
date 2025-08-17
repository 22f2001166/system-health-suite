export async function getMachines(filters = {}) {
  const params = new URLSearchParams(filters).toString();
  const res = await fetch(`http://127.0.0.1:8000/machines?${params}`);
  if (!res.ok) throw new Error("Failed to fetch machines");
  const data = await res.json();
  return data.items || [];
}

export async function exportMachinesCSV(filters = {}) {
  const params = new URLSearchParams(filters).toString();
  const res = await fetch(`http://127.0.0.1:8000/machines.csv?${params}`);
  if (!res.ok) throw new Error("Failed to export CSV");
  const blob = await res.blob();
  return blob;
}
