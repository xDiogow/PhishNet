import { Link, useSearchParams } from 'react-router-dom'
import { AlertTriangle, ShieldAlert, Eye, Link2, Clock, BookOpen, CheckCircle, Shield, Mail, MousePointerClick, LogIn, Skull, ThumbsUp } from 'lucide-react'

const redFlags = [
  {
    iconElement: <Link2 aria-hidden="true" className="h-5 w-5" />,
    title: 'Suspicious link',
    description: "The URL in the email didn't match the real website. Always check the address bar before entering any information.",
  },
  {
    iconElement: <Clock aria-hidden="true" className="h-5 w-5" />,
    title: 'Sense of urgency',
    description: 'The email pressured you to act quickly. Attackers use urgency to prevent you from thinking clearly.',
  },
  {
    iconElement: <Eye aria-hidden="true" className="h-5 w-5" />,
    title: 'Unexpected request',
    description: 'Legitimate services rarely ask you to re-enter your credentials via an email link without a clear reason.',
  },
  {
    iconElement: <ShieldAlert aria-hidden="true" className="h-5 w-5" />,
    title: 'Unverified sender',
    description: "The sender's email address may have looked real but wasn't from the official domain.",
  },
]

const spotSteps = [
  {
    icon: <Mail aria-hidden="true" className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />,
    text: 'Hover over any link before clicking — verify the real destination in your browser status bar.',
  },
  {
    icon: <Eye aria-hidden="true" className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />,
    text: "Check the sender's email address carefully — not just the display name, but the full domain.",
  },
  {
    icon: <Clock aria-hidden="true" className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />,
    text: 'Treat urgency as a red flag — real services give you time; attackers want you to panic.',
  },
  {
    icon: <MousePointerClick aria-hidden="true" className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />,
    text: 'When in doubt, go directly to the website by typing the address yourself — never via the email link.',
  },
  {
    icon: <LogIn aria-hidden="true" className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />,
    text: 'Forward suspicious emails to your security or IT team before taking any action.',
  },
]

export default function CaughtPage() {
  const [searchParams] = useSearchParams()
  const isReported = searchParams.get('reported') === 'true'

  if (isReported) {
    return (
      <div className="min-h-screen bg-slate-900 pt-16">

        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-900/20 via-slate-900 to-emerald-900/20"></div>
          <div className="relative max-w-3xl mx-auto px-6 py-24 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/10 ring-1 ring-green-500/30 mb-8">
              <ThumbsUp aria-hidden="true" className="h-10 w-10 text-green-400" />
            </div>

            <div className="inline-flex items-center gap-2 rounded-full bg-green-500/10 px-4 py-2 text-sm text-green-400 ring-1 ring-inset ring-green-500/20 mb-6">
              <CheckCircle aria-hidden="true" className="h-4 w-4" />
              <span>Phishing Simulation — You reported this email</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight">
              Great job — you spotted it!
            </h1>

            <p className="text-lg text-gray-300 leading-relaxed">
              This was a <strong className="text-white">controlled security test</strong> run by your organization,
              and you passed. By reporting this email instead of clicking links or submitting credentials,
              you demonstrated exactly the right instinct.
            </p>
          </div>
        </section>

        {/* What you did right */}
        <section className="py-16 bg-slate-800/50">
          <div className="max-w-3xl mx-auto px-6">
            <div className="bg-green-900/20 border border-green-500/20 rounded-xl p-8">
              <h2 className="text-2xl font-bold text-white mb-4">Why this matters</h2>
              <div className="space-y-4 text-gray-300 leading-relaxed">
                <div className="flex gap-4">
                  <CheckCircle aria-hidden="true" className="h-6 w-6 text-green-400 flex-shrink-0 mt-0.5" />
                  <p>Reporting suspicious emails alerts your security team early — stopping an attack before it spreads.</p>
                </div>
                <div className="flex gap-4">
                  <CheckCircle aria-hidden="true" className="h-6 w-6 text-green-400 flex-shrink-0 mt-0.5" />
                  <p>You protected your credentials and your organization's data by not entering anything on an untrusted page.</p>
                </div>
                <div className="flex gap-4">
                  <CheckCircle aria-hidden="true" className="h-6 w-6 text-green-400 flex-shrink-0 mt-0.5" />
                  <p>Every reported phishing email helps build a stronger collective defence for the whole team.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Keep it up */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-3xl mx-auto px-6">
            <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/20 rounded-2xl p-10 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-green-500/10 ring-1 ring-green-500/30 mb-6">
                <BookOpen aria-hidden="true" className="h-7 w-7 text-green-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Keep sharpening your instincts</h3>
              <p className="text-gray-300 text-lg leading-relaxed mb-8">
                Security awareness is a habit, not a one-time test. The ANSSI phishing guide covers everything
                from spotting fake domains to reporting procedures — well worth the 15 minutes.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-500 px-6 py-3 text-sm font-semibold text-slate-900 hover:bg-green-400 transition-colors"
                >
                  <BookOpen aria-hidden="true" className="h-4 w-4" />
                  Read the ANSSI phishing guide
                </a>
                <a
                  href="https://www.phishing.fr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-700 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-600 transition-colors"
                >
                  Learn more at phishing.fr
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-slate-950 py-10 border-t border-slate-800">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
            <Link to="/" className="flex items-center gap-2 text-white">
              <Shield aria-hidden="true" className="h-5 w-5 text-cyan-400" />
              <span className="font-bold text-lg">PhishNet</span>
            </Link>
            <p className="text-gray-500 text-sm">Security awareness simulation — no credentials were stored.</p>
          </div>
        </footer>

      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 pt-16">

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900/20 via-slate-900 to-orange-900/20"></div>
        <div className="relative max-w-3xl mx-auto px-6 py-24 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 ring-1 ring-red-500/30 mb-8">
            <AlertTriangle aria-hidden="true" className="h-10 w-10 text-red-400" />
          </div>

          <div className="inline-flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-sm text-red-400 ring-1 ring-inset ring-red-500/20 mb-6">
            <ShieldAlert aria-hidden="true" className="h-4 w-4" />
            <span>Phishing Simulation — You submitted your credentials</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight">
            You fell for a phishing attack
          </h1>

          <p className="text-lg text-gray-300 leading-relaxed">
            This was a <strong className="text-white">controlled security test</strong> run by your organization.
            No real harm was done and <strong className="text-white">no credentials were stored</strong> — but
            in a real attack, what you just entered would now be in an attacker's hands.
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
                <p>You entered your credentials on that fake page — the form submitted them to an unknown server.</p>
              </li>
              <li className="flex gap-4 items-start">
                <span className="text-3xl font-bold text-red-500/40 leading-none">04</span>
                <p className="flex items-start gap-2">
                  <Skull aria-hidden="true" className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                  In a real attack, those credentials are now stolen and can be used to take over your accounts.
                </p>
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
                  {flag.iconElement}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{flag.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{flag.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How to spot phishing next time */}
      <section className="py-20 bg-slate-800/50">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-3">How to spot it next time</h2>
            <p className="text-gray-400">Apply these habits every time you receive an unexpected email.</p>
          </div>

          <div className="space-y-4">
            {spotSteps.map((step, index) => (
              <div key={index} className="flex items-start gap-4 bg-slate-800 border border-slate-700 rounded-xl p-5">
                <CheckCircle aria-hidden="true" className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-gray-300 leading-relaxed">{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Training CTA */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-3xl mx-auto px-6">
          <div className="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 border border-cyan-500/20 rounded-2xl p-10 text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-cyan-500/10 ring-1 ring-cyan-500/30 mb-6">
              <BookOpen aria-hidden="true" className="h-7 w-7 text-cyan-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">Build your phishing radar</h3>
            <p className="text-gray-300 text-lg leading-relaxed mb-8">
              One test isn't enough. The ANSSI guide to phishing covers everything from spotting fake
              domains to reporting procedures — it takes 15 minutes and could save your account.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-900 hover:bg-cyan-400 transition-colors"
              >
                <BookOpen aria-hidden="true" className="h-4 w-4" />
                Read the ANSSI phishing guide
              </a>
              <a
                href="https://www.phishing.fr"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-700 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-600 transition-colors"
              >
                Learn more at phishing.fr
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 py-10 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-white">
            <Shield aria-hidden="true" className="h-5 w-5 text-cyan-400" />
            <span className="font-bold text-lg">PhishNet</span>
          </Link>
          <p className="text-gray-500 text-sm">Security awareness simulation — no credentials were stored.</p>
        </div>
      </footer>

    </div>
  )
}
