import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 gap-8">
      <Card className="w-96">
        <CardHeader>
          <CardTitle>AI Telegram Bot Dashboard</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            shadcn/ui integration successful! 
          </p>
          <div className="flex gap-2">
            <Badge>Next.js 15</Badge>
            <Badge variant="secondary">TypeScript</Badge>
            <Badge variant="outline">Tailwind CSS</Badge>
          </div>
          <Button className="w-full">Get Started</Button>
        </CardContent>
      </Card>
    </main>
  )
}
