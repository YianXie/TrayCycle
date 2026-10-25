/**
 * Upload - allows the user to upload a photo of their lunch to the backend server
 *
 * Displays a box for users to upload their files
 * Allows the preview of the images before upload
 * Upload button to upload to server
 */
import { Alert, Box, Button, Paper, Stack, Typography } from "@mui/material";
import { type ChangeEvent, useState } from "react";

import usePageTitle from "../UsePageTitle";
import api from "../api.ts";
import "../styles/Upload.css";

export default function Upload() {
    usePageTitle("Upload");
    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
        const selected = event.target.files?.[0];
        event.target.value = "";

        if (!selected) return;
        if (!selected.type.startsWith("image/")) {
            setError("Image Please");
            return;
        }
        const url = URL.createObjectURL(selected);
        setPreviewUrl(url);
        setFile(selected);
        setError("");
        return () => URL.revokeObjectURL(url);
    }

    function handleRemoveImage() {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
        setFile(null);
        setPreviewUrl("");
    }

    async function uploadImg() {
        if (!file) return;

        const body = new FormData();
        body.append("image", file);

        setIsLoading(true);

        try {
            const resp = await api.post("/captures", body, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            console.log("Successful", resp.data);
        } catch (error: unknown) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Upload failed. Please try again."
            );
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }
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

                        <Button onClick={handleRemoveImage}>
                            Remove image
                        </Button>

                        <Button
                            onClick={uploadImg}
                            variant="contained"
                            disabled={isLoading}
                            disableElevation
                        >
                            {!isLoading ? "Upload Image" : "Uploading..."}
                        </Button>
                    </>
                )}
            </Stack>
        </Paper>
    );
}
