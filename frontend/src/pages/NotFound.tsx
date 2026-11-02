import { Button, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export default function NotFound() {
    return (
        <Stack spacing={2} alignItems="flex-start">
            <Typography variant="h2" component="p">
                404
            </Typography>

            <Typography>The page you requested does not exist.</Typography>

            <Button component={RouterLink} to="/" variant="contained">
                Back to home
            </Button>
        </Stack>
    );
}
