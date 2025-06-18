import { P } from "@/components/Layout";
import { cn } from "@/lib/utils";
import Image, { StaticImageData } from "next/image";
import { FaLinkedin } from "react-icons/fa";
import { FaSquareXTwitter } from "react-icons/fa6";
import brendanSamek from './brendan_samek.jpeg';
import briceScheschuk from './brice_scheschuk.jpeg';
import joshHarris from './josh_harris.jpeg';
import lucyHargreaves from './lucy_hargreaves.jpeg';
import makSok from './mak_sok.jpeg';
import natalieLancaster from './natalie_lancaster.jpeg';
import shaneParrish from './shane_parrish.jpeg';
import toddScheidt from './todd_scheidt.jpeg';

const contributors: Contributor[] = [
  // {
  //   name: "Alfred Yang",
  //   photoSrc: alfredYang,
  //   linkedin_username: "alfredqy",
  //   x_username: "alfredqy",
  // },
  {
    name: "Brice Scheschuk",
    photoSrc: briceScheschuk,
    linkedin_username: "brice-scheschuk-cpa-ca-095721a",
    x_username: "scheschuk",
  },
  {
    name: 'Josh Harris',
    photoSrc: joshHarris,
    x_username: 'dynemetis',
    linkedin_username: 'joshua-harris-86188983'
  },
  // {
  //   name: 'Josh Ossip',
  //   photoSrc: joshOssip,
  //   linkedin_username: 'josh-ossip-b37549282'
  // },
  {
    name: 'Lucy Hargreaves',
    photoSrc: lucyHargreaves,
    x_username: 'lucyhargreaves4',
    linkedin_username: 'lucyghargreaves'
  },
  {
    name: 'Shane Parrish',
    photoSrc: shaneParrish,
    x_username: 'ShaneAParrish',
    linkedin_username: 'shane-parrish-050a2183'
  },
  {
    name: 'Brendan Samek',
    photoSrc: brendanSamek,
    linkedin_username: 'brendan-samek'
  },
  {
    name: 'Makara Sok',
    photoSrc: makSok,
    linkedin_username: 'makara-sok',
    x_username: 'maktouch'
  },
  {
    name: 'Natalie Lancaster',
    photoSrc: natalieLancaster,
    linkedin_username: 'natalie-lancaster-2485bba',
  },
  {
    name: 'Todd Scheidt',
    photoSrc: toddScheidt,
    linkedin_username: 'toddscheidt',
  }
].sort((a, b) => a.name.localeCompare(b.name));

interface Contributor {

  name: string;
  photoSrc: StaticImageData;
  linkedin_username?: string;
  x_username?: string;

}

const ContributorCard: React.FC<Contributor> = ({
  name,
  photoSrc,
  linkedin_username,
  x_username,
}) => {
  return (
    <div className={cn(
      "bg-white rounded-xl p-6 shadow-stat transition-all duration-300 hover:shadow-lg fade-in max-w-[200px]",
    )}>
      <div className="pt-[100%] relative overflow-hidden bg-white">
        <Image className="bottom-0 left-0 object-cover absolute top-0 align-middle inline-block w-full h-full max-w-full" src={photoSrc} alt={name} />
      </div>

      <P className="mt-2">{name}</P>

      <div className="flex gap-2">
        {linkedin_username && (
          <a href={`https://linkedin.com/in/${linkedin_username}`} className="text-2xl text-gray-500" target="_blank" rel="noopener noreferrer">
            <FaLinkedin />
          </a>
        )}

        {x_username && (
          <a href={`https://x.com/${x_username}`} className="text-2xl text-gray-500" target="_blank" rel="noopener noreferrer">
            <FaSquareXTwitter />
          </a>
        )}
      </div>
    </div>
  );
};



export function Contributors() {
  return (
    <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6 ">
      {contributors.map(contributor => (
        <ContributorCard key={contributor.name} {...contributor} />
      ))}
    </div>
  )
}