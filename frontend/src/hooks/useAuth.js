import { useAuthStore } from "../store";
import { authAPI, usersAPI } from "../api";

export function useAuth() {
  const { user, isLoggedIn, login, logout, setUser } = useAuthStore();

  const handleLogin = async (email, password) => {
    const res = await authAPI.login({ email, password });
    login(res.data.access, res.data.refresh, null);

    // Fetch user profile
    const profile = await usersAPI.profile();
    setUser(profile.data);
    return profile.data;
  };

  const handleLogout = () => logout();

  const fetchProfile = async () => {
    const res = await usersAPI.profile();
    setUser(res.data);
    return res.data;
  };

  return { user, isLoggedIn, handleLogin, handleLogout, fetchProfile };
}
