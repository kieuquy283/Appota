'use client';

import React from 'react';
import { DemoUser } from '@/lib/types';

interface UserSelectorProps {
  users: DemoUser[];
  selectedUser: DemoUser | null;
  onSelectUser: (user: DemoUser) => void;
}

export const UserSelector: React.FC<UserSelectorProps> = ({
  users,
  selectedUser,
  onSelectUser,
}) => {
  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'PEOPLE_MANAGER':
      case 'MANAGER':
        return 'Quản lý';
      case 'HR':
        return 'Nhân sự';
      case 'EMPLOYEE':
      default:
        return 'Nhân viên';
    }
  };

  const getEmploymentLabel = (type: string) => {
    switch (type) {
      case 'FULL_TIME':
        return 'Toàn thời gian';
      case 'PART_TIME':
        return 'Bán thời gian';
      case 'INTERN':
        return 'Thực tập';
      case 'CONTRACTOR':
        return 'Hợp đồng';
      default:
        return 'Nhân sự';
    }
  };

  if (!users || users.length === 0) {
    return (
      <div style={{ fontSize: '0.82rem', color: '#EF4444', padding: '0.5rem 0' }}>
        Không có dữ liệu người dùng demo.
      </div>
    );
  }

  const currentUser = selectedUser || users[0];
  const teamPart =
    currentUser.team && currentUser.team !== currentUser.department
      ? ` · ${currentUser.team}`
      : '';

  return (
    <div>
      <select
        id="demo-user-selector"
        className="user-selector-select"
        value={currentUser.user_id}
        onChange={(e) => {
          const found = users.find((u) => u.user_id === e.target.value);
          if (found) {
            onSelectUser(found);
          }
        }}
      >
        {users.map((u) => (
          <option key={u.user_id} value={u.user_id}>
            {u.name} — {u.company} / {u.department}
          </option>
        ))}
      </select>

      <div className="user-card" id={`user-card-${currentUser.user_id}`}>
        <div className="user-card-header">
          <span className="user-card-name">{currentUser.name}</span>
          <span className="user-card-id">{currentUser.user_id}</span>
        </div>
        <div className="user-card-role-line">
          {getRoleLabel(currentUser.role)} · {currentUser.department}
          {teamPart}
        </div>
        <div className="user-chip-row">
          <span className="kg-chip kg-chip-company">{currentUser.company}</span>
          <span className="kg-chip kg-chip-type">
            {getEmploymentLabel(currentUser.employment_type)}
          </span>
        </div>
      </div>
    </div>
  );
};
