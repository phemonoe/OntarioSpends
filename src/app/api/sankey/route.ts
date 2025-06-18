// @ts-nocheck
import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { PrismaClient } from "@/generated/prisma";

const prisma = new PrismaClient();

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const year = parseInt(searchParams.get("year") ?? "2024", 10);

  // 1. Try static file first (public/data/sankey_<year>.json)
  const staticPath = path.join(process.cwd(), "public", "data", `sankey_${year}.json`);
  if (fs.existsSync(staticPath)) {
    const json = fs.readFileSync(staticPath, "utf-8");
    return new NextResponse(json, { headers: { "Content-Type": "application/json" } });
  }

  // 2. Fallback to live query if file not present
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
    return NextResponse.json({ error: "Root rows missing" }, { status: 404 });
  }

  const byParent = new Map<string, any[]>();
  rows.forEach((r) => {
    const key = r.parent_id === null ? "root" : r.parent_id.toString();
    const list = byParent.get(key) ?? [];
    list.push(r);
    byParent.set(key, list);
  });

  function build(parentKey: string): any[] {
    return (byParent.get(parentKey) ?? []).map((row) => {
      const children = build(row.id.toString());
      return children.length
        ? { name: row.item, children }
        : { name: row.item, amount: Number(row.amount ?? 0) / 1_000_000_000 };
    });
  }

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

  return NextResponse.json(payload);
} 