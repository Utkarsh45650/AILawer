import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Bot, FileText, Gavel } from 'lucide-react';
import Link from 'next/link';

const features = [
  {
    title: 'Summarize Legal Document',
    description: 'Upload a PDF and get a concise summary, mind map, and flowchart.',
    icon: FileText,
    href: '/summarize',
    cta: 'Start Summarizing',
  },
  {
    title: 'AI Chat Assistant',
    description: 'Ask legal questions and receive step-by-step advice.',
    icon: Bot,
    href: '/chat',
    cta: 'Ask AI',
  },
  {
    title: 'Find an Expert Lawyer',
    description: 'Browse our directory of legal professionals and book appointments.',
    icon: Gavel,
    href: '/lawyers',
    cta: 'Browse Lawyers',
  },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-headline text-4xl font-bold tracking-tight text-primary">Welcome back, Alex!</h1>
        <p className="mt-2 text-lg text-muted-foreground">
          Your AI-powered legal toolkit is ready. What would you like to do today?
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <Card key={feature.title} className="flex flex-col transition-all hover:shadow-lg hover:-translate-y-1">
            <CardHeader>
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="font-headline text-xl">{feature.title}</CardTitle>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
            <CardContent className="mt-auto">
              <Button asChild className="w-full">
                <Link href={feature.href}>
                  {feature.cta}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-xl">Recent Activity</CardTitle>
          <CardDescription>A log of your recent interactions with LawLens AI.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed bg-muted/50">
            <p className="text-muted-foreground">No recent activity</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
