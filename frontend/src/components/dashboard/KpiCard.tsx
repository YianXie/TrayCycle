import { Card, CardContent, Typography } from "@mui/material";

export type KpiCardProps = {
    value: string;
    label: string;
    hint?: string;
};

function KpiCard({ value, label, hint }: KpiCardProps) {
    return (
        <Card
            variant="outlined"
            sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                borderColor: "divider",
            }}
        >
            <div style={{ height: 3, background: "currentColor" }} />
            <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h3" component="p">
                    {value}
                </Typography>
                <Typography variant="body2">{label}</Typography>
                {hint && (
                    <Typography variant="caption" color="text.secondary">
                        {hint}
                    </Typography>
                )}
            </CardContent>
        </Card>
    );
}

export default KpiCard;
