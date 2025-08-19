import { Outlet, useLocation } from "react-router-dom";
import NavBar from './pages/navBar'

export default function Layout() {
    const location = useLocation();
    const hideNav = location.pathname === '/sign-in';
    return (
        <>
        {!hideNav && <NavBar />}
        <Outlet />
        </>
    );
}