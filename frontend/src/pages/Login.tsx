/**
 * Login page for the TriCycle web application.
 *
 * Allows the user to log in with their username and password.
 * If the login is successful, the user is redirected to the page they were trying to access before being prompted to log in, or to the dashboard if no specific page was requested.
 */
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import type { SubmitEvent } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Login() {
    const { token, login } = useAuth();
    const location = useLocation();
    const from = location.state?.location || "/dashboard";
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    // Once a token exists (already logged in, or just logged in), go back to
    // where the user came from.
    if (token) return <Navigate to={from} replace />;

    const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError("");
        setSubmitting(true);
        try {
            await login(username, password);
        } catch (error) {
            console.error("Login failed:", error);
            throw error;
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                p: 2,
            }}
        >
            <Paper
                component="form"
                onSubmit={handleSubmit}
                sx={{ p: 4, width: "100%", maxWidth: 360 }}
            >
                <Typography variant="h5" gutterBottom>
                    Log in
                </Typography>
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}
                <TextField
                    label="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username"
                    autoFocus
                    required
                    fullWidth
                    margin="normal"
                />
                <TextField
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    required
                    fullWidth
                    margin="normal"
                />
                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={submitting}
                    sx={{ mt: 2 }}
                >
                    {submitting ? "Logging in..." : "Log in"}
                </Button>
            </Paper>
        </Box>
    );
}
