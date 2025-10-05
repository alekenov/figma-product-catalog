import { CvetyInput } from './ui/cvety-input';
import { useState } from 'react';

interface UserProfile {
  name: string;
  phone: string;
  avatar?: string;
}

interface ProfileInfoProps {
  profile: UserProfile;
  onProfileChange: (profile: UserProfile) => void;
}

export function ProfileInfo({ profile, onProfileChange }: ProfileInfoProps) {
  const [editingProfile, setEditingProfile] = useState(false);

  const handleSave = () => {
    setEditingProfile(false);
  };

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <div className="flex items-center justify-between">
        <h2 className="text-title text-[var(--text-primary)]">
          Мой профиль
        </h2>
        <button
          onClick={() => editingProfile ? handleSave() : setEditingProfile(true)}
          className="px-3 py-1 text-button-small text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] hover:bg-[var(--brand-primary)]/5 transition-colors"
        >
          {editingProfile ? "Сохранить" : "Редактировать"}
        </button>
      </div>

      <div className="flex items-center gap-[var(--spacing-4)]">
        <div className="w-16 h-16 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
          <span className="text-subtitle text-white">
            {profile.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </span>
        </div>

        <div className="flex-1 space-y-[var(--spacing-2)]">
          {!editingProfile ? (
            <>
              <h3 className="text-body-emphasis text-[var(--text-primary)]">
                {profile.name}
              </h3>
              <p className="text-caption text-[var(--text-secondary)]">
                {profile.phone}
              </p>
            </>
          ) : (
            <div className="space-y-[var(--spacing-2)]">
              <CvetyInput
                value={profile.name}
                onChange={(e) =>
                  onProfileChange({
                    ...profile,
                    name: e.target.value,
                  })
                }
                placeholder="Ваше имя"
              />
              <CvetyInput
                value={profile.phone}
                onChange={(e) =>
                  onProfileChange({
                    ...profile,
                    phone: e.target.value,
                  })
                }
                placeholder="Номер телефона"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}