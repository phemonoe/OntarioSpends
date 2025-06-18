"use client";

import { TenureChart } from "@/app/[lang]/(main)/spending/TenureChart";
import { BarChart } from "@/components/BarChart";
import { DepartmentList } from "@/components/DepartmentList";
import { ExternalLink, H1, H2, InternalLink, Intro, P, Page, PageContent, Section } from "@/components/Layout";
import NoSSR from "@/components/NoSSR";
import { Sankey } from "@/components/Sankey";
import { Trans, useLingui } from "@lingui/react/macro";

const StatBox = ({ title, value, description }: { title: React.ReactNode, value: string, description: React.ReactNode }) => (
	<div className="flex flex-col mr-8 mb-8">
		<div className="text-sm text-gray-600 mb-1">{title}</div>
		<div className="text-3xl font-bold mb-1">{value}</div>
		<div className="text-sm text-gray-600">{description}</div>
	</div>
);


const ageData = [
	{ name: '<20', Count: 1756 },
	{ name: '20-24', Count: 33596 },
	{ name: '25-29', Count: 78800 },
	{ name: '30-34', Count: 89426 },
	{ name: '35-39', Count: 187657 },
	{ name: '40-44', Count: 216806 },
	{ name: '45-49', Count: 216024 },
	{ name: '50-54', Count: 190226 },
	{ name: '55-59', Count: 146872 },
	{ name: '60-64', Count: 84865 },
	{ name: '65+', Count: 39494 },
]

export default function Spending() {
	const { t } = useLingui()
	return (
		<Page>
			<PageContent>
				<Section>
					<H1><Trans>Government Spending</Trans></H1>
					<Intro>
						<Trans>Get data-driven insights into how governmental revenue and spending affect Canadian lives and programs.</Trans>
					</Intro>
				</Section>
				<Section>
					<H2><Trans>FY 2024 Government Revenue and Spending</Trans></H2>
					<P>
						<Trans>Explore revenue and spending categories or filter by agency for deeper insights.</Trans>
					</P>
				</Section>
			</PageContent>
			<div className='sankey-chart-container relative overflow-hidden sm:(mr-0 ml-0) md:(min-h-[776px] min-w-[1280px] w-screen -ml-[50vw] -mr-[50vw] left-1/2 right-1/2)'>
				<NoSSR>
					<Sankey />
				</NoSSR>
				<div className="absolute bottom-3 left-6"><ExternalLink className="text-xs text-gray-400" href="https://www.canada.ca/en/public-services-procurement/services/payments-accounting/public-accounts/2024.html">Source</ExternalLink></div>
				<div className="absolute top-0 left-0 w-[100vw] h-full  backdrop-blur-sm z-10 text-white md:hidden flex items-center justify-center">
					<ExternalLink
						className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
						href="/spending-full-screen"
					>
						<Trans>View this chart in full screen</Trans>
					</ExternalLink>
				</div>
			</div>
			<PageContent>

				<Section>
					<H2><Trans>Government Workforce</Trans></H2>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
						<StatBox
							title={t`Headcount`}
							value="441,000"
							description={t`Total full-time equivalents`}
						/>

						<StatBox
							title={t`Departments + Agencies`}
							value="94"
							description={t`Federal organizations`}
						/>

						<StatBox
							title={t`Total Wages`}
							value="$65.3B"
							description={t`Annual payroll`}
						/>

						<div>
							<h3 className="font-medium mb-2"><Trans>Type of Tenure</Trans></h3>
							<p className="text-sm text-gray-600"><Trans>80% of employees are in permanent roles</Trans></p>
							<div className="mt-4">
								<NoSSR>
									<TenureChart />
								</NoSSR>
							</div>
						</div>

						<div>
							<h3 className="font-medium mb-2"><Trans>Age</Trans></h3>
							<p className="text-sm text-gray-600"><Trans>The average employee is 43.3 years old</Trans></p>
							<div className="mt-4">
								<NoSSR>
									<BarChart
										className="h-40"
										data={ageData}
										index="name"
										showLegend={false}
										categories={["Count"]}
										showGridLines={false}
										valueFormatter={(value) => Intl.NumberFormat('en-US', {
											notation: 'compact',
										}).format(Number(value))}
									/>
								</NoSSR>
							</div>
						</div>
						<div>
							<h3 className="font-medium mb-2"><Trans>Compensation per Employee</Trans></h3>
							<p className="text-sm text-gray-600"><Trans>The average employee makes $136,345/yr</Trans></p>
						</div>
						<P className="text-sm">
							<Trans>Sources:</Trans> <ExternalLink href="https://www.pbo-dpb.ca/en/additional-analyses--analyses-complementaires/BLOG-2425-009--personnel-expenditure-analysis-tool-update-2023-24-personnel-expenditures--mise-jour-outil-analyse-depenses-personnel-depenses-personnel-2023-2024"><Trans>PBO</Trans></ExternalLink>, <ExternalLink href="https://www.canada.ca/en/treasury-board-secretariat/services/innovation/human-resources-statistics/demographic-snapshot-federal-public-service-2023.html"><Trans>Treasury Board</Trans></ExternalLink>
						</P>
					</div>
				</Section>
				<Section>
					<H2><Trans>Government Departments explained</Trans></H2>
					<DepartmentList />
				</Section>
				<Section>
					<H2><Trans>Sources</Trans></H2>
					<P><Trans>All government spending data is sourced from official databases, but due to the complexity of these systems, occasional errors may occur despite our best efforts. We aim to make this information more accessible and accurate, and we welcome feedback. If you notice any issues, please let us know <InternalLink href="/contact">here</InternalLink> — we appreciate it and will work to address them promptly.</Trans></P>
				</Section>
			</PageContent>

		</Page>
	);
}
