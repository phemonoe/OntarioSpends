import { H1, H2, Intro, Page, PageContent, Section } from "@/components/Layout";
import { initLingui, PageLangParam } from "@/initLingui";
import { Trans, useLingui } from "@lingui/react/macro";
import { PropsWithChildren } from "react";
import { Contributors } from "./contributors";
import FAQ from "./faq";


export async function generateMetadata(props: PropsWithChildren<PageLangParam>) {
  const lang = (await props.params).lang
  initLingui(lang)

  const { t } = useLingui()
  return {
    title: t`Making Government Spending Clear | About Us | Canada Spends`,
    description: t`We don't tell you what to think—we give you the facts. Meet the team making government spending data accessible to all Canadians.`,
  }
}


export default async function About(props: PropsWithChildren<PageLangParam>) {
  const lang = (await props.params).lang
  initLingui(lang)

  return (
    <Page>

      <PageContent>
        <Section>
          <H1><Trans>Canada, you need the facts.</Trans></H1>
          <Intro>
            <Trans>Every year, hundreds of billions of dollars move through the Government of Canada's budget. This data is technically available but the information is difficult to understand and spread across PDFs and databases that most Canadians don't know about.</Trans>
          </Intro>
          <Intro>
            <Trans>It doesn't have to be this way.</Trans>
          </Intro>
          <Intro>
            <Trans>Canada Spends is a platform to make government spending more transparent. We take raw data and transform it into easy to understand facts for Canadians. We don't tell you what to think. We don't weigh in on whether spending is good or bad. We give you the facts so you can decide for yourself.</Trans>
          </Intro>
          <Intro>
            <Trans>— Canada Spends Team</Trans>
          </Intro>
        </Section>

        <Section>
          <H2><Trans>Contributors / Supporters</Trans></H2>

          <Contributors />
        </Section>

        <Section>
          <H2><Trans>Frequently Asked Questions</Trans></H2>
          <FAQ />
        </Section>

      </PageContent >



    </Page >
  );
}
