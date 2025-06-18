import { cn } from "@/lib/utils";
import React from 'react';

interface StatCardProps {
  title: string | React.ReactNode;
  value: string | React.ReactNode;
  subtitle: string | React.ReactNode;
  className?: string;
  animationDelay?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  className,
  animationDelay = "fade-in-delay-1"
}) => {
  return (
    <div className={cn(
      "bg-white rounded-xl p-6 shadow-stat transition-all duration-300 hover:shadow-lg fade-in",
      animationDelay,
      className
    )}>
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <div className="flex flex-col space-y-1">
        <p className="text-4xl font-bold tracking-tight stat-highlight inline-block">{value}</p>
        <p className="text-sm text-gray-500">{subtitle}</p>
      </div>
    </div>
  );
};

export const StatCardContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 ">
      {children}
    </div>
  );
};