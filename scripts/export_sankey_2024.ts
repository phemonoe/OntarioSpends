#!/usr/bin/env tsx
// @ts-nocheck
/**
 * Export Sankey JSON for fiscal-year 2024 from the flow_edge table.
 * Writes to public/data/sankey_2024.json so the front-end can fetch it as a static asset.
 */
import { PrismaClient } from "@/generated/prisma";
import fs from "fs";
import path from "path";

(async () => {
  const prisma = new PrismaClient();
  const year = 2024;

  const rows = await prisma.flow_edge.findMany({
    where: { fiscal_year: year },
    select: {
      id: true,
      parent_id: true,
      item: true,
      amount: true,
      item_type: true,
    },
  });

  const incomeRoot = rows.find((r) => r.parent_id === null && r.item === "Income");
  const expenseRoot = rows.find((r) => r.parent_id === null && r.item === "Expenses");
  if (!incomeRoot || !expenseRoot) {
    throw new Error("Root rows missing");
  }

  // Build parent map
  const byParent = new Map<string, any[]>();
  rows.forEach((r) => {
    const key = r.parent_id === null ? "root" : r.parent_id.toString();
    const list = byParent.get(key) ?? [];
    list.push(r);
    byParent.set(key, list);
  });
  const build = (parentKey: string): any[] => {
    return (byParent.get(parentKey) ?? []).map((row) => {
      const children = build(row.id.toString());
      return children.length
        ? { name: row.item, children }
        : { name: row.item, amount: Number(row.amount ?? 0) / 1_000_000_000 };
    });
  };

  let revenueTotal = 0;
  let spendingTotal = 0;
  rows.forEach((r) => {
    const amt = Number(r.amount ?? 0) / 1_000_000_000;
    if (r.item_type === "revenue") revenueTotal += amt;
    else spendingTotal += amt;
  });

  const payload = {
    total: revenueTotal - spendingTotal,
    revenue: revenueTotal,
    spending: spendingTotal,
    revenue_data: { name: "Revenue", children: build(incomeRoot.id.toString()) },
    spending_data: { name: "Spending", children: build(expenseRoot.id.toString()) },
  };

  const outDir = path.join(process.cwd(), "public", "data");
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `sankey_${year}.json`);
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2));
  console.log(`✅ Wrote ${outPath}`);

  await prisma.$disconnect();
})(); 