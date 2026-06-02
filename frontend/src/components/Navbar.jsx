import { Fish, Bell, LogOut, User, Settings } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useUser } from "../contexts/UserContext";
import { logout } from "../services/authService";
import { generateAvatarUrl } from "../utils/avatarUtils";
import logo from "../../public/images/logo.svg"

const navigation = [
  { name: 'Dashboard', path: '/dashboard', adminOnly: false },
  { name: 'Team', path: '/team', adminOnly: false },
  { name: 'Campaigns', path: '/campaigns', adminOnly: false },
  { name: 'Templates', path: '/templates', adminOnly: false },
  { name: 'Audit Logs', path: '/audit-logs', adminOnly: false },
  { name: 'Instances', path: '/instances', adminOnly: true },
  { name: 'Tenants', path: '/tenants', adminOnly: true },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAdmin, setUser } = useUser();

  const handleSignOut = async () => {
    await logout();
    setUser(null);
    navigate('/login');
    setUserMenuOpen(false);
  };

  const isCurrentPath = (path) => {
    return location.pathname === path;
  };

  const visibleNavigation = navigation.filter(item => !item.adminOnly || isAdmin());

  // Check if we're in a protected route (dashboard area)
  const isProtectedRoute = location.pathname.startsWith('/dashboard') || 
                          location.pathname.startsWith('/team') ||
                          location.pathname.startsWith('/campaigns') ||
                          location.pathname.startsWith('/templates') ||
                          location.pathname.startsWith('/audit-logs') ||
                          location.pathname.startsWith('/instances') ||
                          location.pathname.startsWith('/tenants');

  // If not in protected route, show landing page navbar
  if (!isProtectedRoute) {
    return (
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <img src={logo} className="w-8 h-8" alt="logo" />
              <span className="text-xl text-white">PhishNet</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <a
                href="/#features"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Features
              </a>
              <a
                href="/#training"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Training
              </a>
              <a
                href="/#pricing"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Pricing
              </a>
              <a
                href="/#about"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                About
              </a>
            </div>

            {/* CTA Buttons */}
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-slate-300 hover:text-cyan-400"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-md"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  // Dashboard navbar (white theme)
  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <img src={logo} className="w-8 h-8" alt="logo" />
            <span className="text-xl font-bold text-gray-900">PhishNet</span>
          </div>

          {/* Desktop Navigation */}
          <div className="flex items-center gap-1">
            {visibleNavigation.map((item) => {
              const isCurrent = isCurrentPath(item.path);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={classNames(
                    isCurrent
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900',
                    'rounded-md px-3 py-2 text-sm font-medium transition-colors'
                  )}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Right side - Notifications and User Menu */}
          <div className="flex items-center gap-4">
            {/* Notifications */}
            <button
              type="button"
              className="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
            >
              <Bell className="w-5 h-5" />
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              >
                <img
                  alt=""
                  src={
                    user
                      ? generateAvatarUrl(user.first_name, user.last_name, user.email)
                      : 'https://ui-avatars.com/api/?name=User&background=random&color=fff&size=128'
                  }
                  className="w-8 h-8 rounded-full border-2 border-gray-200"
                />
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 z-20 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                    </div>
                    <Link
                      to="#"
                      className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      Your profile
                    </Link>
                    <Link
                      to="#"
                      className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Settings className="w-4 h-4" />
                      Settings
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign out
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
