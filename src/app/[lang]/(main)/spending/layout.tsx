import { initLingui } from "@/initLingui";

import { PageLangParam } from "@/initLingui";
import { useLingui } from "@lingui/react/macro";
import { PropsWithChildren } from "react";

export async function generateMetadata(props: PropsWithChildren<PageLangParam>) {
  const lang = (await props.params).lang
  initLingui(lang)

  const { t } = useLingui()
  return {
    title: t`Government Workforce & Spending Data | See the Breakdown`,
    description: t`See how Canada's government spends tax dollars—track workforce data, spending trends, and federal debt with clear, non-partisan insights.`,
  }
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (<>
    {children}
  </>);
}
