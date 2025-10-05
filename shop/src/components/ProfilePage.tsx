import { Header } from "./Header";
import { MinimalFooter } from "./MinimalFooter";
import { ProfileInfo } from "./ProfileInfo";
import { OrderHistory } from "./OrderHistory";
import { QuickActions } from "./QuickActions";
import { useState } from "react";

interface UserProfile {
  name: string;
  phone: string;
  avatar?: string;
}

export function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>({
    name: "Анна Смирнова",
    phone: "+7 (701) 234-56-78",
  });

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header />

        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
          <ProfileInfo 
            profile={profile} 
            onProfileChange={setProfile} 
          />
          
          <OrderHistory />
          
          <QuickActions />

          {/* Выход */}
          <div className="pb-[var(--spacing-6)]">
            <button className="w-full p-[var(--spacing-3)] text-button text-[var(--brand-error)] border border-[var(--brand-error)] rounded-[var(--radius-md)] hover:bg-[var(--brand-error)]/5 transition-colors">
              Выйти из аккаунта
            </button>
          </div>
        </div>

        <MinimalFooter />
      </div>
    </div>
  );
}