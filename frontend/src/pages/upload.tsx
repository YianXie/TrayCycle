import { useEffect, useState, type ChangeEvent } from "react";
import "../styles/Upload.css"

import {Box,Paper,Card,Stack,Button,IconButton,Typography,TextField,Divider,Alert,CircularProgress,} from "@mui/material";
export default function Upload() {
    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState("");
    const [error, setError] = useState("");

    function handleFileChange(event: ChangeEvent<HTMLInputElement>){
        const selected = event.target.files?.[0];
        event.target.value = "";

        if(!selected) return;
        if(!selected.type.startsWith("image/")){
            setError("Image Please");
            return;
        }
        setFile(selected);
        setError("");
    }
    useEffect(() => {
        if(!file){
            setPreviewUrl("");
            return;
        }

        const url = URL.createObjectURL(file);

        return ()=>URL.revokeObjectURL(url);
    },[file]);
    return(
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
            </>
            )}
        </Stack>
        </Paper>
    );
}