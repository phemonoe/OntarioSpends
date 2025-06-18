'use client';

import { useHits } from 'react-instantsearch';
import Link from "next/link";
import { SearchResult } from '../types/search';
import { formatCurrency } from '../utils/csvUtils';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/table";
import { Button } from "@/components/button";

// --- ResultsTable Component --- 
export function ResultsTable() {
  const { hits } = useHits<SearchResult>();

  return (
    <div className="border rounded-md overflow-hidden mb-8">
      <Table className="table-fixed w-full">
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="w-[40%] pl-4 pr-2 sm:pl-6">Recipient / Department</TableHead>
            <TableHead className="w-[27%] hidden md:table-cell px-2">Program</TableHead>
            <TableHead className="w-[8%] hidden sm:table-cell px-2">Fiscal Year</TableHead>
            <TableHead className="w-[15%] text-right px-2">Amount</TableHead>
            <TableHead className="w-[10%] text-center px-2 pr-4 sm:pr-6">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {hits.map((hit) => {
            const typeSlug = hit.type?.split('/')[1] ?? 'unknown';
            const href = `/search/${typeSlug}/${hit.key || hit.objectID}`;
            const displayRecipient = hit.vendor_name || hit.recipient;
            const formattedAmount = formatCurrency(hit.amount);

            return (
              <TableRow key={hit.objectID} className="hover:bg-gray-50">
                <TableCell className="pl-4 pr-2 sm:pl-6">
                  <div className="max-w-md truncate">
                    <div className="font-medium truncate" title={displayRecipient}>{displayRecipient}</div>
                    <div className="text-sm text-gray-500 truncate" title={hit.payer}>
                      {hit.payer}
                    </div>
                  </div>
                </TableCell>
                <TableCell className="hidden md:table-cell max-w-[200px] truncate px-2" title={hit.program}>
                  {hit.program}
                </TableCell>
                <TableCell className="hidden sm:table-cell px-2">{hit.fiscal_year}</TableCell>
                <TableCell className="text-right font-medium text-blue-600 px-2 tabular-nums">${formattedAmount}</TableCell>
                <TableCell className="text-center px-2 pr-4 sm:pr-6">
                  {/* TODO: Link aggregated records to internal detail page once API/ID issue is resolved */}
                  {!hit.is_aggregated ? (
                    // Link to internal detail page for non-aggregated
                    <Link href={href} legacyBehavior={false}>
                      <Button variant="ghost" size="sm" className="h-8 px-2">
                        View
                      </Button>
                    </Link>
                  ) : (
                    // Link to external source_url for aggregated (temporary)
                    hit.source_url ? (
                      <a href={hit.source_url} target="_blank" rel="noopener noreferrer">
                        {/* Use same style/text as internal link button */}
                        <Button variant="ghost" size="sm" className="h-8 px-2">
                          View
                        </Button>
                      </a>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span> // Show N/A if no source_url
                    )
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
} 