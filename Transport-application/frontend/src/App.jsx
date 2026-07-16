import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import ApplyPass from "./pages/ApplyPass.jsx";
import AadharConfirm from "./pages/AadharConfirm.jsx";

function isAuthed() {
  return Boolean(localStorage.getItem("token"));
}

function PrivateRoute({ children }) {
  return isAuthed() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <div className="page">
      <Routes>
        <Route path="/" element={<Navigate to={isAuthed() ? "/apply" : "/login"} replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/apply"
          element={
            <PrivateRoute>
              <ApplyPass />
            </PrivateRoute>
          }
        />
        <Route
          path="/confirm/:applicationId"
          element={
            <PrivateRoute>
              <AadharConfirm />
            </PrivateRoute>
          }
        />
      </Routes>
    </div>
  );
}
