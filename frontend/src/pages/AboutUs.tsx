/**
 * About us page component - who we are and what this entire project aims to achieve
 *
 * Displays our team name: TriCycle
 * Displays our goal: To reduce food waste at SAS and do our part to contribute achieving the UN SDGs
 * Displays that our focus is UN SDG 12, specifically food waste
 * Displays some stats about how food waste is a real problem in SAS, SG, and worldwide
 */
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";

import TrayCycleLogo from "/logo.png";

type StatProps = {
    value: string;
    label: string;
    detail?: string;
    source: string;
};

function Stat({ value, label, detail, source }: StatProps) {
    return (
        <Card
            variant="outlined"
            sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                borderColor: "divider",
                transition: "border-color 120ms ease",
                "&:hover": { borderColor: "primary.main" },
            }}
        >
            <Box sx={{ height: 3, bgcolor: "primary.main" }} />
            <CardContent
                sx={{
                    flexGrow: 1,
                    display: "flex",
                    flexDirection: "column",
                    gap: 0.5,
                }}
            >
                <Typography
                    variant="h2"
                    component="p"
                    sx={{
                        fontWeight: 700,
                        lineHeight: 1.1,
                        letterSpacing: "-0.03em",
                        fontVariantNumeric: "tabular-nums",
                    }}
                >
                    {value}
                </Typography>
                <Typography variant="body2">{label}</Typography>
                {detail && (
                    <Typography variant="caption" color="text.secondary">
                        {detail}
                    </Typography>
                )}
                <Box sx={{ mt: "auto", pt: 1.5 }}>
                    <Link
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        variant="caption"
                        underline="hover"
                    >
                        Go To Source
                    </Link>
                </Box>
            </CardContent>
        </Card>
    );
}

function toRomanNumeral(num: number) {
    const map: Record<string, number> = {
        M: 1000,
        CM: 900,
        D: 500,
        CD: 400,
        C: 100,
        XC: 90,
        L: 50,
        XL: 40,
        X: 10,
        IX: 9,
        V: 5,
        IV: 4,
        I: 1,
    };
    let result = "";
    for (const key in map) {
        while (num >= map[key]) {
            result += key;
            num -= map[key];
        }
    }
    return result;
}

export default function AboutUs() {
    const GLOBAL_STATS = [
        {
            value: "25-30%",
            label: "of all food produced is lost or wasted",
            detail: "≈1.6 billion tonnes every year",
            source: "https://earth.org/facts-about-food-waste/",
        },
        {
            value: "1 in 5",
            label: "foods are wasted before they can be consumed",
            detail: "World Food Programme estimate",
            source: "https://borgenproject.org/food-waste-in-singapore/",
        },
        {
            value: "60%",
            label: "of consumer-level waste comes from households",
            detail: "Food service 28%, retail 12%",
            source: "https://earth.org/facts-about-food-waste/",
        },
        {
            value: "8-10%",
            label: "of global greenhouse gas emissions come from food waste",
            detail: "Almost 5 times the entire aviation industry",
            source: "https://www.ozharvest.org/food-waste-facts/",
        },
    ];
    const SG_STATS = [
        {
            value: "~11%",
            label: "of Singapore's waste is food waste",
            detail: "Enough to fill Semakau, our only landfill, by 2035",
            source: "https://borgenproject.org/food-waste-in-singapore/",
        },
        {
            value: ">90%",
            label: "of Singapore's food is imported",
            detail: "Wasting it wastes the carbon, water and money behind those imports",
            source: "https://pmc.ncbi.nlm.nih.gov/articles/PMC12444370/",
        },
    ];
    const SDG_TARGETS = [
        {
            id: "12.3",
            title: "Halve food waste by 2030",
            text: "Halve per-capita global food waste at the retail and consumer level, and reduce losses along production and supply chains.",
            source: "https://sdgs.un.org/goals/goal12",
        },
        {
            id: "12.5",
            title: "Cut waste generation",
            text: "Substantially reduce waste generation through prevention, reduction, recycling and reuse.",
            source: "https://sdgs.un.org/goals/goal12",
        },
    ];
    const WHY_THIS_PROJECT = [
        {
            title: "We target the right sector",
            text: "School canteens sit in the food service sector, which produces 28% of consumer-level food waste.",
        },
        {
            title: "Measure to manage",
            text: "Tracking reveals which dishes get thrown away and when, so portions and ordering can be adjusted.",
        },
        {
            title: "Tangibility and Accountability",
            text: "Seeing a day's waste as kilograms of food turns an abstract global problem into something students and faculty can see and act on.",
        },
        {
            title: "Zero Waste starts at school",
            text: "A micro-model of Singapore's national Zero Waste vision.",
        },
    ];
    return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <Box
                component="section"
                sx={{
                    display: "flex",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: { xs: 5, md: 7 },
                    p: { xs: 3, md: 4 },
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                    background: (theme) =>
                        `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, transparent 70%)`,
                }}
            >
                {/* Display the TriCycle logo */}
                <Box
                    component="img"
                    src={TrayCycleLogo}
                    alt="TrayCycle logo"
                    sx={{ height: { xs: 48, md: 64 }, width: "auto" }}
                />
                <Box>
                    <Typography variant="overline" color="text.secondary">
                        TriCycle
                    </Typography>
                    <Typography variant="h4" component="h1" gutterBottom>
                        TrayCycle
                    </Typography>
                    <Typography
                        variant="h6"
                        color="text.secondary"
                        sx={{ maxWidth: "67ch" }}
                    >
                        {/* Description of the TriCycle project */}A
                        camera-based plate-waste tracker for the SAS cafeteria.
                        Measures what gets thrown away, so the kitchen knows
                        what to change.
                    </Typography>
                </Box>
            </Box>
            {/* Facts about the problem that we are addressing */}
            <Box component="section">
                <Typography variant="h5" component="h2" gutterBottom>
                    The problem, worldwide
                </Typography>
                <Grid container spacing={3}>
                    {GLOBAL_STATS.map((stat) => (
                        <Grid key={stat.value} size={{ xs: 12, md: 6 }}>
                            <Stat {...stat} />
                        </Grid>
                    ))}
                </Grid>
            </Box>
            <Divider></Divider>
            <Box component="section">
                <Typography variant="h5" component="h2" gutterBottom>
                    The problem in Singapore
                </Typography>
                <Grid container spacing={3}>
                    {SG_STATS.map((stat) => (
                        <Grid key={stat.value} size={{ xs: 12, md: 6 }}>
                            <Stat {...stat} />
                        </Grid>
                    ))}
                </Grid>
            </Box>

            <Box component="section">
                <Card
                    sx={{
                        p: { xs: 2.5, md: 3 },
                        bgcolor: "action.hover",
                        border: "1px solid",
                        borderColor: "divider",
                        boxShadow: "none",
                    }}
                >
                    {/* Description of the UN SDG 12 */}
                    <Chip label="UN SDG 12" color="primary" size="small" />
                    <Typography
                        variant="h5"
                        component="h2"
                        sx={{ mt: 1.5, mb: 2 }}
                    >
                        Responsible consumption and production
                    </Typography>
                    <Grid container spacing={2.5}>
                        {SDG_TARGETS.map((target) => (
                            <Grid key={target.id} size={{ xs: 12, md: 6 }}>
                                <Typography variant="subtitle1" component="h3">
                                    Target {target.id} — {target.title}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                >
                                    {target.text}{" "}
                                    <Link
                                        href={target.source}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        underline="hover"
                                    >
                                        Go to source
                                    </Link>
                                </Typography>
                            </Grid>
                        ))}
                    </Grid>
                </Card>
            </Box>
            {/* Why this project matters, and how it contributes to the UN SDGs */}
            <Box component="section">
                <Typography variant="h5" component="h2" gutterBottom>
                    Why this project matters
                </Typography>
                <Stack spacing={2}>
                    {WHY_THIS_PROJECT.map((item, index) => (
                        <Stack key={item.title} direction="row" spacing={2}>
                            <Box
                                sx={{
                                    width: 32,
                                    height: 32,
                                    flexShrink: 0,
                                    borderRadius: "50%",
                                    bgcolor: "primary.main",
                                    color: "primary.contrastText",
                                    display: "grid",
                                    placeItems: "center",
                                    fontSize: 14,
                                    fontWeight: 700,
                                }}
                            >
                                {toRomanNumeral(index + 1)}
                            </Box>
                            <Box>
                                <Typography variant="subtitle1" component="h3">
                                    {item.title}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                >
                                    {item.text}
                                </Typography>
                            </Box>
                        </Stack>
                    ))}
                </Stack>
            </Box>
        </Box>
    );
}
