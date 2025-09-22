import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Check, Star, Crown, Zap, LogOut } from 'lucide-react';

const SubscriptionPage: React.FC = () => {
  const [selectedTier, setSelectedTier] = useState<'free' | 'premium' | 'enterprise'>('free');
  const [loading, setLoading] = useState(false);
  const { user, completeSubscriptionSetup, logout } = useAuth();

  const handleSelectPlan = async () => {
    setLoading(true);
    try {
      // Here you would typically call an API to update the user's subscription
      // For now, we'll just simulate the action
      console.log('Selected plan:', selectedTier);
      
      // Complete the subscription setup
      completeSubscriptionSetup(selectedTier);
    } catch (error) {
      console.error('Error selecting plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'free' as const,
      name: 'Basic',
      price: 'Free',
      icon: <Star className="plan-icon" />,
      features: [
        'Chat advice',
        '5 custom case study uses per week',
        'Basic legal guidance',
        'Community support'
      ],
      popular: false
    },
    {
      id: 'premium' as const,
      name: 'Premium',
      price: '$29/month',
      icon: <Crown className="plan-icon" />,
      features: [
        'All Basic features',
        'Unlimited custom case study uses',
        'Priority chat support',
        'Advanced legal analysis',
        'Document upload & analysis'
      ],
      popular: true
    },
    {
      id: 'enterprise' as const,
      name: 'Enterprise',
      price: '$99/month',
      icon: <Zap className="plan-icon" />,
      features: [
        'All Premium features',
        'Expert lawyer consultations',
        'Unlimited expert advice sessions',
        'Priority support',
        'Custom integrations',
        'Team collaboration'
      ],
      popular: false
    }
  ];

  return (
    <div className="subscription-page">
      {/* Navigation Bar */}
      <div className="subscription-nav">
        <div className="nav-content">
          <div className="nav-left">
            <h1 className="logo">🏛️ LegalAI</h1>
          </div>
          <div className="nav-right">
            <div className="user-info">
              <span className="user-name">{user?.full_name}</span>
            </div>
            <button className="logout-btn" onClick={logout} title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </div>

      <div className="subscription-container">
        <div className="subscription-header">
          <h1>Welcome, {user?.full_name}!</h1>
          <p>Choose the perfect plan for your legal needs</p>
        </div>

        <div className="plans-grid">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`plan-card ${selectedTier === plan.id ? 'selected' : ''} ${plan.popular ? 'popular' : ''}`}
              onClick={() => setSelectedTier(plan.id)}
            >
              {plan.popular && <div className="popular-badge">Most Popular</div>}
              
              <div className="plan-header">
                {plan.icon}
                <h3>{plan.name}</h3>
                <div className="plan-price">{plan.price}</div>
              </div>

              <ul className="plan-features">
                {plan.features.map((feature, index) => (
                  <li key={index}>
                    <Check size={16} className="feature-icon" />
                    {feature}
                  </li>
                ))}
              </ul>

              <div className="plan-select">
                {selectedTier === plan.id && (
                  <div className="selected-indicator">
                    <Check size={20} />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="subscription-actions">
          <button
            className="continue-btn"
            onClick={handleSelectPlan}
            disabled={loading}
          >
            {loading ? 'Processing...' : `Continue with ${plans.find(p => p.id === selectedTier)?.name}`}
          </button>
          
          <p className="subscription-note">
            You can upgrade or downgrade your plan anytime from your account settings.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;