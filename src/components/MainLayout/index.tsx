"use client";
import { Footer } from "@/components/MainLayout/Footer";
import { Trans, useLingui } from "@lingui/react/macro";
import Image from "next/image";
import Link from "next/link";
import logoFull from "./logo-full.svg";
import logoGlyph from "./logo-glyph.svg";
import { useState, memo } from "react";
import { X, Menu } from "lucide-react";
import { usePathname } from 'next/navigation';

// Memoize NavLink
const NavLink = memo(({ href, children, active = false }: { href: string, children: React.ReactNode, active?: boolean }) => {
	return (
		<Link
			href={href}
			className={`relative py-2 text-sm font-medium ${
				active
					? "text-black after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-black"
					: "text-gray-600 hover:text-black"
			}`}
		>
			{children}
		</Link>
	);
});
NavLink.displayName = 'NavLink'; // Add display name for better debugging

export const MainLayout = ({ children }: { children: React.ReactNode }) => {
	const { t, i18n } = useLingui();
	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const pathname = usePathname();

	return (
		<>
			<div className="sticky z-[100] border-b-gray-200 border-b-2 w-full border-solid px-4 sm:px-12 py-0">
				<div className="w-full max-w-6xl mx-auto">
					<div className="items-stretch auto-cols-fr justify-between flex min-h-16 gap-2 sm:gap-8 m-auto">
						<Link
							className="items-center float-left justify-center flex pl-0"
							href={`/${i18n.locale}`}
						>
							<Image
								className="cursor-pointer align-middle w-40 h-12 max-w-full hidden sm:block"
								alt="Canada Spends Logo"
								src={logoFull}
							/>
							<Image
								className="cursor-pointer align-middle inline-block w-40 h-12 max-w-full sm:hidden min-w-[75px]"
								alt="Canada Spends Logo"
								src={logoGlyph}
							/>
						</Link>
						{/* Desktop Navigation */}
						<nav className="hidden md:flex items-center space-x-8">
							<NavLink href={`/${i18n.locale}/spending`} active={pathname === `/${i18n.locale}/spending`}>
								<Trans>Government Spending</Trans>
							</NavLink>
							<NavLink href={`/${i18n.locale}/search`} active={pathname === `/${i18n.locale}/search`}>
								<Trans>Spending Database</Trans>
							</NavLink>
							<NavLink href={`/${i18n.locale}/about`} active={pathname === `/${i18n.locale}/about`}>
								<Trans>About</Trans>
							</NavLink>
							<NavLink href={`/${i18n.locale}/contact`} active={pathname === `/${i18n.locale}/contact`}>
								<Trans>Contact</Trans>
							</NavLink>
						</nav>
						{/* Mobile menu button */}
						<div className="flex md:hidden">
							<button type="button" className="p-2 text-gray-700" onClick={() => setIsMenuOpen(!isMenuOpen)}>
								<span className="sr-only">{isMenuOpen ? "Close menu" : "Open menu"}</span>
								{isMenuOpen ? (
									<X className="h-6 w-6" aria-hidden="true" />
								) : (
									<Menu className="h-6 w-6" aria-hidden="true" />
								)}
							</button>
						</div>
					</div>
				</div>
			</div>
			{/* Mobile menu */}
			{isMenuOpen && (
				<div className="md:hidden border-t border-gray-200">
					<div className="px-2 pt-2 pb-3 space-y-1">
						<MobileNavLink href={`/${i18n.locale}/spending`} active={pathname === `/${i18n.locale}/spending`}>
							<Trans>Government Spending</Trans>
						</MobileNavLink>
						<MobileNavLink href={`/${i18n.locale}/search`} active={pathname === `/${i18n.locale}/search`}>
							<Trans>Spending Database</Trans>
						</MobileNavLink>
						<MobileNavLink href={`/${i18n.locale}/about`} active={pathname === `/${i18n.locale}/about`}>
							<Trans>About</Trans>
						</MobileNavLink>
						<MobileNavLink href={`/${i18n.locale}/contact`} active={pathname === `/${i18n.locale}/contact`}>
							<Trans>Contact</Trans>
						</MobileNavLink>
					</div>
				</div>
			)}
			<div>
				<div className="min-h-full items-center flex-col justify-between overflow-clip">
					<div className="w-full max-w-[120.00rem] m-auto">
						<main >
							{children}
						</main>
					</div>
				</div>
			</div>
			<Footer />
		</>
	);
};

interface NavLinkProps {
	href: string;
	children: React.ReactNode;
	active?: boolean;
}

// Memoize MobileNavLink
const MobileNavLink = memo(({ href, children, active = false }: NavLinkProps) => {
	return (
		<Link
			href={href}
			className={`block px-3 py-2 text-base font-medium ${active ? "text-black" : "text-gray-600 hover:text-black"}`}
		>
			{children}
		</Link>
	);
});
MobileNavLink.displayName = 'MobileNavLink'; // Add display name
