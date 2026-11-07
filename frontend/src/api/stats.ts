import api from "../api";
import type { Stats, StatsParams } from "../types/stats";

const USE_MOCK = false;

function buildMockStats(): Stats {
    return {
        bowl_count: 67,
        average_waste_percent: 40.299,
        total_waste_kg: 8.36,
        average_waste_kg: 0.125,

        daily: [
            {
                date: "2026-10-26",
                bowl_count: 10,
                average_waste_percent: 50,
                total_waste_kg: 1.61,
                average_waste_kg: 0.161,
            },
            {
                date: "2026-10-27",
                bowl_count: 9,
                average_waste_percent: 47.222,
                total_waste_kg: 1.23,
                average_waste_kg: 0.137,
            },
            {
                date: "2026-10-28",
                bowl_count: 11,
                average_waste_percent: 25,
                total_waste_kg: 0.86,
                average_waste_kg: 0.078,
            },
            {
                date: "2026-10-29",
                bowl_count: 8,
                average_waste_percent: 40.625,
                total_waste_kg: 1.05,
                average_waste_kg: 0.131,
            },
            {
                date: "2026-10-30",
                bowl_count: 9,
                average_waste_percent: 41.667,
                total_waste_kg: 1.2,
                average_waste_kg: 0.133,
            },
            {
                date: "2026-10-31",
                bowl_count: 10,
                average_waste_percent: 45,
                total_waste_kg: 1.35,
                average_waste_kg: 0.135,
            },
            {
                date: "2026-11-01",
                bowl_count: 10,
                average_waste_percent: 35,
                total_waste_kg: 1.06,
                average_waste_kg: 0.106,
            },
        ],

        dishes: [
            {
                dish_id: 1,
                dish_name: "Chicken rice",
                bowl_count: 25,
                average_waste_percent: 39,
                total_waste_kg: 3.9,
                average_waste_kg: 0.156,
                daily: [
                    {
                        date: "2026-10-26",
                        bowl_count: 4,
                        average_waste_percent: 56.25,
                        total_waste_kg: 0.9,
                        average_waste_kg: 0.225,
                    },
                    {
                        date: "2026-10-27",
                        bowl_count: 3,
                        average_waste_percent: 33.333,
                        total_waste_kg: 0.4,
                        average_waste_kg: 0.133,
                    },
                    {
                        date: "2026-10-28",
                        bowl_count: 4,
                        average_waste_percent: 25,
                        total_waste_kg: 0.4,
                        average_waste_kg: 0.1,
                    },
                    {
                        date: "2026-10-29",
                        bowl_count: 3,
                        average_waste_percent: 50,
                        total_waste_kg: 0.6,
                        average_waste_kg: 0.2,
                    },
                    {
                        date: "2026-10-30",
                        bowl_count: 4,
                        average_waste_percent: 43.75,
                        total_waste_kg: 0.7,
                        average_waste_kg: 0.175,
                    },
                    {
                        date: "2026-10-31",
                        bowl_count: 3,
                        average_waste_percent: 41.667,
                        total_waste_kg: 0.5,
                        average_waste_kg: 0.167,
                    },
                    {
                        date: "2026-11-01",
                        bowl_count: 4,
                        average_waste_percent: 25,
                        total_waste_kg: 0.4,
                        average_waste_kg: 0.1,
                    },
                ],
                waste_bucket_distribution: {
                    "0": 5,
                    "25": 9,
                    "50": 4,
                    "75": 6,
                    "100": 1,
                },
            },
            {
                dish_id: 3,
                dish_name: "Curry vegetables",
                bowl_count: 18,
                average_waste_percent: 44.444,
                total_waste_kg: 2.24,
                average_waste_kg: 0.124,
                daily: [
                    {
                        date: "2026-10-26",
                        bowl_count: 3,
                        average_waste_percent: 41.667,
                        total_waste_kg: 0.35,
                        average_waste_kg: 0.117,
                    },
                    {
                        date: "2026-10-27",
                        bowl_count: 2,
                        average_waste_percent: 62.5,
                        total_waste_kg: 0.35,
                        average_waste_kg: 0.175,
                    },
                    {
                        date: "2026-10-28",
                        bowl_count: 3,
                        average_waste_percent: 33.333,
                        total_waste_kg: 0.28,
                        average_waste_kg: 0.093,
                    },
                    {
                        date: "2026-10-29",
                        bowl_count: 2,
                        average_waste_percent: 37.5,
                        total_waste_kg: 0.21,
                        average_waste_kg: 0.105,
                    },
                    {
                        date: "2026-10-30",
                        bowl_count: 2,
                        average_waste_percent: 25,
                        total_waste_kg: 0.14,
                        average_waste_kg: 0.07,
                    },
                    {
                        date: "2026-10-31",
                        bowl_count: 3,
                        average_waste_percent: 58.333,
                        total_waste_kg: 0.49,
                        average_waste_kg: 0.163,
                    },
                    {
                        date: "2026-11-01",
                        bowl_count: 3,
                        average_waste_percent: 50,
                        total_waste_kg: 0.42,
                        average_waste_kg: 0.14,
                    },
                ],
                waste_bucket_distribution: {
                    "0": 4,
                    "25": 3,
                    "50": 6,
                    "75": 3,
                    "100": 2,
                },
            },
            {
                dish_id: 2,
                dish_name: "Noodles",
                bowl_count: 24,
                average_waste_percent: 38.542,
                total_waste_kg: 2.22,
                average_waste_kg: 0.093,
                daily: [
                    {
                        date: "2026-10-26",
                        bowl_count: 3,
                        average_waste_percent: 50,
                        total_waste_kg: 0.36,
                        average_waste_kg: 0.12,
                    },
                    {
                        date: "2026-10-27",
                        bowl_count: 4,
                        average_waste_percent: 50,
                        total_waste_kg: 0.48,
                        average_waste_kg: 0.12,
                    },
                    {
                        date: "2026-10-28",
                        bowl_count: 4,
                        average_waste_percent: 18.75,
                        total_waste_kg: 0.18,
                        average_waste_kg: 0.045,
                    },
                    {
                        date: "2026-10-29",
                        bowl_count: 3,
                        average_waste_percent: 33.333,
                        total_waste_kg: 0.24,
                        average_waste_kg: 0.08,
                    },
                    {
                        date: "2026-10-30",
                        bowl_count: 3,
                        average_waste_percent: 50,
                        total_waste_kg: 0.36,
                        average_waste_kg: 0.12,
                    },
                    {
                        date: "2026-10-31",
                        bowl_count: 4,
                        average_waste_percent: 37.5,
                        total_waste_kg: 0.36,
                        average_waste_kg: 0.09,
                    },
                    {
                        date: "2026-11-01",
                        bowl_count: 3,
                        average_waste_percent: 33.333,
                        total_waste_kg: 0.24,
                        average_waste_kg: 0.08,
                    },
                ],
                waste_bucket_distribution: {
                    "0": 3,
                    "25": 11,
                    "50": 6,
                    "75": 2,
                    "100": 2,
                },
            },
        ],
    };
}

export async function getStats(params: StatsParams): Promise<Stats> {
    if (USE_MOCK) return buildMockStats();
    const { data } = await api.get<Stats>("/api/wastes/stats", { params });
    return data;
}
