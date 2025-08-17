import React, { useEffect, useState } from "react";
import { Container, Typography, Paper, Box } from "@mui/material";
import MachineTable from "./components/MachineTable";
import { getMachines } from "./services/api";

function App() {
  const [machines, setMachines] = useState([]);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const items = await getMachines();
        setMachines(items);
      } catch (err) {
        console.error(err);
        setMachines([]);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 600 }}>
          System Health Dashboard
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary">
          Monitoring all machines in real-time
        </Typography>
      </Paper>

      <Box sx={{ mt: 4 }}>
        <MachineTable machines={machines} />
      </Box>
    </Container>
  );
}

export default App;
