// POC only — hardcoded credentials matching backend roles from .env
export const USERS = [
  { username: 'admin',            password: 'admin123',    role: 'admin' },
  { username: 'gm',               password: 'gm123',       role: 'general_manager' },
  { username: 'manager',          password: 'manager123',  role: 'location_manager' },
  { username: 'chef',             password: 'chef123',     role: 'chef' },
  { username: 'waiter',           password: 'waiter123',   role: 'waiter' },
  { username: 'cashier',         password: 'cashier123',  role: 'cashier' },
  { username: 'analyst',          password: 'analyst123',  role: 'analyst' },
];

export function authenticate(username, password) {
  return USERS.find(u => u.username === username && u.password === password) || null;
}
