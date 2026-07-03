import { useState } from "react";
import { Fish, Bell, LogOut, User, Settings, Menu, X } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu as HMenu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
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
  { name: 'Tenants', path: '/tenants', adminOnly: true },
];

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAdmin, setUser } = useUser();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignOut = async () => {
    await logout();
    setUser(null);
    navigate('/login');
  };

  const isCurrentPath = (path) => location.pathname === path;

  const visibleNavigation = navigation.filter(item => {
    if (!item.adminOnly) return true
    return isAdmin()
  });

  const isProtectedRoute = location.pathname.startsWith('/dashboard') ||
                          location.pathname.startsWith('/team') ||
                          location.pathname.startsWith('/campaigns') ||
                          location.pathname.startsWith('/templates') ||
                          location.pathname.startsWith('/audit-logs') ||
                          location.pathname.startsWith('/tenants');

  if (!isProtectedRoute) {
    return (
      <nav aria-label="Main navigation" className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <img src={logo} className="w-8 h-8" alt="PhishNet logo" />
              <span className="text-xl text-white">PhishNet</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="/#features" className="text-slate-300 hover:text-cyan-400 transition-colors">Features</a>
              <a href="/#training" className="text-slate-300 hover:text-cyan-400 transition-colors">Training</a>
              <a href="/#pricing" className="text-slate-300 hover:text-cyan-400 transition-colors">Pricing</a>
              <a href="/#about" className="text-slate-300 hover:text-cyan-400 transition-colors">About</a>
            </div>

            <div className="flex items-center gap-3">
              <Link to="/login" className="text-slate-300 hover:text-cyan-400 text-sm">Sign In</Link>
              <Link to="/register" className="bg-cyan-500 hover:bg-cyan-600 text-white px-3 py-1.5 rounded-md text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav aria-label="Application navigation" className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <img src={logo} className="w-8 h-8" alt="PhishNet logo" />
            <span className="text-xl font-bold text-gray-900">PhishNet</span>
          </div>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-1" role="list">
            {visibleNavigation.map((item) => {
              const isCurrent = isCurrentPath(item.path);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  role="listitem"
                  aria-current={isCurrent ? 'page' : undefined}
                  className={`${isCurrent ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'} rounded-md px-3 py-2 text-sm font-medium transition-colors`}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Right side: bell + avatar + hamburger */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label="Notifications"
              className="relative p-2 text-gray-600 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
            >
              <Bell aria-hidden="true" className="w-5 h-5" />
            </button>

            {/* Avatar dropdown (desktop) */}
            <HMenu as="div" className="relative hidden md:block">
              <MenuButton
                aria-label={`User menu for ${user && user.first_name ? user.first_name : 'user'}`}
                className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              >
                <img
                  alt={user ? `${user.first_name} ${user.last_name}` : 'User avatar'}
                  src={
                    user
                      ? generateAvatarUrl(user.first_name, user.last_name, user.email)
                      : 'https://ui-avatars.com/api/?name=User&background=random&color=fff&size=128'
                  }
                  className="w-8 h-8 rounded-full border-2 border-gray-200"
                />
              </MenuButton>

              <MenuItems
                transition
                className="absolute right-0 z-20 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 transition data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
              >
                <div className="px-4 py-2 border-b border-gray-200" role="none">
                  <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                </div>
                <MenuItem>
                  <Link to="#" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 data-focus:bg-gray-50">
                    <User aria-hidden="true" className="w-4 h-4" />
                    Your profile
                  </Link>
                </MenuItem>
                <MenuItem>
                  <Link to="#" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 data-focus:bg-gray-50">
                    <Settings aria-hidden="true" className="w-4 h-4" />
                    Settings
                  </Link>
                </MenuItem>
                <MenuItem>
                  <button
                    onClick={handleSignOut}
                    className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 data-focus:bg-gray-50"
                  >
                    <LogOut aria-hidden="true" className="w-4 h-4" />
                    Sign out
                  </button>
                </MenuItem>
              </MenuItems>
            </HMenu>

            {/* Hamburger button (mobile only) */}
            <button
              type="button"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
            >
              {mobileMenuOpen
                ? <X aria-hidden="true" className="w-5 h-5" />
                : <Menu aria-hidden="true" className="w-5 h-5" />
              }
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div id="mobile-menu" className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-4 pt-2 pb-3 space-y-1" role="list">
            {visibleNavigation.map((item) => {
              const isCurrent = isCurrentPath(item.path);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  role="listitem"
                  aria-current={isCurrent ? 'page' : undefined}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`${isCurrent ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'} block rounded-md px-3 py-2 text-base font-medium transition-colors`}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Mobile user info + sign out */}
          <div className="border-t border-gray-200 px-4 py-3">
            <div className="flex items-center gap-3 mb-3">
              <img
                alt={user ? `${user.first_name} ${user.last_name}` : 'User avatar'}
                src={
                  user
                    ? generateAvatarUrl(user.first_name, user.last_name, user.email)
                    : 'https://ui-avatars.com/api/?name=User&background=random&color=fff&size=128'
                }
                className="w-9 h-9 rounded-full border-2 border-gray-200"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <LogOut aria-hidden="true" className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
