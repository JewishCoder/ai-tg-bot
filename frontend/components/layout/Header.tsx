import Link from "next/link"
import { siteConfig } from "@/config/site"

export function Header() {
  return (
    <header className="bg-background/95 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50 w-full border-b backdrop-blur">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold">{siteConfig.name}</span>
          </Link>
        </div>
      </div>
    </header>
  )
}
