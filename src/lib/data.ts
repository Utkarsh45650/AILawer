import type { ImagePlaceholder } from './placeholder-images';
import { PlaceHolderImages } from './placeholder-images';

const placeholderMap = new Map(PlaceHolderImages.map(p => [p.id, p.imageUrl]));

export const lawyers = [
  {
    id: 1,
    name: 'Ananya Sharma',
    avatarUrl: placeholderMap.get('lawyer-1') || '',
    rating: 4.9,
    reviews: 128,
    specialties: ['Corporate Law', 'Mergers & Acquisitions'],
    availability: 5,
  },
  {
    id: 2,
    name: 'Rohan Mehta',
    avatarUrl: placeholderMap.get('lawyer-2') || '',
    rating: 4.8,
    reviews: 95,
    specialties: ['Family Law', 'Divorce'],
    availability: 8,
  },
  {
    id: 3,
    name: 'Priya Singh',
    avatarUrl: placeholderMap.get('lawyer-3') || '',
    rating: 4.9,
    reviews: 210,
    specialties: ['Criminal Defense', 'Litigation'],
    availability: 3,
  },
  {
    id: 4,
    name: 'Vikram Desai',
    avatarUrl: placeholderMap.get('lawyer-4') || '',
    rating: 4.7,
    reviews: 82,
    specialties: ['Intellectual Property', 'Patents'],
    availability: 12,
  },
  {
    id: 5,
    name: 'Sonia Kapoor',
    avatarUrl: placeholderMap.get('lawyer-5') || '',
    rating: 4.8,
    reviews: 150,
    specialties: ['Real Estate Law', 'Contracts'],
    availability: 7,
  },
  {
    id: 6,
    name: 'Arjun Verma',
    avatarUrl: placeholderMap.get('lawyer-6') || '',
    rating: 4.6,
    reviews: 77,
    specialties: ['Immigration Law', 'Visas'],
    availability: 9,
  },
];

export const subscriptionTiers = [
  {
    name: 'Basic',
    price: 0,
    description: 'For casual users exploring our services.',
    features: [
      '5 AI Chat queries per month',
      '1 Document summarization (up to 10 pages)',
      'Limited access to lawyer directory',
    ],
  },
  {
    name: 'Standard',
    price: 29,
    description: 'For individuals with regular legal needs.',
    features: [
      '50 AI Chat queries per month',
      '5 Document summarizations (up to 25 pages)',
      'Full access to lawyer directory',
      '1 Appointment booking per month',
    ],
  },
  {
    name: 'Premium',
    price: 79,
    description: 'For professionals and small businesses.',
    features: [
      'Unlimited AI Chat queries',
      '20 Document summarizations (up to 100 pages)',
      'Priority support',
      '5 Appointment bookings per month',
    ],
  },
  {
    name: 'Platinum',
    price: 199,
    description: 'Ultimate access for power users.',
    features: [
      'All Premium features',
      'Unlimited document summarizations',
      'Dedicated case manager',
      'Unlimited appointment bookings',
    ],
  },
];
