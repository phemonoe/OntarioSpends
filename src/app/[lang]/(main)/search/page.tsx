import {ExternalLink, H1, Intro, P, Page, PageContent, Section} from "@/components/Layout";
import { Metadata } from "next";
import Search from "@/components/Search";
export const metadata: Metadata = {
  title: 'Spending Database | Canada Spends',
  description: 'A searchable database of federal spending data, consolidated from multiple open data sources.',
}


export default function Contact() {
  return (
    <Page>
      <PageContent className="sm:px-0 px-0">
        <Section className="px-6 mb-4">
          <H1>Federal Spending Database</H1>
          <Intro>
                Use this tool to search how the Government of Canada spends money. The data in this tool comes from multiple publicly available Government of Canada sources including 
                Grants and Contributions, Contracts over $10K, Contracts under $10K, and Research funding databases (SSHRC, NSERC, CIHR), Global Affairs Canada projects. 
                Type in one or more keywords and filter the results by year, department, or location to explore the data.
          </Intro>
          <div className="mt-6">
          </div>
        </Section>
        <Section className="sm:px-0 mb-4">
          <Search />
        </Section>
        <Section className="px-6 mb-4">
          <P className="text-xs text-gray-400">
While we make every effort to ensure accuracy, we rely on government-released information and cannot guarantee completeness or correctness. Users access and use this tool at their own risk, and Canada Spends is not responsible for any errors or omissions in the data.
          </P>
        </Section>
      </PageContent>
    </Page>
  )
}