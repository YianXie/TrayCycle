/**
 * Upload - allows the user to upload a photo of their lunch to the backend server
 *
 * Displays a box for users to upload their files
 * Allows the preview of the images before upload
 * Upload button to upload to server
 */
import {
    Alert,
    Box,
    Button,
    Card,
    CircularProgress,
    Divider,
    IconButton,
    Paper,
    Stack,
    TextField,
    Typography,
} from "@mui/material";
import { type ChangeEvent, useEffect, useState } from "react";

import "../styles/Upload.css";

export default function Upload() {
    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState("");
    const [error, setError] = useState("");

    function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
        const selected = event.target.files?.[0];
        event.target.value = "";

        if (!selected) return;
        if (!selected.type.startsWith("image/")) {
            setError("Image Please");
            return;
        }
        setFile(selected);
        setError("");
    }
    useEffect(() => {
        if (!file) {
            setPreviewUrl("");
            return;
        }

        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        return () => URL.revokeObjectURL(url);
    }, [file]);
    return (
        <Paper variant="outlined" sx={{ p: 3, maxWidth: 500 }}>
            <Stack spacing={2}>
                <Typography variant="h6">Photo</Typography>

                <Button variant="contained" component="label">
                    Choose image
                    <input
                        type="file"
                        accept="image/*"
                        hidden
                        onChange={handleFileChange}
                    />
                </Button>

                {error && <Alert severity="error">{error}</Alert>}

                {previewUrl && (
                    <Box
                        component="img"
                        src={previewUrl}
                        alt="Selected image preview"
                        sx={{
                            width: "100%",
                            height: 250,
                            objectFit: "contain",
                            borderRadius: 2,
                        }}
                    />
                )}

                {file && (
                    <>
                        <Typography variant="body2">{file.name}</Typography>

                        <Button onClick={() => setFile(null)}>
                            Remove image
                        </Button>

                        <Button variant="contained" disableElevation>
                            Upload Image
                            {/* Finish when API is done */}
                        </Button>
                    </>
                )}
            </Stack>
        </Paper>
    );
}
