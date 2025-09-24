import { Outlet, useLocation } from "react-router-dom";
import NavBar from './components/NavBar'
import EmailVerificationBanner from './components/EmailVerificationBanner'

export default function Layout() {
    const location = useLocation();
    const hideNav = location.pathname === '/sign-in' || location.pathname === '/sign-up' || location.pathname === '/forgot-password';
    return (
        <>
        {!hideNav && <NavBar />}
        {!hideNav && <EmailVerificationBanner />}
        <Outlet />
        </>
    );
}