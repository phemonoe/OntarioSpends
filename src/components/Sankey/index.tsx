"use client";
// @ts-nocheck

import { useEffect, useState } from "react";
import { SankeyChart } from "./SankeyChart";
import { SankeyData } from "./SankeyChartD3";

export function Sankey() {
	const [data, setData] = useState<SankeyData | null>(null);

	useEffect(() => {
		fetch("/data/sankey_2024_compact.json")
			.then((r) => r.json())
			.then((d) => setData(d));
	}, []);

	if (!data) return <div className="text-center py-10">Loading…</div>;

	return <SankeyChart data={data} />;
}
