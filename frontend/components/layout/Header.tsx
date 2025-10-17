import Link from "next/link"
import { Github } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { siteConfig } from "@/config/site"

export function Header() {
  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />
      <div className="flex flex-1 items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">{siteConfig.name}</h1>
        </div>
        <Button variant="ghost" size="icon" asChild>
          <Link 
            href={siteConfig.links.github} 
            target="_blank" 
            rel="noopener noreferrer"
            aria-label="GitHub repository"
          >
            <Github className="h-5 w-5" />
          </Link>
        </Button>
      </div>
    </header>
  )
}
