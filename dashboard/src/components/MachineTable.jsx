import React from "react";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, Typography
} from "@mui/material";

const statusChip = (ok) => (
  <Chip
    label={ok ? "OK" : "Issue"}
    color={ok ? "success" : "error"}
    size="small"
    sx={{ fontWeight: 600 }}
  />
);

const MachineTable = ({ machines }) => {
  return (
    <TableContainer component={Paper} sx={{ boxShadow: 3 }}>
      <Table>
        <TableHead sx={{ backgroundColor: "#f5f5f5" }}>
          <TableRow>
            {["Machine ID", "OS", "Disk Encrypted", "OS Up to Date", "Antivirus Active", "Sleep ≤ 10min", "Last Check-In"].map((header) => (
              <TableCell key={header} sx={{ fontWeight: 600, textAlign: "center" }}>
                {header}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {machines.length > 0 ? (
            machines.map((m) => (
              <TableRow key={m.machine_id} hover>
                <TableCell align="center">{m.hostname || m.machine_id}</TableCell>
                <TableCell align="center">{m.os?.system} {m.os?.release}</TableCell>
                <TableCell align="center">{statusChip(!m.issues?.unencrypted_disk)}</TableCell>
                <TableCell align="center">{statusChip(!m.issues?.outdated_os)}</TableCell>
                <TableCell align="center">{statusChip(!m.issues?.no_antivirus)}</TableCell>
                <TableCell align="center">{statusChip(!m.issues?.idle_sleep_too_high)}</TableCell>
                <TableCell align="center">{new Date(m.last_check_in).toLocaleString()}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={7} align="center">
                <Typography color="text.secondary">No machines reporting yet</Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default MachineTable;
