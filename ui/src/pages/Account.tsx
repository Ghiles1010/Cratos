import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { account } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

// ── Schemas ───────────────────────────────────────────────────────────────────

const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
});

const usernameSchema = z.object({
  new_username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type PasswordFormValues = z.infer<typeof passwordSchema>;
type UsernameFormValues = z.infer<typeof usernameSchema>;

// ── Change Password Card ──────────────────────────────────────────────────────

function ChangePasswordCard() {
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmit = async (values: PasswordFormValues) => {
    setSuccessMsg(null);
    setErrorMsg(null);
    try {
      const data = await account.changePassword(values.current_password, values.new_password);
      setSuccessMsg(data.detail || 'Password changed successfully');
      reset();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to change password');
    }
  };

  return (
    <div className="rounded-lg border border-border bg-bg-card overflow-hidden">
      <div className="border-b border-border px-5 py-3">
        <h2 className="text-sm font-semibold text-text-primary">Change Password</h2>
        <p className="mt-0.5 text-xs text-text-muted">Update your account password</p>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void handleSubmit(onSubmit)(e);
        }}
        className="p-5 space-y-4"
      >
        <Input
          id="current_password"
          type="password"
          label="Current Password"
          placeholder="Enter current password"
          error={errors.current_password?.message}
          {...register('current_password')}
        />
        <Input
          id="new_password"
          type="password"
          label="New Password"
          placeholder="Min. 8 characters"
          error={errors.new_password?.message}
          {...register('new_password')}
        />
        {successMsg && (
          <p className="text-sm text-emerald-400">{successMsg}</p>
        )}
        {errorMsg && (
          <p className="text-sm text-red-400">{errorMsg}</p>
        )}
        <Button type="submit" variant="primary" size="md" disabled={isSubmitting}>
          {isSubmitting ? 'Saving…' : 'Change password'}
        </Button>
      </form>
    </div>
  );
}

// ── Change Username Card ──────────────────────────────────────────────────────

function ChangeUsernameCard() {
  const { refreshUser } = useAuth();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<UsernameFormValues>({
    resolver: zodResolver(usernameSchema),
  });

  const onSubmit = async (values: UsernameFormValues) => {
    setSuccessMsg(null);
    setErrorMsg(null);
    try {
      const data = await account.changeUsername(values.password, values.new_username);
      setSuccessMsg(data.detail || 'Username changed successfully');
      reset();
      await refreshUser();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to change username');
    }
  };

  return (
    <div className="rounded-lg border border-border bg-bg-card overflow-hidden">
      <div className="border-b border-border px-5 py-3">
        <h2 className="text-sm font-semibold text-text-primary">Change Username</h2>
        <p className="mt-0.5 text-xs text-text-muted">Update your account username</p>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void handleSubmit(onSubmit)(e);
        }}
        className="p-5 space-y-4"
      >
        <Input
          id="new_username"
          type="text"
          label="New Username"
          placeholder="Enter new username"
          error={errors.new_username?.message}
          {...register('new_username')}
        />
        <Input
          id="username_password"
          type="password"
          label="Password"
          placeholder="Enter your password to confirm"
          error={errors.password?.message}
          {...register('password')}
        />
        {successMsg && (
          <p className="text-sm text-emerald-400">{successMsg}</p>
        )}
        {errorMsg && (
          <p className="text-sm text-red-400">{errorMsg}</p>
        )}
        <Button type="submit" variant="primary" size="md" disabled={isSubmitting}>
          {isSubmitting ? 'Saving…' : 'Change username'}
        </Button>
      </form>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Account() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Account</h1>
        <p className="mt-1 text-sm text-text-muted">
          Manage your account credentials
        </p>
      </div>

      <ChangePasswordCard />
      <ChangeUsernameCard />
    </div>
  );
}
