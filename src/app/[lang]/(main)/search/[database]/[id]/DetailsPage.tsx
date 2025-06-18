import {ReactNode} from "react";
import {Badge} from "@/components/badge";
import BackButton from "./BackButton";

interface DetailsPageProps {
  type: string;
  program: string;
  award_amount: number;
  source_url: string;
  fiscal_year: string;
  title: string;
  recipient: string;
  summary: string;
  children: ReactNode;
  keywords?: string[];
  reference_number?: string;
  database?: string;
  vendor_name?: string;
}

export async function DetailsPage({
  type,
  summary,
  program,
  title,
  award_amount,
  fiscal_year,
  source_url,
  recipient,
  keywords = [],
  children = null,
  reference_number,
  database,
  vendor_name,
}: DetailsPageProps) {
  let finalSourceUrl = source_url;

  if (database === 'contracts-over-10k' && reference_number && vendor_name) {
    const encodedRef = encodeURIComponent(reference_number);
    // Double-encode vendor_name because the API's `filters` parameter
    // is URL-encoded as a whole, and nested values must be pre-encoded
    // to preserve reserved characters (e.g., "|", ":").
    const encodedVendor = encodeURIComponent(encodeURIComponent(vendor_name));
    const filters = `reference_number%3A${encodedRef}%7Cvendor_name%3A${encodedVendor}`;
    finalSourceUrl = `${source_url}?filters=${filters}`;
  }

  // Simplified link text
  const linkText = "View source data";

  return (
    <main className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-semibold leading-tight max-w-2xl">
          {type}: {program}
        </h1>
        <BackButton />
      </div>
      <div className="rounded-2xl border p-6 shadow-sm bg-white">
        <div className="flex justify-between items-start mb-2">
          <h2 className="text-2xl font-bold">{recipient}</h2>
          <div className="text-right text-lg font-bold text-blue-600 whitespace-nowrap tabular-nums">
            ${Number(award_amount).toLocaleString()}
          </div>
        </div>
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="text-xs text-gray-500 mb-4 font-bold">FY {fiscal_year}</p>
        <div className="font-bold text-gray-900">Summary</div>
        <div className="text-sm text-gray-700 mb-4 whitespace-pre-wrap">
          {(summary || '—')}
        </div>
        <div className="grid md:grid-cols-2 grid-cols-1 gap-x-8 gap-y-2 text-sm">
          {children}
        </div>
        {keywords.length > 0 && (
          <>
            <div className="font-bold text-gray-900 mt-2">Keywords</div>
            <div>
              {keywords.map((kw: string) => (
                <Badge className="mr-1" variant="outline" key={kw}>{kw}</Badge>
              ))}
            </div>
          </>
        )}
        {finalSourceUrl && (
          <div className="mt-6">
            <a href={finalSourceUrl} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              {linkText}
            </a>
          </div>
        )}
      </div>
    </main>
  )
}