import { BeehiivClient } from "@beehiiv/sdk";
import { NextResponse } from "next/server";

const PUBLICATION_ID = 'pub_2db2d145-9348-4073-bdab-f3e1ae7d6a73'

const client = new BeehiivClient({ token: process.env.BEEHIIV_KEY! });

export async function POST(request: Request) {
  const { email, utmSource, utmMedium, utmCampaign } = await request.json();

  await client.subscriptions.create(PUBLICATION_ID, {
    email: email,
    reactivateExisting: true,
    sendWelcomeEmail: false,
    utmSource: utmSource,
    utmMedium: utmMedium,
    utmCampaign: utmCampaign,
    referringSite: "canadaspends.com",
  });

  return NextResponse.json({ message: 'ok' });
}