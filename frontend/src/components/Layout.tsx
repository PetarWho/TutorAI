import React, { useState } from "react";
import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  GraduationCap,
  LogOut,
  Upload,
  Home,
  Search,
  Settings,
  X,
  Menu
} from "lucide-react";

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: Home },
    { name: "Courses", href: "/courses", icon: GraduationCap },
    { name: "Upload Lecture", href: "/upload", icon: Upload },
    { name: "Search", href: "/search", icon: Search },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 shadow-xl lg:shadow-none
          transform transition-transform duration-300 ease-in-out
          flex flex-col h-full
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <GraduationCap className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 tracking-tight">
              Tutor AI
            </span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`
                  group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200
                  ${
                    active
                      ? "bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }
                `}
              >
                <Icon
                  className={`
                    mr-3 h-5 w-5 flex-shrink-0 transition-colors
                    ${active ? "text-blue-600" : "text-gray-400 group-hover:text-gray-500"}
                  `}
                />
                {item.name}
              </Link>
            );
          })}
        </div>

        {user && (
          <div className="p-4 border-t border-gray-100 bg-gray-50/50">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold border-2 border-white shadow-sm">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user.username}
                </p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <button className="flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <Settings className="mr-2 h-3.5 w-3.5" />
                Settings
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center justify-center px-3 py-2 text-xs font-medium text-red-600 bg-white border border-gray-200 rounded-lg hover:bg-red-50 hover:border-red-100 transition-colors"
              >
                <LogOut className="mr-2 h-3.5 w-3.5" />
                Logout
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72 transition-all duration-300">
        <header className="sticky top-0 z-20 flex h-16 items-center border-b border-gray-200 bg-white/80 backdrop-blur-md px-4 shadow-sm lg:hidden">
           <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden hover:text-gray-900"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          <span className="ml-4 text-lg font-bold text-gray-900">Tutor AI</span>
        </header>

        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;