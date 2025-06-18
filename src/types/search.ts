export interface SearchResult {
  key: string;
  type: string;
  recipient: string;
  vendor_name?: string;
  payer: string;
  fiscal_year: string;
  program: string;
  timestamp: string;
  amount: number;
  description: string;
  award_type: string;
  province?: string;
  country?: string;
  is_aggregated?: number;
  source_url?: string;
  objectID: string; // Keep objectID as it's used by InstantSearch internally
}

// Define more specific types for facet sorting
type FacetSortAttribute = "count" | "name" | "isRefined";
type FacetSortByDirection = `${FacetSortAttribute}:${'asc' | 'desc'}`;

export interface RefinementListComboboxProps {
  attribute: string;
  placeholder: string;
  width?: string;
  popoverWidth?: string;
  // Update sortBy to use the more specific type
  sortBy?: FacetSortByDirection[];
} 