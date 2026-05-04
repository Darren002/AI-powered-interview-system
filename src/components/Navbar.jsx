import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black border-b border-black-200" style={{ backgroundColor: '#000000' }}>
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-lg font-bold text-white">CyberHire</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            <Link
              to="/"
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                isActive('/')
                  ? 'bg-white text-black'
                  : 'text-white-400 hover:text-white hover:bg-white/10'
              }`}
            >
              Home
            </Link>

            <Link
              to="/dashboard"
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                isActive('/dashboard')
                  ? 'bg-white text-black'
                  : 'text-white-400 hover:text-white hover:bg-white/10'
              }`}
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
