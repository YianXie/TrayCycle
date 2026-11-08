import api from "../api/client";
import { MOCK_DATA } from "../mocks/data";
import type { Stats, StatsParams } from "../types/stats";

export async function getStats(params: StatsParams): Promise<Stats> {
    const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

    if (USE_MOCK) {
        return MOCK_DATA;
    }

    const { data } = await api.get<Stats>("/api/wastes/stats", { params });
    return data;
}
