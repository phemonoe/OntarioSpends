"use client"

import { InternalLink } from "@/components/Layout";
import { useDepartments } from "@/hooks/useDepartments";
import { Trans, useLingui } from "@lingui/react/macro";

interface DepartmentProps {
  name: string;
  slug: string;
}

const DepartmentItem = ({ name, slug }: DepartmentProps) => {
  const { i18n } = useLingui()
  return <div className="py-3 border-b border-gray-200">
    <InternalLink href={`/${i18n.locale}/spending/${slug}`} className="font-medium text-gray-600">{name}</InternalLink>
  </div>
}





export const DepartmentList = (props: { current?: string }) => {

  const departments = useDepartments()
  const BrowsableDepartment = departments.filter(d => !!d.href && !!d.slug).sort((a, b) => a.name.localeCompare(b.name)) as {
    name: string;
    slug: string;
  }[]

  return <div className="text-gray-600 leading-relaxed mb-4">
    {BrowsableDepartment.filter(d => {
      return (d.name !== props.current) || (d.slug !== props.current)
    }).map((department) => <DepartmentItem key={department.slug} {...department} />)}
    <div className="py-3 border-b border-gray-200">
      <Trans>More coming soon...</Trans>
    </div>
  </div>
}