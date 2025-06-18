'use client';

import Link from "next/link";
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';
import { SearchResult } from '../types/search';
import { formatCurrency } from '../utils/csvUtils';
import { cn } from '@/lib/utils';

// Rename Hit to HitCard for clarity, or keep as Hit if preferred
export function HitCard({ hit }: { hit: SearchResult }) {
  const typeSlug = hit.type?.split('/')[1] ?? 'unknown';
  // Use objectID provided by InstantSearch for unique key in lists/maps
  const href = `/search/${typeSlug}/${hit.key || hit.objectID}`;
  const displayRecipient = hit.vendor_name || hit.recipient;
  const formattedAmount = formatCurrency(hit.amount);
  const isAggregated = hit.is_aggregated; // Check the flag

  // Define card content separately to avoid repetition
  const cardContent = (
    <Card className={cn(
      "w-full mb-4 transition-shadow duration-200",
      (href || hit.source_url) && "hover:shadow-md"
    )}>
      <CardHeader>
        <CardTitle className="flex justify-between text-lg">
          <h2>{displayRecipient}</h2>
          <b className="text-blue-600 tabular-nums">${formattedAmount}</b> {/* Added tabular-nums */}
        </CardTitle>
        <p className="text-sm text-gray-700">{hit.payer}</p>
        <p className="text-sm text-gray-500">{hit.program} {hit.timestamp && <span>({hit.timestamp})</span>}</p>
      </CardHeader>
      <CardContent>
        <p className="whitespace-pre-wrap line-clamp-6 text-gray-800">{(hit.description || "").replace(/\\n/g, "\n\n")}</p>
      </CardContent>
    </Card>
  );

  // Conditionally wrap with Link or <a>
  if (isAggregated) {
    return hit.source_url ? (
      <a href={hit.source_url} target="_blank" rel="noopener noreferrer" className="block"> {/* Added block class */} 
        {cardContent}
      </a>
    ) : (
      cardContent // Render card without link if no source_url
    );
  } else {
    // Link to internal detail page for non-aggregated
    return <Link href={href}>{cardContent}</Link>;
  }
} 