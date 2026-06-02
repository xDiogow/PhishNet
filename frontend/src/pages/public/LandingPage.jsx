import { Link } from 'react-router-dom'
import {
  Shield,
  Target,
  Users,
  TrendingUp,
  Mail,
  Lock,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  FileText,
  Zap,
  Globe,
  ArrowRight,
  PlayCircle
} from 'lucide-react'

export default function LandingPage() {
  const features = [
    {
      icon: Target,
      title: 'Realistic Simulations',
      description: 'Create authentic phishing campaigns that mirror real-world threats to test your team\'s awareness.'
    },
    {
      icon: Users,
      title: 'Team Management',
      description: 'Organize and track multiple teams across your organization with granular control and reporting.'
    },
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Gain deep insights with comprehensive reporting and metrics to measure security awareness.'
    },
    {
      icon: FileText,
      title: 'Template Library',
      description: 'Access a growing library of pre-built templates or create custom phishing scenarios.'
    },
    {
      icon: Zap,
      title: 'Automated Campaigns',
      description: 'Schedule and automate phishing simulations to continuously test and train your workforce.'
    },
    {
      icon: Lock,
      title: 'Enterprise Security',
      description: 'Bank-level security with encryption, multi-tenancy, and compliance-ready infrastructure.'
    }
  ]

  const steps = [
    {
      number: '01',
      title: 'Create Campaign',
      description: 'Choose from our template library or design your own phishing email campaign.'
    },
    {
      number: '02',
      title: 'Select Targets',
      description: 'Define your target groups and schedule when the simulation should be deployed.'
    },
    {
      number: '03',
      title: 'Monitor Results',
      description: 'Track real-time metrics and see who clicked, opened, or reported the phishing attempt.'
    },
    {
      number: '04',
      title: 'Train & Improve',
      description: 'Use insights to provide targeted training and improve your organization\'s security posture.'
    }
  ]

  const stats = [
    { value: '10,000+', label: 'Simulations Launched' },
    { value: '500+', label: 'Organizations' },
    { value: '94%', label: 'Success Rate' },
    { value: '24/7', label: 'Support' }
  ]

  const plans = [
    {
      name: 'Small Enterprise',
      price: '$299',
      period: 'per month, billed annually',
      description: 'Ideal for organizations up to 100 employees starting their security awareness journey.',
      features: ['Up to 100 users', '20 campaign templates', 'Real-time analytics dashboard', 'Email & chat support'],
      cta: 'Get Started',
      href: '/register',
      highlighted: false,
    },
    {
      name: 'Medium Enterprise',
      price: '$899',
      period: 'per month, billed annually',
      description: 'Designed for organizations between 100 and 1,000 employees with advanced training needs.',
      features: ['Up to 1,000 users', 'Unlimited templates', 'Advanced analytics & reporting', 'Automated campaigns', 'Audit logs', 'Priority support', 'Custom branding', 'API access'],
      cta: 'Get Started',
      href: '/register',
      highlighted: true,
    },
    {
      name: 'Large Enterprise',
      price: 'Custom',
      period: 'contact us',
      description: 'Fully tailored for large organizations with complex infrastructure and compliance requirements.',
      features: ['Unlimited users', 'Custom templates & branding', 'Full audit logs', 'Multi-tenancy', 'On-premise deployment option', 'Dedicated account manager', 'SLA guarantee', 'Compliance reporting (SOC2, ISO 27001)'],
      cta: 'Contact Sales',
      href: '/register',
      highlighted: false,
    }
  ]

  const values = [
    {
      icon: Shield,
      title: 'Security First',
      description: 'Every feature is built with security at its core. We protect your data with bank-level encryption and compliance-ready infrastructure.'
    },
    {
      icon: Users,
      title: 'People-Centered',
      description: 'We believe the human element is your greatest defense. Our platform empowers every employee to become a security asset.'
    },
    {
      icon: TrendingUp,
      title: 'Continuous Improvement',
      description: 'Cyber threats evolve daily. Our platform evolves with them, constantly delivering new templates and threat intelligence.'
    },
    {
      icon: Globe,
      title: 'Global Reach',
      description: 'Trusted by organizations across the globe, PhishNet supports multi-language campaigns and international compliance standards.'
    }
  ]

  return (
    <div className="min-h-screen bg-slate-900 pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-slate-900 to-blue-900/20"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMjIiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIxIDEuNzktNCA0LTRzNCAxLjc5IDQgNC0xLjc5IDQtNCA0LTQtMS43OS00LTR6bTAgMTBjMC0yLjIxIDEuNzktNCA0LTRzNCAxLjc5IDQgNC0xLjc5IDQtNCA0LTQtMS43OS00LTR6bTAgMTBjMC0yLjIxIDEuNzktNCA0LTRzNCAxLjc5IDQgNC0xLjc5IDQtNCA0LTQtMS43OS00LTR6bTEwLTIwYzAtMi4yMSAxLjc5LTQgNC00czQgMS43OSA0IDQtMS43OSA0LTQgNC00LTEuNzktNC00em0wIDEwYzAtMi4yMSAxLjc5LTQgNC00czQgMS43OSA0IDQtMS43OSA0LTQgNC00LTEuNzktNC00em0wIDEwYzAtMi4yMSAxLjc5LTQgNC00czQgMS43OSA0IDQtMS43OSA0LTQgNC00LTEuNzktNC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-20"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-24 sm:py-32 lg:py-40">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 rounded-full bg-cyan-500/10 px-4 py-2 text-sm text-cyan-400 ring-1 ring-inset ring-cyan-500/20 mb-8">
              <Shield className="h-4 w-4" />
              <span>Enterprise-Grade Security Awareness Training</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Protect Your Organization<br />
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Against Phishing Attacks
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-10 leading-relaxed">
              Train your workforce to recognize and report phishing attempts with realistic simulations, 
              comprehensive analytics, and automated training programs.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/register"
                className="group inline-flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105 shadow-lg shadow-cyan-500/30"
              >
                Get Started Free
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all border border-white/20"
              >
                <PlayCircle className="h-5 w-5" />
                Watch Demo
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="mt-16 flex flex-wrap justify-center items-center gap-8 text-gray-400 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-16 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400 text-sm md:text-base">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Everything You Need to Build a
              <span className="block text-cyan-400">Security-Aware Workforce</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Comprehensive tools and features designed to strengthen your organization's 
              human firewall against cyber threats.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative bg-slate-800/50 rounded-xl p-8 border border-slate-700 hover:border-cyan-500/50 transition-all hover:shadow-lg hover:shadow-cyan-500/10"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-cyan-500/10 text-cyan-400 mb-4 group-hover:scale-110 transition-transform">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="training" className="py-24 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              How PhishNet Works
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Four simple steps to launch effective phishing simulations and 
              improve your team's security awareness.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-1/2 w-full h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
                )}
                
                <div className="relative bg-slate-800 rounded-xl p-6 border border-slate-700">
                  <div className="text-6xl font-bold text-cyan-500/20 mb-4">
                    {step.number}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Enterprise Plans,
              <span className="block text-cyan-400">Built to Scale</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              All plans are tailored to your organization's size and needs. Contact our sales team for a custom quote.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 items-stretch">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`group relative flex flex-col rounded-xl p-8 border transition-all hover:shadow-lg ${
                  plan.highlighted
                    ? 'bg-cyan-500/10 border-cyan-500 ring-2 ring-cyan-500 hover:shadow-cyan-500/20'
                    : 'bg-slate-800/50 border-slate-700 hover:border-cyan-500/50 hover:shadow-cyan-500/10'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-cyan-500 text-white text-xs font-semibold px-4 py-1 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                  <div className="flex items-end gap-1 mb-1">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                  </div>
                  <p className="text-sm text-gray-400">{plan.period}</p>
                  <p className="text-gray-400 mt-4 leading-relaxed">{plan.description}</p>
                </div>
                <ul className="space-y-3 flex-1 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-3 text-gray-300">
                      <CheckCircle className="h-5 w-5 text-cyan-400 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to={plan.href}
                  className={`inline-flex items-center justify-center gap-2 w-full px-6 py-3 rounded-lg font-semibold transition-all ${
                    plan.highlighted
                      ? 'bg-cyan-500 hover:bg-cyan-600 text-white shadow-lg shadow-cyan-500/30 hover:scale-105'
                      : 'bg-white/10 hover:bg-white/20 text-white border border-white/20'
                  }`}
                >
                  {plan.cta}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-24 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Built by Security Experts,
              <span className="block text-cyan-400">For Security Teams</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              PhishNet was founded with a single mission: make enterprise-grade phishing
              simulation accessible to every organization, regardless of size or budget.
              We combine deep security expertise with intuitive design to deliver training
              that actually changes behavior.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div
                key={index}
                className="group relative bg-slate-800 rounded-xl p-8 border border-slate-700 hover:border-cyan-500/50 transition-all hover:shadow-lg hover:shadow-cyan-500/10"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-cyan-500/10 text-cyan-400 mb-4 group-hover:scale-110 transition-transform">
                    <value.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">{value.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{value.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Alert Section */}
      <section className="py-24 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 rounded-2xl p-12 border border-red-500/20">
            <div className="flex flex-col md:flex-row items-center gap-8">
              <div className="flex-shrink-0">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 text-red-400">
                  <AlertTriangle className="h-10 w-10" />
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-3xl font-bold text-white mb-3">
                  91% of Cyber Attacks Start with Phishing
                </h3>
                <p className="text-xl text-gray-300 mb-6">
                  Don't let your organization become another statistic. Start training 
                  your team today with realistic phishing simulations.
                </p>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-semibold transition-all"
                >
                  Protect Your Organization
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-cyan-900/30 to-blue-900/30">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Strengthen Your Security?
          </h2>
          <p className="text-xl text-gray-300 mb-10">
            Join hundreds of organizations using PhishNet to train their teams 
            and reduce phishing risks.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105 shadow-lg shadow-cyan-500/30"
            >
              Start Free Trial
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 bg-white text-slate-900 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2 text-white">
              <Shield className="h-6 w-6 text-cyan-400" />
              <span className="text-xl font-bold">PhishNet</span>
            </div>
            <div className="text-gray-500 text-sm">
              © 2024 PhishNet. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
