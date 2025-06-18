// @ts-nocheck

import { PrismaClient } from '../src/generated/prisma'
import fs from 'fs'
import path from 'path'
import { parse } from 'csv-parse/sync'

const prisma = new PrismaClient()

const ROOT = path.resolve(__dirname, '..')
const REV_CSV = path.join(ROOT, 'clean_revenue_2024.csv')
const EXP_CSV = path.join(ROOT, 'clean_expenses_2024.csv')

async function main() {
  // fetch root ids
  const incomeRoot = await prisma.flow_edge.findFirst({ where: { item: 'Income', fiscal_year: 2024 } })
  const expenseRoot = await prisma.flow_edge.findFirst({ where: { item: 'Expenses', fiscal_year: 2024 } })
  if (!incomeRoot || !expenseRoot) {
    throw new Error('Root rows for 2024 missing. Please insert Income and Expenses roots first.')
  }

  // in-memory cache parentId+item -> id
  const nodeCache = new Map<string, bigint>()
  nodeCache.set(`root-income`, BigInt(incomeRoot.id))
  nodeCache.set(`root-expense`, BigInt(expenseRoot.id))

  // helper to get or create child node
  async function getNode(parentId: number, item: string, itemType: 'revenue' | 'expense'): Promise<number> {
    const key = `${parentId}-${item}`
    if (nodeCache.has(key)) return nodeCache.get(key)!
    const created = await prisma.flow_edge.create({
      data: {
        item,
        amount: 0,
        parent_id: parentId,
        fiscal_year: 2024,
        item_type: itemType,
        jurisdiction: 'Ontario'
      },
      select: { id: true }
    })
    nodeCache.set(key, BigInt(created.id))
    return created.id
  }

  // process revenue csv
  const revCsv = fs.readFileSync(REV_CSV, 'utf8')
  const revRows: any[] = parse(revCsv, { columns: true, skip_empty_lines: true })
  const revInserts: any[] = []
  for (const r of revRows) {
    const revType = r['revenue_type'] as string
    const revDetail = r['revenue_detail'] as string
    const amt = r['amount_dollars']
    if (!revType || !revDetail || !amt) continue
    const typeNodeId = await getNode(incomeRoot.id, revType, 'revenue')
    revInserts.push({
      item: revDetail,
      amount: amt,
      parent_id: typeNodeId,
      fiscal_year: 2024,
      item_type: 'revenue' as const,
      jurisdiction: 'Ontario'
    })
  }

  // process expense csv
  const expCsv = fs.readFileSync(EXP_CSV, 'utf8')
  const expRows: any[] = parse(expCsv, { columns: true, skip_empty_lines: true })
  const expInserts: any[] = []
  for (const row of expRows) {
    const pathParts = [
      row['Ministry Name'],
      row['Expenditure Category (Operating / Capital)'],
      row['Program Name'],
      row['Activity / Item'],
      row['Sub Item'],
      row['Standard Account (Expense/Asset Name)'],
      row['Account Details (Expense/Asset Details)']
    ].filter((p: string) => p && p.length > 0)
    let parentId = expenseRoot.id
    for (let i = 0; i < pathParts.length - 1; i++) {
      parentId = await getNode(parentId, pathParts[i], 'expense')
    }
    const leafItem = pathParts[pathParts.length - 1] || 'Unlabelled'
    const amt = row['amount_dollars']
    expInserts.push({
      item: leafItem,
      amount: amt,
      parent_id: parentId,
      fiscal_year: 2024,
      item_type: 'expense' as const,
      jurisdiction: 'Ontario'
    })
  }

  console.log(`Prepared ${revInserts.length} revenue leaves and ${expInserts.length} expense leaves.`)

  // batch insert
  if (revInserts.length) {
    await prisma.flow_edge.createMany({ data: revInserts, skipDuplicates: true })
  }
  if (expInserts.length) {
    const batchSize = 1000
    for (let i = 0; i < expInserts.length; i += batchSize) {
      await prisma.flow_edge.createMany({ data: expInserts.slice(i, i + batchSize), skipDuplicates: true })
    }
  }

  console.log('Insertion complete.')
}

main()
  .catch(err => { console.error(err); process.exit(1) })
  .finally(() => prisma.$disconnect()) 