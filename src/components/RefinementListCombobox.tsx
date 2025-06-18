'use client';

import { useState, useEffect, ReactNode } from 'react';
import { useRefinementList } from 'react-instantsearch';
import { RefinementListComboboxProps } from '../types/search'; // Import the type
import { Badge } from "@/components/badge";
import { ChevronsUpDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/command";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/popover";

// --- RefinementListCombobox Component --- 
export function RefinementListCombobox({ attribute, placeholder, width, popoverWidth, sortBy }: RefinementListComboboxProps) {
  const { 
    items,
    refine,
    searchForItems,
  } = useRefinementList({ 
    attribute, 
    limit: 30, 
    sortBy: sortBy 
  });

  const [open, setOpen] = useState(false)
  const refinedItems = items.filter(i => i.isRefined)
  const refinedItem = refinedItems.length > 0 ? refinedItems[0] : null

  const [_search, setSearch] = useState("")
  const [searchChanged, setSearchChanged] = useState(false)
  const [cachedItems, setCachedItems] = useState(items)

  const searchItems = (value: string) => {
    setSearch(value)
    searchForItems(value)
    setSearchChanged(true)
  }

  useEffect(() => {
    if (searchChanged) {
      setCachedItems(items)
    } else {
      setCachedItems(items)
    }
  }, [items, searchChanged])

  useEffect(() => {
    if (!open) {
      setCachedItems(items);
      setSearchChanged(false);
    }
  }, [open, items]);

  let label: ReactNode = refinedItem?.label ?? ""
  if (refinedItems.length > 1) {
    label = <span>{label}<Badge variant="outline" className="ml-1 text-[10px]">{`+${refinedItems.length - 1}`} more</Badge></span>
  }

  return (
    <Popover open={open} onOpenChange={(isOpen) => {
      setOpen(isOpen)
      if (!isOpen) {
        searchItems("")
      }
    }}>
      <PopoverTrigger asChild>
        <Button variant="outline" role="combobox" aria-expanded={open} className={cn("w-full pr-2 justify-between", width)}>
          <span className="overflow-hidden whitespace-nowrap text-ellipsis">
            {refinedItem ? label : placeholder}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className={cn("w-full p-0", popoverWidth || "w-[300px]")}>
        <Command shouldFilter={false}>
          <CommandInput placeholder="Search..." className="h-9" onValueChange={searchItems} />
          <CommandList>
            <CommandEmpty>No results found.</CommandEmpty>
            <CommandGroup>
              {cachedItems.map((item) => (
                <CommandItem
                  key={item.value}
                  value={item.value}
                  onSelect={() => {
                    setSearchChanged(false);
                    refine(item.value);
                    // Keep popover open for multi-select or close if desired:
                    // setOpen(false);
                  }}
                  className="flex justify-between"
                >
                  <span className="flex gap-1 items-center">
                    <Check className={cn("ml-n1 h-4 w-4", items.find((i) => i.value === item.value)?.isRefined ? "opacity-100" : "opacity-0")} />
                    {item.label}
                  </span>
                  <Badge variant="outline" className="text-[9px] text-gray-500">{item.count}</Badge>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
} 