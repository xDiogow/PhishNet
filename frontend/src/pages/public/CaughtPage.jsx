import { Link } from 'react-router-dom'
import { AlertTriangle, ShieldAlert, Eye, Link2, Clock, KeyRound, CheckCircle, Shield } from 'lucide-react'

const redFlags = [
  {
    icon: Link2,
    title: 'Suspicious link',
    description: "The URL in the email didn't match the real website. Always check the address bar before entering any information.",
  },
  {
    icon: Clock,
    title: 'Sense of urgency',
    description: 'The email pressured you to act quickly. Attackers use urgency to prevent you from thinking clearly.',
  },
  {
    icon: Eye,
    title: 'Unexpected request',
    description: 'Legitimate services rarely ask you to re-enter your credentials via an email link without a clear reason.',
  },
  {
    icon: ShieldAlert,
    title: 'Unverified sender',
    description: "The sender's email address may have looked real but wasn't from the official domain.",
  },
]

const nextSteps = [
  'Change your password immediately on every service where you use the same one.',
  'Enable two-factor authentication (2FA) on your accounts.',
  'Report suspicious emails to your IT or security team instead of clicking them.',
  'When in doubt, go directly to the website by typing the address yourself.',
]

export default function CaughtPage() {
  return (
    <div className="min-h-screen bg-slate-900 pt-16">

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900/20 via-slate-900 to-orange-900/20"></div>
        <div className="relative max-w-3xl mx-auto px-6 py-24 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 ring-1 ring-red-500/30 mb-8">
            <AlertTriangle className="h-10 w-10 text-red-400" />
          </div>

          <div className="inline-flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-sm text-red-400 ring-1 ring-inset ring-red-500/20 mb-6">
            <ShieldAlert className="h-4 w-4" />
            <span>Phishing Simulation — Your credentials were captured</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight">
            You fell for a phishing attack
          </h1>

          <p className="text-lg text-gray-300 leading-relaxed">
            This was a <strong className="text-white">controlled security test</strong> run by your organization.
            No real harm was done — but if this had been a real attack, the credentials you just entered
            would now be in the hands of an attacker.
          </p>
        </div>
      </section>

      {/* What happened */}
      <section className="py-16 bg-slate-800/50">
        <div className="max-w-3xl mx-auto px-6">
          <div className="bg-red-900/20 border border-red-500/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4">What just happened?</h2>
            <ol className="space-y-4 text-gray-300 leading-relaxed list-none">
              <li className="flex gap-4">
                <span className="text-3xl font-bold text-red-500/40 leading-none">01</span>
                <p>You received a phishing email designed to look like a trustworthy message.</p>
              </li>
              <li className="flex gap-4">
                <span className="text-3xl font-bold text-red-500/40 leading-none">02</span>
                <p>You clicked a link inside that email and landed on a fake login page.</p>
              </li>
              <li className="flex gap-4">
                <span className="text-3xl font-bold text-red-500/40 leading-none">03</span>
                <p>You entered your credentials — username and password — on that fake page.</p>
              </li>
              <li className="flex gap-4">
                <span className="text-3xl font-bold text-red-500/40 leading-none">04</span>
                <p>In a real attack, those credentials are now stolen and can be used to access your accounts.</p>
              </li>
            </ol>
          </div>
        </div>
      </section>

      {/* Red flags */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-3">Red flags you may have missed</h2>
            <p className="text-gray-400">These are the warning signs that should have raised suspicion.</p>
          </div>

          <div className="grid sm:grid-cols-2 gap-6">
            {redFlags.map((flag, index) => (
              <div key={index} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-orange-500/10 text-orange-400 mb-4">
                  <flag.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{flag.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{flag.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What to do next */}
      <section className="py-20 bg-slate-800/50">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-3">What to do next time</h2>
            <p className="text-gray-400">Follow these steps to protect yourself from real phishing attacks.</p>
          </div>

          <div className="space-y-4">
            {nextSteps.map((step, index) => (
              <div key={index} className="flex items-start gap-4 bg-slate-800 border border-slate-700 rounded-xl p-5">
                <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-gray-300 leading-relaxed">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Golden rule */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-3xl mx-auto px-6">
          <div className="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 border border-cyan-500/20 rounded-2xl p-10 text-center">
            <KeyRound className="h-10 w-10 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-3">The golden rule</h3>
            <p className="text-gray-300 text-lg leading-relaxed">
              Never enter your credentials on a page you reached by clicking an email link.
              Always navigate to the site yourself by typing the address in the browser.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 py-10 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-white">
            <Shield className="h-5 w-5 text-cyan-400" />
            <span className="font-bold text-lg">PhishNet</span>
          </Link>
          <p className="text-gray-500 text-sm">This was a security awareness simulation. No real data was stored.</p>
        </div>
      </footer>

    </div>
  )
}
