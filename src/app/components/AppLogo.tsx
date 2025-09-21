import { Scale } from 'lucide-react';
import Link from 'next/link';

export function AppLogo() {
  return (
    <Link href="/dashboard" className="flex items-center gap-2 group outline-none">
      <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
        <Scale className="h-6 w-6 text-primary" />
      </div>
      <h1 className="font-headline text-xl font-semibold text-primary tracking-wide">
        LawLens AI
      </h1>
    </Link>
  );
}
