import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import SettingsModal from './components/SettingsModal';
import ChatPage from './pages/ChatPage';
import HistoryPage from './pages/HistoryPage';
import LoginPage from './pages/LoginPage';

export default function App() {
  const [user, setUser]   = useState(() => {
    const saved = localStorage.getItem('ca_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [theme, setTheme] = useState(() => localStorage.getItem('ca_theme') || 'dark');
  const [streamMode, setStreamMode] = useState(() => localStorage.getItem('ca_stream_mode') || 'standard');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    localStorage.setItem('ca_stream_mode', streamMode);
  }, [streamMode]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ca_theme', theme);
  }, [theme]);

  const handleLogin = (authenticatedUser) => {
    localStorage.setItem('ca_user', JSON.stringify(authenticatedUser));
    setUser(authenticatedUser);
  };

  const handleLogout = () => {
    localStorage.removeItem('ca_user');
    setUser(null);
  };

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  if (!user) return <LoginPage onLogin={handleLogin} theme={theme} onToggleTheme={toggleTheme} />;

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar
          userId={user.username}
          role={user.role}
          theme={theme}
          onToggleTheme={toggleTheme}
          onSettingsClick={() => setShowSettings(true)}
          onLogout={handleLogout}
        />
        <main className="app-main">
          <Routes>
            <Route path="/"        element={<ChatPage userId={user.username} role={user.role} streamMode={streamMode} />} />
            <Route path="/history" element={<HistoryPage userId={user.username} role={user.role} streamMode={streamMode} />} />
          </Routes>
        </main>
        {showSettings && (
          <SettingsModal
            userId={user.username}
            role={user.role}
            streamMode={streamMode}
            onSave={(nextStreamMode) => setStreamMode(nextStreamMode)}
            onClose={() => setShowSettings(false)}
          />
        )}
      </div>
    </BrowserRouter>
  );
}
