import { Outlet } from "react-router-dom";
import NavBar from './pages/navBar'

export default function Layout() {
    return (
        <>
        <NavBar />
        <Outlet />
        </>
    );
}