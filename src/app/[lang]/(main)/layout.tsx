import { MainLayout } from "@/components/MainLayout";
import { initLingui, PageLangParam } from "@/initLingui";
import { PropsWithChildren } from "react";

export default async function RootLayout(props: PropsWithChildren<PageLangParam>) {
	const lang = (await props.params).lang
	initLingui(lang)
	return (
		<MainLayout>{props.children}</MainLayout>
	);
}
