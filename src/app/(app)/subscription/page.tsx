import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { subscriptionTiers } from '@/lib/data';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SubscriptionPage() {
  const currentUserTier = 'Standard';

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="font-headline text-3xl font-bold">Subscription Plans</h1>
        <p className="text-muted-foreground">Choose the plan that fits your legal needs.</p>
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {subscriptionTiers.map((tier) => (
          <Card
            key={tier.name}
            className={cn(
              'flex flex-col',
              currentUserTier === tier.name && 'border-2 border-primary shadow-lg'
            )}
          >
            <CardHeader>
              <CardTitle className="font-headline text-2xl">{tier.name}</CardTitle>
              <CardDescription>{tier.description}</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">${tier.price}</span>
                <span className="text-muted-foreground">/month</span>
              </div>
            </CardHeader>
            <CardContent className="flex-grow">
              <ul className="space-y-3">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-start">
                    <Check className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-primary" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button className="w-full" disabled={currentUserTier === tier.name}>
                {currentUserTier === tier.name ? 'Current Plan' : `Choose ${tier.name}`}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
