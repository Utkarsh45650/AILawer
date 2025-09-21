import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { lawyers } from '@/lib/data';
import { Star } from 'lucide-react';
import Image from 'next/image';

export default function LawyersPage() {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="font-headline text-3xl font-bold">Lawyer Directory</h1>
        <p className="text-muted-foreground">Find and book an expert lawyer for your needs.</p>
      </div>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {lawyers.map((lawyer) => (
          <Card key={lawyer.id} className="flex flex-col transition-all hover:shadow-lg hover:-translate-y-1">
            <CardHeader className="items-center text-center">
              <Avatar className="h-24 w-24 border-4 border-card">
                <AvatarImage asChild src={lawyer.avatarUrl} alt={lawyer.name}>
                   <Image
                      src={lawyer.avatarUrl}
                      width={96}
                      height={96}
                      alt={lawyer.name}
                      data-ai-hint="professional portrait"
                    />
                </AvatarImage>
                <AvatarFallback>{lawyer.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <CardTitle className="font-headline pt-2 text-xl">{lawyer.name}</CardTitle>
              <div className="flex items-center gap-1 text-sm text-amber-500">
                <Star className="h-4 w-4 fill-current" />
                <span>
                  {lawyer.rating.toFixed(1)} ({lawyer.reviews} reviews)
                </span>
              </div>
            </CardHeader>
            <CardContent className="flex-grow">
              <div className="flex flex-wrap justify-center gap-2">
                {lawyer.specialties.map((spec) => (
                  <Badge key={spec} variant="secondary">
                    {spec}
                  </Badge>
                ))}
              </div>
              <p className="mt-4 text-center text-sm text-muted-foreground">
                Available slots: <span className="font-semibold text-foreground">{lawyer.availability}</span>
              </p>
            </CardContent>
            <CardFooter>
              <Button className="w-full">Book Appointment</Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
