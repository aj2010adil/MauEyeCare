import React from 'react';
import { useAuth } from './AuthContext';

interface RoleGuardProps {
  roles: string[];
  children: React.ReactNode;
}

const RoleGuard: React.FC<RoleGuardProps> = ({ roles, children }) => {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    // Redirect to unauthorized page or display a message
    return <div>Unauthorized</div>;
  }

  return <>{children}</>;
};

export default RoleGuard;