"use client"

import { ExternalLink } from "@/components/Layout";
import { useFormState } from "@/hooks/useFormState";
import { Trans, useLingui } from "@lingui/react/macro";
import { cx } from "class-variance-authority";
import Image from "next/image";
import { useState } from "react";
import { FaXTwitter } from "react-icons/fa6";
import { useLocalStorage } from 'usehooks-ts';
import logoText from "./logo-text.svg";


const Subscribe = () => {
	const { t } = useLingui()
	const [subscribed, setSubcribed] = useLocalStorage('subscribed_newsletter', false)
	const [loading, setLoading] = useState(false)
	const [formState, { email }] = useFormState({
		email: ''
	})

	const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setLoading(true)
		await fetch('/api/newsletter', {
			method: 'POST',
			body: JSON.stringify({ email: formState.email, utmSource: 'CanadaSpends', utmMedium: 'organic', utmCampaign: 'footer' }),
		});
		setLoading(false)
		setSubcribed(true)
	}


	return <div className="mt-10 xl:mt-0">
		<h3 className="text-sm/6 font-semibold text-gray-900"><Trans>Subscribe to our newsletter</Trans></h3>

		{subscribed ? (
			<p className="mt-2 text-sm/6 text-gray-600">
				<Trans>Thank you for subscribing!</Trans>
			</p>
		) : (<>
			<p className="mt-2 text-sm/6 text-gray-600">
				<Trans>Get the facts weekly, right in your inbox.</Trans>
			</p>
			<form className={cx("mt-6 sm:flex sm:max-w-md", loading && "opacity-50")} onSubmit={onSubmit}>
				<label htmlFor="email-address" className="sr-only">
					<Trans>Email address</Trans>
				</label>
				<input
					disabled={loading}
					{...email('email')}
					required
					placeholder={t`Enter your email`}
					autoComplete="email"
					className="w-full min-w-0 bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:w-64 sm:text-sm/6 xl:w-full"
				/>
				<div className="mt-4 sm:ml-4 sm:mt-0 sm:shrink-0">
					<button
						disabled={loading}
						type="submit"
						className="flex w-full items-center justify-center bg-indigo-950 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
					>
						<Trans>Subscribe</Trans>
					</button>
				</div>
			</form>
		</>
		)}
	</div>
}

export const Footer = () => {
	return (
		<footer className="border-t-gray-200 border-t-2 border-solid">
			<div className="w-full max-w-6xl mx-auto px-4 sm:px-6 ">
				<div className="mx-auto max-w-7xl px-6 pb-8 pt-20 sm:pt-24 lg:px-8 lg:pt-32">
					<div className="xl:grid xl:grid-cols-3 xl:gap-8">
						<div className="grid grid-cols-2 gap-8 xl:col-span-2">
							<div className="md:grid md:grid-cols-2 md:gap-8">
								<div>
									<Image src={logoText} alt="Canada Spends Logo" height={300} />
									<ul role="list" className="mt-6 space-y-4">
										<li>
											<a href="/spending" className="text-sm/6 text-gray-600 hover:text-gray-900">
												<Trans>Spending</Trans>
											</a>
										</li>
										<li>
											<a href="/about" className="text-sm/6 text-gray-600 hover:text-gray-900">
												<Trans>About</Trans>
											</a>
										</li>
										<li>
											<a href="/contact" className="text-sm/6 text-gray-600 hover:text-gray-900">
												<Trans>Contact</Trans>
											</a>
										</li>
									</ul>
								</div>
							</div>
						</div>
						<Subscribe />
					</div>

					<div className="mt-16 border-t border-gray-900/10 pt-8 sm:mt-20 md:flex md:items-center md:justify-between lg:mt-24">
						<div className="flex gap-x-6 md:order-2">
							<ExternalLink href="https://x.com/canada_spends" className="text-gray-600 hover:text-gray-800">
								<span className="sr-only">X</span>
								<FaXTwitter aria-hidden="true" className="size-6" />
							</ExternalLink>
						</div>
						<p className="mt-8 text-sm/6 text-gray-600 md:order-1 md:mt-0">
							<Trans>&copy; 2025 Canada Spends. All rights reserved. A Project of <ExternalLink href="https://www.buildcanada.com" className="underline text-gray-900 font-bold">Build Canada</ExternalLink>.</Trans>
						</p>
					</div>
				</div>
			</div>
		</footer>
	);
};
