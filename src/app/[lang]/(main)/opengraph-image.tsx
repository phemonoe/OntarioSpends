import { readFile } from 'fs/promises'
import { ImageResponse } from 'next/og'
import { join } from 'path'

export const alt = 'About Acme'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

export default async function Img({ params }: { params: { slug: string } }) {

  const logoData = await readFile(join(process.cwd(), 'public', 'logo.png'))
  const logoSrc = Uint8Array.from(logoData).buffer

  return new ImageResponse(
    (
      <div
        style={{
          fontFamily: 'Plus Jakarta Sans',
          fontSize: 48,
          background: 'white',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
        }}
      >
        {/* @ts-ignore */}
        <img src={logoSrc} alt="Canada Spends" width={616} height={170} />
      </div>
    ),
    {
      ...size,

    }
  )
}