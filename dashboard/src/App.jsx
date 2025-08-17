import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import MachineTable from "./components/MachineTable";
import { getMachines, exportMachinesCSV } from "./services/api";

function App() {
  const [machines, setMachines] = useState([]);
  const [filters, setFilters] = useState({ os: "", issue: "", q: "", sort_by: "hostname", order: "asc" });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const items = await getMachines(filters);
        setMachines(items);
      } catch (err) {
        console.error(err);
        setMachines([]);
      }
    };
    fetchData();
  }, [filters]);
  
  const handleExportCSV = async () => {
    try {
      const blob = await exportMachinesCSV(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "machines.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("CSV export failed:", err);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ py: 3, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          System Health Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Monitoring all machines in real-time
        </Typography>
      </Paper>

      <Box
        sx={{
          mt: 3,
          display: "flex",
          flexWrap: "wrap",
          gap: 2,
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>OS</InputLabel>
          <Select
            value={filters.os}
            label="OS"
            onChange={(e) => setFilters({ ...filters, os: e.target.value })}
          >
            <MenuItem value="">All OS</MenuItem>
            <MenuItem value="Windows">Windows</MenuItem>
            <MenuItem value="Linux">Linux</MenuItem>
            <MenuItem value="Darwin">macOS</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Issue</InputLabel>
          <Select
            value={filters.issue}
            label="Issue"
            onChange={(e) => setFilters({ ...filters, issue: e.target.value })}
          >
            <MenuItem value="">All Issues</MenuItem>
            <MenuItem value="unencrypted_disk">Unencrypted Disk</MenuItem>
            <MenuItem value="outdated_os">Outdated OS</MenuItem>
            <MenuItem value="no_antivirus">No Antivirus</MenuItem>
            <MenuItem value="idle_sleep_too_high">Sleep Misconfig</MenuItem>
          </Select>
        </FormControl>

        <TextField
          size="small"
          label="Search Hostname"
          variant="outlined"
          value={filters.q}
          onChange={(e) => setFilters({ ...filters, q: e.target.value })}
          sx={{ minWidth: 200 }}
        />

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={filters.sort_by}
            label="Sort By"
            onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
          >
            <MenuItem value="hostname">Name</MenuItem>
            <MenuItem value="os">OS</MenuItem>
            <MenuItem value="last_check_in">Last Check-in</MenuItem>
          </Select>
        </FormControl>

        <Button variant="contained" color="primary" onClick={handleExportCSV}>
          Export CSV
        </Button>
      </Box>


      <Box sx={{ mt: 4 }}>
        <MachineTable machines={machines} />
      </Box>
    </Container>
  );
}

export default App;
